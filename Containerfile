# Use a lightweight base image with Python
FROM python:3.9-slim

# Install required dependencies for PostgreSQL and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Initialize the PostgreSQL database
RUN service postgresql start && \
    su - postgres -c "psql -c \"CREATE USER postgres WITH PASSWORD 'postgres';\"" && \
    su - postgres -c "psql -c \"CREATE DATABASE coding_platform OWNER postgres;\"" && \
    su - postgres -c "psql coding_platform < init.sql"

# Expose port for the Flask app
EXPOSE 5000

# Command to start both PostgreSQL and Flask using supervisord
CMD ["sh", "-c", "service postgresql start && gunicorn -w 4 -b 0.0.0.0:5000 app:app"]
