# TestProject

Projeto em construção.

## Automação para criar quadro, milestones e issues no GitHub

Para facilitar a criação do **Project (quadro)**, **milestones** e **issues**, este repositório inclui:

- `backlog_github_project.json`: backlog e estrutura de labels/marcos.
- `scripts/bootstrap_github_project.py`: automação para provisionar no GitHub.

### 1) Simular (dry-run)

```bash
python3 scripts/bootstrap_github_project.py --owner <OWNER_REPO> --repo <NOME_REPO>
```

### 2) Aplicar de fato no GitHub

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python3 scripts/bootstrap_github_project.py --owner <OWNER_REPO> --repo <NOME_REPO> --apply
```

### Definir cronograma estimado

Informe a data prevista de início do projeto para o script calcular as datas em sequência:

```bash
python3 scripts/bootstrap_github_project.py --owner <OWNER_REPO> --repo <NOME_REPO> --project-start-date 2026-05-01
```

Ao usar `--apply`, o script:

- preenche a data alvo (`due_on`) dos milestones com base na última issue de cada marco;
- inclui no corpo de cada issue a sequência, início estimado, fim estimado e duração estimada;
- usa a mesma data de fim estimada para todas as issues associadas ao mesmo milestone: a data final do próprio milestone.

As durações podem ser configuradas no `backlog_github_project.json`:

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

Se `estimated_days` não for informado em uma issue, o script usa `default_issue_duration_days`.

### 3) Criar também um Project v2 vinculado ao repositório

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python3 scripts/bootstrap_github_project.py --owner <OWNER_REPO> --repo <NOME_REPO> --apply --create-project --project-title "Fábrica IA - Plano de Execução"
```

O GitHub Projects v2 exige que o Project seja criado sob um owner (`User` ou `Organization`). Depois de criar o Project, o script o vincula ao repositório com `linkProjectV2ToRepository`, para que ele fique associado ao repo em vez de ficar solto apenas na conta do usuário.

### 4) Usar um Project v2 já existente e vinculá-lo ao repositório

```bash
export GITHUB_TOKEN=<SEU_TOKEN>
python3 scripts/bootstrap_github_project.py --owner <OWNER_REPO> --repo <NOME_REPO> --apply --project-number <NUMERO_PROJECT>
```

### Permissões necessárias do token (`GITHUB_TOKEN`)

Para automações que criam/atualizam **milestones**, **issues** e **Project v2** via API do GitHub, use um token com as permissões abaixo.

#### Fine-grained Personal Access Token (recomendado)

- **Repository permissions**
  - `Issues: Read and write`
  - `Metadata: Read-only`
- **Account/Organization permissions** (quando houver operação com Project v2)
  - `Projects: Read and write`

#### Classic Personal Access Token

- `repo` (repositórios privados)
- `project` (Project v2)
- `read:org` (se o repositório pertencer a uma organização)

> Observações:
> - Se a organização usa SSO/SAML, é necessário autorizar o token na organização.
> - Se não for manipular Project v2, a permissão de `Projects` não é necessária.
> - Se o token tiver apenas `repo` e `workflow`, consultas de organização no GraphQL podem falhar com `INSUFFICIENT_SCOPES`.
