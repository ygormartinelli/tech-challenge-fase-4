# Tech Challenge — Fase 4

Observabilidade contínua, detecção de drift, qualidade de dados e governança de um modelo de risco de crédito.

Projeto acadêmico em preparação. O objetivo é demonstrar a sustentação e a confiabilidade de um classificador simples de crédito, com evidências reproduzíveis.

## Estado atual

Estrutura e planejamento criados. Dataset ainda não baixado ou auditado; contratos, modelo, simulações, relatórios, MLflow e CI ainda não implementados. Não há resultados experimentais nesta etapa.

- [Atividades, dependências e critérios de aceite](docs/planejamento.md)
- [Índice de issues no GitHub](docs/issues.md)
- [Arquitetura proposta e decisões](docs/arquitetura.md)
- [Dataset recomendado e critérios de seleção](docs/dataset.md)
- [Mapa da rubrica e evidências previstas](docs/criterios.md)

## Estrutura

```text
.github/ISSUE_TEMPLATE/  Modelo de atividade com aceite e evidências
configs/                Configurações de contrato, modelo, drift e observabilidade
data/raw/               Fonte original preservada, fora do Git
data/processed/         Referência, validação e produção separadas, fora do Git
docs/                   Planejamento, decisões e rastreabilidade
models/                 Modelos e metadados gerados, fora do Git
notebooks/              EDA com conclusões que orientam o pipeline
reports/                HTML, métricas e evidências sanitizadas
scripts/                Entradas para aquisição, pipeline e demonstração
src/credit_monitoring/  Implementação do pipeline e monitoramento
tests/                  Testes unitários e integração
```

Os diretórios são pontos de organização; nenhum módulo funcional foi implementado. Dependências de produção e desenvolvimento, versão Python, `pyproject.toml` e `uv.lock` serão definidos e validados na atividade T02. Os comandos de execução serão documentados após teste em ambiente limpo.

## Fluxo proposto

Fonte → auditoria e separação dos dados → contrato → transformação → treino/predição → comparação estatística → relatório e alertas. Logs estruturados e MLflow acompanharão as etapas. Lote inválido deverá encerrar o fluxo antes da transformação e da inferência.

O projeto usará uma base real para o baseline. Lotes com drift serão simulações identificadas. Mudança de distribuição, queda de desempenho e mudança da relação entre entrada e alvo serão tratadas como fenômenos distintos, com evidências próprias.

## Governança, privacidade e causalidade

Esta seção concentra o plano inicial e será completada com evidências na T09:

- **Finalidade e origem:** uso acadêmico de dados financeiros públicos; registrar fonte, licença, atribuição, versão e checksum. O uso público não substitui a avaliação de privacidade.
- **Minimização:** excluir identificadores das features, limitar atributos aos necessários e justificar o uso de atributos demográficos. Não registrar linhas de clientes nos logs, exemplos de falhas ou relatórios públicos.
- **Acesso e armazenamento:** dados e modelos locais fora do Git; segredos em ambiente local, nunca versionados. Publicar somente evidências revisadas e sanitizadas.
- **Base legal:** documentar separadamente o contexto acadêmico e o cenário hipotético de concessão de crédito, consultando a legislação e orientações oficiais aplicáveis. A base legal permanece pendente de análise contextual; este projeto não certifica conformidade jurídica.
- **Retenção:** definir responsável, prazo vinculado à finalidade acadêmica e procedimento de exclusão de dados, modelos, logs e backups; documentar exceções justificadas. Prazo ainda pendente.
- **Vieses:** comparar métricas por grupos quando o tamanho permitir, registrar incertezas e evitar que a exclusão de atributos protegidos seja apresentada como garantia de equidade.
- **Causalidade:** formular hipóteses e fatores de confusão; distinguir intervenções simuladas de evidência sobre a economia real. Drift de entrada não prova concept drift nem perda de acurácia. Uma simulação com mecanismo de rótulos alterado demonstra apenas o comportamento controlado especificado.
- **Resposta operacional:** definir responsável e ações de investigação para falha de contrato, drift e queda de desempenho; retreinamento dependerá de revisão e validação, sem disparo automático apenas por drift.

## Evidências e vídeo

O [mapa da rubrica](docs/criterios.md) identifica os resultados a produzir. Relatórios, screenshots e vídeo serão adicionados após execução real. O vídeo seguirá STAR e terá no máximo cinco minutos; seu link ficará destacado no início deste README quando disponível.

## Convenções

Documentação e comentários em português; código e identificadores em inglês. Commits semânticos, sem emojis. Issues só serão concluídas com critérios de aceite verificados e evidências. Não versionar datasets, ambientes, credenciais ou artefatos de execução por padrão.
