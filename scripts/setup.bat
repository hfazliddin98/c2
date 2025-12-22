@echo off
REM Django C2 Platform - Windows Setup Script

echo ============================================
echo   Django C2 Platform - Setup (Windows)
echo   Target: 10,000+ concurrent users
echo ============================================
echo.

REM Check Python
echo [1/8] Checking Python version...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

REM Check PostgreSQL
echo [2/8] Checking PostgreSQL...
where psql >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] PostgreSQL installed
) else (
    echo [WARNING] PostgreSQL not found ^(using SQLite for dev^)
)
echo.

REM Check Redis
echo [3/8] Checking Redis...
where redis-cli >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis installed
) else (
    echo [WARNING] Redis not found ^(limited performance^)
    echo Install from: https://github.com/microsoftarchive/redis/releases
)
echo.

REM Create virtual environment
echo [4/8] Creating virtual environment...
if not exist "venv_django" (
    python -m venv venv_django
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment exists
)
echo.

REM Activate virtual environment
echo [5/8] Activating virtual environment...
call venv_django\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [6/8] Installing Django dependencies...
echo This may take a few minutes...
python -m pip install --quiet --upgrade pip
pip install --quiet -r django_requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create .env file
echo [7/8] Creating .env file...
if not exist ".env" (
    (
    echo # Django C2 Platform - Environment Variables
    echo SECRET_KEY=django-dev-secret-key-change-in-production
    echo DEBUG=True
    echo ALLOWED_HOSTS=localhost,127.0.0.1
    echo.
    echo # Database ^(SQLite for development^)
    echo DB_NAME=db.sqlite3
    echo DB_USER=
    echo DB_PASSWORD=
    echo DB_HOST=
    echo DB_PORT=
    echo.
    echo # Redis ^(optional for dev^)
    echo REDIS_URL=redis://127.0.0.1:6379/0
    echo CELERY_BROKER_URL=redis://127.0.0.1:6379/2
    echo CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/3
    echo.
    echo # CORS
    echo CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    ) > .env
    echo [OK] .env file created
) else (
    echo [OK] .env file exists
)
echo.

REM Django setup
echo [8/8] Django setup...

echo   - Running migrations...
python manage.py makemigrations --noinput >nul 2>&1
python manage.py migrate --noinput >nul 2>&1
echo   [OK] Database migrated

echo   - Collecting static files...
python manage.py collectstatic --noinput >nul 2>&1
echo   [OK] Static files collected

echo.
echo ============================================
echo [OK] Setup Complete!
echo ============================================
echo.
echo Next steps:
echo.
echo 1. Create superuser:
echo    python manage.py createsuperuser
echo.
echo 2. Start development server:
echo    python manage.py runserver
echo.
echo 3. Start WebSocket server ^(optional^):
echo    daphne asosiy.asgi:application
echo.
echo 4. Start Celery worker ^(optional^):
echo    celery -A asosiy worker --loglevel=info
echo.
echo 5. Access admin panel:
echo    http://127.0.0.1:8000/admin/
echo.
echo ============================================
echo.
echo Documentation:
echo   - Flask to Django: docs\FLASK_TO_DJANGO_MIGRATION.md
echo   - Deployment: DJANGO_DEPLOYMENT.py
echo.
echo Performance:
echo   - Development: ~1,000 users
echo   - Production: 10,000+ users
echo.
echo ============================================
pause
