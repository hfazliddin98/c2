#!/bin/bash
# Django C2 Platform - Quick Setup Script
# Automated setup for development environment

echo "============================================"
echo "  Django C2 Platform - Setup"
echo "  Target: 10,000+ concurrent users"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python version
echo -e "${YELLOW}[1/8]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
echo ""

# Check PostgreSQL (optional for dev)
echo -e "${YELLOW}[2/8]${NC} Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL installed${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL not found (using SQLite for dev)${NC}"
fi
echo ""

# Check Redis (optional for dev)
echo -e "${YELLOW}[3/8]${NC} Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✅ Redis installed${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not found (limited performance)${NC}"
    echo "   Install: sudo apt install redis-server"
fi
echo ""

# Create virtual environment
echo -e "${YELLOW}[4/8]${NC} Creating virtual environment..."
if [ ! -d "venv_django" ]; then
    python3 -m venv venv_django
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[5/8]${NC} Activating virtual environment..."
source venv_django/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[6/8]${NC} Installing Django dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r django_requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Create .env file
echo -e "${YELLOW}[7/8]${NC} Creating .env file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Django C2 Platform - Environment Variables
SECRET_KEY=django-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Redis (optional for dev)
REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/2
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/3

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi
echo ""

# Django setup
echo -e "${YELLOW}[8/8]${NC} Django setup..."

# Migrations
echo "  - Running migrations..."
python manage.py makemigrations --noinput > /dev/null 2>&1
python manage.py migrate --noinput > /dev/null 2>&1
echo -e "${GREEN}  ✅ Database migrated${NC}"

# Collect static files
echo "  - Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1
echo -e "${GREEN}  ✅ Static files collected${NC}"

echo ""
echo "============================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "============================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Start development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Start WebSocket server (optional):"
echo "   daphne asosiy.asgi:application"
echo ""
echo "4. Start Celery worker (optional):"
echo "   celery -A asosiy worker --loglevel=info"
echo ""
echo "5. Access admin panel:"
echo "   http://127.0.0.1:8000/admin/"
echo ""
echo "============================================"
echo ""
echo "📚 Documentation:"
echo "  - Flask to Django: docs/FLASK_TO_DJANGO_MIGRATION.md"
echo "  - Deployment: DJANGO_DEPLOYMENT.py"
echo ""
echo "⚡ Performance:"
echo "  - Development: ~1,000 users"
echo "  - Production: 10,000+ users"
echo ""
echo "============================================"
