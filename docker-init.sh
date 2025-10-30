#!/bin/bash
# Initialization script for Docker container

set -e

echo "🚀 Initializing CEE Pipeline..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until python -c "
import psycopg2
import os
import time
import sys

max_tries = 30
tries = 0

while tries < max_tries:
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'cee_pipeline'),
            user=os.getenv('POSTGRES_USER', 'cee_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'cee_password_change_me'),
            host='postgres'
        )
        conn.close()
        print('PostgreSQL is ready!')
        sys.exit(0)
    except:
        tries += 1
        print(f'PostgreSQL not ready, attempt {tries}/{max_tries}')
        time.sleep(2)

print('PostgreSQL connection failed after all retries')
sys.exit(1)
" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✓ PostgreSQL is ready!"

# Initialize database tables
echo "📊 Creating database tables..."
python -c "
from cee_pipeline.database.database import db
db.create_tables()
print('✓ Database tables created!')
"

# Download NLTK data (if not already done)
echo "📚 Ensuring NLTK data is available..."
python -c "
import nltk
nltk.download('punkt', quiet=True)
print('✓ NLTK data ready!')
"

echo "✓ Initialization complete!"
echo ""
echo "🎉 CEE Pipeline is ready!"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Dashboard: http://localhost/dashboard/dashboard.html"
echo ""

# Start the application
exec "$@"
