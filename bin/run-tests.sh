#!/bin/bash

# Simple test runner for Alfred Butler API

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check pytest
if ! command -v pytest &> /dev/null; then
    log_error "pytest not found. Install with: pip install -r requirements.dev.txt"
    exit 1
fi

# Simple test runner
run_tests() {
    local test_type="$1"
    local test_path="$2"
    
    log_info "Running $test_type tests..."
    
    if pytest $test_path -v; then
        log_success "$test_type tests passed!"
        return 0
    else
        log_error "$test_type tests failed!"
        return 1
    fi
}

# Main function
main() {
    local test_type="${1:-all}"
    
    echo "🧪 Alfred Butler API Test Runner"
    echo "================================"
    
    case $test_type in
        "unit")
            run_tests "Unit" "tests/unit/"
            ;;
        "integration")
            run_tests "Integration" "tests/integration/"
            ;;
        "coverage")
            log_info "Running tests with coverage..."
            if pytest --cov=src --cov-report=term-missing --cov-report=html; then
                log_success "Coverage tests completed!"
                log_info "HTML report: htmlcov/index.html"
            else
                log_error "Coverage tests failed!"
                exit 1
            fi
            ;;
        "all")
            echo
            run_tests "Unit" "tests/unit/" || exit 1
            echo
            run_tests "Integration" "tests/integration/" || exit 1
            echo
            log_success "All tests passed! 🎉"
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [test_type]"
            echo
            echo "Available test types:"
            echo "  unit         - Run unit tests only"
            echo "  integration  - Run integration tests"
            echo "  coverage     - Run tests with coverage report"
            echo "  all          - Run all tests (default)"
            echo "  help         - Show this help"
            ;;
        *)
            log_error "Unknown test type: $test_type"
            echo "Use '$0 help' for available options"
            exit 1
            ;;
    esac
}

main "$@"