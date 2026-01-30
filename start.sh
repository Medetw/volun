#!/bin/bash

# Volunteering Platform - Simple Start Script
# Made for easy project management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Volunteering Platform${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if docker-compose is installed
check_docker() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_status "Docker and docker-compose are installed ✓"
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services (default)"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  build     Build all images"
    echo "  logs      Show logs"
    echo "  clean     Remove all containers and volumes"
    echo "  dev       Start in development mode"
    echo "  prod      Start in production mode"
    echo "  status    Show container status"
    echo "  help      Show this help message"
}

# Start services
start_services() {
    print_header
    print_status "Starting Volunteering Platform..."
    
    docker-compose up -d --build
    
    print_status "Services are starting up..."
    print_status "Please wait a moment for services to be ready."
    
    echo ""
    print_status "🌐 Frontend: http://localhost"
    print_status "🔧 Backend API: http://localhost/api/"
    print_status "🗄️  Database: localhost:5432"
    print_status "📦 Redis: localhost:6379"
    echo ""
    print_status "To view logs: $0 logs"
    print_status "To stop services: $0 stop"
}

# Stop services
stop_services() {
    print_header
    print_status "Stopping all services..."
    
    docker-compose down
    
    print_status "All services stopped ✓"
}

# Restart services
restart_services() {
    print_header
    print_status "Restarting all services..."
    
    docker-compose down
    docker-compose up -d --build
    
    print_status "All services restarted ✓"
}

# Build images
build_images() {
    print_header
    print_status "Building all Docker images..."
    
    docker-compose build
    
    print_status "All images built successfully ✓"
}

# Show logs
show_logs() {
    print_header
    print_status "Showing logs (Ctrl+C to exit)..."
    
    docker-compose logs -f
}

# Clean everything
clean_all() {
    print_header
    print_warning "This will remove ALL containers, volumes, and images!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing everything..."
        
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        
        print_status "Everything cleaned ✓"
    else
        print_status "Operation cancelled."
    fi
}

# Development mode
dev_mode() {
    print_header
    print_status "Starting in DEVELOPMENT mode..."
    
    docker-compose -f docker-compose.dev.yml up -d --build
    
    print_status "Development environment started ✓"
    print_status "🔧 Backend (hot reload): http://localhost:8000"
    print_status "🗄️  Database: localhost:5432"
    print_status "📦 Redis: localhost:6379"
}

# Production mode
prod_mode() {
    print_header
    print_status "Starting in PRODUCTION mode..."
    
    if [ ! -f .env ]; then
        print_error ".env file not found! Please create it for production."
        exit 1
    fi
    
    docker-compose -f docker-compose.prod.yml up -d --build
    
    print_status "Production environment started ✓"
    print_status "🌐 Application: http://localhost"
}

# Show status
show_status() {
    print_header
    print_status "Container status:"
    
    docker-compose ps
    
    echo ""
    print_status "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Main script logic
main() {
    check_docker
    
    case "${1:-start}" in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "build")
            build_images
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            clean_all
            ;;
        "dev")
            dev_mode
            ;;
        "prod")
            prod_mode
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
