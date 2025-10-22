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
    
    @patch('app.requests.post')
    def test_logs_request_details_on_success(self, mock_post, client, caplog):
        """Test that successful translations log request details"""
        # Mock the LibreTranslate API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'translatedText': 'Hola mundo'}
        mock_post.return_value = mock_response
        
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
    
    @patch('app.requests.post')
    def test_logs_error_details_on_api_failure(self, mock_post, client, caplog):
        """Test that API errors log detailed information"""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request: Invalid language code'
        mock_post.return_value = mock_response
        
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
        assert any('Translation API error' in msg for msg in log_messages)
        assert any('Status: 400' in msg for msg in log_messages)
        assert any('Bad Request' in msg for msg in log_messages)
    
    @patch('app.requests.post')
    def test_logs_empty_translation_response(self, mock_post, client, caplog):
        """Test that empty translation responses are logged"""
        # Mock API response with empty translated text
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'translatedText': ''}
        mock_post.return_value = mock_response
        
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
    
    @patch('app.requests.post')
    def test_logs_request_exception_with_traceback(self, mock_post, client, caplog):
        """Test that request exceptions log traceback"""
        # Mock network error
        from requests.exceptions import ConnectionError
        mock_post.side_effect = ConnectionError('Connection refused')
        
        # Set log level to capture error messages
        with caplog.at_level(logging.ERROR):
            response = client.post('/api/translate', json={
                'text': 'Hello world',
                'source_lang': 'en',
                'target_lang': 'es'
            })
        
        assert response.status_code == 503
        
        # Check that detailed error was logged
        log_messages = [record.message for record in caplog.records]
        assert any('Translation service error' in msg for msg in log_messages)
        assert any('Connection refused' in msg for msg in log_messages)
        assert any('Full traceback' in msg for msg in log_messages)
        assert any('Request URL' in msg for msg in log_messages)
        assert any('Request payload' in msg for msg in log_messages)
    
    @patch('app.requests.post')
    def test_logs_general_exception_with_traceback(self, mock_post, client, caplog):
        """Test that general exceptions log traceback"""
        # Mock general error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_post.return_value = mock_response
        
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
