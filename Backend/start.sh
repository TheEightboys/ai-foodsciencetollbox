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

# Determine if we're using SQLite or PostgreSQL
USING_SQLITE=false
if [ -z "${DATABASE_URL:-}" ]; then
    echo "No DATABASE_URL set — using SQLite."
    USING_SQLITE=true
fi

# Wait for database to be ready (only for PostgreSQL)
if [ "$USING_SQLITE" = false ]; then
    echo "Waiting for database..."
    parse_db_url
    echo "Checking database at $DB_HOST:$DB_PORT..."
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
fi

# Run migrations — always run for SQLite (ephemeral filesystem)
echo "Running migrations..."
python manage.py migrate --noinput 2>&1 && echo "✓ Migrations completed successfully" || {
    echo "WARNING: Migrations encountered issues, retrying with --run-syncdb..."
    python manage.py migrate --run-syncdb --noinput 2>&1 || echo "Migration issues persist, continuing..."
}

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

# Auto-configure Stripe price IDs from environment variables (if set)
if [ -n "$STRIPE_PRO_PRICE_ID" ]; then
    echo "Configuring Stripe Pro price ID from environment..."
    python manage.py update_stripe_prices --pro "$STRIPE_PRO_PRICE_ID" 2>&1 || {
        echo "WARNING: Failed to configure Stripe Pro price ID, continuing..."
    }
fi

# Create superuser if it doesn't exist (non-interactive)
# Run in background to not block startup if it fails
echo "Creating superuser (if not exists)..."
python manage.py create_superuser --email admin@foodsciencetoolbox.com --password Admin --first-name Admin --last-name User 2>&1 || {
    echo "WARNING: Failed to create superuser, continuing..."
    echo "You can run 'python manage.py create_superuser' manually later."
}

# Test if Django can import the WSGI application (single lightweight check)
echo "Testing WSGI application import..."
if python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production'); import django; django.setup(); from config.wsgi import application; print('WSGI application loaded successfully')" 2>&1; then
    echo "✓ WSGI application test passed"
else
    echo "WARNING: WSGI import test failed, continuing anyway..."
fi

# Start Gunicorn with better error handling
echo "Starting Gunicorn on 0.0.0.0:8000..."
echo "Current working directory: $(pwd)"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-not set}"

# Ensure DJANGO_SETTINGS_MODULE is set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}

# Start Gunicorn - use exec to replace shell process
# MEMORY OPTIMIZATIONS applied (target: stay under 512 MB on Render free):
#
#   1. celery/redis/django-redis REMOVED from requirements — saves ~80 MB at startup
#   2. django.contrib.admin REMOVED from production INSTALLED_APPS — saves ~40 MB
#   3. google-auth libraries lazy-imported in views — saves ~50 MB at startup
#   4. USE_I18N=False, duplicate CORS middleware removed, conn_max_age=60
#   5. No --preload — avoids master-process copy-on-write memory bloat
#   6. gthread with 2 threads — concurrent I/O without gevent monkey-patching overhead
#
# Expected startup memory: ~120-160 MB (down from ~280 MB)
# Peak per-request memory: ~200-250 MB (well under 512 MB limit)
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --worker-class gthread \
    --workers 1 \
    --threads 2 \
    --timeout 300 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance
