#!/usr/bin/env bash
# ==================================================
# ZEMPAA DIGITAL CITY — RENDER PRODUCTION BUILD SCRIPT
# MIGRATION-DRIFT SAFE VERSION
# ==================================================

set -o errexit
set -o nounset

echo "=================================================="
echo "SKILLINE — STARTING BUILD"
echo "=================================================="


# 3. Install Python dependencies
pip install --no-cache-dir -r requirements.txt

# 4. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input


# --------------------------------------------------
# 6. Run remaining migrations safely
# --------------------------------------------------
echo "Running remaining migrations..."
python manage.py makemigrations 
python manage.py migrate --no-input

echo "=================================================="
echo "✅ SKILLINE BUILD COMPLETED SUCCESSFULLY"
echo "=================================================="
