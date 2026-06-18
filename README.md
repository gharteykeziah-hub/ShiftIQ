# Financial Reality Engine

**Financial Reality Engine is a decision system that models the real-time tradeoffs between time, income, and financial stability for students with variable income.**

It is not a budgeting app. It is not a spreadsheet. It is a system that answers questions like:
*"What happens to my finances if I drop this shift?"*
*"Which of my two jobs is actually worth more per hour of my life?"*
*"How far am I from my savings goal at my current trajectory?"*

---

<!-- Screenshot: run the app, navigate to Dashboard, press Cmd+Shift+4, save as screenshot.png
     then replace this comment with: ![FRE Dashboard](screenshot.png) -->

---

## Why This Exists

Every budgeting app assumes you have a salary. You enter your monthly income, your monthly expenses, and it tells you your budget. That model fails completely for students.

A student working two campus jobs has:
- Income that changes week to week based on hours scheduled
- Shifts that appear and disappear based on academic calendar
- Decisions like "should I take this shift or study for finals?" that have direct financial consequences
- No way to model what dropping a shift actually does to their stability score

Spreadsheets can track what happened. They cannot model what *will* happen if you change one variable.

FRE was built to close that gap: a system that understands schedule-based income, models decisions before you make them, and gives you a financial risk score that reflects your actual situation — not a fictional monthly salary.

---

## System Architecture

```
                        ┌─────────────────┐
                        │  Schedule Input  │
                        │  (page_schedule) │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ Schedule Service │  ← sync, dedup, rate propagation
                        └────────┬────────┘
                                 │
               ┌─────────────────▼─────────────────┐
               │         Schedule Analytics         │  ← pure functions, no GUI
               │  income_by_job · daily_totals      │
               │  shift_impact · job_efficiency     │
               └─────────────────┬─────────────────┘
                                 │
               ┌─────────────────▼─────────────────┐
               │          Financial State           │  ← single source of truth
               │  scores · projections · net flow   │
               └──────┬──────────────────┬──────────┘
                      │                  │
          ┌───────────▼──┐        ┌──────▼──────────┐
          │ Insight Engine│        │ Scenario Engine  │
          │ Simulation    │        │ Monte Carlo      │
          └───────────┬──┘        └──────┬──────────┘
                      │                  │
               ┌──────▼──────────────────▼──────┐
               │            UI Pages             │
               │  Dashboard · Analytics · Goals  │
               └─────────────────────────────────┘
```

**Architectural rules enforced throughout:**
- The database layer does not touch the UI
- The UI does not perform calculations
- Score logic lives only in `financial_state.py` — `insight_engine.py` delegates to it
- Schedule analytics functions are pure: they accept event lists, return data structures, make no DB or GUI calls
- Business logic is extracted from UI classes so it can be tested without a window

---

## Hero Systems

### 1 — Decision Engine

The feature that separates FRE from a tracker.

**Shift Impact** (`schedule_analytics.shift_impact`)

Given any scheduled shift, computes in real time:
- Hours and dollars lost if removed
- New weekly income and net weekly flow after removal
- Risk score delta — how much your stability drops
- Plain-English recommendation based on whether removal causes a deficit

**Job Efficiency Ranking** (`schedule_analytics.job_efficiency_report`)

Ranks every job by effective $/hr and flags scheduling friction:
early morning starts (before 8am) and late ends (after 10pm). Surfaces in Analytics → Income as a ranked table so a student can compare jobs not just by pay but by total cost to their schedule and sleep.

Both are pure functions. Both are unit tested. Both are displayed in the UI.

---

### 2 — Financial State Engine

Single source of truth for every number in the app.

`financial_state.py` owns all calculations: weekly income, weekly expenses, net flow, savings rate, projections, health score, risk score. No other module recalculates these. `insight_engine.py` calls `state.risk_score()` — it does not reimplement it. This means the dashboard, the PDF export, the CSV export, and the analytics page can never show different numbers for the same metric.

The risk score model starts at 50 and adjusts based on net flow direction, expense ratio, savings band, and balance floor. The health score maps savings rate to a 5-tier band. Both are deterministic and auditable.

---

### 3 — Simulation Engine

Two forecast modes in `simulation.py`:

**What-If Simulator** — models a one-time financial event (car repair, unexpected expense, bonus) and projects balance week-by-week over a custom horizon.

**Monte Carlo** — runs 500 iterations of the user's financial life with randomised weekly variance. Returns deficit probability, safe probability, average/best/worst case balance, and a histogram. Answers: *"given my current trajectory, what is the probability I run out of money in 12 weeks?"*

---

## Performance

| Operation | Input | Time |
|---|---|---|
| `date_range_summary()` | 2,000 events | ~7ms |
| `shift_impact()` | 1 event + state | ~3μs |
| Monte Carlo simulation | 500 iterations × 52 weeks | < 1s |
| Full test suite (140+ tests) | — | < 2s |

Schedule analytics processes 2,000 events across variant job name spellings and correctly resolves them to canonical groups in under 10ms.

---

## Engineering Notes

**Canonical name deduplication**

`"admissions"`, `"Admissions"`, and `"ADMISSIONS"` are the same job. Previously each module had its own copy of `_canon()` — a silent data corruption risk where any one copy drifting would cause job names to stop matching across the income sync, analytics, and dedup pipeline. Centralised into `utils.canon_name()`, imported by every module that handles names. All four duplicate definitions replaced with one-line delegates.

**ScenarioEngine projection bug**

The original projection code applied `extra_weekly` income inside a per-job loop. A user with 3 jobs got 3× the extra weekly income in every forecast. Fixed so `extra_weekly` is added once to the total weekly base. The regression test specifically validates that `project_balance()` with `extra_weekly=50` produces identical results for a 1-job state and a 3-job state after accounting for the difference in base income.

**Testable service layer**

The schedule-to-financial sync was originally 60 lines of business logic inside `App.__init__` — untestable without a Tk window. Extracted into `schedule_service.sync_schedule_to_jobs(state)`. Pure Python, no GUI dependency, returns a count of jobs updated. Now covered by the test suite.

**Overnight shift math**

Shifts crossing midnight (e.g. 11pm–7am) return the correct 8 hours, not negative 16. `_shift_hours()` detects `end < start` and adds 1440 minutes. Covered by a dedicated test case.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI | tkinter (standard library) |
| Database | SQLite via sqlite3 (standard library) |
| Charts | matplotlib (FigureCanvasTkAgg) |
| PDF export | reportlab |
| Tests | pytest |

No web framework. No ORM. No UI toolkit beyond what ships with Python.

---

## Project Structure

```
├── Core
│   ├── financial_state.py    # All financial calculations — single source of truth
│   ├── model.py              # Job + Expense data classes with frequency conversion
│   ├── database.py           # SQLite persistence, migration, backup, snapshots
│   ├── utils.py              # canon_name() — shared across all modules
│   └── config.py             # Constants and thresholds
│
├── Engines
│   ├── schedule_analytics.py # Pure analytics: income by job, shift impact, job efficiency
│   ├── schedule_service.py   # Schedule → financial sync (testable, no GUI)
│   ├── insight_engine.py     # Score labels and insight generation
│   ├── scenario_engine.py    # Side-by-side scenario projection
│   ├── simulation.py         # What-If simulator + Monte Carlo
│   └── time_engine.py        # Free-block analysis, opportunity cost
│
├── Pages
│   ├── app.py                # App shell, navigation, sidebar
│   ├── page_dashboard.py
│   ├── page_schedule.py      # Weekly calendar, shift entry, conflict detection
│   ├── page_analytics.py     # 5-tab analytics with decision engine output
│   ├── page_forecast.py
│   ├── page_goals.py
│   └── page_settings.py
│
└── test_fre.py               # 140+ pytest tests
```

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/financial-reality-engine.git
cd financial-reality-engine
pip3 install -r requirements.txt
python3 main.py
```

`finance.db` is created on first launch and listed in `.gitignore`.

**macOS:** if the window appears blank, run `brew install python-tk`.

---

## Running Tests

```bash
python3 -m pytest test_fre.py -v
```

Covers: frequency conversion, all financial calculations, score edge cases, ScenarioEngine bug regression, schedule analytics pure functions, shift impact decision engine, job efficiency ranking, Monte Carlo simulation, all database operations (temp file — real data never touched), and stress tests with 2,000-event sets.

---

## What I Would Improve Next

- **Replace tkinter with a modern UI** (PySide6 or a web frontend) — tkinter limits layout flexibility and has no responsive design
- **Add an API layer** — expose financial state and schedule analytics as REST endpoints so the system could power a mobile app or web dashboard
- **Migrate SQLite → PostgreSQL** for multi-device sync and concurrent access
- **Add predictive income modeling** — use the history table to fit a simple time-series model and forecast income variance, not just project from current averages
- **Real-time shift conflict alerts** — if a new shift overlaps an existing one, surface the financial impact before the user confirms the add
- **Export to accounting formats** — CSV exports compatible with YNAB or Mint import so FRE data flows into other tools

---

*Built by Aba.*
