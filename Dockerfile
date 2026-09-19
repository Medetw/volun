# Use official Python + Node image (has both runtimes)
FROM nikolaik/python-nodejs:python3.12-nodejs20

WORKDIR /app

# Copy everything
COPY . .

# Run build script
RUN chmod +x build.sh && ./build.sh

# Set working directory to backend for gunicorn
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Start gunicorn directly (no cd needed)
CMD gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
