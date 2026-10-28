# Operação e resposta aos alertas

Executar os comandos a partir da raiz do repositório. Configuração em `configs/pipeline.json`; sementes e parâmetros são registrados em cada execução. O pipeline é local por lotes, sem agendamento ou serviço remoto.

## Métricas

| Métrica | Unidade | Interpretação |
| --- | --- | --- |
| `<etapa>_success` | 0/1 | Sucesso da etapa; etapas posteriores a uma falha não executam |
| `<etapa>_seconds` | segundos | Latência medida com relógio monotônico |
| `<etapa>_input_rows` | registros | Volume entregue à etapa |
| `<etapa>_cpu_seconds` | segundos de CPU | CPU consumida pelo processo durante a etapa |
| `<etapa>_rss_mb` | MiB | Memória residente ao final da etapa; não é pico nem série temporal |
| `received_rows`, `accepted_rows`, `rejected_rows` | registros | Rejeição é integral por lote |
| `drifted_features_count/share` | contagem/proporção | Colunas com PSI ≥0,2 |
| `psi_<feature>` | adimensional | Magnitude do PSI calculada pelo Evidently |
| `alerts` | eventos | Uma falha de contrato, um alerta por feature e um alerta por queda de desempenho |
| `performance_roc_auc`, `performance_pr_auc` | 0–1 | Apenas cenários com alvo observado ou sintético identificado |

Logs JSONL em `logs/pipeline.jsonl`, resultados em `reports/generated/<execução>/summary.json` e runs no MLflow compartilham `run_id`/cenário. O run pai tem commit, indicação de alterações locais, configuração, versões e modelo; os filhos têm hashes de origem/modelo. A execução com contrato inválido aparece como `FAILED`, mesmo quando a demonstração geral termina conforme esperado.

## Política de drift

PSI ≥0,2 por feature aciona investigação; o alerta global do Evidently usa fração mínima 1/19, equivalente a pelo menos uma feature das 19 monitoradas. A hipótese de drift é exploratória: o limiar é heurístico, não uma probabilidade de erro. KS é complementar, com α familiar de 0,05 dividido por 19 (Bonferroni); em variáveis discretas os p-valores têm limitações. A discretização do PSI afeta sua sensibilidade.

O controle independente fornece uma observação de falsos alertas, não uma estimativa confiável da taxa de falso positivo. Em produção real seriam necessárias várias janelas e calibração prévia com histórico estável.

Para a demonstração de concept drift, a queda de ROC-AUC de pelo menos 0,1 em relação ao controle aciona um alerta. São os mesmos X com rótulos sintéticos modificados; o resultado não estima desempenho futuro real. Sem rótulos, só é possível alertar sobre mudanças observáveis de entrada/predição.

## Resposta operacional

Responsável acadêmico: Ygor. Falha de contrato: isolar lote, verificar esquema e origem, corrigir na fonte e reprocessar com novo identificador; não flexibilizar silenciosamente a regra. Drift: revisar distribuições, mudanças de produto/coleta e representatividade; examinar magnitude e rótulos quando disponíveis. Queda de desempenho: comparar grupos e custos, investigar causa e avaliar fallback/revisão humana no cenário de negócio. Retreinamento só após dados auditados, avaliação independente e decisão registrada.

Falhas inesperadas propagam erro e encerram a execução; MLflow e logs guardam a etapa que falhou. Somente a rejeição esperada do cenário `invalid` é tratada como parte da demonstração. Não há acionamento externo por email/SMS nem retreinamento automático.

## Interpretação da infraestrutura

Memória, CPU, latência e status demonstram a execução local. Não são SLO de disponibilidade de uma fintech. A UI do MLflow é ligada a `127.0.0.1`, sem exposição pública; suporte a execução de jobs do MLflow no Windows não é necessário, pois o pipeline é executado pelo CLI. Modelos são salvos como artefatos, sem registro de implantação.
