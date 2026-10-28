# Apresentação da Fase 4

- [PowerPoint editável](Tech_Challenge_Fase4_STAR.pptx): 8 slides no formato STAR.
- [Roteiro de fala e fontes](Roteiro_Fase4.md): aproximadamente 4min40s, também incluído nas notas dos slides.

Os slides incluem prints reais do MLflow, Evidently e GitHub Actions. Os cenários alterados aparecem como simulações. Os números vêm dos arquivos em `reports/evidence/`, com links e identificação das execuções nas notas.

Na revisão de 28/10/2026, o slide 4 passou a destacar o funcionamento normal: **5.810 predições concluídas**, sem rejeições, na execução `54c176366b40`. O novo print do MLflow mostra o run `01844b2da8dc43c9b77eae15b04fb32c` com `Finished` e as métricas de inferência. O teste de lote inválido continua explicado como um cenário separado com erros inseridos propositalmente. A revisão alterou somente esse slide e seu roteiro; os outros sete slides mantiveram renderizações idênticas.

A evidência do CI corresponde ao commit `20bb848`, execução [40738193953](https://github.com/ygormartinelli/tech-challenge-fase-4/actions/runs/40738193953). O [print completo](../../reports/evidence/github-ci-main.jpg) está preservado. As capturas de MLflow e Evidently vêm das execuções locais indicadas em `docs/validacao.md`, enquanto as métricas consolidadas vêm da reprodução independente `4fcf49530f99`.

O PPTX passou por validação de estrutura, dimensões, fontes e tabelas nativas. Os oito slides foram renderizados após reimportar o arquivo final e revisados visualmente. Essa verificação não equivale a um teste dentro do aplicativo Microsoft PowerPoint.

Para ensaiar, use o modo do apresentador e as notas. A gravação e a submissão acadêmica ainda precisam ser feitas pelo autor.
