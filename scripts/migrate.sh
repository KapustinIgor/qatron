#!/bin/bash
# Database migration script for QAtron Control Plane

set -e

COMPOSE_DIR="deployment/docker-compose"
SERVICE_NAME="control-plane"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}QAtron Database Migration Script${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if control-plane container exists and is running
if ! docker compose -f "$COMPOSE_DIR/docker-compose.yml" ps control-plane | grep -q "Up"; then
    echo -e "${YELLOW}Warning: Control Plane container is not running.${NC}"
    echo "Attempting to start services..."
    docker compose -f "$COMPOSE_DIR/docker-compose.yml" up -d postgres control-plane
    
    echo "Waiting for services to be ready..."
    sleep 5
    
    # Wait for postgres to be healthy
    echo "Waiting for PostgreSQL to be ready..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec -T postgres pg_isready -U qatron > /dev/null 2>&1; then
            echo -e "${GREEN}PostgreSQL is ready!${NC}"
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo -e "${RED}Error: PostgreSQL did not become ready in time.${NC}"
        exit 1
    fi
fi

# Check current migration status
echo ""
echo -e "${GREEN}Current migration status:${NC}"
docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec -T control-plane alembic current || echo "No migrations applied yet"

# Run migration
echo ""
echo -e "${GREEN}Running migrations...${NC}"
if docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec -T control-plane alembic upgrade head; then
    echo ""
    echo -e "${GREEN}✓ Migrations completed successfully!${NC}"
    echo ""
    echo -e "${GREEN}Current migration status:${NC}"
    docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec -T control-plane alembic current
else
    echo ""
    echo -e "${RED}✗ Migration failed. Check the error messages above.${NC}"
    exit 1
fi
