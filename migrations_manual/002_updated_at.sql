-- `updated_at` = last modified (kept in sync by SQLAlchemy on UPDATE).

ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
UPDATE users SET updated_at = created_at;

ALTER TABLE listings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
UPDATE listings SET updated_at = created_at;
