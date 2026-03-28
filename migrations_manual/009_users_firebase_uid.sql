-- Link Firebase Auth users to app users (optional column).

ALTER TABLE users ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR UNIQUE;
CREATE INDEX IF NOT EXISTS ix_users_firebase_uid ON users(firebase_uid);
