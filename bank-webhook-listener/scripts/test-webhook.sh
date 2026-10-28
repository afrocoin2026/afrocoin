#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://localhost:8443}"
HMAC_KEY="${HMAC_KEY:-KONGPAY_SUPER_SECRET_KEY_2026}"
PG_SERVICE="${PG_SERVICE:-postgres}"   # Compose 中的服务名
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-kongpay_db}"

EVID="EVT-MAKE-$(date +%s)"
BODY="{\"event_id\":\"$EVID\",\"account_number\":\"42\",\"amount\":1234.56,\"currency\":\"IDR\",\"sender_name\":\"Makefile\",\"reference\":\"INV-MAKE\",\"status\":\"COMPLETED\"}"
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$HMAC_KEY" | awk '{print $2}')

echo "▶ POST $EVID"
curl -sS -X POST "$BASE_URL/api/v1/bank-webhook" \
  --cacert ca.crt --cert client.crt --key client.key \
  -H "Content-Type: application/json" -H "X-Hub-Signature: $SIG" \
  -d "$BODY"
echo

echo "▶ DB row:"
# 关键改动：使用 docker compose exec，并用 -T 禁用 TTY
docker compose exec -T "$PG_SERVICE" psql -U "$PG_USER" -d "$PG_DB" -c \
  "SELECT id,event_id,status,created_at FROM bank_transactions WHERE event_id='$EVID';"

echo "▶ counter:"
curl -s http://localhost:9090/metrics | grep '^kongpay_transactions_success_total'
