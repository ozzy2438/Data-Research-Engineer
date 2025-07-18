#!/bin/bash

# Data Research Engineer - Server Setup and Run Script

echo "🔍 Data Research Engineer - Starting Backend Server"
echo "=================================================="

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p data results

echo "🚀 Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "Frontend should be served separately (open frontend/index.html in browser)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py 