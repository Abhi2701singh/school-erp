#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "================================================="
echo " Building EduManage School ERP for Cloudflare... "
echo "================================================="

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect static files for Cloudflare CDN Edge
python manage.py collectstatic --no-input

# 3. Copy Cloudflare headers to staticfiles directory
cp static/_headers staticfiles/_headers 2>/dev/null || true
cp static/_redirects staticfiles/_redirects 2>/dev/null || true

# 4. Apply Database Migrations
python manage.py migrate --no-input

# 5. Initialize Super Admin
python seed_demo_data.py

echo "================================================="
echo " ✅ Cloudflare Build Completed Successfully!    "
echo "================================================="
