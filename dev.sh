#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p)
}
trap cleanup EXIT

echo "🚀 Starting Development Environment..."

# Start Backend
echo "🐍 Starting Django Backend..."
python manage.py runserver &

# Start Frontend
echo "⚛️ Starting Next.js Frontend..."
cd frontend && npm run dev &

# Wait for both processes
wait
