-- Manual fix for feature_notification_requests table
-- Run this SQL script directly on your production database

-- Create the feature_notification_requests table
CREATE TABLE IF NOT EXISTS feature_notification_requests (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    feature_name VARCHAR(200) NOT NULL,
    user_email VARCHAR(254) NOT NULL,
    notified BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    notified_at TIMESTAMP WITH TIME ZONE NULL,
    UNIQUE (user_id, feature_name)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS feature_notification_requests_user_id_idx 
    ON feature_notification_requests(user_id);

CREATE INDEX IF NOT EXISTS feature_notification_requests_feature_name_idx 
    ON feature_notification_requests(feature_name);

CREATE INDEX IF NOT EXISTS feature_notification_requests_notified_idx 
    ON feature_notification_requests(notified);

-- Record this migration as applied
INSERT INTO django_migrations (app, name, applied)
VALUES ('notifications', '0001_initial', NOW())
ON CONFLICT DO NOTHING;

-- Success message
SELECT 'Table feature_notification_requests created successfully!' as status;

