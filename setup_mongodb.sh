#!/bin/bash

# MongoDB Setup Script for AgentERP
echo "Setting up MongoDB for AgentERP..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if MongoDB container is already running
if docker ps | grep -q agenterp-mongo; then
    echo "✅ MongoDB container is already running"
    echo "📍 Connection: mongodb://localhost:27017"
    exit 0
fi

# Start MongoDB container
echo "🐳 Starting MongoDB container..."
docker run -d \
    --name agenterp-mongo \
    -p 27017:27017 \
    -v mongodb_data:/data/db \
    --restart unless-stopped \
    mongo:latest

# Wait for MongoDB to start
echo "⏳ Waiting for MongoDB to start..."
sleep 5

# Test connection
if docker exec agenterp-mongo mongo --eval "db.adminCommand('ping')" &> /dev/null; then
    echo "✅ MongoDB is running successfully!"
    echo "📍 Connection URL: mongodb://localhost:27017"
    echo "📍 Database: agenterp"
    echo ""
    echo "🔄 Restart your backend server to connect to MongoDB"
else
    echo "❌ Failed to start MongoDB"
    exit 1
fi