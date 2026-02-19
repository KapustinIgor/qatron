#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Print colored message
print_message() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Print usage
usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|ps|up|down} [service]"
    echo ""
    echo "Commands:"
    echo "  start [service]    - Start all services or a specific service"
    echo "  stop [service]     - Stop all services or a specific service"
    echo "  restart [service]  - Restart all services or a specific service"
    echo "  status             - Show status of all services"
    echo "  logs [service]     - Show logs (use -f to follow)"
    echo "  ps                 - List all containers"
    echo "  up                 - Start services in detached mode (alias for start)"
    echo "  down               - Stop and remove containers"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 stop                     # Stop all services"
    echo "  $0 restart                  # Restart all services"
    echo "  $0 start control-plane      # Start only control-plane service"
    echo "  $0 logs control-plane       # Show control-plane logs"
    echo "  $0 logs -f control-plane    # Follow control-plane logs"
    exit 1
}

# Check if docker compose is available
check_docker_compose() {
    if ! command -v docker >/dev/null 2>&1; then
        print_message "$RED" "ERROR: Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        print_message "$RED" "ERROR: Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Start services
start_services() {
    local service=$1
    print_message "$YELLOW" "Starting QAtron services..."

    if [ -n "$service" ]; then
        print_message "$BLUE" "Starting service: $service"
        docker compose up -d "$service"
    else
        docker compose up -d
    fi

    print_message "$GREEN" "✓ Services started"
    if [ -z "$service" ]; then
        print_message "$YELLOW" "Waiting for services to be healthy..."
        sleep 5
        docker compose ps
    fi
}

# Stop services
stop_services() {
    local service=$1
    print_message "$YELLOW" "Stopping QAtron services..."

    if [ -n "$service" ]; then
        print_message "$BLUE" "Stopping service: $service"
        docker compose stop "$service"
    else
        docker compose stop
    fi

    print_message "$GREEN" "✓ Services stopped"
}

# Restart services
restart_services() {
    local service=$1
    print_message "$YELLOW" "Restarting QAtron services..."

    if [ -n "$service" ]; then
        print_message "$BLUE" "Restarting service: $service"
        docker compose restart "$service"
    else
        docker compose restart
    fi

    print_message "$GREEN" "✓ Services restarted"
}

# Show status
show_status() {
    print_message "$YELLOW" "QAtron Services Status:"
    echo ""
    docker compose ps
}

# Show logs
show_logs() {
    local follow_flag=""
    local service=""

    # Check for -f flag
    if [ "$1" = "-f" ]; then
        follow_flag="-f"
        service=$2
    else
        service=$1
    fi

    if [ -n "$service" ]; then
        print_message "$BLUE" "Showing logs for: $service"
        docker compose logs $follow_flag "$service"
    else
        print_message "$BLUE" "Showing logs for all services"
        docker compose logs $follow_flag
    fi
}

# List containers
list_containers() {
    docker compose ps
}

# Stop and remove containers
down_services() {
    print_message "$YELLOW" "Stopping and removing QAtron containers..."
    docker compose down
    print_message "$GREEN" "✓ Containers stopped and removed"
}

# Main script logic
check_docker_compose

case "${1:-}" in
    start|up)
        start_services "${2:-}"
        ;;
    stop)
        stop_services "${2:-}"
        ;;
    restart)
        restart_services "${2:-}"
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "${2:-}" "${3:-}"
        ;;
    ps)
        list_containers
        ;;
    down)
        down_services
        ;;
    *)
        usage
        ;;
esac
