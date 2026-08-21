from datetime import datetime

from fastapi import FastAPI, HTTPException

from app.models import User, Group, Expense, RecurringExpense
from app.settlement import minimize_transactions
from dateutil.relativedelta import relativedelta


app = FastAPI(
    title="SplitUp API",
    description="Group expense splitter for hostel and PG roommates",
    version="0.3.0",
)


# ---------------------------------------------------------
# Temporary in-memory storage
# PostgreSQL will replace this later.
# ---------------------------------------------------------

users: dict[int, User] = {}
groups: dict[int, Group] = {}
expenses: dict[int, Expense] = {}
recurring_expenses: dict[int, RecurringExpense] = {}


# ---------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to SplitUp API",
        "status": "in progress",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ---------------------------------------------------------
# Group endpoints
# ---------------------------------------------------------

@app.post("/groups")
def create_group(group: Group):

    if group.id in groups:
        raise HTTPException(
            status_code=400,
            detail="Group already exists",
        )

    groups[group.id] = group

    return group


# ---------------------------------------------------------
# Recurring Expense endpoints
# ---------------------------------------------------------

@app.post("/recurring-expenses")
def create_recurring_expense(recurring: RecurringExpense):

    # Check that group exists
    if recurring.group_id not in groups:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    # Check duplicate recurring expense
    if recurring.id in recurring_expenses:
        raise HTTPException(
            status_code=400,
            detail="Recurring expense already exists",
        )

    # Check that all split users belong to the group
    group_members = set(groups[recurring.group_id].member_ids)

    for user_id in recurring.split_user_ids:
        if user_id not in group_members:
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id} is not a member of this group",
            )

    # Check that payer belongs to the group
    if recurring.paid_by not in group_members:
        raise HTTPException(
            status_code=400,
            detail="Payer is not a member of this group",
        )

    # Store recurring expense
    recurring_expenses[recurring.id] = recurring

    return recurring


def generate_next_expense(recurring: RecurringExpense) -> Expense:
    """
    Convert a recurring expense into a normal expense.
    """

    expense = Expense(
        id=max(expenses.keys(), default=0) + 1,
        group_id=recurring.group_id,
        description=recurring.description,
        amount=recurring.amount,
        paid_by=recurring.paid_by,
        created_at=datetime.now(),
        is_recurring=True,
        split_user_ids=recurring.split_user_ids,
    )

    return expense


@app.post("/recurring-expenses/{recurring_id}/generate")
def generate_recurring_expense(recurring_id: int):

    # Find recurring expense
    if recurring_id not in recurring_expenses:
        raise HTTPException(
            status_code=404,
            detail="Recurring expense not found",
        )

    recurring = recurring_expenses[recurring_id]

    # Generate normal expense
    expense = generate_next_expense(recurring)

    # Store generated expense
    expenses[expense.id] = expense

    # Update next due date
    if recurring.frequency == "monthly":
        recurring.next_due_date = (
            recurring.next_due_date + relativedelta(months=1)
        )

    elif recurring.frequency == "weekly":
        recurring.next_due_date = (
            recurring.next_due_date + relativedelta(weeks=1)
        )

    elif recurring.frequency == "daily":
        recurring.next_due_date = (
            recurring.next_due_date + relativedelta(days=1)
        )

    return {
        "recurring_id": recurring_id,
        "generated_expense": expense,
        "next_due_date": recurring.next_due_date,
    }


# ---------------------------------------------------------
# Expense endpoints
# ---------------------------------------------------------

@app.post("/expenses")
def create_expense(expense: Expense):

    if expense.id in expenses:
        raise HTTPException(
            status_code=400,
            detail="Expense already exists",
        )

    if expense.group_id not in groups:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    # Make sure all split participants belong to the group
    group_members = set(groups[expense.group_id].member_ids)

    for user_id in expense.split_user_ids:
        if user_id not in group_members:
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id} is not a member of this group",
            )

    # Make sure payer belongs to the group
    if expense.paid_by not in group_members:
        raise HTTPException(
            status_code=400,
            detail="Payer is not a member of this group",
        )

    # At least one person must be included
    if not expense.split_user_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one split participant is required",
        )

    expenses[expense.id] = expense

    return expense


# ---------------------------------------------------------
# Balance calculation
# ---------------------------------------------------------

def calculate_group_balances(group_id: int):

    """
    Calculate the net balance of every member in a group.

    Positive balance:
        The user should receive money.

    Negative balance:
        The user owes money.

    Each expense is split equally among
    the users listed in split_user_ids.
    """

    balances = {
        user_id: 0.0
        for user_id in groups[group_id].member_ids
    }

    for expense in expenses.values():

        if expense.group_id != group_id:
            continue

        # Person who paid gets credit for full amount
        balances[expense.paid_by] += expense.amount

        # Divide expense equally
        share = expense.amount / len(expense.split_user_ids)

        for user_id in expense.split_user_ids:
            balances[user_id] -= share

    return balances


# ---------------------------------------------------------
# Balance endpoint
# ---------------------------------------------------------

@app.get("/groups/{group_id}/balances")
def get_group_balances(group_id: int):

    if group_id not in groups:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    balances = calculate_group_balances(group_id)

    return {
        "group_id": group_id,
        "balances": balances,
    }


# ---------------------------------------------------------
# Settlement endpoint
# ---------------------------------------------------------

@app.get("/groups/{group_id}/settlement")
def get_settlement(group_id: int):

    if group_id not in groups:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    balances = calculate_group_balances(group_id)

    settlement = minimize_transactions(balances)

    return {
        "group_id": group_id,
        "settlement": settlement,
    }