#!/bin/bash

# Sports Brief Builder - Easy Start Script

echo "🏆 Sports Brief Builder - Starting..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚙️  Please edit .env and add your OpenAI API key:"
    echo "   nano .env"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
source .env
if [ "$OPENAI_API_KEY" == "your_openai_api_key_here" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not configured!"
    echo "📝 Please edit .env and add your API key:"
    echo "   nano .env"
    exit 1
fi

echo "✅ Configuration validated"
echo ""

# Create data directory if it doesn't exist
mkdir -p data

echo "🐳 Starting Docker containers..."
echo ""

# Build and start containers
docker compose up --build

echo ""
echo "🎉 Application is ready!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
