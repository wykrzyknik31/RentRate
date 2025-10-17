# RentRate

A platform for tenants to review rooms, apartments, and landlords.

## Overview

RentRate is a full-stack web application that allows tenants to share their experiences by reviewing properties and landlords. The platform helps renters make informed decisions by providing transparency about rental properties and landlords.

## Architecture

- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Backend**: Flask REST API with SQLAlchemy ORM
- **Database**: SQLite (easily upgradeable to PostgreSQL for production)

## Features

- ✅ View all reviews with property and landlord ratings
- ✅ Submit new reviews for properties
- ✅ Rate properties (1-5 stars)
- ✅ Rate landlords (1-5 stars, optional)
- ✅ Filter reviews by property
- ✅ Responsive design with modern UI
- ✅ RESTful API endpoints
- ✅ Real-time data fetching

## Getting Started

### Prerequisites

- Python 3.8+ with pip
- Node.js 18+ with npm
- Git

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

1. **View Reviews**: Open `http://localhost:3000` to see all reviews
2. **Add Review**: Click "Add Review" button to submit a new review
3. **Fill Form**: Enter property details, your review, and optionally landlord information
4. **Submit**: Click "Submit Review" to save your review

## API Documentation

### Endpoints

#### Health Check
```
GET /api/health
```
Returns the API status.

#### Get All Reviews
```
GET /api/reviews
```
Optional query parameter: `property_id` to filter reviews by property.

#### Create Review
```
POST /api/reviews
Content-Type: application/json

{
  "address": "123 Main St, Apt 4B",
  "property_type": "apartment",
  "reviewer_name": "John Doe",
  "rating": 4,
  "review_text": "Great apartment!",
  "landlord_name": "Jane Smith",  // optional
  "landlord_rating": 5  // optional
}
```

#### Get Single Review
```
GET /api/reviews/<review_id>
```

#### Get All Properties
```
GET /api/properties
```
Returns all properties with review statistics.

#### Get Single Property
```
GET /api/properties/<property_id>
```
Returns property details with all reviews.

## Project Structure

```
RentRate/
├── backend/
│   ├── app.py              # Flask application and API routes
│   ├── requirements.txt    # Python dependencies
│   ├── rentrate.db        # SQLite database (auto-generated)
│   └── README.md          # Backend documentation
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   └── ReviewList.tsx    # Review list component
│   │   ├── add-review/
│   │   │   └── page.tsx          # Add review page
│   │   ├── page.tsx              # Home page
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── public/                   # Static assets
│   ├── .env.local               # Environment variables
│   ├── package.json             # Node dependencies
│   └── tsconfig.json            # TypeScript config
└── README.md                    # This file
```

## Development

### Adding New Features

1. **Backend**: Add new routes in `backend/app.py` and database models
2. **Frontend**: Create new pages in `frontend/app/` or components in `frontend/app/components/`

### Database Schema

**Property Table**
- id (Primary Key)
- address (String)
- property_type (String: room/apartment/house)
- created_at (DateTime)

**Review Table**
- id (Primary Key)
- property_id (Foreign Key to Property)
- reviewer_name (String)
- rating (Integer: 1-5)
- review_text (Text)
- landlord_name (String, optional)
- landlord_rating (Integer: 1-5, optional)
- created_at (DateTime)

## Future Enhancements

- User authentication and authorization
- Image uploads for properties
- Advanced search and filtering
- Landlord profiles
- Response system for landlords
- Email notifications
- Property verification system
- Mobile app

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.