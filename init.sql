-- Database initialization script for AI Video Narrator

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    credits INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(500),
    output_path VARCHAR(1000),
    storage_object_name VARCHAR(500),
    storage_url TEXT,
    file_size BIGINT,
    thumbnail_url TEXT,
    status VARCHAR(50) DEFAULT 'processing',
    voice_config JSONB,
    audio_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_users_email ON users(email);

-- Insert default admin user (password: admin123)
-- Password hash for 'admin123' with bcrypt
INSERT INTO users (email, password_hash, credits) 
VALUES (
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqL.4jYOzC',
    1000
) ON CONFLICT (email) DO NOTHING;
