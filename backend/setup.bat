@echo off
echo 🚀 Setting up Image AI Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo 🔐 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your database credentials and secret key!
) else (
    echo ✅ .env file already exists
)

echo ✅ Backend setup completed!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your database credentials
echo 2. Start PostgreSQL: docker-compose up -d postgres
echo 3. Run migrations: alembic upgrade head
echo 4. Start the backend: python start.py
echo.
echo 🔗 Useful commands:
echo - Start database: docker-compose up -d postgres
echo - View logs: docker-compose logs postgres
echo - Stop database: docker-compose down
echo - Run migrations: alembic upgrade head
echo - Create migration: alembic revision --autogenerate -m "description"
echo.
pause
