-- Step 1: Find the correct user table name
-- Run this first to see all tables
\dt

-- Look for tables that might be the user table:
-- Common names: auth_user, users, accounts_user, custom_user, etc.

-- Step 2: Once you find the user table, run this (replace TABLE_NAME with actual name):
-- Example: If table is 'users':
-- CREATE TABLE IF NOT EXISTS feature_notification_requests (
--     id BIGSERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     ...
-- );

