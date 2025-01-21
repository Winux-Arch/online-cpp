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
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Set up PostgreSQL database
# Create the database and set password only if PostgreSQL isn't already set up
RUN /etc/init.d/postgresql start && \
    su - postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'coding_platform'\" | grep -q 1 || psql -c \"CREATE DATABASE coding_platform;\"" && \
    su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\"" && \
    su - postgres -c "psql coding_platform < /app/init.sql" && \
    /etc/init.d/postgresql stop

# Expose port for the Flask app
EXPOSE 5000

# Run PostgreSQL and the Flask app
CMD ["sh", "-c", "/etc/init.d/postgresql start && gunicorn -w 4 -b 0.0.0.0:5000 app:app"]
