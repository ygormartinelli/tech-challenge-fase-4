# Seleção e auditoria do dataset

## Candidata recomendada

[Default of Credit Card Clients — UCI](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients), DOI [10.24432/C55S3H](https://doi.org/10.24432/C55S3H).

A página oficial informa 30.000 instâncias, 23 features e classificação binária de inadimplência, com licença CC BY 4.0 e download público. Há limite de crédito, idade, histórico de pagamentos e faturas. A recomendação atende ao tamanho e domínio descritos no enunciado, sujeita à auditoria do arquivo real.

Fonte consultada em 28/10/2026. Atribuição: Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H.

## Limitações a assumir

São dados históricos de Taiwan, com histórico mensal de 2005; não representam automaticamente o crédito brasileiro atual. O alvo é inadimplência de cartão, não uma decisão de aprovação de empréstimo. O cenário acadêmico deverá declarar essa aproximação. Limite de crédito não é renda, e a base não fornece desemprego para a simulação sugerida como exemplo no enunciado.

Não há validação local ainda. A quantidade informada pelo catálogo deve ser conferida após leitura e tratamento, sem replicar linhas para satisfazer o mínimo de 5.000 amostras. A licença da base não define a licença do código do projeto.

## Aquisição futura

Na T01, obter o arquivo pelo botão de download da página oficial ou pelo cliente UCI, registrar data, URL, checksum, formato e dicionário. Manter o arquivo em `data/raw/`, ignorado pelo Git. Essa fonte tem acesso público; Ygor não precisa fornecer um arquivo ou credenciais neste momento.

## Critérios para aceitar a base

- Confirmar ao menos 5.000 registros reais utilizáveis e alvo financeiro binário observado.
- Conferir chave, duplicatas exatas e de features, nulos, codificações não documentadas e inconsistências de domínio.
- Investigar vazamento pelo alvo, identificadores, variáveis posteriores ao evento e sobreposição entre subconjuntos.
- Descrever desbalanceamento, distribuições, outliers e atributos demográficos; distinguir valores raros válidos de erros.
- Definir pelo menos três regras rígidas justificadas pelo dicionário e pela auditoria. Não inventar renda nem impor limites arbitrários para faturas que podem admitir valores negativos.
- Verificar licença e atribuição; documentar minimização e limitações de representatividade.
- Registrar decisão de aceite ou rejeição e respectivas evidências antes de treinar.

Se Ygor preferir uma base própria ou as alternativas Home Credit/Lending Club, será necessário informar a fonte, o arquivo/dicionário e as condições de acesso e uso. Credenciais não devem ser enviadas pelo chat nem incluídas no repositório.
