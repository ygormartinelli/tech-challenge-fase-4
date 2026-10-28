# Evidências e limites da validação

## Confirmação do fluxo válido

Nova execução completa em 28/10/2026 com `uv run credit-monitor run`, no commit `c1c0393e0a888ce299d8100f4c885cddb1807867`, árvore limpa. Execução **54c176366b40**, run de controle **01844b2da8dc43c9b77eae15b04fb32c**. O [JSON integral](../reports/evidence/confirmation-54c176366b40.json) preserva as métricas dessa execução, sem substituir a reprodução independente abaixo.

O controle recebeu e aceitou **5.810 registros**, produziu **5.810 predições** e rejeitou **zero** registros. Ingestão, validação, transformação, inferência e drift terminaram com `success`. A ROC-AUC foi **0,7713085508780955**, sem alertas de drift. O [print real do MLflow](../reports/evidence/mlflow-control.jpg) mostra `control`, `Finished`, `inference_success=1` e `inference_input_rows=5810`.

O simulador cria uma cópia separada denominada `invalid` e injeta idade de 12 anos, limite −1 e ID duplicado. As violações `in_range(18, 120)`, `greater_than(0)` e `field_uniqueness` rejeitam integralmente apenas essa cópia. Esse teste negativo não significa que o modelo deixou de funcionar. O controle e os cenários de drift concluem a inferência normalmente. Não foi necessário alterar código, regras ou dados para obter sucesso no controle.

## Execução reproduzida

Em 28/10/2026, o pipeline foi executado em uma cópia Git separada, com `.venv` novo e novo download da fonte pública. Comandos: `uv sync --locked`, `uv run pytest -q` e `uv run credit-monitor run`. A configuração é a padrão do repositório. A reprodução inicial usou `0b5d5b8`; após a correção de política/telemetria, a cópia foi atualizada por fast-forward e reexecutada.

Evidência final: execução **4fcf49530f99**, commit **bc0ae1abc23914fcd294acedab9761193fd4ae41**, árvore limpa (`working_tree_dirty=false`). O [summary.json](../reports/evidence/summary.json) registra versões, configuração, hashes, runs e métricas por etapa. Alterações posteriores de documentação/exportação não modificam o algoritmo validado.

## Resultados

| Verificação | Evidência |
| --- | --- |
| Base real e partições | [Auditoria agregada](../reports/evidence/audit.json): 30.000 registros, 29.049 após exclusão conservadora; referência 17.429, validação e produção 5.810 cada |
| Baseline e recarga | [Avaliação](../reports/evidence/training.json): ROC-AUC 0,765916, PR-AUC 0,524948; predições iguais após recarregar modelo |
| Bloqueio | Lote `invalid`: 5.810 rejeitados, zero predições, somente ingestão/validação executadas; status FAILED verificado na UI do MLflow |
| Controle | Zero features com drift; ROC-AUC 0,771309 |
| Drift severo | `pay_0` PSI 9,258705; `limit_bal` PSI 2,677119; duas features sinalizadas |
| Concept drift sintético | Entradas idênticas ao controle; ROC-AUC 0,491168; queda 0,280141 e alerta de desempenho |
| Testes locais | 13 testes aprovados, incluindo integração Evidently, bloqueio antes do modelo e ausência de sobreposição de perfis |
| CI | [Execução 40703144664](https://github.com/ygormartinelli/tech-challenge-fase-4/actions/runs/40703144664): sucesso em Windows e Ubuntu no commit `0b5d5b8`; consultar Actions para validações posteriores |
| Visualização | HTML consolidado e Evidently abertos no navegador; UI real do MLflow com runs, falhas e métricas operacionais inspecionada |

Relatórios publicados: [resumo HTML](../reports/evidence/index.html), [Evidently severo](../reports/evidence/drift_severe/evidently.html). Baixe o HTML para abrir no navegador: o GitHub exibe código em vez de executar HTML. Para reduzir duplicação de JavaScript no Git, somente um HTML Evidently é publicado; todos os quatro são gerados localmente pelo pipeline.

Capturas reais: [Evidently](../reports/evidence/evidently-drift.jpg) e [MLflow rejeitado](../reports/evidence/mlflow-rejected.jpg). As capturas foram feitas na cópia principal (run `155695f2ee9d` para o Evidently e `a060aa620fa2` para a rejeição), enquanto os JSON publicados vêm da reprodução independente. Os identificadores diferem deliberadamente; não representam a mesma execução.

## O que os testes cobrem

Contratos rejeitam idade inválida, limites/pagamentos negativos, status fora de domínio, nulos, ID repetido, colunas extras/ausentes e lote vazio. Faturas negativas válidas são aceitas. O teste com modelo espião verifica que lote rejeitado nunca alcança transformação/inferência. A partição exclui perfis repetidos e é determinística. A simulação preserva rótulos observados e produz o mesmo resultado sintético com a seed. Evidently não alerta sobre referência idêntica e identifica duas mudanças conhecidas.

CI usa fixtures sintéticas de teste; o tamanho delas não é usado para alegar atendimento ao mínimo acadêmico. Dados reais e reprodução completa foram conferidos localmente em Windows. Instalação e testes em Linux foram executados no GitHub Actions, sem a aquisição/execução completa da base real nesse sistema.

## Limitações registradas

- Dependências emitem avisos de depreciação do Evidently/NumPy e Litestar, sem falhar os testes. Não foram silenciados para aparentar limpeza.
- A UI do MLflow no Windows avisa sobre ausência de suporte ao executor de jobs. O projeto usa tracking local e CLI, ambos verificados; não depende desse executor.
- Recursos medidos são do processo, não uptime, pico de memória ou infraestrutura de produção.
- Controle sem alerta em uma única amostra não estima taxa de falso positivo. Não houve validação temporal real nem validação externa brasileira.
- Contrato, split e baseline são determinísticos; latência, memória, timestamps e IDs de execução variam. Não exigir igualdade desses valores para reproduzir a conclusão.
- Modelo, base individual, banco MLflow e logs completos permanecem locais. A publicação contém estatísticas agregadas; não foi realizado um estudo formal de risco de reidentificação.
- Vídeo, avaliação acadêmica e submissão ainda não realizados.
