FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and others
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source code is mounted via volume in dev, but copied for completeness
COPY src /app/src

EXPOSE 8000

# Run uvicorn via python script
CMD ["python", "src/main.py"]
