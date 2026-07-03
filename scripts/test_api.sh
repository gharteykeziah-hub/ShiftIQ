#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# test_api.sh — Smoke-test every ShiftIQ API endpoint with curl.
#
# Usage:
#   # Against local dev server (default):
#   ./scripts/test_api.sh
#
#   # Against a deployed server:
#   BASE_URL=https://your-app.awsapprunner.com ./scripts/test_api.sh
#
# Requires: curl, jq (jq is optional — output is still readable without it)
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL="${BASE_URL:-http://localhost:8000}"
PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # no colour

_check() {
    local label="$1"
    local expected="$2"
    local actual="$3"
    if echo "$actual" | grep -q "$expected"; then
        echo -e "  ${GREEN}✓${NC}  $label"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗${NC}  $label"
        echo "      expected to find: $expected"
        echo "      got: $(echo "$actual" | head -c 200)"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo -e "${BLUE}ShiftIQ API — endpoint smoke test${NC}"
echo -e "${BLUE}Target: $BASE_URL${NC}"
echo "─────────────────────────────────────────────"

# ── Health ────────────────────────────────────────────────────────────────────
echo ""
echo "Health"
R=$(curl -sf "$BASE_URL/api/health")
_check "GET /api/health" '"status":"ok"' "$R"

# ── State ─────────────────────────────────────────────────────────────────────
echo ""
echo "Financial State"
R=$(curl -sf "$BASE_URL/api/state")
_check "GET /api/state — has balance"        '"balance"'       "$R"
_check "GET /api/state — has weekly_income"  '"weekly_income"' "$R"
_check "GET /api/state — has health_score"   '"health_score"'  "$R"

# ── Balance ───────────────────────────────────────────────────────────────────
echo ""
echo "Balance"
R=$(curl -sf -X PUT "$BASE_URL/api/balance" \
    -H "Content-Type: application/json" \
    -d '{"amount": 820.0}')
_check "PUT /api/balance" '"balance":820' "$R"

# ── Jobs ──────────────────────────────────────────────────────────────────────
echo ""
echo "Jobs"
R=$(curl -sf -X POST "$BASE_URL/api/jobs" \
    -H "Content-Type: application/json" \
    -d '{"name":"Campus Dining","amount":280,"frequency":"Weekly"}')
_check "POST /api/jobs" '"name":"Campus Dining"' "$R"

R=$(curl -sf "$BASE_URL/api/jobs")
_check "GET /api/jobs" '"Campus Dining"' "$R"

R=$(curl -sf -X PUT "$BASE_URL/api/jobs/Campus%20Dining" \
    -H "Content-Type: application/json" \
    -d '{"name":"Campus Dining","amount":300,"frequency":"Weekly"}')
_check "PUT /api/jobs/{name}" '"amount":300' "$R"

# ── Expenses ──────────────────────────────────────────────────────────────────
echo ""
echo "Expenses"
R=$(curl -sf -X POST "$BASE_URL/api/expenses" \
    -H "Content-Type: application/json" \
    -d '{"name":"Rent","amount":700,"category":"Housing","date":"2026-01-01","frequency":"Monthly"}')
_check "POST /api/expenses" '"name":"Rent"' "$R"

R=$(curl -sf "$BASE_URL/api/expenses")
_check "GET /api/expenses" '"Rent"' "$R"

R=$(curl -sf -X PUT "$BASE_URL/api/expenses/Rent" \
    -H "Content-Type: application/json" \
    -d '{"name":"Rent","amount":750,"category":"Housing","date":"2026-01-01","frequency":"Monthly"}')
_check "PUT /api/expenses/{name}" '"amount":750' "$R"

# ── Projection ────────────────────────────────────────────────────────────────
echo ""
echo "Projection"
R=$(curl -sf "$BASE_URL/api/projection?weeks=4")
_check "GET /api/projection" '"timeline"' "$R"

# ── Insights ──────────────────────────────────────────────────────────────────
echo ""
echo "Insights"
R=$(curl -sf "$BASE_URL/api/insights")
_check "GET /api/insights" '"health_score"' "$R"
_check "GET /api/insights — insights list" '"insights"' "$R"

# ── History ───────────────────────────────────────────────────────────────────
echo ""
echo "History"
R=$(curl -sf "$BASE_URL/api/history")
_check "GET /api/history" '"snapshots"' "$R"

# ── Simulation ────────────────────────────────────────────────────────────────
echo ""
echo "Simulation"
R=$(curl -sf -X POST "$BASE_URL/api/simulate/monte-carlo" \
    -H "Content-Type: application/json" \
    -d '{"weeks":4,"n":100}')
_check "POST /api/simulate/monte-carlo" '"average"' "$R"

R=$(curl -sf -X POST "$BASE_URL/api/simulate/whatif" \
    -H "Content-Type: application/json" \
    -d '{"description":"Car repair","dollar_change":-400,"weeks":4}')
_check "POST /api/simulate/whatif" '"history"' "$R"

# ── Analytics ─────────────────────────────────────────────────────────────────
echo ""
echo "Analytics"
R=$(curl -sf "$BASE_URL/api/analytics/income")
_check "GET /api/analytics/income" '{}' "$R"

R=$(curl -sf "$BASE_URL/api/analytics/efficiency")
_check "GET /api/analytics/efficiency" '[]' "$R"

# ── Cleanup ───────────────────────────────────────────────────────────────────
curl -sf -X DELETE "$BASE_URL/api/jobs/Campus%20Dining" > /dev/null
curl -sf -X DELETE "$BASE_URL/api/expenses/Rent" > /dev/null

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "─────────────────────────────────────────────"
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}All $TOTAL checks passed.${NC}"
else
    echo -e "${RED}$FAIL of $TOTAL checks failed.${NC}"
    exit 1
fi
echo ""
