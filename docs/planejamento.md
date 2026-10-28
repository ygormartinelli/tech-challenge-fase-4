# Plano de atividades

Planejamento inicial de 28/10/2026. Execução individual por Ygor, com prazo em 11/11/2026 e meta interna proposta de entrega em 09/11. Consulte o [cronograma](cronograma.md). A implementação foi autorizada; checklists só serão concluídos com evidências.

Fluxo: T01 → T02 → T03 → T04 → T05 → T06/T07 → T08 → T09 → T10 → T11. T06 e T07 podem avançar após T05. T09 pode ser preparada desde T01, mas só concluída após os resultados. T10 inclui integração de todas as etapas. A numeração estável permite vincular issues e commits.

Estados: Backlog → Em andamento → Em revisão → Concluído. Mover para Concluído apenas com checklist atendido e evidências vinculadas. Falhas ou decisões pendentes devem ser registradas na própria issue.

## T01 — Auditar e selecionar a base financeira

Dependências: nenhuma. Prioridade: alta.

- [x] Obter a candidata UCI; registrar origem, licença, atribuição e checksum.
- [x] Executar EDA: alvo, contagens, nulos, categorias, duplicatas, vazamento, distribuição e vieses potenciais.
- [x] Confirmar ≥5.000 registros reais utilizáveis; justificar tratamentos e exclusões.
- [x] Definir features, chave, alvo e separação sem sobreposição entre treino/referência, validação e produção.
- [x] Registrar decisão de aceite e conclusões que orientam contrato e simulação.

Aceite: relatório de auditoria e manifesto de dados revisáveis, com contagens antes/depois e limitações; nenhuma duplicação artificial para atingir o mínimo.

Evidências: notebook/relatório de EDA, metadados e decisão em `docs/dataset.md`.

## T02 — Preparar ambiente reproduzível e configuração

Dependências: T01. Prioridade: alta.

- [x] Verificar compatibilidade e escolher versões de Python, Pandera, Evidently, scikit-learn e MLflow.
- [x] Criar `pyproject.toml`, grupos de dependências de produção/desenvolvimento e `uv.lock`.
- [x] Configurar Ruff, pytest, paths, seeds e parâmetros externalizados.
- [x] Documentar e testar instalação limpa e importação das bibliotecas selecionadas.

Aceite: ambiente reproduzível pelo lockfile, sem dependências globais implícitas ou segredos versionados.

Evidências: arquivos de ambiente e comandos testados com saída registrada.

## T03 — Implementar contratos e bloquear lote inválido

Dependências: T01, T02. Prioridade: alta. Rubrica: validação, 25%.

- [x] Definir schemas de treino e inferência com pelo menos três regras rígidas baseadas nos dados.
- [x] Implementar validação anterior à transformação/inferência e falha explícita.
- [x] Criar lote válido e lote com violações conhecidas, sem expor registros reais nas mensagens.
- [x] Testar cada regra e comprovar que nenhum resultado de inferência é emitido para lote rejeitado.

Aceite: lote válido aceito, inválido bloqueado e motivo rastreável; alvo obrigatório apenas onde disponível/necessário.

Evidências: contrato, testes, comando de demonstração e logs sanitizados.

## T04 — Treinar e avaliar baseline de crédito

Dependências: T01, T02, T03. Prioridade: alta.

- [x] Treinar pipeline simples com pré-processamento ajustado apenas no treino e baseline ingênuo de comparação.
- [x] Avaliar em validação independente: ROC-AUC, PR-AUC, precision, recall e matriz de confusão, com limiar documentado.
- [x] Registrar seed, versões, features, tamanho das partições e ausência de IDs/target nas entradas.
- [x] Salvar modelo/metadados e verificar carregamento e predição reproduzível.

Aceite: modelo funcional com métricas reais e limitações, sem meta arbitrária de acurácia ou ajuste no conjunto de produção.

Evidências: artefato local do modelo, relatório de avaliação e manifesto das partições.

## T05 — Simular lotes de produção e data drift

Dependências: T03, T04. Prioridade: alta. Rubrica: drift, 25%.

- [x] Criar controle válido, lote inválido e cenários graduais de drift com seeds e parâmetros registrados.
- [x] Alterar pelo menos duas features relevantes justificadas pela EDA/modelo, preservando o contrato.
- [x] Gerar predições para lotes válidos com o baseline congelado.
- [x] Manter rastreabilidade dos registros originais e declarar a sequência temporal como simulada.

Aceite: cenários reproduzíveis e separados; drift estatístico não depende de violar o contrato; nenhuma amostra sintética contada como cliente independente.

Evidências: scripts, configuração e comparação das distribuições antes/depois.

## T06 — Detectar drift com Evidently e gerar HTML

Dependências: T05. Prioridade: alta. Rubrica: drift, 25%.

- [x] Comparar treino/referência versus controle e lotes de produção usando Evidently.
- [x] Definir e registrar PSI/KS ou métodos adequados a cada tipo, limiares, tamanhos e política de alertas.
- [x] Gerar relatório HTML e resumo estruturado com features afetadas, estatísticas e decisão de drift.
- [x] Verificar os cenários conhecidos e investigar alertas no controle; documentar magnitude e limitações dos testes.

Aceite: relatório abre e identifica as duas features alteradas com evidência estatística; resultados do controle também reportados.

Evidências: HTML sanitizado, métricas e testes de integração da geração de relatório.

## T07 — Demonstrar concept drift e limites causais

Dependências: T04, T05. Prioridade: alta.

- [x] Especificar mecanismo controlado que altera P(y|X), distinguindo-o de apenas alterar P(X).
- [x] Isolar e identificar rótulos sintéticos, sem sobrescrever os rótulos reais nem usá-los como validação do desempenho real.
- [x] Comparar métricas por cenário/janela quando rótulos estiverem disponíveis e definir regra de alerta de desempenho.
- [x] Explicar atraso de rótulos, incerteza, diferença entre alerta de drift e queda de desempenho e limites de inferência causal.

Aceite: demonstração explicitamente sintética com mecanismo conhecido e resultados reproduzíveis; nenhuma alegação de concept drift real derivada apenas de PSI/KS.

Evidências: configuração do mecanismo, avaliação comparativa e interpretação no README.

## T08 — Centralizar logs, métricas e rastreamento

Dependências: T03, T04, T06, T07. Prioridade: alta. Rubrica: observabilidade, 20%.

- [x] Correlacionar logs JSON e MLflow por execução, lote, cenário, modelo e versão dos dados.
- [x] Registrar status por etapa, latência, volumes recebidos/aceitos/rejeitados e alertas de falha/drift/desempenho.
- [x] Registrar falhas de contrato mesmo quando o pipeline encerra antecipadamente.
- [x] Evidenciar saúde operacional e recursos do processo/infraestrutura local com métricas documentadas.
- [x] Abrir a interface real do MLflow, inspecionar sucesso e falha e vincular relatórios e configurações.

Aceite: visualização funcional cobrindo saúde do pipeline e alertas; lista de métricas com significado, unidade e condição de alerta; complementar visualização se MLflow não cobrir a evidência necessária.

Evidências: runs, logs sanitizados e screenshots reais, com comandos de inicialização testados.

## T09 — Consolidar governança, privacidade e causalidade

Dependências: T01, T06, T07, T08. Prioridade: alta. Rubrica: governança, 15%.

- [x] Consolidar arquitetura, origem/licença, minimização, atributos pessoais e controle de acesso no README.
- [x] Fundamentar base legal no contexto acadêmico e no cenário de crédito usando fontes oficiais atuais.
- [x] Definir retenção, exclusão, responsáveis e revisão dos artefatos antes da publicação.
- [x] Analisar vieses por grupos com tamanho e incerteza reportados, limites de representatividade e mitigação.
- [x] Apresentar hipóteses causais, confundidores, limites do experimento e resposta operacional aos alertas.

Aceite: README completo, coerente com o que foi executado, sem alegar conformidade automática ou causalidade demonstrada por correlação/drift.

Evidências: seção consolidada no README com referências oficiais e resultados do projeto.

## T10 — Validar ponta a ponta e CI

Dependências: T02 a T09. Prioridade: alta.

- [x] Automatizar lint e testes relevantes no GitHub Actions usando dependências travadas.
- [x] Cobrir lote válido, bloqueio do inválido, ausência de sobreposição, simulação, relatórios e telemetria de falha.
- [x] Usar fixtures pequenas identificadas nos testes, sem apresentá-las como dataset acadêmico.
- [x] Reproduzir aquisição e execução completa em ambiente limpo com dados reais, registrando duração e resultados.
- [x] Revisar comandos do README, links, segredos e artefatos públicos; mapear cada critério para evidência verificável.

Aceite: CI aprovada e execução local completa documentada; distinguir o que CI testa do que foi validado manualmente, sem resultados fictícios.

Evidências: execução da CI, comandos testados e mapa final de evidências com commit/configuração.

## T11 — Gravar vídeo STAR e finalizar entrega

Dependências: T09, T10. Prioridade: alta. Rubrica: vídeo, 15%.

- [x] Preparar roteiro separado do README: situação, tarefa, ação e resultado.
- [ ] Gravar demonstração real do bloqueio, relatório de drift e monitoramento, incluindo aprendizados e limitações.
- [ ] Conferir duração de no máximo cinco minutos, áudio, legibilidade e acesso ao vídeo.
- [ ] Destacar link no início do README, revisar entrega e concluir issues com evidências.

Aceite: vídeo STAR acessível de até cinco minutos e repositório reproduzível, sem roteiro ou marcações de gravação no README final.

Evidências: link do vídeo, revisão final e checklist da rubrica concluído.
