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
