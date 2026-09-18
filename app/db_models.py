from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


class GroupDB(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class GroupMemberDB(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    paid_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    is_recurring = Column(Integer, nullable=False, default=0)

class ExpenseSplitDB(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True)
    expense_id = Column(
        Integer,
        ForeignKey("expenses.id"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

class RecurringExpenseDB(Base):
    __tablename__ = "recurring_expenses"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    paid_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    frequency = Column(String, nullable=False)
    next_due_date = Column(DateTime, nullable=False)


class RecurringExpenseSplitDB(Base):
    __tablename__ = "recurring_expense_splits"

    id = Column(Integer, primary_key=True)
    recurring_expense_id = Column(
        Integer,
        ForeignKey("recurring_expenses.id"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )