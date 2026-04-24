# TestProject

Projeto em construcao.

## Automacao para criar quadro, milestones e issues no GitHub

Para facilitar a criacao do **Project (quadro)**, **milestones** e **issues**, este repositorio inclui:

- `backlog_github_project.json`: backlog e estrutura de labels/marcos.
- `scripts/bootstrap_github_project.py`: automacao para provisionar no GitHub.

### 1) Simular (dry-run)

```bash
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO>
```

### 2) Aplicar de fato no GitHub

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --apply
```

### Definir cronograma estimado

Informe a data prevista de inicio do projeto para o script calcular as datas em sequencia:

```bash
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --project-start-date 2026-05-01
```

Ao usar `--apply`, o script:

- preenche a data alvo (`due_on`) dos milestones com base na ultima issue de cada marco;
- inclui no corpo de cada issue a sequencia, inicio estimado, fim estimado e duracao estimada;
- usa a mesma data de fim estimada para todas as issues associadas ao mesmo milestone: a data final do proprio milestone.

As duracoes podem ser configuradas no `backlog_github_project.json`:

```json
{
  "schedule": {
    "project_start_date": "2026-05-01",
    "default_issue_duration_days": 1
  },
  "issues": [
    {
      "title": "[Atividade] Exemplo",
      "milestone": "M1",
      "labels": ["fase:i", "tipo:atividade"],
      "estimated_days": 3
    }
  ]
}
```

Se `estimated_days` nao for informado em uma issue, o script usa `default_issue_duration_days`.

### 3) Criar tambem um Project v2 e incluir as issues

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --apply --create-project --project-title "Fabrica IA - Plano de Execucao"
```

### 4) Usar um Project v2 ja existente

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --apply --project-number <NUMERO_PROJECT>
```

### Escopos minimos (Classic Personal Access Token)

- Para criar/atualizar **issues** e **milestones** em repositorio privado:
  - `repo`
- Para operar **Project v2** (criar project/adicionar itens):
  - `project`
- Para consultar dados da **organizacao** via GraphQL (ex.: campo `organization { id }`):
  - `read:org`

> Se o token tiver apenas `repo` e `workflow`, consultas de organizacao no GraphQL podem falhar com `INSUFFICIENT_SCOPES`.
