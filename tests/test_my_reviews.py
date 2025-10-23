"""Unit tests for My Reviews functionality"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db, Review, Property, User
import json


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


def create_user(client, email='test@example.com', password='Test1234'):
    """Helper function to create and login a user"""
    response = client.post('/api/register',
                          json={
                              'email': email,
                              'password': password,
                              'terms_accepted': True
                          },
                          content_type='application/json')
    return response


def create_review_as_user(client, review_data):
    """Helper function to create a review as authenticated user"""
    return client.post('/api/reviews',
                      json=review_data,
                      content_type='application/json')


class TestMyReviewsEndpoint:
    """Test suite for /api/my-reviews endpoint"""
    
    def test_get_my_reviews_requires_authentication(self, client):
        """Test GET /api/my-reviews returns 401 without authentication"""
        response = client.get('/api/my-reviews')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_my_reviews_returns_empty_list_for_new_user(self, client):
        """Test GET /api/my-reviews returns empty list for user with no reviews"""
        # Create and login user
        create_user(client, 'user1@example.com', 'Test1234')
        
        # Get user's reviews
        response = client.get('/api/my-reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_my_reviews_returns_users_reviews(self, client):
        """Test GET /api/my-reviews returns only the authenticated user's reviews"""
        # Create first user and add a review
        create_user(client, 'user1@example.com', 'Test1234')
        
        review1_data = {
            'address': '123 User1 Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5,
            'review_text': 'User 1 review'
        }
        create_review_as_user(client, review1_data)
        
        # Logout and create second user
        client.post('/api/logout')
        create_user(client, 'user2@example.com', 'Test1234')
        
        review2_data = {
            'address': '456 User2 Avenue',
            'city': 'TestCity',
            'property_type': 'house',
            'rating': 4,
            'review_text': 'User 2 review'
        }
        create_review_as_user(client, review2_data)
        
        # Get user2's reviews
        response = client.get('/api/my-reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['review_text'] == 'User 2 review'
        assert data[0]['property']['address'] == '456 User2 Avenue'
    
    def test_get_my_reviews_sorted_by_most_recent(self, client):
        """Test GET /api/my-reviews returns reviews sorted by most recent first"""
        import time
        
        create_user(client, 'user@example.com', 'Test1234')
        
        # Create first review
        review1_data = {
            'address': '123 First Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5,
            'review_text': 'First review'
        }
        create_review_as_user(client, review1_data)
        
        time.sleep(0.1)
        
        # Create second review
        review2_data = {
            'address': '456 Second Avenue',
            'city': 'TestCity',
            'property_type': 'house',
            'rating': 4,
            'review_text': 'Second review'
        }
        create_review_as_user(client, review2_data)
        
        # Get reviews
        response = client.get('/api/my-reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['review_text'] == 'Second review'
        assert data[1]['review_text'] == 'First review'


class TestUpdateReviewEndpoint:
    """Test suite for PUT /api/reviews/<id> endpoint"""
    
    def test_update_review_requires_authentication(self, client):
        """Test PUT /api/reviews/<id> returns 401 without authentication"""
        response = client.put('/api/reviews/1',
                             json={'rating': 4},
                             content_type='application/json')
        assert response.status_code == 401
    
    def test_update_review_not_found(self, client):
        """Test PUT /api/reviews/<id> returns 404 for non-existent review"""
        create_user(client)
        
        response = client.put('/api/reviews/999',
                             json={'rating': 4},
                             content_type='application/json')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_update_review_forbidden_for_non_owner(self, client):
        """Test PUT /api/reviews/<id> returns 403 if user doesn't own the review"""
        # Create user1 and a review
        create_user(client, 'user1@example.com', 'Test1234')
        
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Logout and create user2
        client.post('/api/logout')
        create_user(client, 'user2@example.com', 'Test1234')
        
        # Try to update user1's review as user2
        response = client.put(f'/api/reviews/{review_id}',
                             json={'rating': 3},
                             content_type='application/json')
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_update_review_rating_succeeds(self, client):
        """Test updating review rating"""
        create_user(client)
        
        # Create a review
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5,
            'review_text': 'Original text'
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Update rating
        response = client.put(f'/api/reviews/{review_id}',
                             json={'rating': 3},
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['rating'] == 3
        assert data['review_text'] == 'Original text'
    
    def test_update_review_text_succeeds(self, client):
        """Test updating review text"""
        create_user(client)
        
        # Create a review
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5,
            'review_text': 'Original text'
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Update text
        response = client.put(f'/api/reviews/{review_id}',
                             json={'review_text': 'Updated text'},
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['review_text'] == 'Updated text'
        assert data['rating'] == 5
    
    def test_update_review_invalid_rating_returns_400(self, client):
        """Test updating review with invalid rating returns 400"""
        create_user(client)
        
        # Create a review
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Try to update with invalid rating
        response = client.put(f'/api/reviews/{review_id}',
                             json={'rating': 10},
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_update_review_landlord_info_succeeds(self, client):
        """Test updating landlord information"""
        create_user(client)
        
        # Create a review
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Update landlord info
        response = client.put(f'/api/reviews/{review_id}',
                             json={
                                 'landlord_name': 'Mr. Landlord',
                                 'landlord_rating': 4
                             },
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['landlord_name'] == 'Mr. Landlord'
        assert data['landlord_rating'] == 4


class TestDeleteReviewEndpoint:
    """Test suite for DELETE /api/reviews/<id> endpoint"""
    
    def test_delete_review_requires_authentication(self, client):
        """Test DELETE /api/reviews/<id> returns 401 without authentication"""
        response = client.delete('/api/reviews/1')
        assert response.status_code == 401
    
    def test_delete_review_not_found(self, client):
        """Test DELETE /api/reviews/<id> returns 404 for non-existent review"""
        create_user(client)
        
        response = client.delete('/api/reviews/999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_delete_review_forbidden_for_non_owner(self, client):
        """Test DELETE /api/reviews/<id> returns 403 if user doesn't own the review"""
        # Create user1 and a review
        create_user(client, 'user1@example.com', 'Test1234')
        
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Logout and create user2
        client.post('/api/logout')
        create_user(client, 'user2@example.com', 'Test1234')
        
        # Try to delete user1's review as user2
        response = client.delete(f'/api/reviews/{review_id}')
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_delete_review_succeeds(self, client):
        """Test deleting own review succeeds"""
        create_user(client)
        
        # Create a review
        review_data = {
            'address': '123 Test Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        response = create_review_as_user(client, review_data)
        review_id = response.get_json()['id']
        
        # Delete the review
        response = client.delete(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Verify review is deleted
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 404
    
    def test_delete_review_removes_from_my_reviews(self, client):
        """Test deleted review no longer appears in my-reviews"""
        create_user(client)
        
        # Create two reviews
        review1_data = {
            'address': '123 First Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        response1 = create_review_as_user(client, review1_data)
        review1_id = response1.get_json()['id']
        
        review2_data = {
            'address': '456 Second Avenue',
            'city': 'TestCity',
            'property_type': 'house',
            'rating': 4
        }
        create_review_as_user(client, review2_data)
        
        # Verify both reviews exist
        response = client.get('/api/my-reviews')
        assert len(response.get_json()) == 2
        
        # Delete first review
        client.delete(f'/api/reviews/{review1_id}')
        
        # Verify only one review remains
        response = client.get('/api/my-reviews')
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['property']['address'] == '456 Second Avenue'


class TestAnonymousReviews:
    """Test suite to ensure anonymous reviews still work"""
    
    def test_anonymous_review_creation_still_works(self, client):
        """Test creating a review without authentication still works"""
        review_data = {
            'address': '123 Anonymous Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5,
            'review_text': 'Anonymous review'
        }
        
        response = client.post('/api/reviews',
                              json=review_data,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['rating'] == 5
        assert data['review_text'] == 'Anonymous review'
    
    def test_anonymous_reviews_not_in_my_reviews(self, client):
        """Test anonymous reviews don't appear in any user's my-reviews"""
        # Create an anonymous review
        review_data = {
            'address': '123 Anonymous Street',
            'city': 'TestCity',
            'property_type': 'apartment',
            'rating': 5
        }
        client.post('/api/reviews',
                   json=review_data,
                   content_type='application/json')
        
        # Create a user and check my-reviews
        create_user(client)
        response = client.get('/api/my-reviews')
        data = response.get_json()
        assert len(data) == 0
