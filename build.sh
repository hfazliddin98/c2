#!/usr/bin/env bash
# Render Build Script
# Render.com deploy uchun avtomatik build

set -o errexit  # Exit on error

echo "🚀 Render Build Script Started..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --no-input

# Create superuser (if not exists)
echo "👤 Creating superuser (if not exists)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@c2platform.com', 'admin123')
    print('✅ Superuser created: admin / admin123')
else:
    print('ℹ️ Superuser already exists')
EOF

echo "✅ Build completed successfully!"
