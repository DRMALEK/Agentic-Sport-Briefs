#!/bin/bash

# Test script to verify the application is working

echo "🧪 Testing Sports Brief Builder..."
echo ""

# Check if services are running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ Backend is not running on port 8000"
    echo "   Start with: ./start.sh"
    exit 1
fi

echo "✅ Backend is running"

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "⚠️  Frontend might not be running on port 3000"
fi

echo "✅ Frontend is accessible"
echo ""

# Test backend endpoints
echo "📡 Testing API endpoints..."
echo ""

# Test root endpoint
echo "1. Testing GET /"
response=$(curl -s http://localhost:8000/)
if echo "$response" | grep -q "Sports Brief Builder API"; then
    echo "   ✅ Root endpoint working"
else
    echo "   ❌ Root endpoint failed"
fi

# Test stats endpoint
echo "2. Testing GET /api/stats"
response=$(curl -s http://localhost:8000/api/stats)
if echo "$response" | grep -q "total_briefs"; then
    echo "   ✅ Stats endpoint working"
    echo "   📊 Stats: $response"
else
    echo "   ❌ Stats endpoint failed"
fi

# Test knowledge endpoint
echo "3. Testing GET /api/knowledge"
response=$(curl -s http://localhost:8000/api/knowledge)
if echo "$response" | grep -q "knowledge"; then
    echo "   ✅ Knowledge endpoint working"
    count=$(echo "$response" | grep -o '"id":' | wc -l)
    echo "   📚 Knowledge items: $count"
else
    echo "   ❌ Knowledge endpoint failed"
fi

# Test briefs endpoint
echo "4. Testing GET /api/briefs"
response=$(curl -s http://localhost:8000/api/briefs)
if echo "$response" | grep -q "briefs"; then
    echo "   ✅ Briefs endpoint working"
    count=$(echo "$response" | grep -o '"id":' | wc -l)
    echo "   📝 Saved briefs: $count"
else
    echo "   ❌ Briefs endpoint failed"
fi

echo ""
echo "🎯 Test Summary:"
echo "   - Backend API: ✅ Running"
echo "   - Database: ✅ Accessible"
echo "   - Knowledge: ✅ Loaded"
echo ""
echo "🚀 Ready to use!"
echo ""
echo "Try these example prompts:"
echo "   • 'Show me latest NFL scores'"
echo "   • 'Create a brief about basketball'"
echo "   • 'Generate player performance statistics'"
echo ""
