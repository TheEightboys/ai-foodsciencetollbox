#!/bin/bash
# Don't use set -e - we want to handle errors gracefully
# Don't use set -u - environment variables might not be set

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    echo "Activating virtual environment..."
    source /opt/venv/bin/activate
    echo "Virtual environment activated. Python: $(which python)"
else
    echo "Warning: Virtual environment not found at /opt/venv, using system Python"
fi

# Verify Python and Gunicorn are available
echo "Checking Python installation..."
python --version || { echo "ERROR: Python not found!"; exit 1; }

echo "Checking Gunicorn installation..."
gunicorn --version || { echo "ERROR: Gunicorn not found!"; exit 1; }

# Verify and install fpdf2 if missing (required for PDF generation)
echo "Checking fpdf2 installation..."
if python -c "from fpdf import FPDF" 2>/dev/null; then
    echo "✓ fpdf2 is installed and working"
else
    echo "WARNING: fpdf2 not found or not working, attempting to install..."
    # Use fpdf2 2.7.* - pure Python, no dependencies
    python -m pip install --upgrade --force-reinstall "fpdf2==2.7.*" 2>&1 || {
        echo "ERROR: Failed to install fpdf2. PDF generation will not work."
        echo "Please ensure fpdf2 is in requirements.txt and rebuild the deployment."
    }
    # Verify installation
    if python -c "from fpdf import FPDF" 2>/dev/null; then
        echo "✓ fpdf2 installed successfully"
    else
        echo "ERROR: fpdf2 installation failed. PDF downloads will not work."
    fi
fi

# Function to parse DATABASE_URL and extract host/port
parse_db_url() {
    # Use parameter expansion to safely check if DATABASE_URL is set
    if [ -n "${DATABASE_URL:-}" ]; then
        # Parse DATABASE_URL: postgresql://user:pass@host:port/dbname
        DB_HOST_PORT=$(echo "$DATABASE_URL" | sed -e 's/.*@\([^/]*\).*/\1/')
        DB_HOST=$(echo "$DB_HOST_PORT" | cut -d: -f1)
        DB_PORT=$(echo "$DB_HOST_PORT" | cut -d: -f2)
        if [ -z "$DB_PORT" ]; then
            DB_PORT=5432
        fi
    else
        DB_HOST=${DB_HOST:-localhost}
        DB_PORT=${DB_PORT:-5432}
    fi
}

# Wait for database to be ready
echo "Waiting for database..."
parse_db_url
echo "Checking database at $DB_HOST:$DB_PORT..."

# Wait for database with timeout
timeout=30
counter=0
while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "WARNING: Database connection timeout after ${timeout}s, continuing anyway..."
        break
    fi
    sleep 1
    counter=$((counter + 1))
done
echo "Database check complete!"

# Run migrations
echo "Running migrations..."
# Check if database is available before running migrations
parse_db_url
if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
    echo "Database is available, running migrations..."
    
    # First, create migrations for apps that don't have them
    echo "Creating migrations for apps that need them..."
    python manage.py makemigrations accounts memberships payments generators downloads notifications legal 2>&1 | grep -v "No changes detected" || true
    
    # Then run migrations
    if python manage.py migrate --noinput 2>&1; then
        echo "✓ Migrations completed successfully"
    else
        MIGRATION_EXIT_CODE=$?
        echo "WARNING: Migrations encountered issues (exit code: $MIGRATION_EXIT_CODE)"
        echo "Attempting to run migrations with --run-syncdb for initial setup..."
        # Try with --run-syncdb for fresh databases
        python manage.py migrate --run-syncdb --noinput 2>&1 || {
            echo "Migration issues persist. The application will continue to start."
            echo "You may need to run migrations manually:"
            echo "  1. python manage.py makemigrations"
            echo "  2. python manage.py migrate"
        }
    fi
else
    echo "WARNING: Database is not available at $DB_HOST:$DB_PORT"
    echo "Skipping migrations for now. They will run when the database is available."
    echo "You may need to run migrations manually once the database is connected."
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 || {
    echo "WARNING: Static files collection failed, continuing..."
    # Try without --clear flag
    python manage.py collectstatic --noinput 2>&1 || echo "Static files collection failed again, continuing..."
}

# Load legal documents if they don't exist
echo "Loading legal documents..."
python manage.py load_legal_documents 2>&1 || {
    echo "WARNING: Failed to load legal documents, continuing..."
}

# Load email templates
echo "Loading email templates..."
python manage.py load_email_templates 2>&1 || {
    echo "WARNING: Failed to load email templates, continuing..."
    echo "You can run 'python manage.py load_email_templates' manually later."
}

# Initialize membership tiers if they don't exist
# Run in background to not block startup if it fails
echo "Initializing membership tiers..."
python manage.py init_tiers 2>&1 || {
    echo "WARNING: Failed to initialize membership tiers, continuing..."
    echo "You can run 'python manage.py init_tiers' manually later."
}

# Create superuser if it doesn't exist (non-interactive)
# Run in background to not block startup if it fails
echo "Creating superuser (if not exists)..."
python manage.py create_superuser --email admin@foodsciencetoolbox.com --password Admin --first-name Admin --last-name User 2>&1 || {
    echo "WARNING: Failed to create superuser, continuing..."
    echo "You can run 'python manage.py create_superuser' manually later."
}

# Test if Django can import the WSGI application
echo "Testing WSGI application import..."
if python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production'); import django; django.setup(); from config.wsgi import application; print('WSGI application loaded successfully')" 2>&1; then
    echo "✓ WSGI application test passed"
else
    echo "ERROR: Failed to load WSGI application!"
    echo "Attempting to show detailed error..."
    python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production'); import django; django.setup(); from config.wsgi import application" 2>&1 || true
    echo "Attempting to continue anyway..."
fi

# Verify Django can start (database connection errors are expected if DB isn't ready)
echo "Verifying Django configuration..."
# Run check - database connection errors are OK during startup
# The check will still validate other things like URL config, models, etc.
python manage.py check 2>&1 | grep -v "connection to server" | grep -v "Connection refused" || {
    echo "NOTE: Django check completed (database connection errors are expected if DB isn't ready yet)"
}

# Test WSGI import one more time before starting
echo "Final WSGI application test..."
if python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
try:
    import django
    django.setup()
    from config.wsgi import application
    print('✓ WSGI application is ready')
    sys.exit(0)
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1; then
    echo "✓ WSGI test passed"
else
    echo "ERROR: WSGI application failed to load!"
    echo "Showing detailed error..."
    python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
try:
    import django
    django.setup()
    from config.wsgi import application
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1 || true
    echo "WARNING: Continuing despite WSGI test failure..."
fi

# Start Gunicorn with better error handling
echo "Starting Gunicorn on 0.0.0.0:8000..."
echo "Gunicorn will bind to 0.0.0.0:8000 and serve the Django application"
echo "Current working directory: $(pwd)"
echo "Python path: $(which python)"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-not set}"

# Ensure DJANGO_SETTINGS_MODULE is set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}

# Start Gunicorn - use exec to replace shell process
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 300 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    --preload
