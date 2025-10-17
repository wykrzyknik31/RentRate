#!/bin/bash
# API Test Script for RentRate Backend

API_URL="http://localhost:5000"

echo "Testing RentRate API endpoints..."
echo "=================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Endpoint"
echo "GET $API_URL/api/health"
curl -s $API_URL/api/health | python -m json.tool
echo ""
echo ""

# Test 2: Get all reviews
echo "2. Testing Get All Reviews"
echo "GET $API_URL/api/reviews"
curl -s $API_URL/api/reviews | python -m json.tool | head -20
echo "..."
echo ""

# Test 3: Get all properties
echo "3. Testing Get All Properties"
echo "GET $API_URL/api/properties"
curl -s $API_URL/api/properties | python -m json.tool
echo ""
echo ""

# Test 4: Create a new review
echo "4. Testing Create Review"
echo "POST $API_URL/api/reviews"
RESPONSE=$(curl -s -X POST $API_URL/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "address": "555 Test Street",
    "property_type": "apartment",
    "reviewer_name": "Test User",
    "rating": 5,
    "review_text": "This is a test review created by the API test script.",
    "landlord_name": "Test Landlord",
    "landlord_rating": 5
  }')
echo $RESPONSE | python -m json.tool
REVIEW_ID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo ""
echo ""

# Test 5: Get specific review
echo "5. Testing Get Specific Review"
echo "GET $API_URL/api/reviews/$REVIEW_ID"
curl -s $API_URL/api/reviews/$REVIEW_ID | python -m json.tool
echo ""
echo ""

echo "=================================="
echo "All API tests completed!"
