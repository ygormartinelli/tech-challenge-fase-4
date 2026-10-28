"""Contratos rígidos; mensagens de erro expõem apenas regras, nunca clientes."""

import pandas as pd
import pandera.pandas as pa

from credit_monitoring.data import FEATURES, TARGET


class ContractViolation(ValueError):
    def __init__(self, rules: list[str]):
        self.rules = sorted(set(rules))
        super().__init__("Lote rejeitado pelas regras: " + ", ".join(self.rules))


def schema(labeled: bool = False) -> pa.DataFrameSchema:
    columns = {
        "id": pa.Column(int, pa.Check.gt(0), unique=True),
        "age": pa.Column(int, pa.Check.in_range(18, 120)),
        "sex": pa.Column(int, pa.Check.isin([1, 2])),
        "education": pa.Column(int, pa.Check.isin(range(7))),
        "marriage": pa.Column(int, pa.Check.isin(range(4))),
    }
    for feature in FEATURES:
        if feature == "limit_bal":
            check = pa.Check.gt(0)
        elif feature.startswith("pay_amt"):
            check = pa.Check.ge(0)
        elif feature.startswith("pay_"):
            check = pa.Check.isin(range(-2, 10))
        else:
            check = None  # Faturas negativas são permitidas na fonte.
        columns[feature] = pa.Column(int, check, nullable=False)
    if labeled:
        columns[TARGET] = pa.Column(int, pa.Check.isin([0, 1]))
    return pa.DataFrameSchema(columns, strict=True, coerce=False)


def validate(frame: pd.DataFrame, labeled: bool = False) -> pd.DataFrame:
    if frame.empty:
        raise ContractViolation(["empty_batch"])
    try:
        return schema(labeled).validate(frame, lazy=True)
    except pa.errors.SchemaErrors as error:
        # Não serializar failure_case, índice ou linhas do DataFrame.
        rules = [str(check) for check in error.failure_cases["check"].dropna().unique()]
        raise ContractViolation(rules) from None
