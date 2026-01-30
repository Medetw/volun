# Stage 1: Build stage
FROM node:20-bookworm AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production stage with Nginx
FROM nginx:bookworm AS production

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy built app from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy optimized Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80


# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
