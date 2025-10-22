from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import jwt
import re
from functools import wraps
import langdetect
from langdetect import detect_langs, LangDetectException
import traceback
from google.cloud import translate_v2 as translate
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Support both PostgreSQL (for Docker) and SQLite (for local development)
db_host = os.environ.get('DB_HOST')
if db_host:
    # PostgreSQL configuration for Docker
    postgres_user = os.environ.get('POSTGRES_USER', 'rentrate')
    postgres_password = os.environ.get('POSTGRES_PASSWORD', 'rentrate')
    postgres_db = os.environ.get('POSTGRES_DB', 'rentrate')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_password}@{db_host}:5432/{postgres_db}'
else:
    # SQLite configuration for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rentrate.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')

# Security configuration
IS_PRODUCTION = app.config['ENV'] == 'production'

# File upload configuration
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PHOTOS = 5

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# Models
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # room, apartment, house
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='property', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
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
    photos = db.relationship('Photo', backref='review', lazy=True, cascade='all, delete-orphan')

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
            'photos': [photo.to_dict() for photo in self.photos],
            'created_at': self.created_at.isoformat()
        }

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'review_id': self.review_id,
            'filename': self.filename,
            'url': f'/api/photos/{self.id}',
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

class Translation(db.Model):
    """Cache for translated texts to avoid repeated API calls"""
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    source_lang = db.Column(db.String(10), nullable=False)
    target_lang = db.Column(db.String(10), nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Create unique constraint on original_text, source_lang, target_lang combination
    __table_args__ = (
        db.Index('idx_translation_lookup', 'original_text', 'source_lang', 'target_lang'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_text': self.original_text,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'translated_text': self.translated_text,
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

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API Routes
@app.route('/', methods=['GET'])
def root():
    """Root endpoint - returns API status and available endpoints"""
    return jsonify({
        'status': 'ok',
        'message': 'RentRate API is running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'reviews': '/api/reviews',
            'properties': '/api/properties',
            'auth': {
                'register': '/api/register',
                'login': '/api/login',
                'profile': '/api/profile',
                'logout': '/api/logout'
            }
        },
        'documentation': 'See README.md for full API documentation'
    }), 200

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
    # Check if request has files
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle multipart form data with files
        data = {}
        for key in request.form:
            try:
                # Try to parse JSON values
                import json
                data[key] = json.loads(request.form[key])
            except:
                data[key] = request.form[key]
        
        files = request.files.getlist('photos')
    else:
        # Handle JSON data without files
        data = request.get_json()
        files = []
    
    # Validate required fields (reviewer_name is optional and defaults to "Anonymous")
    required_fields = ['address', 'city', 'property_type', 'rating']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate rating
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
    
    if data.get('landlord_rating') and (not isinstance(data['landlord_rating'], int) or data['landlord_rating'] < 1 or data['landlord_rating'] > 5):
        return jsonify({'error': 'Landlord rating must be an integer between 1 and 5'}), 400
    
    # Validate photos
    if len(files) > MAX_PHOTOS:
        return jsonify({'error': f'Maximum {MAX_PHOTOS} photos allowed'}), 400
    
    for file in files:
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({'error': f'Invalid file type. Only JPG, JPEG, and PNG files are allowed'}), 400
    
    # Check if property exists or create new one
    property = Property.query.filter_by(address=data['address']).first()
    if not property:
        property = Property(
            address=data['address'],
            city=data['city'],
            property_type=data['property_type']
        )
        db.session.add(property)
        db.session.commit()
    elif not property.city or property.city != data['city']:
        # Update city if not set or if it changed
        property.city = data['city']
        db.session.commit()
    
    # Create review (use "Anonymous" if reviewer_name is not provided)
    review = Review(
        property_id=property.id,
        reviewer_name=data.get('reviewer_name', 'Anonymous') or 'Anonymous',
        rating=data['rating'],
        review_text=data.get('review_text'),
        landlord_name=data.get('landlord_name'),
        landlord_rating=data.get('landlord_rating')
    )
    
    db.session.add(review)
    db.session.commit()
    
    # Handle photo uploads
    for file in files:
        if file and file.filename:
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save file
            file.save(filepath)
            
            # Create photo record
            photo = Photo(
                review_id=review.id,
                filename=original_filename,
                filepath=filepath
            )
            db.session.add(photo)
    
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

@app.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    """Get a photo by ID"""
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    
    if not os.path.exists(photo.filepath):
        return jsonify({'error': 'Photo file not found'}), 404
    
    return send_file(photo.filepath, mimetype='image/jpeg')

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text from one language to another using Google Translate API"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('text'):
        return jsonify({'error': 'Text is required'}), 400
    if not data.get('target_lang'):
        return jsonify({'error': 'Target language is required'}), 400
    
    text = data['text']
    target_lang = data['target_lang'].lower()
    
    # Detect source language if not provided
    source_lang = data.get('source_lang')
    if not source_lang:
        try:
            # Detect language with confidence score
            detected = detect_langs(text)
            if detected:
                source_lang = detected[0].lang
            else:
                return jsonify({'error': 'Could not detect source language'}), 400
        except LangDetectException:
            return jsonify({'error': 'Could not detect source language'}), 400
    else:
        source_lang = source_lang.lower()
    
    # If source and target are the same, return original text
    if source_lang == target_lang:
        return jsonify({
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'from_cache': False
        }), 200
    
    # Check cache first
    cached_translation = Translation.query.filter_by(
        original_text=text,
        source_lang=source_lang,
        target_lang=target_lang
    ).first()
    
    if cached_translation:
        return jsonify({
            'translated_text': cached_translation.translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'from_cache': True
        }), 200
    
    # Use Google Translate API for translation
    # Get API key from environment variable
    google_api_key = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')
    
    if not google_api_key:
        app.logger.error("GOOGLE_TRANSLATE_API_KEY environment variable is not set")
        return jsonify({
            'error': 'Translation service not configured. Please set GOOGLE_TRANSLATE_API_KEY environment variable.'
        }), 503
    
    try:
        # Initialize Google Translate client with API key
        translate_client = translate.Client(api_key=google_api_key)
        
        # Log request details for debugging
        app.logger.info(f"Translation request - source: {source_lang}, target: {target_lang}, text length: {len(text)}")
        
        # Call Google Translate API
        result = translate_client.translate(
            text,
            source_language=source_lang,
            target_language=target_lang,
            format_='text'
        )
        
        translated_text = result.get('translatedText', '')
        
        if not translated_text:
            app.logger.error(f"Translation API returned empty text - Response: {result}")
            return jsonify({'error': 'Translation failed'}), 500
        
        # Cache the translation
        new_translation = Translation(
            original_text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            translated_text=translated_text
        )
        db.session.add(new_translation)
        db.session.commit()
        
        app.logger.info(f"Translation successful - source: {source_lang}, target: {target_lang}")
        
        return jsonify({
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'from_cache': False
        }), 200
        
    except Exception as e:
        # Log detailed error with traceback for debugging
        app.logger.error(f"Translation error: {str(e)}")
        app.logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Translation service error',
            'details': str(e)
        }), 500

@app.route('/api/detect-language', methods=['POST'])
def detect_language():
    """Detect the language of provided text"""
    data = request.get_json()
    
    if not data.get('text'):
        return jsonify({'error': 'Text is required'}), 400
    
    text = data['text']
    
    try:
        # Detect language with confidence scores
        detected = detect_langs(text)
        if detected:
            languages = [{'lang': d.lang, 'prob': d.prob} for d in detected]
            return jsonify({
                'detected_language': detected[0].lang,
                'confidence': detected[0].prob,
                'all_detected': languages
            }), 200
        else:
            return jsonify({'error': 'Could not detect language'}), 400
    except LangDetectException:
        return jsonify({'error': 'Could not detect language'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
