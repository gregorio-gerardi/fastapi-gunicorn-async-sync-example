#!/bin/bash

# Test script for the FastAPI endpoints

BASE_URL="http://localhost:8000"

echo "Testing FastAPI endpoints..."
echo ""

echo "1. Testing root endpoint:"
curl -s "$BASE_URL/" | jq '.' || curl -s "$BASE_URL/"
echo ""

echo "2. Testing health check:"
curl -s "$BASE_URL/health" | jq '.' || curl -s "$BASE_URL/health"
echo ""

echo "3. Testing async-task:"
curl -s "$BASE_URL/async-task" | jq '.' || curl -s "$BASE_URL/async-task"
echo ""

echo "4. Testing sync-with-async endpoint (sync endpoint using async primitives):"
curl -s "$BASE_URL/sync-with-async?seconds=0.3" | jq '.' || curl -s "$BASE_URL/sync-with-async?seconds=0.3"
echo ""

echo "5. Testing concurrent endpoint:"
curl -s "$BASE_URL/concurrent" | jq '.' || curl -s "$BASE_URL/concurrent"
echo ""

echo "Done!"

