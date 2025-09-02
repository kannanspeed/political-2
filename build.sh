#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting build process..."

# Upgrade pip
pip install --upgrade pip

# Install system dependencies if needed
# apt-get update && apt-get install -y python3-dev

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-render.txt

echo "✅ Build completed successfully!"
