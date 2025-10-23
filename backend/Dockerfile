# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Install psycopg2 for PostgreSQL support and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org psycopg2-binary && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY . .

# Make startup script executable
RUN chmod +x startup.sh

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run startup script (includes migration + Flask app)
CMD ["./startup.sh"]
