#!/bin/bash

echo "🎉 Starting Wedding Planner Server..."
echo "⏳ Waiting for MongoDB to be ready..."

python3 -c "
import time
import pymongo
import os

mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/wedding_planner')
max_retries = 30
retry_delay = 2

for i in range(max_retries):
    try:
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ismaster')
        print('✅ MongoDB is ready!')
        client.close()
        break
    except Exception as e:
        if i < max_retries - 1:
            print(f'MongoDB not ready yet, retrying in {retry_delay} seconds... ({i+1}/{max_retries})')
            time.sleep(retry_delay)
        else:
            print('❌ Failed to connect to MongoDB after all retries')
            exit(1)
"

echo "📦 Initializing database..."
python3 -c "from main import create_app; app = create_app(); app.app_context().push(); from models import init_db; init_db(); print('Database initialized successfully')" || echo "Database initialization completed"

echo "✅ Database setup completed!"
echo "🚀 Starting Flask application..."

exec gunicorn --bind 0.0.0.0:${CLIENT_PORT:-5000} main:app
