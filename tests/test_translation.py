"""Unit tests for translation endpoints"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db, Translation


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


class TestDetectLanguageEndpoint:
    """Test suite for language detection endpoint"""
    
    def test_detect_language_english(self, client):
        """Test detecting English text"""
        response = client.post('/api/detect-language', json={
            'text': 'This is a test in English language'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'detected_language' in data
        assert data['detected_language'] == 'en'
        assert 'confidence' in data
        assert data['confidence'] > 0.9
    
    def test_detect_language_missing_text(self, client):
        """Test detection with missing text"""
        response = client.post('/api/detect-language', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestTranslateEndpoint:
    """Test suite for translation endpoint"""
    
    def test_translate_missing_text(self, client):
        """Test translation with missing text"""
        response = client.post('/api/translate', json={
            'target_lang': 'en'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_translate_missing_target_lang(self, client):
        """Test translation with missing target language"""
        response = client.post('/api/translate', json={
            'text': 'Hello world'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_translate_same_language(self, client):
        """Test translation when source and target are the same"""
        text = 'Hello world'
        response = client.post('/api/translate', json={
            'text': text,
            'source_lang': 'en',
            'target_lang': 'en'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['translated_text'] == text
        assert data['source_lang'] == 'en'
        assert data['target_lang'] == 'en'
    
    @patch('app.translate.Client')
    @patch.dict('os.environ', {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_translate_with_api_success(self, mock_translate_client, client):
        """Test successful translation via API"""
        # Mock the Google Translate API response
        mock_client_instance = Mock()
        mock_client_instance.translate.return_value = {'translatedText': 'Hola mundo'}
        mock_translate_client.return_value = mock_client_instance
        
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['translated_text'] == 'Hola mundo'
        assert data['source_lang'] == 'en'
        assert data['target_lang'] == 'es'
        assert data['from_cache'] is False
    
    @patch('app.translate.Client')
    @patch.dict('os.environ', {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_translate_caching(self, mock_translate_client, client):
        """Test that translations are cached"""
        # Mock the Google Translate API response
        mock_client_instance = Mock()
        mock_client_instance.translate.return_value = {'translatedText': 'Hola mundo'}
        mock_translate_client.return_value = mock_client_instance
        
        # First request - should call API
        response1 = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1['from_cache'] is False
        
        # Second request - should use cache
        response2 = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2['from_cache'] is True
        assert data2['translated_text'] == 'Hola mundo'
        
        # API should only be called once
        assert mock_client_instance.translate.call_count == 1
    
    @patch('app.translate.Client')
    @patch.dict('os.environ', {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_translate_api_error(self, mock_translate_client, client):
        """Test handling of API errors"""
        # Mock API error
        mock_client_instance = Mock()
        mock_client_instance.translate.side_effect = Exception('API Error')
        mock_translate_client.return_value = mock_client_instance
        
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
    
    def test_translate_missing_api_key(self, client):
        """Test handling when API key is not configured"""
        response = client.post('/api/translate', json={
            'text': 'Hello world',
            'source_lang': 'en',
            'target_lang': 'es'
        })
        
        assert response.status_code == 503
        data = response.get_json()
        assert 'error' in data
        assert 'not configured' in data['error'].lower()
