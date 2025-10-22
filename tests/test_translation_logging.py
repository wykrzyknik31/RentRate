"""Unit tests for enhanced translation endpoint logging"""
import pytest
import sys
import os
from unittest.mock import patch, Mock
import logging

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


class TestTranslationLogging:
    """Test suite for enhanced translation logging"""
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_logs_request_details_on_success(self, mock_translate_client, client, caplog):
        """Test that successful translations log request details"""
        # Mock the Google Translate API response
        mock_client_instance = Mock()
        mock_client_instance.translate.return_value = {'translatedText': 'Hola mundo'}
        mock_translate_client.return_value = mock_client_instance
        
        # Set log level to capture info messages
        with caplog.at_level(logging.INFO):
            response = client.post('/api/translate', json={
                'text': 'Hello world',
                'source_lang': 'en',
                'target_lang': 'es'
            })
        
        assert response.status_code == 200
        
        # Check that request details were logged
        log_messages = [record.message for record in caplog.records]
        assert any('Translation request' in msg for msg in log_messages)
        assert any('source: en' in msg for msg in log_messages)
        assert any('target: es' in msg for msg in log_messages)
        assert any('Translation successful' in msg for msg in log_messages)
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_logs_error_details_on_api_failure(self, mock_translate_client, client, caplog):
        """Test that API errors log detailed information"""
        # Mock API error
        mock_client_instance = Mock()
        mock_client_instance.translate.side_effect = Exception('Invalid language code')
        mock_translate_client.return_value = mock_client_instance
        
        # Set log level to capture error messages
        with caplog.at_level(logging.ERROR):
            response = client.post('/api/translate', json={
                'text': 'Hello world',
                'source_lang': 'en',
                'target_lang': 'invalid'
            })
        
        assert response.status_code == 500
        
        # Check that error details were logged
        log_messages = [record.message for record in caplog.records]
        assert any('Translation error' in msg for msg in log_messages)
        assert any('Invalid language code' in msg for msg in log_messages)
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_logs_empty_translation_response(self, mock_translate_client, client, caplog):
        """Test that empty translation responses are logged"""
        # Mock API response with empty translated text
        mock_client_instance = Mock()
        mock_client_instance.translate.return_value = {'translatedText': ''}
        mock_translate_client.return_value = mock_client_instance
        
        # Set log level to capture error messages
        with caplog.at_level(logging.ERROR):
            response = client.post('/api/translate', json={
                'text': 'Hello world',
                'source_lang': 'en',
                'target_lang': 'es'
            })
        
        assert response.status_code == 500
        
        # Check that empty text error was logged
        log_messages = [record.message for record in caplog.records]
        assert any('returned empty text' in msg for msg in log_messages)
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_logs_api_exception_with_traceback(self, mock_translate_client, client, caplog):
        """Test that API exceptions log traceback"""
        # Mock API error
        mock_client_instance = Mock()
        mock_client_instance.translate.side_effect = Exception('API connection error')
        mock_translate_client.return_value = mock_client_instance
        
        # Set log level to capture error messages
        with caplog.at_level(logging.ERROR):
            response = client.post('/api/translate', json={
                'text': 'Hello world',
                'source_lang': 'en',
                'target_lang': 'es'
            })
        
        assert response.status_code == 500
        
        # Check that detailed error was logged
        log_messages = [record.message for record in caplog.records]
        assert any('Translation error' in msg for msg in log_messages)
        assert any('API connection error' in msg for msg in log_messages)
        assert any('Full traceback' in msg for msg in log_messages)
    
    @patch('app.translate.Client')
    @patch.dict(os.environ, {'GOOGLE_TRANSLATE_API_KEY': 'test-api-key'})
    def test_logs_general_exception_with_traceback(self, mock_translate_client, client, caplog):
        """Test that general exceptions log traceback"""
        # Mock client creation error
        mock_translate_client.side_effect = ValueError('Invalid API key format')
        
        # Set log level to capture error messages
        with caplog.at_level(logging.ERROR):
            response = client.post('/api/translate', json={
                'text': 'Hello world',
                'source_lang': 'en',
                'target_lang': 'es'
            })
        
        assert response.status_code == 500
        
        # Check that detailed error was logged
        log_messages = [record.message for record in caplog.records]
        assert any('Translation error' in msg for msg in log_messages)
        assert any('Full traceback' in msg for msg in log_messages)
