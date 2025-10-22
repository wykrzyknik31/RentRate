"""Unit tests for translation configuration"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db


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


class TestTranslationConfiguration:
    """Test suite for translation service configuration"""
    
    @patch('app.requests.post')
    @patch.dict(os.environ, {'LIBRETRANSLATE_URL': 'https://custom.libretranslate.com'})
    def test_translation_uses_custom_url(self, mock_post, client):
        """Test that translation uses URL from environment variable"""
        # Mock the LibreTranslate API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'translatedText': 'Hola mundo'}
        mock_post.return_value = mock_response
        
        # Make translation request
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        
        assert response.status_code == 200
        
        # Verify that the custom URL was used
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'https://custom.libretranslate.com/translate' in str(call_args)
    
    @patch('app.requests.post')
    @patch.dict(os.environ, {
        'LIBRETRANSLATE_URL': 'https://libretranslate.com',
        'LIBRETRANSLATE_API_KEY': 'test-api-key-12345'
    })
    def test_translation_uses_api_key_when_provided(self, mock_post, client):
        """Test that translation includes API key when configured"""
        # Mock the LibreTranslate API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'translatedText': 'Hola mundo'}
        mock_post.return_value = mock_response
        
        # Make translation request
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        
        assert response.status_code == 200
        
        # Verify that the API key was included in the request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['api_key'] == 'test-api-key-12345'
    
    @patch('app.requests.post')
    @patch.dict(os.environ, {'LIBRETRANSLATE_URL': 'https://libretranslate.com'}, clear=False)
    def test_translation_works_without_api_key(self, mock_post, client):
        """Test that translation works when no API key is provided"""
        # Remove API key from environment if it exists
        os.environ.pop('LIBRETRANSLATE_API_KEY', None)
        
        # Mock the LibreTranslate API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'translatedText': 'Witaj świecie'}
        mock_post.return_value = mock_response
        
        # Make translation request
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'pl'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['translated_text'] == 'Witaj świecie'
        
        # Verify that no API key was sent (api_key should not be in payload)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'api_key' not in payload or payload.get('api_key') == ''
