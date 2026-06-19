# Financial Reality Engine (FRE)

A production-grade financial decision system that models how time allocation drives income, risk, and financial stability for variable-income workers.

Built for gig workers, shift employees, freelancers, and hourly workers whose income is not fixed — but derived from time worked.

---

## Why This Project Exists

Traditional budgeting tools assume income is constant.

That assumption breaks for millions of people.

FRE inverts the model:

> Income is not an input. It is computed from time.

```
Income = Σ (shift hours × hourly rate)
```

This enables the system to simulate financial outcomes from schedule changes in real time.

---

## What Makes FRE Different

FRE is not a budgeting app.

It is a financial simulation engine.

It allows users to:

- Simulate income directly from scheduled work shifts
- Measure the financial impact of adding/removing shifts instantly
- Rank jobs by effective hourly value ($/hr efficiency)
- Compute deterministic financial risk (0–100 scoring model)
- Run Monte Carlo simulations (500+ futures) for financial stability
- Project income and balance from real time allocation

---

## Core Insight

Most financial tools assume:

> Income → Budgeting → Outcome

FRE reverses this:

> Time → Income → Financial Stability

This shift enables questions like:

- What happens if I drop this shift?
- Which job actually pays the most per hour worked?
- What is my probability of running out of money in 12 weeks?
- How does my schedule affect long-term financial stability?

---

## System Architecture

```
Schedule Layer
    ↓
Time Engine (conflicts, free blocks, shift logic)
    ↓
Schedule Analytics (pure functions)
    ↓
Financial State Engine (single source of truth)
    ↓
Decision Systems
    ├── Insight Engine (interpretation layer)
    ├── Scenario Engine (what-if comparison)
    └── Monte Carlo Engine (500+ simulations)
    ↓
UI Layer (Tkinter desktop application)
    ↓
Export Layer (PDF + CSV)
```

---

## Core Engineering Design

### 1. Financial State Engine (Single Source of Truth)

All financial metrics are computed in one place:

- income
- expenses
- net flow
- savings rate
- risk score (0–100)
- health score (0–100)

No other module recalculates financial logic.

---

### 2. Pure Analytics Layer

All schedule analytics are pure functions:

- no database access
- no UI dependency
- fully unit testable

---

### 3. Decision Engine

Computes real-time impact of schedule changes:

- income loss / gain
- savings rate change
- risk score delta
- natural language recommendations

---

### 4. Monte Carlo Simulation (500+ Runs)

Simulates financial futures using probabilistic life events.

Outputs:

- probability of deficit
- median / worst / best case outcomes
- balance distribution
- financial stability risk

---

### 5. Schedule-Driven Income Model

Every shift is a financial event:

- start time
- end time
- hourly rate
- date

Income is derived entirely from schedule structure, not user input.

---

## Key Features

- Real-time financial projections from schedule changes
- Shift impact analysis (what-if decision modeling)
- Job efficiency ranking ($/hour comparison across roles)
- Deterministic financial risk scoring system
- 500-run Monte Carlo forecasting engine
- SQLite persistence with schema migration + deduplication
- Fully offline desktop application

---

## Engineering Principles

- Single source of truth for financial state
- Pure functions for all analytics
- Schedule-driven income model (not manual input)
- Dependency injection (testable architecture)
- Deterministic outputs over heuristics
- UI fully separated from business logic

---

## Testing

- 140+ automated pytest tests
- No GUI required for testing
- Covers:
  - financial calculations
  - schedule system
  - simulation engine
  - edge cases (overnight shifts, zero income, conflicts)
  - Monte Carlo stability
  - database integrity

```bash
python3 -m pytest test_fre.py -v
```

---

## Project Structure

```
├── Core
│   ├── financial_state.py      # All financial calculations — single source of truth
│   ├── model.py                # Job + Expense with frequency-aware weekly conversion
│   ├── database.py             # SQLite persistence, migration, backup, dedup
│   ├── utils.py                # canon_name() — shared name normalisation
│   └── config.py               # All constants and thresholds
│
├── Engines
│   ├── schedule_analytics.py   # Pure analytics: income by job, shift impact, efficiency
│   ├── schedule_service.py     # Schedule → financial sync (testable, no GUI)
│   ├── time_engine.py          # Free-block analysis, conflict detection, opportunity cost
│   ├── insight_engine.py       # Score interpretation and insight generation
│   ├── scenario_engine.py      # Side-by-side scenario projection
│   └── simulation.py           # What-If simulator + 500-run Monte Carlo
│
├── Schedule
│   ├── schedule_event.py       # ScheduleEvent dataclass + time helpers
│   ├── schedule_core.py        # Schedule backend — DB ops, week navigation
│   ├── date_parser.py          # Natural language schedule import parser
│   └── shift_parser.py         # Shift input parsing
│
├── Pages
│   ├── app.py                  # App shell, DI container, navigation, exports
│   ├── page_dashboard.py       # Hero balance, stats, insights
│   ├── page_schedule.py        # Weekly calendar, conflict detection, free time
│   ├── page_analytics.py       # 5-tab analytics with decision engine output
│   ├── page_forecast.py        # Projection, scenario comparison, simulation
│   ├── page_goals.py           # Goal tracking, weeks-to-goal, emergency fund
│   └── page_settings.py        # App configuration
│
├── UI
│   ├── theme.py                # Dark/light palettes, ThemeManager, font constants
│   ├── widgets.py              # ScrollFrame, TabBar, card, kv_row, labeled_entry
│   └── charts.py               # matplotlib chart types embedded in tkinter
│
└── test_fre.py                 # 140+ pytest tests — no GUI instantiation required
```

---

## Tech Stack

- Python 3.10+
- Tkinter (GUI)
- SQLite (persistence)
- matplotlib (visualization)
- reportlab (PDF export)
- pytest (testing)

No web framework. No ORM. No UI toolkit beyond what ships with Python.

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/financial-reality-engine.git
cd financial-reality-engine
pip install -r requirements.txt
python3 main.py
```

`finance.db` is created on first launch and listed in `.gitignore`.

> **macOS:** if the window appears blank on first launch, run `brew install python-tk`.

---

## Project Philosophy

This system prioritizes:

- correctness over features
- architecture over UI polish
- deterministic computation over estimation
- simulation over static budgeting
- modeling real-world complexity instead of simplifying it

---

## Future Improvements

- REST API (FastAPI) for external access
- PostgreSQL migration for multi-device sync
- Predictive income modeling (time-series forecasting)
- Recurring shift engine
- Web / mobile frontend (React or Flutter)
- External calendar integration (Google Calendar / .ics)

---

## Author

Aba

Software engineer focused on building systems that model real-world complexity through clean architecture, simulation, and deterministic design.

---

> "The goal is not to track money. The goal is to understand how time creates money."
