# Arquitetura proposta

## Escopo

Pipeline local por lotes, reproduzível e suficiente para demonstrar confiabilidade de um modelo simples. Decisões abaixo são propostas para implementação após a auditoria dos dados.

| Componente | Proposta | Motivo e condição |
| --- | --- | --- |
| Baseline | scikit-learn, regressão logística e baseline ingênuo | Comparação simples, pré-processamento ajustado somente no treino |
| Contratos | Pandera | Validar estrutura e regras antes de transformar ou inferir |
| Drift | Evidently, com PSI e/ou KS explicitamente configurados | A etapa detalhada e a rubrica citam Evidently; preferi-lo à alternativa Alibi |
| Observabilidade | Logs JSON e MLflow local | Centralizar ciclo de vida, parâmetros, métricas, alertas e artefatos por execução |
| Ambiente | uv, lockfile, Ruff e pytest | Instalação reproduzível e verificações automatizadas, versões a validar |

## Separação dos dados

Preservar a fonte bruta e sua soma de verificação. Auditar IDs e duplicatas antes de separar clientes em treino/referência, validação e produção simulada. Registrar proporções, seed, contagens e manifesto dos subconjuntos. Não tratar os meses nas colunas da UCI como novos registros independentes ou partição temporal real.

O treino servirá como referência exigida pelo enunciado; a validação independente sustentará a avaliação do modelo. O subconjunto de produção terá cenários de controle, dados inválidos e drift. Variações do mesmo cliente compartilharão a origem e nunca contarão como novas amostras reais. O alvo não será exigido para inferência; avaliações com rótulos ocorrerão em etapa separada.

## Cenários e interpretação

1. Controle válido: verificar execução completa e comportamento dos alertas sem intervenção planejada.
2. Lote inválido: injetar violações conhecidas e comprovar bloqueio anterior à inferência, com motivo sanitizado.
3. Data drift: alterar pelo menos duas features relevantes, escolhidas após EDA, mantendo o lote válido e registrando intensidade, seed e regras de transformação. Uma hipótese inicial é alterar limite de crédito e padrão de pagamentos; a seleção depende dos dados.
4. Concept drift controlado: definir explicitamente um mecanismo sintético de mudança de P(y|X), manter rótulos sintéticos identificados e isolados e comparar desempenho sob esse mecanismo. Não sobrescrever os rótulos observados nem afirmar descoberta de concept drift real. O mecanismo será documentado antes da execução; o baseline continuará treinado nos dados reais.

Comparar distribuições com métodos e limiares registrados antes da execução, reportar magnitude e tamanho amostral e tratar múltiplas comparações quando pertinente. Rótulos originais não representam necessariamente o resultado contrafactual de features manipuladas; métricas nesse cenário exigem interpretação explícita.

## Telemetria prevista

Cada execução terá `run_id`, `batch_id`, cenário, versão dos dados/modelo/configuração e seed. Registrar status e duração de ingestão, validação, transformação, inferência e monitoramento; volumes recebidos, aceitos e rejeitados; contagem de alertas por tipo e quantidade/proporção de features com drift. Consolidar inclusive execuções interrompidas por contrato.

MLflow deverá permitir inspeção visual de execuções válidas e falhas e seus relatórios. Registrar também recursos observáveis do processo, como memória e CPU, se necessários para evidenciar a infraestrutura local; a decisão e a forma de medição serão validadas na T08. Se o ambiente não evidenciar a saúde exigida, complementar a visualização na própria T08.

## Limites

API, Airflow, Kubernetes, deploy e reaproveitamento da infraestrutura da Fase 3 não fazem parte desta estrutura inicial. A adição de infraestrutura dependerá de necessidade demonstrada pelos critérios de aceite.
