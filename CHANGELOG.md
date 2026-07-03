# Changelog

All notable changes to ShiftIQ are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.3.0] — 2026-07-03

### Added
- `PUT /api/balance` — update current balance via API
- `GET /api/projection` — week-by-week balance projection over N weeks
- `GET /api/insights` — InsightEngine output (health label, risk label, insights list)
- `GET /api/history` — historical daily snapshots for trend charts
- `PUT /api/jobs/{name}` — edit an existing job's amount or frequency
- `PUT /api/expenses/{name}` — edit an existing expense
- CORS middleware — React frontend can call the API from any origin
- `python-dotenv` — environment variables loaded from `.env` for local dev
- `.env.example` — template showing all required environment variables
- `psycopg2-binary` and `SQLAlchemy` — PostgreSQL driver and abstraction layer
- `db_connection.py` — single connection layer routing to SQLite or PostgreSQL
- `db_pg.py` — PostgreSQL-compatible SQL for all core database operations
- `scripts/migrate_to_postgres.py` — one-time migration from SQLite to PostgreSQL
- `test_api.py` — 32 FastAPI TestClient tests covering every Phase 1 endpoint
- `scripts/test_api.sh` — curl smoke test for all endpoints against a live server
- `Dockerfile` — containerises the FastAPI backend for AWS App Runner
- `docker-compose.yml` — local dev environment with FastAPI + PostgreSQL

### Changed
- `database.py` now routes all connections through `db_connection.get_connection()`
- API version bumped to `1.3.0`
- `requirements-api.txt` updated with all new dependencies
- CI workflow now runs `test_api.py` in both test matrix and api-smoke-test jobs

---

## [1.2.0] — 2026-07-02

### Added
- `exceptions.py` — single source of truth for `ValidationError`; all UI pages now import from here
- `CONTRIBUTING.md` — full contributor guide: setup, running tests, project layout, code style, commit convention
- Class and method docstrings across all `page_*.py` files and `financial_state.py`
- Module docstring for `database.py` documenting all five SQLite tables
- 8 new test classes covering `FinancialState` CRUD, database settings, `ValidationError`, both parsers, simulation edge cases, `dedup_jobs`/`dedup_expenses`, and `week_engine`
- `scripts/demo.py` — runnable 60-line demo showing the full value prop with no GUI
- Type hints added to `simulation.py`, `scenario_engine.py`, and `insight_engine.py`

### Changed
- `README.md` rewritten to lead with the product and its value, not the architecture; architecture/Monte Carlo details moved below the fold
- All `raise ValueError` in UI pages replaced with `raise ValidationError`; catch sites updated to `except (ValueError, ValidationError)`
- Unused imports removed from `app.py`, `page_data.py`, `pdf_report.py`, `page_more.py`, `time_engine.py`, `schedule_event.py`, `financial_state.py`
- `page_schedule.py`: long inline word lists extracted to named variables to satisfy 120-char line limit

---

## [0.4.0] — 2026-07-02

### Added
- Function docstrings to `financial_state.py` (all public methods)

### Style
- Linter pass across entire codebase; all warnings resolved

### Removed
- Dead code: unused imports, commented-out blocks, stale variables

---

## [0.3.0] — 2026-06-30

### Changed
- All magic numbers extracted to `config.py`; no inline constants remain
- Free-time calculation consolidated into `time_engine.py`
- Shift planner UI migrated to `schedule_core`

---

## [0.2.0] — 2026-06-29

### Added
- Optimization engine (0/1 knapsack shift selection)
- FastAPI web service (`api.py`); `render.yaml` for one-command deployment
- `IncomeMode` moved to `schedule_core`; `shift_engine` deprecated

---

## [0.1.0] — 2026-06-18

### Added
- Initial release: Financial Reality Engine with tkinter desktop app
- Monte Carlo simulation (NumPy-vectorized, 5× speedup over pure Python)
- SQLite persistence via `database.py`
- Core data models (`Job`, `Expense`) with frequency-aware weekly conversion
- 166 pytest tests covering financial state, optimizer, simulation, and schedule logic
