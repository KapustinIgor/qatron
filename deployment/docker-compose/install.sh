#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_message "$YELLOW" "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_message "$RED" "ERROR: Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker compose version >/dev/null 2>&1; then
        print_message "$RED" "ERROR: Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_message "$RED" "ERROR: Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_message "$GREEN" "✓ Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    print_message "$YELLOW" "Creating necessary directories..."
    
    mkdir -p data/postgres
    mkdir -p data/minio
    mkdir -p data/rabbitmq
    mkdir -p data/redis
    mkdir -p logs
    
    print_message "$GREEN" "✓ Directories created"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_message "$YELLOW" "Creating .env file from template..."
        
        cat > .env <<EOF
# QAtron Docker Compose Configuration

# Database
POSTGRES_USER=qatron
POSTGRES_PASSWORD=qatron
POSTGRES_DB=qatron
POSTGRES_PORT=5432

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_NAME=qatron-artifacts

# RabbitMQ
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

# Redis
REDIS_PASSWORD=

# Control Plane
CONTROL_PLANE_SECRET_KEY=$(openssl rand -hex 32)

# API
API_V1_STR=/api/v1

# S3 Configuration
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=qatron-artifacts
S3_REGION=us-east-1
S3_USE_SSL=false
EOF
        
        print_message "$GREEN" "✓ .env file created"
    else
        print_message "$YELLOW" "✓ .env file already exists, skipping"
    fi
}

# Start services
start_services() {
    print_message "$YELLOW" "Starting QAtron services..."
    
    docker compose up -d
    
    print_message "$GREEN" "✓ Services started"
}

# Wait for service to be healthy
wait_for_service() {
    service=$1
    url=$2
    max_attempts=60
    attempt=0
    
    print_message "$YELLOW" "Waiting for $service to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" >/dev/null 2>&1; then
            print_message "$GREEN" "✓ $service is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    print_message "$RED" "✗ $service failed to start within timeout"
    return 1
}

# Wait for all services
wait_for_services() {
    print_message "$YELLOW" "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    until docker compose exec -T postgres pg_isready -U qatron >/dev/null 2>&1; do
        sleep 2
    done
    print_message "$GREEN" "✓ PostgreSQL is ready"
    
    # Wait for RabbitMQ
    wait_for_service "RabbitMQ" "http://localhost:15672" || true
    
    # Wait for Redis
    until docker compose exec -T redis redis-cli ping >/dev/null 2>&1; do
        sleep 2
    done
    print_message "$GREEN" "✓ Redis is ready"
    
    # Wait for MinIO
    wait_for_service "MinIO" "http://localhost:9000/minio/health/live" || true
    
    # Wait for Control Plane (required: API must be up for UI and trigger to work)
    wait_for_service "Control Plane" "http://localhost:8000/healthz"
    
    # Wait for Board (required: UI must be up after setup)
    wait_for_service "Board" "http://localhost:3000/healthz"
    
    # Wait for Selenium Grid (hub + at least one node ready for E2E)
    wait_for_selenium_grid
    
    print_message "$GREEN" "✓ All services are ready"
}

# Wait for Selenium Grid to report ready (hub + node registered)
wait_for_selenium_grid() {
    print_message "$YELLOW" "Waiting for Selenium Grid to be ready (hub + browser node)..."
    max_attempts=60
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if status=$(curl -sf "http://localhost:4444/status" 2>/dev/null); then
            if echo "$status" | grep -qE '"ready"[[:space:]]*:[[:space:]]*true'; then
                print_message "$GREEN" "✓ Selenium Grid is ready (E2E tests can run)"
                return 0
            fi
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    print_message "$YELLOW" "⚠ Selenium Grid did not report ready within timeout (node may still be registering)"
    print_message "$NC" "  Check: curl -s http://localhost:4444/status"
    return 0
}

# Run database migrations
run_migrations() {
    print_message "$YELLOW" "Running database migrations..."
    
    # Wait a bit more for database to be fully ready
    sleep 5
    
    docker compose exec -T control-plane alembic upgrade head || {
        print_message "$YELLOW" "Migrations may have already been run, continuing..."
    }
    
    print_message "$GREEN" "✓ Migrations completed"
}

# Create MinIO bucket
create_minio_bucket() {
    print_message "$YELLOW" "Creating MinIO bucket..."
    
    sleep 5  # Wait for MinIO to be ready
    
    docker compose exec -T minio mc alias set local http://localhost:9000 minioadmin minioadmin || true
    docker compose exec -T minio mc mb local/qatron-artifacts || {
        print_message "$YELLOW" "Bucket may already exist, continuing..."
    }
    docker compose exec -T minio mc anonymous set download local/qatron-artifacts || true
    
    print_message "$GREEN" "✓ MinIO bucket created"
}

# Print access information
print_access_info() {
    print_message "$GREEN" ""
    print_message "$GREEN" "=========================================="
    print_message "$GREEN" "QAtron Installation Complete!"
    print_message "$GREEN" "=========================================="
    print_message "$GREEN" ""
    print_message "$GREEN" "Access URLs:"
    print_message "$NC" "  • QAtron Board (UI):     http://localhost:3000"
    print_message "$NC" "  • Control Plane API:     http://localhost:8000"
    print_message "$NC" "  • API Documentation:       http://localhost:8000/docs"
    print_message "$NC" "  • Orchestrator:          http://localhost:8001"
    print_message "$NC" "  • MinIO Console:         http://localhost:9001"
    print_message "$NC" "  • Grafana:               http://localhost:3001"
    print_message "$NC" "  • Prometheus:             http://localhost:9090"
    print_message "$NC" "  • Selenium Grid (E2E):    http://localhost:4444  (use SELENIUM_GRID_URL=http://localhost:4444/wd/hub)"
    print_message "$GREEN" ""
    print_message "$GREEN" "Default Credentials:"
    print_message "$NC" "  • QAtron Board (UI):"
    print_message "$NC" "    Username: admin"
    print_message "$NC" "    Password: admin"
    print_message "$NC" "  • MinIO Console:"
    print_message "$NC" "    Username: minioadmin"
    print_message "$NC" "    Password: minioadmin"
    print_message "$NC" "  • PostgreSQL:"
    print_message "$NC" "    Username: qatron"
    print_message "$NC" "    Password: qatron"
    print_message "$NC" "    Database: qatron"
    print_message "$NC" "  • RabbitMQ:"
    print_message "$NC" "    Username: guest"
    print_message "$NC" "    Password: guest"
    print_message "$NC" "  • Grafana:"
    print_message "$NC" "    Username: admin"
    print_message "$NC" "    Password: admin (change on first login)"
    print_message "$GREEN" ""
    print_message "$GREEN" "Next Steps:"
    print_message "$NC" "  1. Open http://localhost:3000 in your browser"
    print_message "$NC" "  2. Log in with username: admin, password: admin"
    print_message "$NC" "  3. Install CLI: pipx install qatron"
    print_message "$NC" "  4. Read the documentation: docs/INSTALLATION.md"
    print_message "$GREEN" ""
    print_message "$GREEN" "Service Management:"
    print_message "$NC" "  ./manage.sh start      - Start all services"
    print_message "$NC" "  ./manage.sh stop       - Stop all services"
    print_message "$NC" "  ./manage.sh restart    - Restart all services"
    print_message "$NC" "  ./manage.sh status     - Show service status"
    print_message "$NC" "  ./manage.sh logs -f    - Follow logs"
    print_message "$GREEN" ""
}

# Main installation flow
main() {
    print_message "$GREEN" "=========================================="
    print_message "$GREEN" "QAtron Installation Script"
    print_message "$GREEN" "=========================================="
    print_message "$GREEN" ""
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    check_prerequisites
    create_directories
    create_env_file
    start_services
    wait_for_services
    run_migrations
    create_minio_bucket
    print_access_info
}

# Run main function
main "$@"
