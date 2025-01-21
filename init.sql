-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    end_date TIMESTAMP NOT NULL
);

-- Create results table
CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    task_id INT REFERENCES tasks(id),
    result TEXT NOT NULL
);

-- Insert a test user
INSERT INTO users (username, password)
VALUES ('testuser', crypt('testpassword', gen_salt('bf')));

-- Insert a test task
INSERT INTO tasks (title, end_date)
VALUES ('Example Task', NOW() + INTERVAL '7 days');
