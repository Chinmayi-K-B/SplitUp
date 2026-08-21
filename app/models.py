from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


class Group(BaseModel):
    id: int
    name: str
    member_ids: list[int]


class Expense(BaseModel):
    id: int
    group_id: int
    description: str
    amount: float
    paid_by: int
    created_at: datetime
    is_recurring: bool = False

    # Users who share this expense.
    # For now, the expense is split equally among them.
    split_user_ids: list[int] = []


class Split(BaseModel):
    id: int
    expense_id: int
    user_id: int
    amount: float


class Balance(BaseModel):
    user_id: int
    amount: float

class RecurringExpense(BaseModel):
    id: int
    group_id: int
    description: str
    amount: float
    paid_by: int
    split_user_ids: list[int]
    frequency: str
    next_due_date: datetime