#!/bin/bash

# Create logs directory
mkdir -p logs

# Build and start services
docker-compose up --build -d

echo "AI Code Review Agent is starting..."
echo "Web interface: http://localhost"
echo "API docs: http://localhost/docs"
echo "Health check: http://localhost/health"

# Show logs
docker-compose logs -f
