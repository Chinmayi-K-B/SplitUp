from typing import Dict, List, Tuple


def minimize_transactions(
    balances: Dict[int, float],
) -> List[Tuple[int, int, float]]:
    """
    Find a settlement plan using the minimum possible number of transactions.

    Parameters
    ----------
    balances : Dict[int, float]
        Maps user_id to their net balance.

        Positive balance -> user should receive money.
        Negative balance -> user owes money.
        Zero balance     -> user is already settled.

    Returns
    -------
    List[Tuple[int, int, float]]
        Each tuple represents:

            (payer, receiver, amount)

        Example:
            (2, 1, 500.0)

        means user 2 pays user 1 Rs. 500.

    Approach
    --------
    The algorithm first uses exact backtracking to determine the
    minimum possible number of transactions.

    A greedy settlement is then generated separately. If the greedy
    plan uses the same minimum number of transactions, it is returned
    because it produces practical transactions where no payer pays
    more than their remaining debt.

    If greedy cannot achieve the minimum transaction count, the exact
    backtracking solution is returned.

    Money is converted to integer paise before calculation to avoid
    floating-point precision problems.

    Time Complexity
    ---------------
    Exact backtracking: exponential in the number of users with
    non-zero balances.

    Greedy settlement: O(n log n), dominated by sorting.

    Space Complexity
    ----------------
    O(n) for the working balance lists and recursion depth.
    """

    # Convert rupees to integer paise for exact calculations.
    working_balances = [
        (user_id, round(balance * 100))
        for user_id, balance in balances.items()
        if round(balance * 100) != 0
    ]

    # A valid settlement must have total balance equal to zero.
    if sum(balance for _, balance in working_balances) != 0:
        raise ValueError(
            "Invalid balances: total balance must be zero."
        )

    best_plan: List[Tuple[int, int, int]] = []

    def backtrack(
        start: int,
        current_balances: List[Tuple[int, int]],
        current_plan: List[Tuple[int, int, int]],
    ) -> None:
        nonlocal best_plan

        # Skip users who are already completely settled.
        while (
            start < len(current_balances)
            and current_balances[start][1] == 0
        ):
            start += 1

        # Everyone is settled.
        if start == len(current_balances):
            if not best_plan or len(current_plan) < len(best_plan):
                best_plan = current_plan.copy()
            return

        # Stop exploring if this branch cannot improve the best solution.
        if best_plan and len(current_plan) >= len(best_plan):
            return

        first_id, first_balance = current_balances[start]

        # Try matching the first unsettled user with every user
        # having the opposite sign.
        for i in range(start + 1, len(current_balances)):
            second_id, second_balance = current_balances[i]

            # Same-sign balances cannot settle each other.
            if first_balance * second_balance >= 0:
                continue

            updated = current_balances.copy()

            # Fully settle the first user.
            if first_balance < 0:
                # First user owes money; second user receives it.
                amount = -first_balance
                updated[i] = (
                    second_id,
                    second_balance + first_balance,
                )
                debtor_id = first_id
                creditor_id = second_id
            else:
                # First user is owed money; second user pays it.
                amount = first_balance
                updated[i] = (
                    second_id,
                    second_balance + first_balance,
                )
                debtor_id = second_id
                creditor_id = first_id

            # First user is now fully settled.
            updated[start] = (first_id, 0)

            current_plan.append(
                (debtor_id, creditor_id, amount)
            )

            backtrack(start + 1, updated, current_plan)

            # Undo this transaction and try another pairing.
            current_plan.pop()

            # If the second user was also fully settled, trying
            # another equivalent pairing is unnecessary.
            if updated[i][1] == 0:
                break

    # Find the exact minimum-transaction solution.
    backtrack(0, working_balances, [])

    exact_plan = [
        (payer, receiver, amount / 100)
        for payer, receiver, amount in best_plan
    ]

    # Generate a practical greedy solution.
    greedy_plan = greedy_settlement(balances)

    # If greedy achieves the exact minimum transaction count,
    # prefer it because its transactions never overshoot a payer's debt.
    if len(greedy_plan) == len(exact_plan):
        return greedy_plan

    # Otherwise, preserve the exact optimal solution.
    return exact_plan


def greedy_settlement(
    balances: Dict[int, float],
) -> List[Tuple[int, int, float]]:
    """
    Create a practical settlement plan using greedy matching.

    The largest debtor is matched with the largest creditor.
    Each transaction uses the smaller of the remaining debt
    and remaining credit.

    Therefore, a payer never pays more than their remaining debt.
    """

    # Convert rupees to integer paise.
    debtors = [
        [user_id, round(-balance * 100)]
        for user_id, balance in balances.items()
        if round(balance * 100) < 0
    ]

    creditors = [
        [user_id, round(balance * 100)]
        for user_id, balance in balances.items()
        if round(balance * 100) > 0
    ]

    # Sort largest amounts first.
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    transactions: List[Tuple[int, int, int]] = []

    debtor_index = 0
    creditor_index = 0

    while (
        debtor_index < len(debtors)
        and creditor_index < len(creditors)
    ):
        debtor_id, debt = debtors[debtor_index]
        creditor_id, credit = creditors[creditor_index]

        # Never transfer more than either side needs.
        amount = min(debt, credit)

        transactions.append(
            (debtor_id, creditor_id, amount)
        )

        # Update remaining amounts.
        debtors[debtor_index][1] -= amount
        creditors[creditor_index][1] -= amount

        # Move to the next debtor if this debt is fully paid.
        if debtors[debtor_index][1] == 0:
            debtor_index += 1

        # Move to the next creditor if this credit is fully satisfied.
        if creditors[creditor_index][1] == 0:
            creditor_index += 1

    return [
        (payer, receiver, amount / 100)
        for payer, receiver, amount in transactions
    ]