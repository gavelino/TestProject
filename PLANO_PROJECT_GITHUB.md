# Plano de organização de Issues no GitHub Project

Este plano transforma o processo do documento `esboco_processo_v0.0.pdf` em um backlog executável no GitHub (milestones, issues e campos de projeto).

## 1) Estrutura recomendada do GitHub Project

### Campos personalizados (Project)
- **Tipo**: `Epic`, `Atividade`, `Entregável`, `Gate`.
- **Fase**: `Fase I - Exploração`, `Fase II - Viabilidade e Concepção`, `Fase III - MVP`, `Fase IV - Piloto`, `Fase V - Escala`.
- **Marco**: `M1`, `M2`, `M3`, `M4`, `M5`.
- **Status**: `Backlog`, `Pronto`, `Em andamento`, `Bloqueado`, `Em validação`, `Concluído`.
- **Órgão demandante**: texto curto.
- **Entregável principal**: texto curto.
- **Data alvo**: data.
- **Critério de saída atendido?**: `Sim`, `Não`, `Parcial`.

### Views (visões)
- **Board por Status** (Kanban de execução).
- **Tabela por Fase** (planejamento macro).
- **Timeline por Marco** (controle de datas e dependências).

### Labels
- `fase:i`, `fase:ii`, `fase:iii`, `fase:iv`, `fase:v`
- `tipo:epic`, `tipo:atividade`, `tipo:entregavel`, `tipo:gate`
- `risco:dados`, `risco:modelagem`, `risco:operacional`, `risco:etica-lgpd`
- `prioridade:alta`, `prioridade:media`, `prioridade:baixa`

---

## 2) Marcos (Milestones) e critérios de encerramento

## M1 — Fase I (Exploração)
**Objetivo do marco:** priorizar problemas e formalizar problema prioritário.

**Entregáveis obrigatórios:**
- Documento de Portfólio de Problemas e Oportunidades de IA.
- Documento de Detalhamento do Problema Priorizado.

**Gate de saída (M1):**
- Portfólio validado com o órgão demandante.
- Problemas priorizados com critérios acordados.
- Decisão explícita de continuidade/não continuidade.
- Problema prioritário detalhado para avançar à Fase II.

## M2 — Fase II (Viabilidade e Concepção)
**Objetivo do marco:** comprovar viabilidade e definir caso de uso/requisitos.

**Entregáveis obrigatórios:**
- Documento de Viabilidade Técnica, Científica e Operacional.
- Relatório EDA.
- Definição de métricas técnicas e critérios mínimos.
- Plano preliminar de desenvolvimento do MVP.
- Documento de Especificação do Caso de Uso de IA.

**Gate de saída (M2):**
- Viabilidade demonstrada com evidências.
- Principais riscos identificados e avaliados.
- Caso de uso refinado com base em evidências.
- Métricas técnicas e de impacto público definidas.
- Aprovação explícita para iniciar MVP.

## M3 — Fase III (Desenvolvimento de MVP)
**Objetivo do marco:** entregar MVP funcional em homologação.

**Entregáveis obrigatórios:**
- Repositório documentado com CI/CD.
- Pipeline de dados implementado e versionado.
- Dataset preparado/documentado.
- Modelo treinado (versão MVP).
- Relatório de avaliação offline.
- Protótipo funcional (API/serviço/aplicação).

**Gate de saída (M3):**
- MVP implantado em homologação.
- Métricas mínimas técnicas atendidas.
- Integração básica com legados validada.

## M4 — Fase IV (Piloto Controlado)
**Objetivo do marco:** validar valor e robustez em operação controlada.

**Entregáveis obrigatórios:**
- Relatório de Validação de Campo.
- Golden Set (dataset de curadoria do piloto).
- Parecer de Ajuste Ético.

**Gate de saída (M4):**
- Impacto positivo comprovado.
- Estabilidade técnica validada.
- Recomendação formal de escala.

## M5 — Fase V (Escala e Operação)
**Objetivo do marco:** operacionalizar e transferir tecnologia com governança.

**Entregáveis obrigatórios:**
- Release package (imagens/binários/scripts validados).
- Kit de Transferência Tecnológica (repositório, manuais, matriz de monitoramento).
- Termo de Transferência de Tecnologia.

**Gate de saída (M5):**
- Solução operacionalizada.
- Governança estabelecida.
- Encerramento formal do projeto.

---

## 3) Backlog inicial de Issues (sugestão pronta)

> Dica: crie **1 Epic por fase** e as atividades/entregáveis como sub-issues.

## Epic — Fase I: Exploração
1. **[Atividade] Levantar problemas e oportunidades com órgão demandante**
2. **[Atividade] Avaliar impacto público e complexidade preliminar**
3. **[Atividade] Priorizar portfólio com critérios acordados**
4. **[Entregável] Documento de Portfólio de Problemas e Oportunidades de IA**
5. **[Atividade] Detalhar problema prioritário (objetivos, stakeholders, dados, riscos)**
6. **[Entregável] Documento de Detalhamento do Problema Priorizado**
7. **[Gate] Validar critérios de saída da Fase I (M1)**

## Epic — Fase II: Viabilidade e Concepção
8. **[Atividade] Executar EDA e mapear qualidade/disponibilidade de dados**
9. **[Atividade] Avaliar viabilidade técnica, científica e operacional**
10. **[Atividade] Definir métricas técnicas e limiares mínimos de aceitação**
11. **[Atividade] Consolidar riscos e plano de mitigação**
12. **[Atividade] Especificar caso de uso de IA e requisitos (funcionais e não funcionais)**
13. **[Entregável] Documento de Viabilidade (técnica/científica/operacional)**
14. **[Entregável] Relatório EDA**
15. **[Entregável] Plano preliminar do MVP**
16. **[Entregável] Documento de Especificação do Caso de Uso de IA**
17. **[Gate] Aprovar avanço para MVP (M2)**

## Epic — Fase III: MVP
18. **[Atividade] Implementar pipeline de dados versionado**
19. **[Atividade] Treinar e versionar modelo MVP**
20. **[Atividade] Implementar avaliação offline e baseline comparativa**
21. **[Atividade] Configurar CI/CD do repositório**
22. **[Atividade] Implementar protótipo funcional (API/serviço/aplicação)**
23. **[Entregável] Repositório com CI/CD e documentação técnica**
24. **[Entregável] Pipeline + dataset preparado e documentado**
25. **[Entregável] Modelo MVP + relatório de avaliação offline**
26. **[Entregável] MVP em homologação**
27. **[Gate] Validar saída da Fase III (M3)**

## Epic — Fase IV: Piloto Controlado
28. **[Atividade] Implantar MVP em ambiente piloto controlado**
29. **[Atividade] Monitorar KPIs técnicos e de negócio no piloto**
30. **[Atividade] Coletar feedback de usuários e curar Golden Set**
31. **[Atividade] Avaliar salvaguardas éticas e conformidade operacional**
32. **[Entregável] Relatório de Validação de Campo**
33. **[Entregável] Golden Set do Piloto**
34. **[Entregável] Parecer de Ajuste Ético**
35. **[Gate] Recomendação formal para escala (M4)**

## Epic — Fase V: Escala e Operação
36. **[Atividade] Preparar release package de produção**
37. **[Atividade] Executar transferência tecnológica para órgão demandante**
38. **[Atividade] Definir e operacionalizar matriz de monitoramento/observabilidade**
39. **[Atividade] Formalizar governança, papéis e responsabilidades**
40. **[Entregável] Release package validado**
41. **[Entregável] Kit de Transferência Tecnológica**
42. **[Entregável] Termo de Transferência de Tecnologia assinado**
43. **[Gate] Encerramento formal do projeto (M5)**

---

## 4) Modelo de issue (padrão)

Use este template para padronizar todas as atividades:

```md
## Contexto
(qual fase/marco e problema que esta issue atende)

## Objetivo
(resultado objetivo da issue)

## Entregáveis
- [ ] item 1
- [ ] item 2

## Critérios de aceite
- [ ] critério mensurável 1
- [ ] critério mensurável 2

## Dependências
(issue #x, issue #y)

## Evidências
(links para documentos, dashboards, PRs, artefatos)
```

---

## 5) Sequenciamento recomendado (ordem de execução)

1. Criar milestones M1..M5.
2. Criar Epics por fase.
3. Criar issues de atividade/entregável e vincular aos Epics.
4. Preencher campos `Fase`, `Marco`, `Entregável principal`, `Data alvo`.
5. Criar 1 issue tipo `Gate` por marco e usar checklist dos critérios de saída.
6. Operar a cadência semanal: planejamento (segunda), status (meio da semana), revisão do gate (sexta).

---

## 6) Resultado esperado no Project

Ao final, você terá:
- Rastreabilidade completa entre fase → atividade → entregável → gate.
- Visão executiva por marcos (M1..M5).
- Clareza de responsabilidades e critérios objetivos de avanço.
- Base consistente para auditoria, governança e prestação de contas.
