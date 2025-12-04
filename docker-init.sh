#!/bin/bash
# Initialization script for Docker container

set -e

echo "🚀 Initializing CEE Pipeline..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
python << 'PYSCRIPT'
import psycopg2
import os
import time
import sys

max_tries = 30
for attempt in range(1, max_tries + 1):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'cee_pipeline'),
            user=os.getenv('POSTGRES_USER', 'cee_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'cee_password_change_me'),
            host='postgres',
            connect_timeout=5
        )
        conn.close()
        print('✓ PostgreSQL is ready!')
        sys.exit(0)
    except Exception as e:
        if attempt < max_tries:
            print(f'PostgreSQL not ready (attempt {attempt}/{max_tries}), waiting...')
            time.sleep(2)
        else:
            print(f'ERROR: Failed to connect to PostgreSQL after {max_tries} attempts')
            print(f'Last error: {e}')
            sys.exit(1)
PYSCRIPT

if [ $? -ne 0 ]; then
    echo "❌ Failed to connect to PostgreSQL"
    exit 1
fi

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
