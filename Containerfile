# Use a lightweight base image with Python
FROM python:3.9-slim

# Install required dependencies for PostgreSQL, build tools, and runtime
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql \
    postgresql-contrib \

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Set up the PostgreSQL database
RUN service postgresql start && \
    su - postgres -c "psql -c \"CREATE DATABASE coding_platform;\"" && \
    su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\"" && \
    su - postgres -c "psql coding_platform < /app/init.sql"

# Expose port for the Flask app
EXPOSE 5000

# Run PostgreSQL and the Flask app
CMD service postgresql start && gunicorn -w 4 -b 0.0.0.0:5000 app:app
