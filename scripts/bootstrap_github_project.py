#!/usr/bin/env python3
"""Cria milestones, labels, issues e (opcionalmente) um Project v2 no GitHub.

Uso (dry-run):
  python scripts/bootstrap_github_project.py --owner ORG --repo REPO

Com cronograma estimado:
  python scripts/bootstrap_github_project.py --owner ORG --repo REPO --project-start-date 2026-05-01

Aplicar de fato:
  GITHUB_TOKEN=... python scripts/bootstrap_github_project.py --owner ORG --repo REPO --apply
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"
DATE_FORMAT = "%Y-%m-%d"


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Data invalida '{value}'. Use AAAA-MM-DD.") from exc


def add_days(start: date, days: int) -> date:
    if days < 1:
        raise ValueError("A duracao estimada deve ser maior ou igual a 1 dia")
    return start + timedelta(days=days - 1)


def iso_date(value: date) -> str:
    return value.strftime(DATE_FORMAT)


def schedule_issues(cfg: dict[str, Any], project_start_date: date | None) -> dict[str, dict[str, Any]]:
    """Calcula datas sequenciais e alinha o fim das issues ao fim do milestone."""
    if project_start_date is None:
        return {}

    default_duration = int(cfg.get("schedule", {}).get("default_issue_duration_days", 1))
    current_start = project_start_date
    issue_order: list[str] = []
    raw_schedule: dict[str, dict[str, Any]] = {}
    due_dates: dict[str, date] = {}

    for index, issue in enumerate(cfg["issues"], start=1):
        duration = int(issue.get("estimated_days", default_duration))
        finish = add_days(current_start, duration)
        issue_order.append(issue["title"])
        raw_schedule[issue["title"]] = {
            "sequence": index,
            "duration_days": duration,
            "start_date": current_start,
            "activity_end_date": finish,
            "milestone": issue["milestone"],
        }
        milestone = issue["milestone"]
        if milestone not in due_dates or finish > due_dates[milestone]:
            due_dates[milestone] = finish
        current_start = finish + timedelta(days=1)

    schedule: dict[str, dict[str, Any]] = {}
    for title in issue_order:
        item = raw_schedule[title]
        schedule[title] = {
            **item,
            "end_date": due_dates[item["milestone"]],
        }

    return schedule


def milestone_due_dates(issue_schedule: dict[str, dict[str, Any]]) -> dict[str, date]:
    out: dict[str, date] = {}
    for item in issue_schedule.values():
        milestone = item["milestone"]
        end_date = item["end_date"]
        if milestone not in out or end_date > out[milestone]:
            out[milestone] = end_date
    return out


def request_json(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} em {method} {url}: {body}") from exc


def graphql(token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    data = request_json("POST", GRAPHQL, token, {"query": query, "variables": variables})
    if "errors" in data:
        raise RuntimeError(f"GraphQL erro: {data['errors']}")
    return data["data"]


def ensure_milestones(
    owner: str,
    repo: str,
    token: str,
    cfg: dict[str, Any],
    apply: bool,
    due_dates: dict[str, date],
) -> dict[str, int]:
    url = f"{API}/repos/{owner}/{repo}/milestones?state=all&per_page=100"
    if not apply:
        print(f"[DRY-RUN] Consultaria milestones: {url}")
        for milestone, due_on in due_dates.items():
            print(f"[DRY-RUN] Milestone {milestone} teria data alvo {iso_date(due_on)}")
        return {}

    current = request_json("GET", url, token)
    by_title = {m["title"]: m["number"] for m in current}
    out: dict[str, int] = {}

    for m in cfg["milestones"]:
        due_on = due_dates.get(m["key"])
        if m["title"] in by_title:
            out[m["key"]] = by_title[m["title"]]
            print(f"[OK] Milestone ja existe: {m['title']} (#{by_title[m['title']]})")
            if due_on:
                request_json(
                    "PATCH",
                    f"{API}/repos/{owner}/{repo}/milestones/{by_title[m['title']]}",
                    token,
                    {"due_on": f"{iso_date(due_on)}T23:59:59Z"},
                )
                print(f"[OK] Data alvo atualizada: {m['title']} -> {iso_date(due_on)}")
            continue

        payload = {"title": m["title"], "description": m["description"]}
        if due_on:
            payload["due_on"] = f"{iso_date(due_on)}T23:59:59Z"
        created = request_json(
            "POST",
            f"{API}/repos/{owner}/{repo}/milestones",
            token,
            payload,
        )
        out[m["key"]] = created["number"]
        suffix = f" - vence em {iso_date(due_on)}" if due_on else ""
        print(f"[NEW] Milestone criada: {m['title']} (#{created['number']}){suffix}")

    return out


def ensure_labels(owner: str, repo: str, token: str, cfg: dict[str, Any], apply: bool) -> None:
    url = f"{API}/repos/{owner}/{repo}/labels?per_page=100"
    if not apply:
        print(f"[DRY-RUN] Consultaria labels: {url}")
        return

    current = request_json("GET", url, token)
    existing = {label["name"] for label in current}

    for label in cfg["labels"]:
        if label["name"] in existing:
            print(f"[OK] Label ja existe: {label['name']}")
            continue
        request_json(
            "POST",
            f"{API}/repos/{owner}/{repo}/labels",
            token,
            {
                "name": label["name"],
                "color": label["color"],
                "description": label["description"],
            },
        )
        print(f"[NEW] Label criada: {label['name']}")


def issue_body(issue: dict[str, Any], schedule: dict[str, Any] | None = None) -> str:
    schedule_block = ""
    if schedule:
        plural = "dia" if schedule["duration_days"] == 1 else "dias"
        schedule_block = (
            "\n## Planejamento\n"
            f"- Sequencia: {schedule['sequence']}\n"
            f"- Inicio estimado: {iso_date(schedule['start_date'])}\n"
            f"- Fim estimado: {iso_date(schedule['end_date'])}\n"
            f"- Duracao estimada: {schedule['duration_days']} {plural}\n"
        )

    return (
        "## Contexto\n"
        f"Fase/marco: **{issue['milestone']}**.\n\n"
        "## Objetivo\n"
        "Executar esta atividade conforme o processo da Fabrica de IA.\n\n"
        "## Entregaveis\n"
        "- [ ] Evidencia principal anexada\n"
        "- [ ] Criterios de aceite validados\n\n"
        "## Criterios de aceite\n"
        "- [ ] Resultado revisado com stakeholders\n"
        "- [ ] Registro no Project atualizado\n"
        f"{schedule_block}"
    )


def ensure_issues(
    owner: str,
    repo: str,
    token: str,
    cfg: dict[str, Any],
    milestones: dict[str, int],
    apply: bool,
    issue_schedule: dict[str, dict[str, Any]],
) -> list[str]:
    titles = [i["title"] for i in cfg["issues"]]
    if not apply:
        print(f"[DRY-RUN] Criaria {len(titles)} issues")
        for item in cfg["issues"]:
            schedule = issue_schedule.get(item["title"])
            if schedule:
                print(
                    "[DRY-RUN] "
                    f"{item['title']}: {iso_date(schedule['start_date'])} "
                    f"-> {iso_date(schedule['end_date'])} "
                    f"({schedule['duration_days']} dia(s))"
                )
        return titles

    current = request_json("GET", f"{API}/repos/{owner}/{repo}/issues?state=all&per_page=100", token)
    existing = {item.get("title"): item for item in current if "pull_request" not in item}

    created_titles: list[str] = []
    for item in cfg["issues"]:
        if item["title"] in existing:
            print(f"[OK] Issue ja existe: {item['title']}")
            created_titles.append(item["title"])
            continue

        payload = {
            "title": item["title"],
            "body": issue_body(item, issue_schedule.get(item["title"])),
            "labels": item["labels"],
            "milestone": milestones[item["milestone"]],
        }
        request_json("POST", f"{API}/repos/{owner}/{repo}/issues", token, payload)
        print(f"[NEW] Issue criada: {item['title']}")
        created_titles.append(item["title"])

    return created_titles


def get_project_owner_id(owner: str, token: str) -> str:
    query_owner = """
    query($login: String!) {
      organization(login: $login) { id }
      user(login: $login) { id }
    }
    """
    data = graphql(token, query_owner, {"login": owner})
    owner_id = data.get("organization", {}).get("id") if data.get("organization") else None
    if owner_id is None:
        owner_id = data.get("user", {}).get("id") if data.get("user") else None
    if owner_id is None:
        raise RuntimeError(f"Nao foi possivel resolver owner '{owner}' como organizacao ou usuario")
    return owner_id


def get_repository_id(owner: str, repo: str, token: str) -> str:
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) { id }
    }
    """
    data = graphql(token, query, {"owner": owner, "repo": repo})
    repository = data.get("repository")
    if repository is None:
        raise RuntimeError(f"Repositorio {owner}/{repo} nao encontrado")
    return repository["id"]


def create_project(owner: str, repo: str, token: str, title: str) -> str:
    owner_id = get_project_owner_id(owner, token)
    mutation = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id title number }
      }
    }
    """
    out = graphql(token, mutation, {"ownerId": owner_id, "title": title})
    p = out["createProjectV2"]["projectV2"]
    print(f"[NEW] Project criado: {p['title']} (number={p['number']})")
    link_project_to_repository(owner, repo, token, p["id"])
    return p["id"]


def get_project_id(owner: str, token: str, project_number: int) -> str:
    query = """
    query($login: String!, $number: Int!) {
      organization(login: $login) { projectV2(number: $number) { id title } }
      user(login: $login) { projectV2(number: $number) { id title } }
    }
    """
    data = graphql(token, query, {"login": owner, "number": project_number})
    org_p = data.get("organization", {}).get("projectV2") if data.get("organization") else None
    usr_p = data.get("user", {}).get("projectV2") if data.get("user") else None
    project = org_p or usr_p
    if not project:
        raise RuntimeError(f"Project number {project_number} nao encontrado em {owner}")
    print(f"[OK] Project encontrado: {project['title']}")
    return project["id"]


def link_project_to_repository(owner: str, repo: str, token: str, project_id: str) -> None:
    repository_id = get_repository_id(owner, repo, token)
    mutation = """
    mutation($projectId: ID!, $repositoryId: ID!) {
      linkProjectV2ToRepository(input: {projectId: $projectId, repositoryId: $repositoryId}) {
        repository { nameWithOwner }
      }
    }
    """
    out = graphql(token, mutation, {"projectId": project_id, "repositoryId": repository_id})
    linked_repo = out["linkProjectV2ToRepository"]["repository"]["nameWithOwner"]
    print(f"[OK] Project vinculado ao repositorio: {linked_repo}")


def add_issues_to_project(owner: str, repo: str, token: str, project_id: str, titles: list[str], apply: bool) -> None:
    if not apply:
        print(f"[DRY-RUN] Adicionaria {len(titles)} issues ao project {project_id}")
        return

    all_issues = request_json("GET", f"{API}/repos/{owner}/{repo}/issues?state=all&per_page=100", token)
    by_title = {i["title"]: i for i in all_issues if "pull_request" not in i}

    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }
    """

    for title in titles:
        issue = by_title.get(title)
        if not issue:
            print(f"[WARN] Issue nao encontrada para adicionar no project: {title}")
            continue
        graphql(token, mutation, {"projectId": project_id, "contentId": issue["node_id"]})
        print(f"[OK] Issue adicionada ao project: {title}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap de milestones/issues/project no GitHub")
    parser.add_argument("--owner", required=True, help="Owner do repositorio (organizacao ou usuario)")
    parser.add_argument("--repo", required=True, help="Nome do repositorio")
    parser.add_argument("--config", default="backlog_github_project.json", help="Arquivo JSON de configuracao")
    parser.add_argument("--apply", action="store_true", help="Executa alteracoes no GitHub")
    parser.add_argument("--create-project", action="store_true", help="Cria novo Project v2")
    parser.add_argument("--project-title", default="Fabrica IA - Plano de Execucao", help="Titulo do novo project")
    parser.add_argument("--project-number", type=int, help="Numero de Project v2 existente")
    parser.add_argument(
        "--project-start-date",
        type=parse_date,
        help="Data estimada de inicio do projeto no formato AAAA-MM-DD. Habilita calculo de prazos.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config(Path(args.config))

    project_start_date = args.project_start_date
    if project_start_date is None and cfg.get("schedule", {}).get("project_start_date"):
        project_start_date = parse_date(cfg["schedule"]["project_start_date"])
    issue_schedule = schedule_issues(cfg, project_start_date)
    due_dates = milestone_due_dates(issue_schedule)

    token = os.getenv("GITHUB_TOKEN", "")
    if args.apply and not token:
        print("ERRO: defina GITHUB_TOKEN para executar com --apply", file=sys.stderr)
        return 2

    milestones = ensure_milestones(args.owner, args.repo, token, cfg, args.apply, due_dates)
    ensure_labels(args.owner, args.repo, token, cfg, args.apply)
    titles = ensure_issues(args.owner, args.repo, token, cfg, milestones, args.apply, issue_schedule)

    if args.create_project or args.project_number:
        if not args.apply:
            print("[DRY-RUN] Criaria/encontraria project e adicionaria issues.")
        else:
            if args.create_project:
                project_id = create_project(args.owner, args.repo, token, args.project_title)
            else:
                project_id = get_project_id(args.owner, token, args.project_number)
                link_project_to_repository(args.owner, args.repo, token, project_id)
            add_issues_to_project(args.owner, args.repo, token, project_id, titles, args.apply)

    print("Concluido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
