# Makefile for running tests
.PHONY: help test test-all test-backend test-frontend test-unit test-integration test-e2e test-coverage test-watch test-parallel test-ci install clean

# Default target
help:
	@echo "Available commands:"
	@echo "  test          - Run all tests (backend + frontend)"
	@echo "  test-backend  - Run only backend tests"
	@echo "  test-frontend - Run only frontend tests"
	@echo "  test-unit     - Run unit tests for both"
	@echo "  test-integration - Run integration tests for both"
	@echo "  test-e2e      - Run end-to-end tests for both"
	@echo "  test-coverage - Run tests with coverage reports"
	@echo "  test-watch    - Run tests in watch mode"
	@echo "  test-parallel - Run tests in parallel"
	@echo "  test-ci       - Run tests for CI/CD"
	@echo "  install       - Install all dependencies"
	@echo "  clean         - Clean up test artifacts"

# Run all tests
test: test-backend test-frontend
	@echo "✅ All tests completed!"

# Run backend tests
test-backend:
	@echo "🧪 Running Backend Tests..."
	@cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run frontend tests
test-frontend:
	@echo "🎨 Running Frontend Tests..."
	@cd frontend && npm run test

# Run unit tests
test-unit: test-backend-unit test-frontend-unit
	@echo "✅ Unit tests completed!"

test-backend-unit:
	@echo "🧪 Running Backend Unit Tests..."
	@cd backend && python -m pytest tests/unit/ -v

test-frontend-unit:
	@echo "🎨 Running Frontend Unit Tests..."
	@cd frontend && npm run test:unit

# Run integration tests
test-integration: test-backend-integration test-frontend-integration
	@echo "✅ Integration tests completed!"

test-backend-integration:
	@echo "🧪 Running Backend Integration Tests..."
	@cd backend && python -m pytest tests/integration/ -v

test-frontend-integration:
	@echo "🎨 Running Frontend Integration Tests..."
	@cd frontend && npm run test:integration

# Run end-to-end tests
test-e2e: test-backend-e2e test-frontend-e2e
	@echo "✅ End-to-end tests completed!"

test-backend-e2e:
	@echo "🧪 Running Backend E2E Tests..."
	@cd backend && python -m pytest tests/e2e/ -v

test-frontend-e2e:
	@echo "🎨 Running Frontend E2E Tests..."
	@cd frontend && npx playwright test

# Run tests with coverage
test-coverage: test-backend-coverage test-frontend-coverage
	@echo "✅ Coverage tests completed!"

test-backend-coverage:
	@echo "🧪 Running Backend Tests with Coverage..."
	@cd backend && python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-frontend-coverage:
	@echo "🎨 Running Frontend Tests with Coverage..."
	@cd frontend && npm run test:coverage

# Run tests in watch mode
test-watch:
	@echo "👀 Running tests in watch mode..."
	@cd backend && python -m pytest tests/ -f --cov=app &
	@cd frontend && npm run test:watch &
	@wait

# Run tests in parallel
test-parallel:
	@echo "⚡ Running tests in parallel..."
	@cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing &
	@cd frontend && npm run test &
	@wait

# Run tests for CI/CD
test-ci: test-backend-ci test-frontend-ci
	@echo "✅ CI tests completed!"

test-backend-ci:
	@echo "🧪 Running Backend CI Tests..."
	@cd backend && python -m pytest tests/ --cov=app --cov-report=xml --junitxml=test-results.xml

test-frontend-ci:
	@echo "🎨 Running Frontend CI Tests..."
	@cd frontend && npx playwright test --reporter=junit --output=test-results.xml

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@npm install
	@cd frontend && npm install
	@cd backend && pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Clean up test artifacts
clean:
	@echo "🧹 Cleaning up test artifacts..."
	@cd backend && rm -rf .coverage htmlcov/ .pytest_cache/ test-results.xml
	@cd frontend && rm -rf coverage/ test-results.xml playwright-report/
	@echo "✅ Cleanup completed!"

# Development commands
dev:
	@echo "🚀 Starting development servers..."
	@cd backend && python -m uvicorn app.main:app --reload &
	@cd frontend && npm run dev &
	@wait

# Build frontend
build:
	@echo "🔨 Building frontend..."
	@cd frontend && npm run build

# Start production backend
start:
	@echo "🚀 Starting production backend..."
	@cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000