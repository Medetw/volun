.PHONY: help build dev prod up down logs clean backup deploy

# Default target
help:
	@echo "Volunteering Platform - Management Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev      - Start development environment"
	@echo "  make dev-up   - Start development services"
	@echo "  make dev-down - Stop development services"
	@echo "  make dev-logs - Show development logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod     - Build and start production environment"
	@echo "  make prod-up  - Start production services"
	@echo "  make prod-down- Stop production services"
	@echo "  make prod-logs- Show production logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make build    - Build all Docker images"
	@echo "  make clean    - Clean Docker system"
	@echo "  make backup   - Backup database"
	@echo "  make deploy   - Deploy to production"
	@echo ""

# Development commands
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build

dev-up:
	@echo "🚀 Starting development services..."
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	@echo "🛑 Stopping development services..."
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Production commands
prod:
	@echo "🚀 Building and starting production environment..."
	docker-compose -f docker-compose.prod.yml up --build -d

prod-up:
	@echo "🚀 Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	@echo "🛑 Stopping production services..."
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Utility commands
build:
	@echo "🔨 Building all Docker images..."
	docker-compose -f docker-compose.dev.yml build
	docker-compose -f docker-compose.prod.yml build

clean:
	@echo "🧹 Cleaning Docker system..."
	docker-compose -f docker-compose.dev.yml down --volumes --remove-orphans
	docker-compose -f docker-compose.prod.yml down --volumes --remove-orphans
	docker system prune -a -f
	docker volume prune -f

backup:
	@echo "💾 Creating database backup..."
	docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres volunteering > ./backups/backup-$(shell date +%Y%m%d-%H%M%S).sql
	@echo "✅ Backup completed"

deploy:
	@echo "🚀 Deploying to production..."
	@echo "1. Pulling latest changes..."
	git pull origin main
	@echo "2. Building and starting services..."
	make prod
	@echo "3. Running migrations..."
	docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
	@echo "4. Collecting static files..."
	docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
	@echo "✅ Deployment completed"

# Status commands
status:
	@echo "📊 Service Status:"
	docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "Development services not running"
	docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "Production services not running"

# SSL setup (for production)
ssl:
	@echo "🔐 Setting up SSL certificates..."
	@echo "Please ensure you have domain pointing to this server"
	@echo "Then run: certbot --nginx -d yourdomain.com -d www.yourdomain.com"
