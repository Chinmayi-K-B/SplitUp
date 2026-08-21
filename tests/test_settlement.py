from app.settlement import minimize_transactions


def test_two_person_split():
    balances = {
        1: 500.0,
        2: -500.0,
    }

    result = minimize_transactions(balances)

    assert len(result) == 1
    assert result[0] == (2, 1, 500.0)


def test_multi_person_split():
    balances = {
        1: 1000.0,
        2: -500.0,
        3: -300.0,
        4: -200.0,
    }

    result = minimize_transactions(balances)

    # Three debtors can settle with the single creditor
    # using exactly three transactions.
    assert len(result) == 3

    # Verify that every transaction involves a valid amount.
    assert all(amount > 0 for _, _, amount in result)


def test_already_settled_group():
    balances = {
        1: 0.0,
        2: 0.0,
        3: 0.0,
    }

    result = minimize_transactions(balances)

    assert result == []