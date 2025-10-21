"""Unit tests for RentRate API endpoints"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db, Review, Property


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


class TestRootEndpoint:
    """Test suite for root endpoint"""
    
    def test_root_returns_200(self, client):
        """Test GET / returns 200 OK with status message"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'message' in data
        assert 'RentRate API' in data['message']


class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    def test_health_returns_200(self, client):
        """Test GET /api/health returns 200 OK"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestReviewsEndpoint:
    """Test suite for reviews endpoint"""
    
    def test_post_review_with_valid_data_returns_201(self, client):
        """Test POST /api/reviews with valid data returns 201"""
        review_data = {
            'address': '123 Test Street',
            'property_type': 'apartment',
            'reviewer_name': 'John Doe',
            'rating': 5,
            'review_text': 'Great place to live!',
            'landlord_name': 'Jane Smith',
            'landlord_rating': 4
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['rating'] == 5
        assert data['property']['address'] == '123 Test Street'
        assert data['reviewer_name'] == 'John Doe'
    
    def test_post_review_without_reviewer_name_succeeds(self, client):
        """Test POST /api/reviews without reviewer_name (anonymous review)"""
        review_data = {
            'address': '456 Test Avenue',
            'property_type': 'house',
            'rating': 4,
            'review_text': 'Good property'
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['rating'] == 4
        assert data['property']['address'] == '456 Test Avenue'
        assert data['reviewer_name'] == 'Anonymous'
    
    def test_post_review_with_minimal_data_succeeds(self, client):
        """Test POST /api/reviews with only required fields"""
        review_data = {
            'address': '789 Minimal Street',
            'property_type': 'room',
            'rating': 3
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['rating'] == 3
        assert data['property']['address'] == '789 Minimal Street'
    
    def test_post_review_missing_address_returns_400(self, client):
        """Test POST /api/reviews without address returns 400"""
        review_data = {
            'property_type': 'apartment',
            'rating': 5
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'address' in data['error'].lower()
    
    def test_post_review_missing_property_type_returns_400(self, client):
        """Test POST /api/reviews without property_type returns 400"""
        review_data = {
            'address': '123 Test Street',
            'rating': 5
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'property_type' in data['error'].lower()
    
    def test_post_review_missing_rating_returns_400(self, client):
        """Test POST /api/reviews without rating returns 400"""
        review_data = {
            'address': '123 Test Street',
            'property_type': 'apartment'
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'rating' in data['error'].lower()
    
    def test_post_review_invalid_rating_returns_400(self, client):
        """Test POST /api/reviews with invalid rating returns 400"""
        review_data = {
            'address': '123 Test Street',
            'property_type': 'apartment',
            'rating': 6  # Invalid: should be 1-5
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'rating' in data['error'].lower()
    
    def test_post_review_invalid_rating_type_returns_400(self, client):
        """Test POST /api/reviews with non-integer rating returns 400"""
        review_data = {
            'address': '123 Test Street',
            'property_type': 'apartment',
            'rating': 'five'  # Invalid: should be integer
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_post_review_invalid_landlord_rating_returns_400(self, client):
        """Test POST /api/reviews with invalid landlord_rating returns 400"""
        review_data = {
            'address': '123 Test Street',
            'property_type': 'apartment',
            'rating': 5,
            'landlord_name': 'Test Landlord',
            'landlord_rating': 10  # Invalid: should be 1-5
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'landlord' in data['error'].lower()
    
    def test_get_reviews_returns_200(self, client):
        """Test GET /api/reviews returns 200"""
        response = client.get('/api/reviews')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
