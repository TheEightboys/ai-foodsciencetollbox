-- SQL script to manually add billing_interval column if migration fails
-- Run this on your production database if the Django migration doesn't work

-- For PostgreSQL:
ALTER TABLE user_memberships 
ADD COLUMN IF NOT EXISTS billing_interval VARCHAR(10) NULL;

-- Add a comment to the column
COMMENT ON COLUMN user_memberships.billing_interval IS 'Billing interval: monthly or yearly subscription';

-- Note: This column is nullable and optional, so existing rows will have NULL values
-- which is acceptable since the field has null=True, blank=True in the model

