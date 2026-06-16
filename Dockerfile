# Onfido SQL Dashboard — Production Docker Image
# Uses Uvicorn workers for ASGI performance
# Build: docker build -t onfido-dashboard .
# Run:   docker run -p 8000:8000 --env-file .env onfido-dashboard

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 17 for SQL Server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY frontend ./frontend
COPY sql ./sql
COPY scripts ./scripts
COPY tests ./tests
COPY etl ./etl

# Expose port
EXPOSE 8000

# Run with 4 Uvicorn workers (adjust WORKERS env if needed)
ENV WORKERS=4
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS}"]
