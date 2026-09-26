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
    echo "⚙️  Please edit .env and add your OpenRouter API key:"
    echo "   nano .env"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if OPENROUTER_API_KEY is set
source .env
if [ "$OPENROUTER_API_KEY" == "your_openrouter_api_key_here" ] || [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  OpenRouter API key not configured!"
    echo "📝 Please edit .env and add your API key:"
    echo "   nano .env"
    exit 1
fi

if [ -z "$APIFY_TOKEN" ] || [ "$APIFY_TOKEN" == "your_apify_token_here" ]; then
    echo "⚠️  APIFY_TOKEN not set - live ESPN data will be unavailable (the rest of the app still works)."
    echo ""
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
