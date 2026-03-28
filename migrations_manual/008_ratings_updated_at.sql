-- Track last edit time on ratings (backup first).

ALTER TABLE ratings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
UPDATE ratings SET updated_at = created_at WHERE updated_at IS NULL;
