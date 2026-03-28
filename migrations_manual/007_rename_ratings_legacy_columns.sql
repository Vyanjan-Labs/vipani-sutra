-- Upgrade path from older rating column names → from_user_id / to_user_id / stars / reputation_scope.
-- Backup first.

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'ratings' AND column_name = 'rater_user_id'
  ) THEN
    ALTER TABLE ratings RENAME COLUMN rater_user_id TO from_user_id;
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'ratings' AND column_name = 'given_by_user_id'
  ) THEN
    ALTER TABLE ratings RENAME COLUMN given_by_user_id TO from_user_id;
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'ratings' AND column_name = 'ratee_user_id'
  ) THEN
    ALTER TABLE ratings RENAME COLUMN ratee_user_id TO to_user_id;
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'ratings' AND column_name = 'rated_user_id'
  ) THEN
    ALTER TABLE ratings RENAME COLUMN rated_user_id TO to_user_id;
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'ratings' AND column_name = 'score'
  ) THEN
    ALTER TABLE ratings RENAME COLUMN score TO stars;
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'ratings' AND column_name = 'rating_kind'
  ) THEN
    ALTER TABLE ratings RENAME COLUMN rating_kind TO reputation_scope;
    UPDATE ratings SET reputation_scope = CASE reputation_scope
      WHEN 'buyer_rates_seller' THEN 'seller'
      WHEN 'seller_rates_buyer' THEN 'buyer'
      ELSE reputation_scope
    END;
  END IF;
END $$;

ALTER TABLE ratings DROP CONSTRAINT IF EXISTS uq_rating_listing_rater_kind;
ALTER TABLE ratings DROP CONSTRAINT IF EXISTS uq_rating_listing_giver_scope;
ALTER TABLE ratings DROP CONSTRAINT IF EXISTS uq_rating_listing_from_scope;
ALTER TABLE ratings ADD CONSTRAINT uq_rating_listing_from_scope
  UNIQUE (listing_id, from_user_id, reputation_scope);

DROP INDEX IF EXISTS ix_ratings_ratee_kind;
DROP INDEX IF EXISTS ix_ratings_rated_scope;
DROP INDEX IF EXISTS ix_ratings_given_by_user_id;
CREATE INDEX IF NOT EXISTS ix_ratings_to_scope ON ratings(to_user_id, reputation_scope);
CREATE INDEX IF NOT EXISTS ix_ratings_from_user_id ON ratings(from_user_id);
