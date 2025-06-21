# Use official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Create data directory
RUN mkdir -p /var/lib/sqlite && \
    chown -R 1000:1000 /var/lib/sqlite

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY requirements.txt .
COPY app.py .
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY services/ /app/services/
RUN chown -R 1000:1000 /app

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]