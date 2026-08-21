# SplitUp — Group Expense Splitter for Roommates

## Problem
In shared hostel/PG living, roommates split rent, WiFi, groceries, and maid 
charges every month — usually tracked manually in a WhatsApp group or a 
notes app. This leads to confusion over who owes what, repeated bills that 
have to be re-entered every cycle, and settlements that involve far more 
back-and-forth payments than necessary.

SplitUp solves this with recurring expense templates and a debt-simplification 
settlement algorithm that minimizes the number of transactions needed to 
settle a group's balances.

## Features
- **Group & expense management** — create groups, add expenses, split 
  equally, by percentage, or by exact amounts
- **Recurring expenses** — define a split once for monthly bills (rent, 
  WiFi, maid) and auto-generate it each cycle instead of re-entering it
- **Settlement algorithm** — computes the minimum number of transactions 
  required to settle all balances in a group, with a fairness-weighted 
  variant that prioritizes paying back whoever has been fronting money 
  consistently
- **Balance tracking** — real-time view of who owes whom, per group

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **Other:** Pydantic for data validation, pytest for testing

## Status
🚧 In progress — core data models and settlement algorithm are being built. 
See [TODO.md](./TODO.md) for the current roadmap.

## Data Model
- `User` — a person in one or more groups
- `Group` — a collection of users sharing expenses
- `Expense` — a single or recurring cost logged by a user, split among 
  group members
- `Split` — how an expense is divided among users (equal, percentage, or 
  exact)
- `Balance` — computed net amount each user owes/is owed within a group

## Why This Project
Built out of a real, recurring annoyance from hostel life — tracking who 
paid for what and settling up every month shouldn't require a spreadsheet 
or a scroll through chat history.