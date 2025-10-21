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
- ✅ User authentication and registration
- ✅ JWT-based session management
- ✅ Secure password hashing with bcrypt

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

4. (Optional) Set environment variables for production:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-random-secret-key
```

5. Run the Flask server:
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

### Troubleshooting

**Issue: 'next' is not recognized as an internal or external command (Windows)**

If you get this error when running `npm run dev`, it means you haven't installed the dependencies yet:

1. Make sure you're in the `frontend` directory
2. Run `npm install` first to install all dependencies
3. Then run `npm run dev`

Alternatively, you can use: `npx next dev`

For more troubleshooting steps, see the [frontend README](frontend/README.md#troubleshooting).

## Usage

1. **View Reviews**: Open `http://localhost:3000` to see all reviews
2. **Register**: Click "Register" to create a new account
3. **Login**: Click "Login" to access your account
4. **Add Review**: Click "Add Review" button to submit a new review (requires login in future versions)
5. **Fill Form**: Enter property details, your review, and optionally landlord information
6. **Submit**: Click "Submit Review" to save your review

## Testing

### Running Tests

The project includes both unit tests for the API and end-to-end tests using Playwright.

#### API Unit Tests

Run the API unit tests (no servers needed):
```bash
pytest tests/test_api.py -v
```

These tests cover:
- Root endpoint (GET /)
- Health check endpoint
- POST /api/reviews with valid data
- POST /api/reviews with minimal/optional fields
- POST /api/reviews validation (missing/invalid fields)
- GET /api/reviews

#### End-to-End Tests

1. Install test dependencies:
```bash
pip install -r tests/requirements.txt
playwright install chromium
```

2. Make sure both backend and frontend servers are running:
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

3. Run the tests:
```bash
pytest tests/test_auth.py -v
```

### Test Coverage

The test suite covers:
- **API Tests**: All API endpoints, validation, and error handling
- **Authentication Tests**: User registration (success and validation failures)
- User login (success and invalid credentials)
- Email and password validation
- Terms acceptance requirement
- Duplicate email handling
- Logout functionality
- Protected endpoint access with and without authentication

## API Documentation

### Endpoints

#### Root Endpoint
```
GET /
```
Returns the API status. Use this to verify the backend is running.

Response:
```json
{
  "status": "ok",
  "message": "RentRate API is running"
}
```

#### Health Check
```
GET /api/health
```
Returns the API health status.

#### Authentication Endpoints

##### Register User
```
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "johndoe",  // optional
  "terms_accepted": true
}
```
Creates a new user account. Password must be at least 8 characters with 1 uppercase letter and 1 number. Returns JWT token in httpOnly cookie.

##### Login
```
POST /api/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```
Authenticates user and returns JWT token in httpOnly cookie.

##### Get Profile (Protected)
```
GET /api/profile
Cookie: token=<jwt_token>
```
Returns the current user's profile. Requires valid JWT token.

##### Logout
```
POST /api/logout
```
Clears the authentication token cookie.

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
  "reviewer_name": "John Doe",  // optional, defaults to "Anonymous"
  "rating": 4,
  "review_text": "Great apartment!",  // optional
  "landlord_name": "Jane Smith",  // optional
  "landlord_rating": 5  // optional
}
```
Required fields: `address`, `property_type`, `rating`

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

**User Table**
- id (Primary Key)
- email (String, Unique)
- username (String, Optional)
- password_hash (String)
- created_at (DateTime)

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

- Image uploads for properties
- Advanced search and filtering
- Landlord profiles
- Response system for landlords
- Email notifications
- Property verification system
- Mobile app
- Password reset functionality
- Email verification
- Two-factor authentication

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.