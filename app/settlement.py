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
    The algorithm uses backtracking.

    At every step, we select the first user with a non-zero balance
    and try settling that user with every possible user having the
    opposite balance.

    The selected user is completely settled in each recursive branch.
    We explore all possible creditor/debtor choices and keep the plan
    requiring the fewest transactions.

    Equal and opposite balances are handled naturally in one
    transaction.

    Money is converted to integer paise before calculation to avoid
    floating-point precision problems.

    Time Complexity
    ---------------
    Worst case: exponential, approximately O(n!), where n is the
    number of users with non-zero balances.

    This is suitable for small hostel/PG groups and allows us to find
    a minimum-transaction settlement plan rather than relying on a
    greedy approximation.

    Space Complexity
    ----------------
    O(n) recursion depth, excluding the stored settlement plan.
    """

    # Convert rupees to integer paise for exact calculations.
    working_balances = [
        (user_id, round(balance * 100))
        for user_id, balance in balances.items()
        if round(balance * 100) != 0
    ]

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

    backtrack(0, working_balances, [])

    return [
        (payer, receiver, amount / 100)
        for payer, receiver, amount in best_plan
    ]