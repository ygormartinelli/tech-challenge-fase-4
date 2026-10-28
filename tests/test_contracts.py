import pytest

from credit_monitoring.contracts import ContractViolation, validate


def test_valid_batch_and_negative_bill(valid_batch):
    valid_batch.loc[0, "bill_amt_1"] = -100
    assert len(validate(valid_batch)) == 20


@pytest.mark.parametrize(
    "column,value",
    [
        ("age", 17),
        ("limit_bal", -1),
        ("pay_amt_1", -1),
        ("pay_0", 10),
        ("sex", 0),
    ],
)
def test_domain_violations(valid_batch, column, value):
    valid_batch.loc[0, column] = value
    with pytest.raises(ContractViolation):
        validate(valid_batch)


def test_duplicate_id(valid_batch):
    valid_batch.loc[1, "id"] = valid_batch.loc[0, "id"]
    with pytest.raises(ContractViolation):
        validate(valid_batch)


def test_missing_value_is_rejected_without_leaking_value(valid_batch):
    valid_batch["limit_bal"] = valid_batch.limit_bal.astype(float)
    valid_batch.loc[0, "limit_bal"] = float("nan")
    with pytest.raises(ContractViolation) as error:
        validate(valid_batch)
    assert "failure_case" not in str(error.value)


def test_extra_missing_empty_and_unlabeled(valid_batch):
    validate(valid_batch)
    for invalid in [valid_batch.assign(secret=1), valid_batch.drop(columns="age"), valid_batch[:0]]:
        with pytest.raises(ContractViolation):
            validate(invalid)
    with pytest.raises(ContractViolation):
        validate(valid_batch, labeled=True)
