# Configurações

`pipeline.json` centraliza fonte, seed, partições, modelo, intensidades dos cenários e limiares. O contrato de domínio está em `src/credit_monitoring/contracts.py` e muda junto com os testes e o dicionário. Configuração é registrada no MLflow; segredos nunca pertencem a estes arquivos. Caminhos de saída são relativos à raiz passada ao CLI.
