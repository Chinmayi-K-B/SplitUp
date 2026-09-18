# SplitUp — Group Expense Splitter for Roommates

SplitUp is a full-stack expense management application designed for
hostel/PG roommates to track shared expenses, calculate balances, and
generate practical settlement plans.

## Problem

In shared hostel/PG living, roommates split expenses such as rent, WiFi,
groceries, and other household bills. Tracking who paid for what manually
can lead to confusion, repeated data entry, and unnecessarily complicated
settlements.

SplitUp provides a centralized system to record shared expenses, track
individual balances, manage recurring expense templates, and generate
settlement plans with a focus on minimizing the number of transactions
while keeping payments practical.

## Features

- **Group & expense management** — create groups, add members, record
  shared expenses, and track expenses by payer and participants
- **Balance tracking** — calculate each member's net amount owed or
  receivable within a group
- **Optimal settlement planning** — use an exact backtracking-based
  settlement algorithm to minimize the number of transactions
- **Practical settlements** — use debt-constrained greedy matching so
  individual transactions do not exceed a payer's outstanding balance
- **Recurring expenses** — create recurring expense templates and
  generate expense instances for future billing cycles
- **Full-stack dashboard** — React frontend connected to a FastAPI backend
  with PostgreSQL persistence
- **Input validation** — validate users, groups, participants, and
  expense data before storing records
- **Automated recalculation** — balances and settlement plans are
  recalculated after new expenses are added

## Tech Stack

- **Frontend:** React, Vite, JavaScript, CSS
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Testing:** pytest
- **Version Control:** Git, GitHub

## Architecture

```text
React Frontend
      |
      | REST API
      v
FastAPI Backend
      |
      +---- SQLAlchemy ---- PostgreSQL
      |
      +---- Balance Calculation
      |
      +---- Settlement Engine
              |
              +---- Exact Backtracking
              |
              +---- Practical Greedy Matching
Settlement Algorithm

The core of SplitUp is its settlement engine.

The system first calculates the net balance of each group member:

Positive balance → the member should receive money
Negative balance → the member owes money
Zero balance → the member is already settled

The exact settlement engine uses backtracking to search possible
debtor-creditor combinations and determine the minimum number of
transactions required for a valid zero-sum balance.

Money is converted to integer paise during settlement calculations to
avoid floating-point precision issues.

A practical greedy settlement layer matches remaining debtors and
creditors using the smaller of the outstanding debt and credit. This
ensures that a payer is never assigned more than their remaining debt.

For example:

Alice   +₹900
Bob     -₹300
Charlie -₹300
Diana   -₹300

The practical settlement is:

Bob     → Alice     ₹300
Charlie → Alice     ₹300
Diana   → Alice     ₹300

This preserves the minimum transaction count while avoiding
counter-intuitive intermediate payments.

Database Schema

The PostgreSQL database currently uses seven tables:

users
groups
group_members
expenses
expense_splits
recurring_expenses
recurring_expense_splits
API

The FastAPI backend currently exposes endpoints for:

GET /health
POST /groups
GET /users
POST /users
POST /expenses
GET /expenses
POST /recurring-expenses
POST /recurring-expenses/{recurring_id}/generate
GET /groups/{group_id}/balances
GET /groups/{group_id}/settlement

Interactive API documentation is available through FastAPI Swagger UI
when running the application locally.

Testing

The settlement engine is covered by pytest tests for:

Two-person settlements
Multi-person settlements
Already-settled groups
Debt-constrained transactions
Practical greedy settlement

Current test status:

5 passed
Current Status

🚧 In progress

The core full-stack workflow is functional:

Add Expense
    ↓
React Frontend
    ↓
FastAPI REST API
    ↓
PostgreSQL
    ↓
Balance Calculation
    ↓
Settlement Engine
    ↓
Updated Dashboard

The current application supports local development and demonstration.
Authentication, production deployment, automatic scheduled recurring
jobs, and advanced split/fairness features remain future improvements.

Future Improvements
User authentication and authorization
Percentage and exact-amount split modes
Automatic scheduled recurring-expense generation
Editing and cancellation of recurring templates
Fairness-aware settlement strategies
Expense history and filtering
Improved settlement explanations
Production deployment
Docker-based deployment with PostgreSQL
More comprehensive API and integration tests
Why This Project

SplitUp was built around a common problem in hostel/PG life: keeping
track of shared expenses and settling balances should not require
spreadsheets, manual calculations, or searching through chat history.
