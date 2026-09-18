from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import SessionLocal
from app.db_models import (
    GroupDB,
    GroupMemberDB,
    UserDB,
    ExpenseDB,
    ExpenseSplitDB,
    RecurringExpenseDB,
    RecurringExpenseSplitDB,
)

from app.models import User, Group, Expense, RecurringExpense
from app.settlement import minimize_transactions
from dateutil.relativedelta import relativedelta


app = FastAPI(
    title="SplitUp API",
    description="Group expense splitter for hostel and PG roommates",
    version="0.3.0",
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# PostgreSQL database storage
# ---------------------------------------------------------

# Application data is stored in PostgreSQL
# using SQLAlchemy models.


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
def create_group(group: Group, db: Session = Depends(get_db)):
    existing = db.get(GroupDB, group.id)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Group already exists",
        )

    db_group = GroupDB(
        id=group.id,
        name=group.name,
    )

    db.add(db_group)

    for user_id in group.member_ids:
        member = GroupMemberDB(
            group_id=group.id,
            user_id=user_id,
        )
        db.add(member)

    db.commit()

    return group

@app.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    existing = db.get(UserDB, user.id)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    db_user = UserDB(
        id=user.id,
        name=user.name,
        email=user.email,
    )

    db.add(db_user)
    db.commit()

    return user
# ---------------------------------------------------------
# Recurring Expense endpoints
# ---------------------------------------------------------

@app.post("/recurring-expenses")
def create_recurring_expense(
    recurring: RecurringExpense,
    db: Session = Depends(get_db),
):
    # Check that the group exists.
    group = db.get(GroupDB, recurring.group_id)

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    # Check that the payer exists.
    payer = db.get(UserDB, recurring.paid_by)

    if not payer:
        raise HTTPException(
            status_code=404,
            detail="Payer not found",
        )

    # Check that the recurring expense ID is not already used.
    existing = db.get(RecurringExpenseDB, recurring.id)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Recurring expense already exists",
        )

    # Check that the payer belongs to the group.
    payer_membership = (
        db.query(GroupMemberDB)
        .filter(
            GroupMemberDB.group_id == recurring.group_id,
            GroupMemberDB.user_id == recurring.paid_by,
        )
        .first()
    )

    if not payer_membership:
        raise HTTPException(
            status_code=400,
            detail="Payer is not a member of this group",
        )

    # At least one person must share the recurring expense.
    if not recurring.split_user_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one split participant is required",
        )

    # Check that every split participant belongs to the group.
    for user_id in recurring.split_user_ids:
        membership = (
            db.query(GroupMemberDB)
            .filter(
                GroupMemberDB.group_id == recurring.group_id,
                GroupMemberDB.user_id == user_id,
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id} is not a member of this group",
            )

    # Create recurring expense template.
    db_recurring = RecurringExpenseDB(
        id=recurring.id,
        group_id=recurring.group_id,
        description=recurring.description,
        amount=recurring.amount,
        paid_by=recurring.paid_by,
        frequency=recurring.frequency,
        next_due_date=recurring.next_due_date,
    )

    db.add(db_recurring)

    # Store the users who share the recurring expense.
    for user_id in recurring.split_user_ids:
        split = RecurringExpenseSplitDB(
            recurring_expense_id=recurring.id,
            user_id=user_id,
        )
        db.add(split)

    db.commit()

    return recurring


@app.post("/recurring-expenses/{recurring_id}/generate")
def generate_recurring_expense(
    recurring_id: int,
    db: Session = Depends(get_db),
):
    # Get the recurring expense template.
    recurring = db.get(RecurringExpenseDB, recurring_id)

    if not recurring:
        raise HTTPException(
            status_code=404,
            detail="Recurring expense not found",
        )

    # Find the next available expense ID.
    last_expense = (
        db.query(ExpenseDB)
        .order_by(ExpenseDB.id.desc())
        .first()
    )

    next_expense_id = (
        last_expense.id + 1
        if last_expense
        else 1
    )

    # Get the users who share this recurring expense.
    split_records = (
        db.query(RecurringExpenseSplitDB)
        .filter(
            RecurringExpenseSplitDB.recurring_expense_id
            == recurring_id
        )
        .all()
    )

    split_user_ids = [
        split.user_id
        for split in split_records
    ]

    if not split_user_ids:
        raise HTTPException(
            status_code=400,
            detail="Recurring expense has no split participants",
        )

    # Create a normal expense from the recurring template.
    db_expense = ExpenseDB(
        id=next_expense_id,
        group_id=recurring.group_id,
        description=recurring.description,
        amount=recurring.amount,
        paid_by=recurring.paid_by,
        created_at=datetime.now(),
        is_recurring=1,
    )

    db.add(db_expense)

    # Store the split participants.
    for user_id in split_user_ids:
        split = ExpenseSplitDB(
            expense_id=next_expense_id,
            user_id=user_id,
        )
        db.add(split)

    # Move the recurring template to its next cycle.
    if recurring.frequency.lower() == "monthly":
        recurring.next_due_date += relativedelta(months=1)

    elif recurring.frequency.lower() == "weekly":
        recurring.next_due_date += relativedelta(weeks=1)

    elif recurring.frequency.lower() == "daily":
        recurring.next_due_date += relativedelta(days=1)

    elif recurring.frequency.lower() == "yearly":
        recurring.next_due_date += relativedelta(years=1)

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported recurring frequency",
        )

    db.commit()

    return {
        "id": next_expense_id,
        "group_id": recurring.group_id,
        "description": recurring.description,
        "amount": recurring.amount,
        "paid_by": recurring.paid_by,
        "is_recurring": True,
        "split_user_ids": split_user_ids,
        "next_due_date": recurring.next_due_date,
    }


# ---------------------------------------------------------
# Expense endpoints
# ---------------------------------------------------------

@app.post("/expenses")
def create_expense(
    expense: Expense,
    db: Session = Depends(get_db),
):
    # Check that the group exists.
    group = db.get(GroupDB, expense.group_id)

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    # Check that the payer exists.
    payer = db.get(UserDB, expense.paid_by)

    if not payer:
        raise HTTPException(
            status_code=404,
            detail="Payer not found",
        )

    # Check that the expense ID is not already used.
    existing = db.get(ExpenseDB, expense.id)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Expense already exists",
        )

    # Check that the payer belongs to the group.
    payer_membership = (
        db.query(GroupMemberDB)
        .filter(
            GroupMemberDB.group_id == expense.group_id,
            GroupMemberDB.user_id == expense.paid_by,
        )
        .first()
    )

    if not payer_membership:
        raise HTTPException(
            status_code=400,
            detail="Payer is not a member of this group",
        )

    # At least one person must share the expense.
    if not expense.split_user_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one split participant is required",
        )

    # Check every split participant belongs to the group.
    for user_id in expense.split_user_ids:
        membership = (
            db.query(GroupMemberDB)
            .filter(
                GroupMemberDB.group_id == expense.group_id,
                GroupMemberDB.user_id == user_id,
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id} is not a member of this group",
            )

    # Create the expense.
    db_expense = ExpenseDB(
        id=expense.id,
        group_id=expense.group_id,
        description=expense.description,
        amount=expense.amount,
        paid_by=expense.paid_by,
        created_at=expense.created_at,
        is_recurring=1 if expense.is_recurring else 0,
    )

    db.add(db_expense)

    # Store each person sharing the expense.
    for user_id in expense.split_user_ids:
        split = ExpenseSplitDB(
            expense_id=expense.id,
            user_id=user_id,
        )
        db.add(split)

    db.commit()

    return expense


# ---------------------------------------------------------
# Balance calculation
# ---------------------------------------------------------

def calculate_group_balances(group_id: int, db: Session):
    """
    Calculate net balances using PostgreSQL data.

    Positive balance = user should receive money.
    Negative balance = user owes money.
    """

    # Get all members of the group.
    memberships = (
        db.query(GroupMemberDB)
        .filter(GroupMemberDB.group_id == group_id)
        .all()
    )

    balances = {
        membership.user_id: 0.0
        for membership in memberships
    }

    # Get all expenses belonging to this group.
    group_expenses = (
        db.query(ExpenseDB)
        .filter(ExpenseDB.group_id == group_id)
        .all()
    )

    for expense in group_expenses:

        # The payer gets credit for the full amount.
        balances[expense.paid_by] += expense.amount

        # Find everyone sharing this expense.
        splits = (
            db.query(ExpenseSplitDB)
            .filter(ExpenseSplitDB.expense_id == expense.id)
            .all()
        )

        if not splits:
            continue

        # Current SplitUp rule: divide equally.
        share = expense.amount / len(splits)

        for split in splits:
            balances[split.user_id] -= share

    return balances


# ---------------------------------------------------------
# Balance endpoint
# ---------------------------------------------------------

@app.get("/groups/{group_id}/balances")
def get_group_balances(
    group_id: int,
    db: Session = Depends(get_db),
):
    group = db.get(GroupDB, group_id)

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    balances = calculate_group_balances(group_id, db)

    return {
        "group_id": group_id,
        "balances": balances,
    }

# ---------------------------------------------------------
# Settlement endpoint
# ---------------------------------------------------------

@app.get("/groups/{group_id}/settlement")
def get_settlement(
    group_id: int,
    db: Session = Depends(get_db),
):
    group = db.get(GroupDB, group_id)

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )

    balances = calculate_group_balances(group_id, db)

    settlement = minimize_transactions(balances)

    return {
        "group_id": group_id,
        "settlement": settlement,
    }