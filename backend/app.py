from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rentrate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    review_text = db.Column(db.Text, nullable=False)
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

# Initialize database
with app.app_context():
    db.create_all()

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'RentRate API is running'}), 200

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
    required_fields = ['address', 'property_type', 'reviewer_name', 'rating', 'review_text']
    for field in required_fields:
        if field not in data:
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
        review_text=data['review_text'],
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
