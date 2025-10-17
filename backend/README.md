# RentRate Backend

Flask-based REST API for the RentRate platform.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if API is running

### Reviews
- `GET /api/reviews` - Get all reviews (optional query param: `property_id`)
- `POST /api/reviews` - Create a new review
- `GET /api/reviews/<id>` - Get a specific review

### Properties
- `GET /api/properties` - Get all properties with review stats
- `GET /api/properties/<id>` - Get a specific property with all reviews

## Request Examples

### Create a Review
```bash
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Apt 4B",
    "property_type": "apartment",
    "reviewer_name": "John Doe",
    "rating": 4,
    "review_text": "Great apartment, spacious and clean!",
    "landlord_name": "Jane Smith",
    "landlord_rating": 5
  }'
```

### Get All Reviews
```bash
curl http://localhost:5000/api/reviews
```
