#!/usr/bin/env python3
import pathlib
T = "\t"
lines = [
    "# KongPay Webhook Listener — auto-generated Makefile",
    "SHELL       := /bin/bash",
    "COMPOSE     ?= docker compose",
    "PG_SERVICE  ?= kongpay_postgres",
    "PG_USER     ?= postgres",
    "PG_DB       ?= kongpay_db",
    "BASE_URL    ?= https://localhost:8443",
    "HMAC_KEY    ?= KONGPAY_SUPER_SECRET_KEY_2026",
    "TEST_DSN    ?= postgres://postgres:password@localhost:5432/kongpay_db?sslmode=disable",
    "",
    ".DEFAULT_GOAL := help",
    ".PHONY: help up down restart rebuild reset ps logs build vet fmt tidy test test-short test-db test-live test-webhook metrics history db psql grafana prom-targets clean",
    "",
]

def rule(name, desc, *cmds):
    lines.append(f"{name}: ## {desc}")
    for c in cmds:
        lines.append(T + c)
    lines.append("")

rule("help", "Show all targets",
     r'''@grep -E "^[a-zA-Z0-9_-]+:.*?## " $(MAKEFILE_LIST) | awk "BEGIN{FS=\":.*?## \"}{printf \"  %-16s %s\\n\", \$$1, \$$2}"''')
rule("up", "Start the stack", "$(COMPOSE) up -d")
rule("down", "Stop the stack", "$(COMPOSE) down")
rule("restart", "Restart all", "$(COMPOSE) restart")
rule("rebuild", "Rebuild backend",
     "$(COMPOSE) build kongpay-backend",
     "$(COMPOSE) up -d --force-recreate kongpay-backend")
rule("reset", "Nuke + up",
     "$(COMPOSE) down -v --remove-orphans",
     "$(COMPOSE) up --build -d")
rule("ps", "Container status", "$(COMPOSE) ps")
rule("logs", "Tail backend logs", "$(COMPOSE) logs -f --tail 50 kongpay_backend")
rule("vet", "go vet", "go vet .")
rule("fmt", "gofmt", "gofmt -w .")
rule("tidy", "go mod tidy", "go mod tidy")
rule("build", "Build binary", "go build -o /tmp/kongpay-app .")
rule("test-short", "Unit tests", "go test . -short -v")
rule("test-db", "DB tests", 'TEST_DATABASE_URL="$(TEST_DSN)" go test . -v')
rule("test-live", "Live mTLS test", "go test . -run TestWebhookMTLS_Live -v")
rule("test", "Unit + DB", "make test-short", "make test-db")
rule("test-all", "All tests", "make test", "make test-live")
rule("test-webhook", "Send signed webhook", "./scripts/test-webhook.sh")
rule("metrics", "KongPay metrics", '@curl -s http://localhost:9090/metrics | grep -E "^kongpay_"')
rule("history", "GET transaction history",
     '@curl -s "$(BASE_URL)/api/v1/transactions" --cacert ca.crt --cert client.crt --key client.key | jq .')
rule("db", "Dump DB",
     '@$(COMPOSE) exec -T $(PG_SERVICE) psql -U $(PG_USER) -d $(PG_DB) -c "SELECT id,event_id,status,created_at FROM bank_transactions ORDER BY id DESC;"')
rule("psql", "Open psql", "$(COMPOSE) exec $(PG_SERVICE) psql -U $(PG_USER) -d $(PG_DB)")
rule("prom-targets", "Prometheus targets",
     r'''@curl -s http://localhost:9091/api/v1/targets | jq -r ".data.activeTargets[] | \"\(.labels.job)\t\(.health)\t\(.scrapeUrl)\""''')
rule("grafana", "Open Grafana",
     '@xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 (admin/admin)"')
rule("clean", "Clean artifacts", "rm -f san.cnf server.csr kongpay-app")

pathlib.Path("Makefile").write_text("\n".join(lines) + "\n")
print("✔ wrote Makefile with", len(lines), "lines")
