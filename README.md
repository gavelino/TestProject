# TestProject

Projeto em construção.

## Automação para criar quadro, milestones e issues no GitHub

Para facilitar a criação do **Project (quadro)**, **milestones** e **issues**, este repositório inclui:

- `backlog_github_project.json`: backlog e estrutura de labels/marcos.
- `scripts/bootstrap_github_project.py`: automação para provisionar no GitHub.

### 1) Simular (dry-run)

```bash
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO>
```

### 2) Aplicar de fato no GitHub

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --apply
```

### 3) Criar também um Project v2 e incluir as issues

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --apply --create-project --project-title "Fábrica IA - Plano de Execução"
```

### 4) Usar um Project v2 já existente

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python scripts/bootstrap_github_project.py --owner <ORG_OU_USUARIO> --repo <NOME_REPO> --apply --project-number <NUMERO_PROJECT>
```

### Escopos mínimos (Classic Personal Access Token)

- Para criar/atualizar **issues** e **milestones** em repositório privado:
  - `repo`
- Para operar **Project v2** (criar project/adicionar itens):
  - `project`
- Para consultar dados da **organização** via GraphQL (ex.: campo `organization { id }`):
  - `read:org`

> Se o token tiver apenas `repo` e `workflow`, consultas de organização no GraphQL podem falhar com `INSUFFICIENT_SCOPES`.
