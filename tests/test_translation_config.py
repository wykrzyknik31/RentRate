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
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key-12345'})
    def test_translation_uses_api_key_when_provided(self, mock_translate_client, client):
        """Test that translation uses API key from environment variable"""
        # Mock the Google Translate API response
        mock_client_instance = Mock()
        mock_client_instance.translate.return_value = {'translatedText': 'Hola mundo'}
        mock_translate_client.return_value = mock_client_instance
        
        # Make translation request
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        
        assert response.status_code == 200
        
        # Verify that the API key was used to create client
        mock_translate_client.assert_called_once_with(api_key='test-api-key-12345')
        
        # Verify that translate was called
        mock_client_instance.translate.assert_called_once()
    
    def test_translation_fails_without_api_key(self, client):
        """Test that translation returns error when no API key is provided"""
        # Make translation request without API key in environment
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'pl'
        })
        
        assert response.status_code == 503
        data = response.get_json()
        assert 'error' in data
        assert 'not configured' in data['error'].lower()
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'another-test-key'})
    def test_translation_uses_different_api_key(self, mock_translate_client, client):
        """Test that translation uses different API key when environment changes"""
        # Mock the Google Translate API response
        mock_client_instance = Mock()
        mock_client_instance.translate.return_value = {'translatedText': 'Witaj świecie'}
        mock_translate_client.return_value = mock_client_instance
        
        # Make translation request
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'pl'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['translated_text'] == 'Witaj świecie'
        
        # Verify that the correct API key was used
        mock_translate_client.assert_called_once_with(api_key='another-test-key')
