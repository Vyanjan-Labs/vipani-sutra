-- Run manually on existing PostgreSQL DB (backup first).

ALTER TABLE users ADD COLUMN IF NOT EXISTS seller_verification_status VARCHAR NOT NULL DEFAULT 'none';
ALTER TABLE users ADD COLUMN IF NOT EXISTS pan_number VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS aadhaar_number VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_buyer BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_seller BOOLEAN NOT NULL DEFAULT TRUE;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'role'
  ) THEN
    ALTER TABLE users DROP COLUMN role;
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'is_admin'
  ) THEN
    ALTER TABLE users DROP COLUMN is_admin;
  END IF;
END $$;
