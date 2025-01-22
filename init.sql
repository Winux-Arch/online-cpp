-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Create tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    end_date TEXT NOT NULL
);

-- Create results table
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task_id INTEGER,
    result TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Insert a test user
INSERT INTO users (username, password)
VALUES ('testuser', 'scrypt:32768:8:1$5SjL8gqRuClrPRo8$0a02edff67dd343e8a5225d9c427e803a0e10a556d5523fb43f2bfe4fc3734307ca9dc237d7a2c89a29ca312aa448b2f7371bbcfaa904158240304c159dd90a8');

-- Insert a test task
INSERT INTO tasks (title, end_date)
VALUES ('Example Task', datetime('now', '+7 days'));
