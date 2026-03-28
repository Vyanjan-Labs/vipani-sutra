-- Seller DOB and sex (age is computed in the API from date_of_birth).

ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS sex VARCHAR;
