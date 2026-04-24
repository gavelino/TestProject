#!/usr/bin/env python3
"""Cria milestones, labels, issues e (opcionalmente) um Project v2 no GitHub.

Uso (dry-run):
  python scripts/bootstrap_github_project.py --owner ORG --repo REPO

Aplicar de fato:
  GITHUB_TOKEN=... python scripts/bootstrap_github_project.py --owner ORG --repo REPO --apply --create-project --project-title "Fábrica IA"
"""

from __future__ import annotations

import argparse
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


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def ensure_milestones(owner: str, repo: str, token: str, cfg: dict[str, Any], apply: bool) -> dict[str, int]:
    url = f"{API}/repos/{owner}/{repo}/milestones?state=all&per_page=100"
    if not apply:
        print(f"[DRY-RUN] Consultaria milestones: {url}")
        return {}

    current = request_json("GET", url, token)
    by_title = {m["title"]: m["number"] for m in current}
    out: dict[str, int] = {}

    for m in cfg["milestones"]:
        if m["title"] in by_title:
            out[m["key"]] = by_title[m["title"]]
            print(f"[OK] Milestone já existe: {m['title']} (#{by_title[m['title']]})")
            continue

        created = request_json(
            "POST",
            f"{API}/repos/{owner}/{repo}/milestones",
            token,
            {"title": m["title"], "description": m["description"]},
        )
        out[m["key"]] = created["number"]
        print(f"[NEW] Milestone criada: {m['title']} (#{created['number']})")

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
            print(f"[OK] Label já existe: {label['name']}")
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


def issue_body(issue: dict[str, Any]) -> str:
    return (
        "## Contexto\n"
        f"Fase/marco: **{issue['milestone']}**.\n\n"
        "## Objetivo\n"
        "Executar esta atividade conforme o processo da Fábrica de IA.\n\n"
        "## Entregáveis\n"
        "- [ ] Evidência principal anexada\n"
        "- [ ] Critérios de aceite validados\n\n"
        "## Critérios de aceite\n"
        "- [ ] Resultado revisado com stakeholders\n"
        "- [ ] Registro no Project atualizado\n"
    )


def ensure_issues(owner: str, repo: str, token: str, cfg: dict[str, Any], milestones: dict[str, int], apply: bool) -> list[str]:
    titles = [i["title"] for i in cfg["issues"]]
    if not apply:
        print(f"[DRY-RUN] Criaria {len(titles)} issues")
        return titles

    current = request_json("GET", f"{API}/repos/{owner}/{repo}/issues?state=all&per_page=100", token)
    existing = {item.get("title"): item for item in current if "pull_request" not in item}

    created_titles: list[str] = []
    for item in cfg["issues"]:
        if item["title"] in existing:
            print(f"[OK] Issue já existe: {item['title']}")
            created_titles.append(item["title"])
            continue

        payload = {
            "title": item["title"],
            "body": issue_body(item),
            "labels": item["labels"],
            "milestone": milestones[item["milestone"]],
        }
        request_json("POST", f"{API}/repos/{owner}/{repo}/issues", token, payload)
        print(f"[NEW] Issue criada: {item['title']}")
        created_titles.append(item["title"])

    return created_titles


def create_project(owner: str, token: str, title: str) -> str:
    query_owner = """
    query($login: String!) {
    #   organization(login: $login) { id }
      user(login: $login) { id }
    }
    """
    data = graphql(token, query_owner, {"login": owner})
    owner_id = data.get("organization", {}).get("id") if data.get("organization") else None
    if owner_id is None:
        owner_id = data.get("user", {}).get("id") if data.get("user") else None
    if owner_id is None:
        raise RuntimeError(f"Não foi possível resolver owner '{owner}' como organização ou usuário")

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
        raise RuntimeError(f"Project number {project_number} não encontrado em {owner}")
    print(f"[OK] Project encontrado: {project['title']}")
    return project["id"]


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
            print(f"[WARN] Issue não encontrada para adicionar no project: {title}")
            continue
        graphql(token, mutation, {"projectId": project_id, "contentId": issue["node_id"]})
        print(f"[OK] Issue adicionada ao project: {title}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap de milestones/issues/project no GitHub")
    parser.add_argument("--owner", required=True, help="Owner da organização ou usuário")
    parser.add_argument("--repo", required=True, help="Nome do repositório")
    parser.add_argument("--config", default="backlog_github_project.json", help="Arquivo JSON de configuração")
    parser.add_argument("--apply", action="store_true", help="Executa alterações no GitHub")
    parser.add_argument("--create-project", action="store_true", help="Cria novo Project v2")
    parser.add_argument("--project-title", default="Fábrica IA - Plano de Execução", help="Título do novo project")
    parser.add_argument("--project-number", type=int, help="Número de Project v2 existente")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config(Path(args.config))

    token = os.getenv("GITHUB_TOKEN", "")
    if args.apply and not token:
        print("ERRO: defina GITHUB_TOKEN para executar com --apply", file=sys.stderr)
        return 2

    milestones = ensure_milestones(args.owner, args.repo, token, cfg, args.apply)
    ensure_labels(args.owner, args.repo, token, cfg, args.apply)
    titles = ensure_issues(args.owner, args.repo, token, cfg, milestones, args.apply)

    if args.create_project or args.project_number:
        if not args.apply:
            print("[DRY-RUN] Criaria/encontraria project e adicionaria issues.")
        else:
            if args.create_project:
                project_id = create_project(args.owner, token, args.project_title)
            else:
                project_id = get_project_id(args.owner, token, args.project_number)
            add_issues_to_project(args.owner, args.repo, token, project_id, titles, args.apply)

    print("Concluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
