-- Split buyer/seller concerns into profile tables (backup DB first).

CREATE TABLE IF NOT EXISTS buyer_profiles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_buyer_profiles_user_id ON buyer_profiles(user_id);

CREATE TABLE IF NOT EXISTS seller_profiles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  shop_name VARCHAR,
  verification_status VARCHAR NOT NULL DEFAULT 'none',
  pan_number VARCHAR,
  aadhaar_number VARCHAR,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_seller_profiles_user_id ON seller_profiles(user_id);

-- Backfill from legacy columns on `users` (if present from 001).
-- shop_name is set to NULL here; if your DB had `users.shop_name` from ORM-only deploys, copy it with a one-off UPDATE after inspecting data.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'seller_verification_status'
  ) THEN
    INSERT INTO seller_profiles (user_id, shop_name, verification_status, pan_number, aadhaar_number, created_at, updated_at)
    SELECT u.id,
           NULL,
           u.seller_verification_status,
           u.pan_number,
           u.aadhaar_number,
           COALESCE(u.updated_at, u.created_at),
           COALESCE(u.updated_at, u.created_at)
    FROM users u
    WHERE u.is_seller = TRUE
      AND NOT EXISTS (SELECT 1 FROM seller_profiles sp WHERE sp.user_id = u.id);
  END IF;
END $$;

INSERT INTO buyer_profiles (user_id, created_at, updated_at)
SELECT u.id, COALESCE(u.updated_at, u.created_at), COALESCE(u.updated_at, u.created_at)
FROM users u
WHERE u.is_buyer = TRUE
  AND NOT EXISTS (SELECT 1 FROM buyer_profiles bp WHERE bp.user_id = u.id)
ON CONFLICT (user_id) DO NOTHING;

ALTER TABLE users DROP COLUMN IF EXISTS seller_verification_status;
ALTER TABLE users DROP COLUMN IF EXISTS pan_number;
ALTER TABLE users DROP COLUMN IF EXISTS aadhaar_number;
ALTER TABLE users DROP COLUMN IF EXISTS shop_name;
