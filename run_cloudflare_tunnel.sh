#!/bin/bash
# ==============================================================================
# 🚀 1-Click Free Cloudflare Deployment & Tunnel Launcher
# ==============================================================================

echo "======================================================================"
echo " Starting EduManage School ERP with Cloudflare Tunnel (100% Free) "
echo "======================================================================"

# 1. Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. Run migrations and collect static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 3. Locate cloudflared binary
CLOUDFLARED_BIN=""
if [ -x "./bin/cloudflared" ]; then
    CLOUDFLARED_BIN="./bin/cloudflared"
elif command -v cloudflared &> /dev/null; then
    CLOUDFLARED_BIN="cloudflared"
fi

if [ -z "$CLOUDFLARED_BIN" ]; then
    echo ""
    echo "⚠️  'cloudflared' binary not found."
    echo "Starting local server on http://127.0.0.1:8000..."
    ./venv/bin/gunicorn school_erp.wsgi:application --bind 127.0.0.1:8000 --workers 3
    exit 0
fi

# 4. Start Gunicorn server in background
echo "Starting Django Gunicorn server on 127.0.0.1:8000..."
./venv/bin/gunicorn school_erp.wsgi:application --bind 127.0.0.1:8000 --workers 3 &
GUNICORN_PID=$!

# 5. Start Cloudflare Tunnel (Quick Free HTTPS Tunnel)
echo ""
echo "🌐 Launching Cloudflare Global Edge Tunnel..."
echo "Your live Cloudflare HTTPS URL will be displayed below 👇"
echo "----------------------------------------------------------------------"
$CLOUDFLARED_BIN tunnel --url http://127.0.0.1:8000

# Cleanup on exit
kill $GUNICORN_PID
