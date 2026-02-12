# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gcc \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements/base.txt requirements/development.txt requirements/production.txt ./requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["/app/start.sh"]