# Roteiro de apresentação — Tech Challenge Fase 4

8 slides. Tempo sugerido: 4min40s. As mesmas falas estão nas notas do PowerPoint.

## Slide 1 — 25 s

Um modelo de crédito pode continuar gerando previsões mesmo quando os dados estão errados ou o comportamento dos clientes muda. Na Fase 4, trabalhei na sustentação desse modelo: como perceber problemas, bloquear entradas inválidas e reunir evidências para investigar uma queda de desempenho. Vou apresentar o fluxo e os resultados dos cenários de teste.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4
- Referência visual: Tech_Challenge_Fase3_STAR_Urgencia.pptx, apresentação pessoal da Fase 3.

## Slide 2 — 30 s

Organizei o pipeline em etapas com responsabilidades claras. O Pandera verifica o contrato antes da predição. O modelo do scikit-learn produz probabilidades. O Evidently compara a distribuição de cada variável com a referência. O MLflow e os logs registram o que aconteceu em cada execução. Para validar o comportamento, executei cinco cenários: controle, dados inválidos, drift moderado, drift severo e uma simulação de concept drift.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/README.md
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/docs/validacao.md

## Slide 3 — 40 s

Usei a base pública Default of Credit Card Clients, da UCI, com trinta mil registros. A auditoria identificou 951 registros pertencentes a perfis financeiros duplicados. Excluí esse conjunto de forma conservadora para evitar sobreposição entre partições. Restaram 29.049 registros, separados em treino, validação e produção simulada. O modelo usa dezenove variáveis financeiras. Na validação, a regressão logística alcançou ROC-AUC de 0,766 e PR-AUC de 0,525. O recall de 0,364 mostra uma limitação importante no limiar escolhido. O objetivo aqui é demonstrar sustentação, sem afirmar prontidão para concessão de crédito.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/audit.json
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/training.json
- https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients

## Slide 4 — 35 s

Neste teste, o lote violou o contrato de dados. As regras incluem identificador único e positivo, faixa de idade válida e limite de crédito maior que zero, além de tipos, nulidade e outras restrições. O pipeline rejeitou o lote inteiro, com 5.810 registros, antes de gerar qualquer predição. O print mostra a execução invalid no MLflow com status Failed. Esse status é esperado: ele registra a rejeição controlada. Assim, uma entrada inválida fica rastreável e não avança silenciosamente pelo fluxo.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/summary.json
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/mlflow-rejected.jpg
- Print da execução local a060aa620fa2, run e7cc6483b67c418c9fc37aeef955171f. A reprodução independente documenta o mesmo comportamento com outros IDs.

## Slide 5 — 40 s

No cenário severo, alterei de forma controlada o limite de crédito e o status de atraso. O Evidently detectou exatamente essas duas variáveis, entre as dezenove monitoradas. O recorte do relatório mostra o PSI de 9,259 em pay_0 e de 2,677 em limit_bal, acima do limiar de 0,20. O relatório completo está salvo em HTML. Também calculei o teste KS como análise complementar, com correção para múltiplas comparações. O cenário de controle não gerou alertas de drift. Esses resultados demonstram a resposta do monitor às mudanças simuladas, sem atribuir uma causa econômica real.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/evidently-drift.jpg
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/drift_severe/evidently.html
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/summary.json
- Print da execução local 155695f2ee9d. O recorte amplia somente o resumo e as duas primeiras linhas. Relatório completo preservado no repositório.

## Slide 6 — 35 s

Para testar concept drift, mantive as entradas iguais às do controle e alterei os rótulos apenas em uma cópia de simulação, em um segmento definido pelas variáveis financeiras. Os rótulos originais foram preservados. Com isso, o monitor de distribuição continuou sem alertas, mas a ROC-AUC caiu de 0,771 para 0,491. A queda de 0,280 acionou o monitor de desempenho. O experimento mostra por que precisamos acompanhar resultados quando os rótulos chegam, além de monitorar as entradas.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/reports/evidence/summary.json
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/docs/validacao.md
- Simulação: probabilidade 0,8 de inverter rótulos no segmento pay_0 <= 0 e bill_amt_1 acima da mediana da referência. Não representa mudança real observada.

## Slide 7 — 30 s

A implementação está integrada à main com o histórico de commits preservado. O print do GitHub Actions mostra a execução aprovada no commit 20bb848, tanto no Ubuntu quanto no Windows. Cada ambiente passou pelos treze testes, além das verificações de estilo. A reprodução independente também registrou hashes dos dados, do modelo e da configuração. Nos logs, cada etapa inclui status, duração, volume, CPU e memória. Isso permite relacionar uma evidência ao código e à execução que a produziram.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/actions/runs/40738193953
- https://github.com/ygormartinelli/tech-challenge-fase-4/commit/20bb84803073268c580a4b154ab59f9de5c0a89b
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/docs/validacao.md
- CI capturado em 28/10/2026. Reprodução independente: execução 4fcf49530f99, commit bc0ae1abc23914fcd294acedab9761193fd4ae41. O código funcional, configuração e testes são os mesmos do merge 20bb848.

## Slide 8 — 45 s

O principal aprendizado foi separar problemas de qualidade, mudanças de distribuição e perda de desempenho. Cada problema exige uma evidência e uma resposta diferente. Na governança, documentei minimização dos dados, auditoria por grupos e limites de uso. Excluir atributos demográficos do preditor não elimina possíveis vieses, porque outras variáveis podem funcionar como proxies. A base é histórica e de Taiwan, então aplicar o modelo no Brasil exigiria nova validação. Os alertas orientam investigação e revisão humana. O repositório reúne código, relatórios, testes e histórico para que os resultados possam ser conferidos.

Fontes:
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/README.md
- https://github.com/ygormartinelli/tech-challenge-fase-4/blob/main/docs/validacao.md