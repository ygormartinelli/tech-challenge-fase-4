# Rubrica e evidências de aceitação

Fonte: documento “MLET - Tech Challenge - Fase 4.md”, lido integralmente em 28/10/2026. Etapas técnicas executadas; evidências em [validacao.md](validacao.md). Vídeo pendente.

| Critério | Peso | Atividades | Evidência esperada |
| --- | --- | --- | --- |
| Validação de dados | 25% | T01, T03, T04 | Contrato com ≥3 regras, lote válido aceito, inválido bloqueado antes da inferência, teste e log sanitizado, baseline treinado |
| Detecção de drift | 25% | T05, T06, T07 | ≥2 features alteradas, predições, comparação referência/produção via Evidently, método/limiar e HTML com variáveis afetadas |
| Observabilidade e logs | 20% | T08 | MLflow/visualização funcionando, logs correlacionados, status, latência, volumes e alertas de sucesso e falha |
| Governança e LGPD | 15% | T09 | README com arquitetura, origem, minimização, base legal contextualizada, retenção, vieses e análise causal |
| Vídeo STAR | 15% | T11 | Vídeo de até 5 minutos com execução real, resultados e limitações; link destacado no README |

Requisitos transversais: histórico semântico, classificação financeira binária com ≥5.000 amostras, separação entre referência e análise, reprodução em ambiente limpo (T10). O contexto também exige abordagem de concept drift, tratada na T07 com mecanismo controlado e limitações explícitas.

Comandos, commit, configuração/seed, resultados, capturas e limitações estão em [validacao.md](validacao.md), [summary.json](../reports/evidence/summary.json), [audit.json](../reports/evidence/audit.json) e [training.json](../reports/evidence/training.json). Governança e análise causal estão consolidadas no README. T11 permanece aberta até gravação, link e revisão final.
