from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import jwt
import re
from functools import wraps

app = Flask(__name__)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rentrate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')

# Security configuration
IS_PRODUCTION = app.config['ENV'] == 'production'

db = SQLAlchemy(app)

# Models
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # room, apartment, house
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='property', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'property_type': self.property_type,
            'created_at': self.created_at.isoformat()
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    reviewer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)  # Optional comment
    landlord_name = db.Column(db.String(100))
    landlord_rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'property': self.property.to_dict() if self.property else None,
            'reviewer_name': self.reviewer_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'landlord_name': self.landlord_name,
            'landlord_rating': self.landlord_rating,
            'created_at': self.created_at.isoformat()
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }

# Initialize database
with app.app_context():
    db.create_all()

# Helper functions
def validate_password(password):
    """Validate password strength: min 8 chars, 1 uppercase, 1 number"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, ""

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in cookies
        if 'token' in request.cookies:
            token = request.cookies.get('token')
        # Also check Authorization header as fallback
        elif 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'RentRate API is running'}), 200

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    if not data.get('terms_accepted'):
        return jsonify({'error': 'You must accept the terms and conditions'}), 400
    
    # Validate email format
    email_valid, email_error = validate_email(data['email'])
    if not email_valid:
        return jsonify({'error': email_error}), 400
    
    # Validate password strength
    password_valid, password_error = validate_password(data['password'])
    if not password_valid:
        return jsonify({'error': password_error}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Hash password
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # Create new user
    user = User(
        email=data['email'],
        username=data.get('username'),
        password_hash=password_hash
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = generate_token(user.id)
    
    # Create response with token in httpOnly cookie
    response = make_response(jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201)
    response.set_cookie(
        'token',
        token,
        httponly=True,
        secure=IS_PRODUCTION,  # Only secure in production (requires HTTPS)
        samesite='Lax',
        max_age=7*24*60*60  # 7 days
    )
    
    return response

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    token = generate_token(user.id)
    
    # Create response with token in httpOnly cookie
    response = make_response(jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200)
    response.set_cookie(
        'token',
        token,
        httponly=True,
        secure=IS_PRODUCTION,  # Only secure in production (requires HTTPS)
        samesite='Lax',
        max_age=7*24*60*60  # 7 days
    )
    
    return response

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile (requires authentication)"""
    return jsonify(current_user.to_dict()), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user by clearing the token cookie"""
    response = make_response(jsonify({'message': 'Logout successful'}), 200)
    response.set_cookie('token', '', expires=0, httponly=True, secure=IS_PRODUCTION, samesite='Lax')
    return response

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get all reviews or filter by property_id"""
    property_id = request.args.get('property_id', type=int)
    
    if property_id:
        reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    else:
        reviews = Review.query.order_by(Review.created_at.desc()).all()
    
    return jsonify([review.to_dict() for review in reviews]), 200

@app.route('/api/reviews', methods=['POST'])
def create_review():
    """Create a new review"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['address', 'property_type', 'reviewer_name', 'rating']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate rating
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
    
    if data.get('landlord_rating') and (not isinstance(data['landlord_rating'], int) or data['landlord_rating'] < 1 or data['landlord_rating'] > 5):
        return jsonify({'error': 'Landlord rating must be an integer between 1 and 5'}), 400
    
    # Check if property exists or create new one
    property = Property.query.filter_by(address=data['address']).first()
    if not property:
        property = Property(
            address=data['address'],
            property_type=data['property_type']
        )
        db.session.add(property)
        db.session.commit()
    
    # Create review
    review = Review(
        property_id=property.id,
        reviewer_name=data['reviewer_name'],
        rating=data['rating'],
        review_text=data.get('review_text'),
        landlord_name=data.get('landlord_name'),
        landlord_rating=data.get('landlord_rating')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify(review.to_dict()), 201

@app.route('/api/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get a specific review by ID"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    return jsonify(review.to_dict()), 200

@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties"""
    properties = Property.query.order_by(Property.created_at.desc()).all()
    
    # Include review count and average rating for each property
    result = []
    for prop in properties:
        prop_dict = prop.to_dict()
        reviews = Review.query.filter_by(property_id=prop.id).all()
        prop_dict['review_count'] = len(reviews)
        if reviews:
            prop_dict['average_rating'] = sum(r.rating for r in reviews) / len(reviews)
        else:
            prop_dict['average_rating'] = 0
        result.append(prop_dict)
    
    return jsonify(result), 200

@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get a specific property with its reviews"""
    property = Property.query.get(property_id)
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    prop_dict = property.to_dict()
    reviews = Review.query.filter_by(property_id=property.id).all()
    prop_dict['reviews'] = [r.to_dict() for r in reviews]
    prop_dict['review_count'] = len(reviews)
    if reviews:
        prop_dict['average_rating'] = sum(r.rating for r in reviews) / len(reviews)
    else:
        prop_dict['average_rating'] = 0
    
    return jsonify(prop_dict), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
