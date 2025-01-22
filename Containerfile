# Use a lightweight base image with Python
FROM python:3.12-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    sqlite3 \
    sqlite3-tools

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Initialize SQLite database
RUN sqlite3 coding_platform.db -init init.sql

# Expose port for the Flask app
EXPOSE 5000

# Run the Flask app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
