#!/bin/bash

echo "🚀 Setting up Image AI Backend..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your database credentials and secret key!"
else
    echo "✅ .env file already exists"
fi

# Initialize Alembic
echo "🗄️ Initializing Alembic..."
alembic init alembic

echo "✅ Backend setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Start PostgreSQL: docker-compose up -d postgres"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start the backend: python start.py"
echo ""
echo "🔗 Useful commands:"
echo "- Start database: docker-compose up -d postgres"
echo "- View logs: docker-compose logs postgres"
echo "- Stop database: docker-compose down"
echo "- Run migrations: alembic upgrade head"
echo "- Create migration: alembic revision --autogenerate -m 'description'"
