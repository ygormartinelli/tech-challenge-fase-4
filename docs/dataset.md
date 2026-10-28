# Seleção e auditoria do dataset

## Candidata recomendada

[Default of Credit Card Clients — UCI](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients), DOI [10.24432/C55S3H](https://doi.org/10.24432/C55S3H).

A página oficial informa 30.000 instâncias, 23 features e classificação binária de inadimplência, com licença CC BY 4.0 e download público. Há limite de crédito, idade, histórico de pagamentos e faturas. A recomendação atende ao tamanho e domínio descritos no enunciado, sujeita à auditoria do arquivo real.

Fonte consultada em 28/10/2026. Atribuição: Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H.

## Limitações a assumir

São dados históricos de Taiwan, com histórico mensal de 2005; não representam automaticamente o crédito brasileiro atual. O alvo é inadimplência de cartão, não uma decisão de aprovação de empréstimo. O cenário acadêmico deverá declarar essa aproximação. Limite de crédito não é renda, e a base não fornece desemprego para a simulação sugerida como exemplo no enunciado.

Auditoria local concluída em 28/10/2026: 30.000 registros, 25 colunas, nenhum nulo e 30.000 IDs únicos. Há 35 duplicatas exatas ignorando ID. Para impedir sobreposição de perfis usados pelo modelo, excluímos todos os 951 registros pertencentes a perfis financeiros repetidos (19 features), inclusive os membros originais. Restaram 29.049 observações: 17.429 de referência, 5.810 de validação e 5.810 de produção. A exclusão é conservadora e altera a população: prevalência de inadimplência passa de 22,12% para aproximadamente 21,54%. Essa limitação não deve ser omitida. A licença da base não define a licença do código.

As evidências agregadas estão em [audit.json](../reports/evidence/audit.json). O relatório inclui checksums, estatísticas, contagens, categorias, correlações exploratórias e manifesto das partições. Nenhuma linha individual é publicada.

## Conclusões da EDA que orientaram decisões

- Idades observadas: 21–79 anos. O contrato aceita 18–120 como domínio documentado do cenário adulto, não como inferência de qualidade baseada em quantis.
- Faturas negativas ocorrem em todos os meses (590–688 registros por coluna); preservá-las. Valores de pagamento e limite têm regras de domínio próprias.
- Educação inclui 0, 5 e 6; estado civil inclui 0. Preservar essas categorias como códigos de origem, sem inventar significados. Esses atributos não entram no modelo.
- Status de pagamento inclui -2 e 0, além das categorias descritas no catálogo. Preservar códigos e tratá-los categoricamente; uma simulação que soma atrasos é uma intervenção numérica simplificada, não uma transição econômica validada.
- Modelo: 19 features financeiras. ID, alvo, sexo, idade, escolaridade e estado civil excluídos das entradas. Sexo e idade usados somente em avaliação agregada de grupos.
- Dinheiro tem forte assimetria e outliers: transformação signed-log seguida de padronização; ajuste somente no treino.
- Desbalanceamento exige PR-AUC, recall e comparação ingênua, além de ROC-AUC. O limiar 0,5 é fixo para a demonstração, não uma política ótima de crédito.
- `pay_0` e `limit_bal` foram escolhidas para as intervenções. A primeira tentativa com `pay_amt_1` não acionou PSI ≥0,2, ilustrando a sensibilidade à discretização e caudas. O commit WIP preserva essa tentativa; o limiar não foi reduzido para fabricar um alerta.
- A base é aceita exclusivamente para a demonstração acadêmica, sem validação externa brasileira ou evidência de causalidade econômica real.

## Aquisição futura

`uv run credit-monitor audit` baixa o ZIP oficial, preserva-o em `data/raw/`, registra data/URL/checksum, lê o XLS e gera partições e relatório. Em reexecuções, confere o checksum registrado. Essa fonte tem acesso público; Ygor não precisa fornecer arquivo ou credenciais.

## Critérios para aceitar a base

- Confirmar ao menos 5.000 registros reais utilizáveis e alvo financeiro binário observado.
- Conferir chave, duplicatas exatas e de features, nulos, codificações não documentadas e inconsistências de domínio.
- Investigar vazamento pelo alvo, identificadores, variáveis posteriores ao evento e sobreposição entre subconjuntos.
- Descrever desbalanceamento, distribuições, outliers e atributos demográficos; distinguir valores raros válidos de erros.
- Definir pelo menos três regras rígidas justificadas pelo dicionário e pela auditoria. Não inventar renda nem impor limites arbitrários para faturas que podem admitir valores negativos.
- Verificar licença e atribuição; documentar minimização e limitações de representatividade.
- Registrar decisão de aceite ou rejeição e respectivas evidências antes de treinar.

Se Ygor preferir uma base própria ou as alternativas Home Credit/Lending Club, será necessário informar a fonte, o arquivo/dicionário e as condições de acesso e uso. Credenciais não devem ser enviadas pelo chat nem incluídas no repositório.
