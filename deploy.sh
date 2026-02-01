#!/bin/bash

# Volunteering Platform Deployment Script
# This script handles deployment to production servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="volunteering-platform"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

check_requirements() {
    log "Checking requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warning ".env file not found. Creating from template..."
        cp .env.example .env
        warning "Please edit .env file with your production values before continuing!"
        exit 1
    fi
    
    success "Requirements check passed"
}

create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./logs/nginx"
    mkdir -p "./logs/backend"
    mkdir -p "./ssl"
    
    success "Directories created"
}

backup_database() {
    log "Creating database backup..."
    
    if docker-compose ps db | grep -q "Up"; then
        BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql"
        docker-compose exec -T db pg_dump -U postgres volunteering > "$BACKUP_FILE"
        
        # Compress backup
        gzip "$BACKUP_FILE"
        success "Database backup created: ${BACKUP_FILE}.gz"
        
        # Keep only last 7 backups
        find "$BACKUP_DIR" -name "backup-*.sql.gz" -type f -mtime +7 -delete
    else
        warning "Database is not running. Skipping backup."
    fi
}

pull_latest_code() {
    log "Pulling latest code from repository..."
    
    # Check if we're in a git repository
    if [ -d ".git" ]; then
        git pull origin main
        success "Latest code pulled"
    else
        warning "Not a git repository. Skipping code pull."
    fi
}

build_and_deploy() {
    log "Building and deploying application..."
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose -f docker-compose.prod.yml down || true
    
    # Build new images
    log "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    success "Application deployed"
}

run_migrations() {
    log "Running database migrations..."
    
    # Wait for backend to be ready
    for i in {1..30}; do
        if docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --check; then
            break
        fi
        log "Waiting for backend to be ready... ($i/30)"
        sleep 2
    done
    
    # Run migrations
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate
    success "Migrations completed"
}

collect_static() {
    log "Collecting static files..."
    
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
    success "Static files collected"
}

health_check() {
    log "Performing health check..."
    
    # Check if all services are running
    for i in {1..10}; do
        if curl -f http://localhost/health &>/dev/null; then
            success "Health check passed"
            return 0
        fi
        log "Health check attempt $i/10..."
        sleep 10
    done
    
    error "Health check failed"
    return 1
}

cleanup() {
    log "Cleaning up old Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this in production)
    # docker volume prune -f
    
    success "Cleanup completed"
}

send_notification() {
    local status=$1
    local message=$2
    
    # You can integrate with Slack, Discord, or email here
    log "Deployment notification: $status - $message"
    
    # Example Slack webhook (uncomment and configure)
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"🚀 $PROJECT_NAME Deployment: $status\\n$message\"}" \
    #     YOUR_SLACK_WEBHOOK_URL
}

main() {
    log "Starting deployment of $PROJECT_NAME..."
    
    # Check requirements
    check_requirements
    
    # Create directories
    create_directories
    
    # Backup current database
    backup_database
    
    # Pull latest code
    pull_latest_code
    
    # Build and deploy
    build_and_deploy
    
    # Run migrations
    run_migrations
    
    # Collect static files
    collect_static
    
    # Health check
    if health_check; then
        success "Deployment completed successfully!"
        send_notification "SUCCESS" "Application deployed and health checks passed"
        cleanup
    else
        error "Deployment failed health checks!"
        send_notification "FAILED" "Application deployed but health checks failed"
        exit 1
    fi
    
    log "Deployment finished at $(date)"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "backup")
        backup_database
        ;;
    "health")
        health_check
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  backup   - Create database backup"
        echo "  health   - Run health check"
        echo "  cleanup  - Clean up Docker resources"
        echo "  help     - Show this help message"
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
