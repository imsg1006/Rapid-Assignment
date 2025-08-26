 
set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
PARALLEL=false
COVERAGE=true
VERBOSE=true
BACKEND_ONLY=false
FRONTEND_ONLY=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE        Test type: all, unit, integration, e2e (default: all)"
    echo "  -p, --parallel         Run tests in parallel"
    echo "  -n, --no-coverage      Disable coverage reporting"
    echo "  -q, --quiet            Reduce verbosity"
    echo "  -b, --backend-only     Run only backend tests"
    echo "  -f, --frontend-only    Run only frontend tests"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Run all tests"
    echo "  $0 -t unit            # Run unit tests only"
    echo "  $0 -p                 # Run tests in parallel"
    echo "  $0 -b                 # Run backend tests only"
    echo "  $0 -f                 # Run frontend tests only"
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "Python3 found: $(python3 --version)"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        print_success "Python found: $(python --version)"
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check pytest
    if $PYTHON_CMD -m pytest --version &> /dev/null; then
        print_success "pytest found"
    else
        print_error "pytest not found. Please install: pip install pytest"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        print_success "Node.js found: $(node --version)"
    else
        print_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        print_success "npm found: $(npm --version)"
    else
        print_error "npm not found. Please install npm"
        exit 1
    fi
}

# Function to run backend tests
run_backend_tests() {
    local test_path="tests/"
    if [ "$TEST_TYPE" != "all" ]; then
        test_path="tests/$TEST_TYPE/"
    fi
    
    print_status "Running backend tests ($TEST_TYPE)..."
    
    local cmd="$PYTHON_CMD -m pytest $test_path"
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd -v"
    fi
    if [ "$COVERAGE" = true ]; then
        cmd="$cmd --cov=app --cov-report=term-missing"
    fi
    
    cd backend
    if eval $cmd; then
        print_success "Backend tests passed"
        cd ..
        return 0
    else
        print_error "Backend tests failed"
        cd ..
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests ($TEST_TYPE)..."
    
    cd frontend
    
    local cmd="npm run test"
    if [ "$TEST_TYPE" = "e2e" ]; then
        cmd="npx playwright test"
    elif [ "$TEST_TYPE" = "unit" ]; then
        cmd="npm run test:unit"
    fi
    
    if eval $cmd; then
        print_success "Frontend tests passed"
        cd ..
        return 0
    else
        print_error "Frontend tests failed"
        cd ..
        return 1
    fi
}

# Function to run tests in parallel
run_tests_parallel() {
    print_status "Running tests in parallel..."
    
    # Start backend tests in background
    run_backend_tests &
    BACKEND_PID=$!
    
    # Start frontend tests in background
    run_frontend_tests &
    FRONTEND_PID=$!
    
    # Wait for both to complete
    wait $BACKEND_PID
    BACKEND_EXIT=$?
    wait $FRONTEND_PID
    FRONTEND_EXIT=$?
    
    # Check results
    if [ $BACKEND_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
        print_success "All tests passed in parallel"
        return 0
    else
        print_error "Some tests failed in parallel"
        return 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Starting full test suite..."
    echo "Test Type: $TEST_TYPE"
    echo "Parallel: $PARALLEL"
    echo "Coverage: $COVERAGE"
    echo "=================================================="
    
    if [ "$PARALLEL" = true ]; then
        run_tests_parallel
    else
        # Run sequentially
        if [ "$BACKEND_ONLY" = true ]; then
            run_backend_tests
        elif [ "$FRONTEND_ONLY" = true ]; then
            run_frontend_tests
        else
            # Run both
            if run_backend_tests && run_frontend_tests; then
                print_success "All tests completed successfully!"
                return 0
            else
                print_error "Some tests failed"
                return 1
            fi
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -n|--no-coverage)
            COVERAGE=false
            shift
            ;;
        -q|--quiet)
            VERBOSE=false
            shift
            ;;
        -b|--backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        -f|--frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate test type
case $TEST_TYPE in
    all|unit|integration|e2e)
        ;;
    *)
        print_error "Invalid test type: $TEST_TYPE"
        print_error "Valid types: all, unit, integration, e2e"
        exit 1
        ;;
esac

# Main execution
main() {
    print_status "🚀 Starting test runner..."
    
    # Check dependencies
    check_dependencies
    
    # Run tests
    if run_all_tests; then
        print_success "🎉 All tests completed successfully!"
        exit 0
    else
        print_error "💥 Some tests failed!"
        exit 1
    fi
}

# Run main function
main "$@"