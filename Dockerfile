# First Stage

FROM node:20 AS frontend

WORKDIR /client

# Copy only dependency files first (for caching)
COPY Client/package*.json ./
RUN npm install

# Copy the rest of the client code
COPY Client/ .
RUN npm run build


# Second Stage

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including curl for health check
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY Server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Server/ .

COPY --from=frontend /client/dist ./dist

# Create catalog directory
RUN mkdir -p catalog

# Create startup script that runs migration then starts server
RUN echo '#!/bin/bash\n\
echo "🎉 Starting Wedding Planner Server..."\n\
echo "📦 Running database migration and setup..."\n\
python migrate_to_mongo.py || echo "Migration failed or already completed"\n\
echo "✅ Database setup completed!"\n\
echo "🚀 Starting Flask application..."\n\
exec gunicorn --bind 0.0.0.0:${CLIENT_PORT:-5000} main:app' > start.sh

# Make startup script executable
RUN chmod +x start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${CLIENT_PORT:-5000}/api/items || exit 1

# Run the startup script instead of direct gunicorn
CMD ["./start.sh"]