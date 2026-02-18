#!/bin/bash

# Test runner script for Volunteer Platform Backend

set -e

echo "🧪 Running Volunteer Platform Backend Tests"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "No virtual environment detected. Consider activating one."
fi

# Install test dependencies if not already installed
print_status "Installing test dependencies..."
pip install pytest pytest-django pytest-mock pytest-cov factory-boy mixer

# Check if PostgreSQL is running (optional)
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 &> /dev/null; then
        print_status "PostgreSQL is running"
    else
        print_warning "PostgreSQL is not running. Tests will use SQLite."
    fi
else
    print_warning "PostgreSQL client not found. Tests will use SQLite."
fi

# Check if Redis is running (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_status "Redis is running"
    else
        print_warning "Redis is not running. Some tests may fail."
    fi
else
    print_warning "Redis client not found. Some tests may fail."
fi

# Create test database if using PostgreSQL
if pg_isready -h localhost -p 5432 &> /dev/null; then
    print_status "Creating test database..."
    createdb -h localhost -p 5432 -U postgres test_volunteering_platform 2>/dev/null || true
fi

# Set environment variables for testing
export DJANGO_SETTINGS_MODULE=config.settings
export DJANGO_DEBUG=1
export DATABASE_URL="postgres://postgres:postgres@localhost:5432/test_volunteering_platform"
export REDIS_URL="redis://localhost:6379/1"

# Run migrations
print_status "Running database migrations..."
python manage.py migrate --settings=config.settings

# Function to run tests with coverage
run_tests_with_coverage() {
    local test_path="$1"
    local test_name="$2"
    
    print_status "Running $test_name tests..."
    if pytest "$test_path" --cov=apps --cov-report=term-missing --cov-append -v; then
        print_status "$test_name tests passed! ✅"
    else
        print_error "$test_name tests failed! ❌"
        return 1
    fi
}

# Run all tests
print_status "Running all tests with coverage..."
if pytest --cov=apps --cov-report=html --cov-report=term --cov-report=xml -v; then
    print_status "All tests passed! 🎉"
else
    print_error "Some tests failed! 💥"
    exit 1
fi

# Run specific test suites (optional)
if [ "$1" = "--specific" ]; then
    echo ""
    print_status "Running specific test suites..."
    
    # Run model tests
    run_tests_with_coverage "apps/*/tests/test_models.py" "Model Tests"
    
    # Run serializer tests
    run_tests_with_coverage "apps/*/tests/test_serializers.py" "Serializer Tests"
    
    # Run API tests
    run_tests_with_coverage "apps/*/tests/test_api.py" "API Tests"
    
    # Run permission tests
    run_tests_with_coverage "apps/*/tests/test_permissions.py" "Permission Tests"
fi

# Generate coverage report
print_status "Generating coverage report..."
coverage html 2>/dev/null || true
coverage xml 2>/dev/null || true

# Show coverage summary
if [ -f "htmlcov/index.html" ]; then
    print_status "Coverage report generated: htmlcov/index.html"
fi

# Run linting (optional)
if [ "$1" = "--lint" ] || [ "$2" = "--lint" ]; then
    echo ""
    print_status "Running code linting..."
    
    # Install linting tools
    pip install black flake8 isort
    
    # Check code formatting
    print_status "Checking code formatting with black..."
    if black --check .; then
        print_status "Code formatting is correct! ✅"
    else
        print_warning "Code formatting issues found. Run 'black .' to fix."
    fi
    
    # Check import sorting
    print_status "Checking import sorting with isort..."
    if isort --check-only .; then
        print_status "Import sorting is correct! ✅"
    else
        print_warning "Import sorting issues found. Run 'isort .' to fix."
    fi
    
    # Run flake8
    print_status "Running flake8..."
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
        print_status "No critical linting issues found! ✅"
    else
        print_warning "Linting issues found."
    fi
fi

# Run security checks (optional)
if [ "$1" = "--security" ] || [ "$2" = "--security" ]; then
    echo ""
    print_status "Running security checks..."
    
    # Install security tools
    pip install safety bandit
    
    # Check dependencies for known vulnerabilities
    print_status "Checking dependencies for vulnerabilities..."
    if safety check; then
        print_status "No known vulnerabilities found! ✅"
    else
        print_warning "Vulnerabilities found in dependencies."
    fi
    
    # Run bandit security linter
    print_status "Running bandit security linter..."
    if bandit -r apps/ -f json -o bandit-report.json; then
        print_status "No security issues found! ✅"
    else
        print_warning "Security issues found. Check bandit-report.json"
    fi
fi

echo ""
print_status "Test run completed! 🚀"
echo ""
echo "Available commands:"
echo "  ./run_tests.sh                    - Run all tests with coverage"
echo "  ./run_tests.sh --specific         - Run specific test suites"
echo "  ./run_tests.sh --lint            - Run tests + linting"
echo "  ./run_tests.sh --security         - Run tests + security checks"
echo "  ./run_tests.sh --specific --lint  - Run specific tests + linting"
echo ""
echo "Quick pytest commands:"
echo "  pytest                            - Run all tests"
echo "  pytest -v                         - Run with verbose output"
echo "  pytest --cov                      - Run with coverage"
echo "  pytest apps/users/tests/           - Run specific app tests"
echo "  pytest -k 'test_create'           - Run tests matching pattern"
