# TODO / Roadmap

## Setup
- [x] Initialize repo, README, project structure
- [ ] Set up FastAPI project skeleton + dependencies (requirements.txt / pyproject.toml)
- [ ] Set up PostgreSQL connection + basic config

## Core Data Models
- [ ] `User` model
- [ ] `Group` model (users, group metadata)
- [ ] `Expense` model (amount, payer, group, one-time vs. recurring flag)
- [ ] `Split` model (how an expense divides among users — equal / percentage / exact)
- [ ] `Balance` model / computed view (net owed per user per group)

## Recurring Expenses
- [ ] Recurring expense template (subject, amount, split rule, frequency)
- [ ] Job/function to auto-generate expense instances each cycle
- [ ] Handle edits/cancellation of a recurring template without breaking past records

## Settlement Algorithm (core piece)
- [ ] Compute net balances per user from all expenses in a group
- [ ] Standard debt-simplification: minimize number of transactions to settle up
- [ ] Add fairness-weighted variant (e.g. prioritize repaying consistent up-front payers, or usage-weighted splits like AC-room electricity)
- [ ] Unit tests covering: simple 2-person split, multi-person circular debt, edge case of already-settled group

## API Layer
- [ ] `POST /groups`, `POST /groups/{id}/members`
- [ ] `POST /expenses` (one-time and recurring)
- [ ] `GET /groups/{id}/balances`
- [ ] `GET /groups/{id}/settlement` — returns minimum transaction plan
- [ ] Basic input validation (Pydantic schemas)

## Frontend / Interface (optional, if time allows)
- [ ] Simple CLI to add expenses and print settlement plan
- [ ] (Stretch) Minimal web UI

## Polish
- [ ] Error handling + meaningful API error messages
- [ ] Docstrings + inline comments on settlement algorithm (interview-readability)
- [ ] Sample seed data / demo script
- [ ] Deploy or at least a working local demo (docker-compose with Postgres)