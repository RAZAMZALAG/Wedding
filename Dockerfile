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

# Install PostgreSQL dev libs & build tools
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY Server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Server/ .

COPY --from=frontend /client/dist ./dist

CMD ["gunicorn", "--bind", "0.0.0.0:${CLIENT_PORT}", "main:create_app()"]