-- Sold-listing buyer + ratings (from_user = rater, to_user = who receives the stars).

ALTER TABLE listings ADD COLUMN IF NOT EXISTS buyer_user_id INTEGER REFERENCES users(id);
CREATE INDEX IF NOT EXISTS ix_listings_buyer_user_id ON listings(buyer_user_id);

CREATE TABLE IF NOT EXISTS ratings (
  id SERIAL PRIMARY KEY,
  listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
  from_user_id INTEGER NOT NULL REFERENCES users(id),
  to_user_id INTEGER NOT NULL REFERENCES users(id),
  reputation_scope VARCHAR NOT NULL,
  stars SMALLINT NOT NULL,
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_rating_listing_from_scope UNIQUE (listing_id, from_user_id, reputation_scope)
);

CREATE INDEX IF NOT EXISTS ix_ratings_listing_id ON ratings(listing_id);
CREATE INDEX IF NOT EXISTS ix_ratings_to_scope ON ratings(to_user_id, reputation_scope);
CREATE INDEX IF NOT EXISTS ix_ratings_from_user_id ON ratings(from_user_id);
