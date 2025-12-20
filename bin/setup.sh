#!/bin/bash

# Setup script for Alfred Butler API
# Checks dependencies and prepares the environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "\n${BLUE}🔧 $1${NC}"
    echo "================================"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    log_header "Alfred Butler API - Environment Setup"
    
    local all_checks_passed=true
    
    # Check container runtime (Docker or Podman)
    log_header "Container Runtime Check"
    
    if command_exists docker; then
        log_success "Docker found: $(docker --version)"
        CONTAINER_RUNTIME="docker"
        COMPOSE_CMD="docker-compose"
        
        # Check if Docker daemon is running
        if docker info >/dev/null 2>&1; then
            log_success "Docker daemon is running"
        else
            log_error "Docker daemon is not running. Please start Docker."
            all_checks_passed=false
        fi
        
        # Check docker-compose
        if command_exists docker-compose; then
            log_success "docker-compose found: $(docker-compose --version)"
        elif docker compose version >/dev/null 2>&1; then
            log_success "Docker Compose (plugin) found: $(docker compose version)"
            COMPOSE_CMD="docker compose"
        else
            log_error "docker-compose not found. Please install Docker Compose."
            all_checks_passed=false
        fi
        
    elif command_exists podman; then
        log_success "Podman found: $(podman --version)"
        CONTAINER_RUNTIME="podman"
        
        # Check podman-compose
        if command_exists podman-compose; then
            log_success "podman-compose found: $(podman-compose --version)"
            COMPOSE_CMD="podman-compose"
        else
            log_error "podman-compose not found. Please install podman-compose."
            log_info "Install with: pip install podman-compose"
            all_checks_passed=false
        fi
        
    else
        log_error "Neither Docker nor Podman found."
        log_info "Please install Docker: https://docs.docker.com/get-docker/"
        log_info "Or install Podman: https://podman.io/getting-started/installation"
        all_checks_passed=false
    fi
    
    # Check Make
    log_header "Build Tools Check"
    
    if command_exists make; then
        log_success "Make found: $(make --version | head -n1)"
    else
        log_error "Make not found. Please install make."
        log_info "Ubuntu/Debian: sudo apt-get install make"
        log_info "macOS: xcode-select --install"
        log_info "Or use Homebrew: brew install make"
        all_checks_passed=false
    fi
    
    # Check Python (for testing)
    log_header "Python Tools Check"
    
    if command_exists python3; then
        log_success "Python3 found: $(python3 --version)"
    else
        log_warning "Python3 not found. Some testing features may not work."
        log_info "Install Python3: https://www.python.org/downloads/"
    fi
    
    # Check curl and jq (for testing)
    if command_exists curl; then
        log_success "curl found: $(curl --version | head -n1)"
    else
        log_warning "curl not found. API testing will not work."
        log_info "Ubuntu/Debian: sudo apt-get install curl"
        log_info "macOS: brew install curl"
    fi
    
    if command_exists jq; then
        log_success "jq found: $(jq --version)"
    else
        log_warning "jq not found. JSON output will not be formatted."
        log_info "Ubuntu/Debian: sudo apt-get install jq"
        log_info "macOS: brew install jq"
    fi
    
    # Check .env file
    log_header "Environment Configuration"
    
    if [[ -f ".env" ]]; then
        log_success ".env file already exists"
        
        # Check if .env has required variables
        local missing_vars=()
        local required_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_DEFAULT_REGION")
        
        for var in "${required_vars[@]}"; do
            if ! grep -q "^${var}=" .env; then
                missing_vars+=("$var")
            fi
        done
        
        if [[ ${#missing_vars[@]} -gt 0 ]]; then
            log_warning "Missing required environment variables in .env:"
            for var in "${missing_vars[@]}"; do
                echo "  - $var"
            done
            log_info "Please check .env.example for reference"
        else
            log_success "All required environment variables are present"
        fi
        
    elif [[ -f ".env.example" ]]; then
        log_info "Creating .env file from .env.example..."
        cp .env.example .env
        log_success ".env file created successfully"
        log_warning "Please edit .env file with your actual AWS credentials and other settings"
        log_info "Required variables to update:"
        echo "  - AWS_ACCESS_KEY_ID"
        echo "  - AWS_SECRET_ACCESS_KEY"
        echo "  - AWS_DEFAULT_REGION"
        echo "  - WEBUI_SECRET_KEY (change to a random string)"
    else
        log_error ".env.example file not found. Cannot create .env file."
        all_checks_passed=false
    fi
    
    # Check project files
    log_header "Project Files Check"
    
    local required_files=("Makefile" "docker-compose.yml" "requirements.txt" "src/api.py")
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "$file exists"
        else
            log_error "$file not found"
            all_checks_passed=false
        fi
    done
    
    # Final summary
    log_header "Setup Summary"
    
    if [[ "$all_checks_passed" == true ]]; then
        log_success "All checks passed! Your environment is ready."
        echo
        log_info "Next steps:"
        echo "  1. Edit .env file with your AWS credentials"
        echo "  2. Run: make up"
        echo "  3. Test: make test"
        echo "  4. Access Open Web UI at: http://localhost:3000"
        echo "  5. API documentation at: http://localhost:8000/docs"
        echo
        log_info "Useful commands:"
        echo "  make help    - Show all available commands"
        echo "  make logs    - View service logs"
        echo "  make down    - Stop all services"
        echo "  make clean   - Remove all containers and volumes"
        
    else
        log_error "Some checks failed. Please fix the issues above before proceeding."
        echo
        log_info "Common solutions:"
        echo "  - Install Docker: https://docs.docker.com/get-docker/"
        echo "  - Install Make: sudo apt-get install make (Ubuntu/Debian)"
        echo "  - Install jq: sudo apt-get install jq (Ubuntu/Debian)"
        exit 1
    fi
}

# Run main function
main "$@"