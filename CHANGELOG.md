# Changelog

## v1.3
- Centralised `canon_name()` into `utils.py` — removed four duplicate implementations across `database.py`, `schedule_analytics.py`, `app.py`, and `page_schedule.py`
- Fixed `ScenarioEngine` projection bug: `extra_weekly` was applied once per job instead of once to the total
- Extracted schedule-to-financial sync from `App.__init__` into `schedule_service.py` (testable without Tk)
- Added `shift_impact()` and `job_efficiency_report()` to `schedule_analytics.py` — the decision engine
- Wired `schedule_analytics` into Analytics → Income and Trends tabs (previously disconnected)
- Enriched CSV and PDF exports with full schedule summary, per-job breakdown, and top earning days
- Expanded test suite to 140+ tests: added `TestCanonName`, `TestScenarioEngineBugRegression`, `TestScheduleAnalytics`, `TestShiftImpact`, `TestJobEfficiency`, `TestStress`

## v1.2
- Schedule planner page: weekly calendar, shift entry with conflict detection, free-block analysis
- Opportunity cost calculation for free time blocks
- Week navigation engine

## v1.1
- Frequency support for all income and expense entries (Daily / Weekly / Biweekly / Monthly)
- Automatic schema migration from old `hourly_rate + hours_per_week` model
- Balance projection chart
- PDF export (reportlab)
- Database backup
- Monte Carlo histogram
- Historical trend tracking (daily snapshots)

## v1.0
- Dashboard with live balance, income, expenses, net flow, insights
- Data management for jobs and expenses
- Financial Health Score and Risk Score
- Goals tracker with weeks-to-goal calculator
- Forecasting: scenario comparison, What-If simulator, Monte Carlo simulation
- Activity log
- CSV export
