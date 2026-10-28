CREATE TABLE IF NOT EXISTS bank_transactions (
    id              BIGSERIAL PRIMARY KEY,
    event_id        TEXT UNIQUE NOT NULL,
    account_number  TEXT NOT NULL,
    amount          NUMERIC(18,2) NOT NULL,
    currency        TEXT NOT NULL,
    sender_name     TEXT,
    reference       TEXT,
    status          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
