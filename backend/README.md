# Image AI Backend

A FastAPI-based backend service for image generation and web search functionality with PostgreSQL database.

## Features

- 🔐 JWT-based authentication system
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- 🔍 Web search integration with DuckDuckGo
- 🎨 Image generation endpoints (ready for MCP integration)
- 📊 User dashboard with search and image history
- 🚀 FastAPI with automatic API documentation
- 🔄 Database migrations with Alembic

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL (or use Docker)

## Quick Start

### 1. Clone and Setup

```bash
cd backend
chmod +x setup.sh  # Make setup script executable
./setup.sh         # Run setup script
```

**Windows users:**
```cmd
cd backend
setup.bat
```

### 2. Configure Environment

Edit the `.env` file with your database credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/image_ai_db

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Start PostgreSQL Database

```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# Check if database is running
docker-compose ps
```

### 4. Run Database Migrations

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat  # Windows

# Run migrations
alembic upgrade head
```

### 5. Start the Backend

```bash
# Start the FastAPI server
python start.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and models
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── security.py          # Authentication and security
│   ├── dependencies.py      # FastAPI dependencies
│   └── routes/              # API route modules
│       ├── auth.py          # Authentication routes
│       ├── dashboard.py     # Dashboard routes
│       ├── image.py         # Image generation routes
│       └── search.py        # Web search routes
├── alembic/                 # Database migrations
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── setup.sh                 # Setup script (Linux/Mac)
├── setup.bat                # Setup script (Windows)
└── start.py                 # Application startup script
```

## Database Management

### Creating Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Database Connection

The application uses PostgreSQL with the following default configuration:
- **Host**: localhost
- **Port**: 5432
- **Database**: image_ai_db
- **Username**: postgres
- **Password**: postgres123

## Development

### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DEBUG` | Debug mode | True |
| `ALLOWED_ORIGINS` | CORS allowed origins | localhost:5173,3000 |

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure PostgreSQL is running: `docker-compose ps`
   - Check database credentials in `.env`
   - Verify database exists: `docker-compose exec postgres psql -U postgres -l`

2. **Port Already in Use**
   - Change port in `.env` file
   - Kill process using the port: `lsof -ti:8000 | xargs kill -9`

3. **Migration Errors**
   - Reset database: `alembic downgrade base`
   - Recreate tables: `alembic upgrade head`

### Logs

```bash
# View application logs
tail -f logs/app.log

# View database logs
docker-compose logs postgres
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Use strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use environment-specific database URLs
5. Set up proper logging
6. Configure reverse proxy (nginx)
7. Use process manager (systemd, supervisor)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
