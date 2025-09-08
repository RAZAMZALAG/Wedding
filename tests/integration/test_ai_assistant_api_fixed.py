"""
Integration tests for AI Assistant API endpoints
Tests the real AI assistant functionality including chat and catalog assistance
"""
import pytest
import json
from tests.conftest import integration_client


class TestAIAssistantAPI:
    """Test AI Assistant API integration"""
    
    def test_ai_endpoints_exist(self, client):
        """Test that AI endpoints are properly registered"""
        # Test specific AI endpoints that should exist
        endpoints_to_test = ['/api/ai/chat', '/api/ai/ask', '/api/ai/ask-image']
        
        for endpoint in endpoints_to_test:
            response = client.post(endpoint,
                                 data=json.dumps({'message': 'test'}),
                                 content_type='application/json')
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404
    
    def test_ai_chat_basic_message(self, client):
        """Test sending basic message to AI chat endpoint"""
        message_data = {
            'message': 'Hello, I need help with wedding planning',
            'language': 'en'
        }
        
        response = client.post('/api/ai/chat',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        # Should handle AI requests (may require auth or API key)
        assert response.status_code != 500
        assert response.status_code != 404
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'response' in data or 'message' in data
    
    def test_ai_chat_hebrew_message(self, client):
        """Test AI assistant with Hebrew message"""
        message_data = {
            'message': 'שלום, אני צריכה עזרה עם התכנון לחתונה',
            'language': 'he'
        }
        
        response = client.post('/api/ai/chat',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code != 500
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'response' in data or 'message' in data
    
    def test_ai_chat_empty_message(self, client):
        """Test AI assistant with empty message"""
        message_data = {
            'message': '',
            'language': 'en'
        }
        
        response = client.post('/api/ai/chat',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        # Should handle empty messages gracefully
        assert response.status_code in [400, 422, 200, 401]  # Various valid responses
    
    def test_ai_chat_missing_message(self, client):
        """Test AI assistant without message field"""
        message_data = {
            'language': 'en'
        }
        
        response = client.post('/api/ai/chat',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code in [400, 422, 401]
    
    def test_ai_chat_malformed_json(self, client):
        """Test AI assistant with malformed JSON"""
        response = client.post('/api/ai/chat',
                             data='{invalid json}',
                             content_type='application/json')
        
        assert response.status_code in [400, 422]
    
    def test_ai_chat_long_message(self, client):
        """Test AI assistant with very long message"""
        long_message = 'Help me plan my wedding ' * 100
        message_data = {
            'message': long_message,
            'language': 'en'
        }
        
        response = client.post('/api/ai/chat',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code != 500
    
    def test_ai_chat_special_characters(self, client):
        """Test AI assistant with special characters"""
        message_data = {
            'message': 'Wedding planning with symbols: @#$%^&*()_+{}[]|\\:";\'<>?,./~`',
            'language': 'en'
        }
        
        response = client.post('/api/ai/chat',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code != 500
    
    def test_ai_ask_endpoint(self, client):
        """Test AI ask endpoint specifically"""
        message_data = {
            'message': 'What wedding items do you recommend for outdoor ceremonies?',
            'language': 'en'
        }
        
        response = client.post('/api/ai/ask',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code != 500
        assert response.status_code != 404
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'response' in data or 'message' in data
    
    def test_ai_catalog_integration(self, client):
        """Test AI integration with catalog queries"""
        message_data = {
            'message': 'Show me wedding tables and chairs from your catalog',
            'language': 'en'
        }
        
        response = client.post('/api/ai/ask',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code != 500
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'response' in data or 'message' in data
            # Response should mention catalog items
            response_text = data.get('response', data.get('message', '')).lower()
            assert any(word in response_text for word in ['table', 'chair', 'catalog', 'item'])
    
    def test_ai_booking_assistance(self, client):
        """Test AI assistance with booking-related queries"""
        message_data = {
            'message': 'How do I book wedding equipment for my event?',
            'language': 'en'
        }
        
        response = client.post('/api/ai/ask',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        assert response.status_code != 500
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'response' in data or 'message' in data
    
    def test_ai_ask_image_endpoint(self, client):
        """Test AI ask-image endpoint (may require image data)"""
        # Test without image first (should handle gracefully)
        message_data = {
            'message': 'Analyze this wedding setup',
            'language': 'en'
        }
        
        response = client.post('/api/ai/ask-image',
                             data=json.dumps(message_data),
                             content_type='application/json')
        
        # Should not crash, may return error about missing image
        assert response.status_code != 500
        assert response.status_code != 404
        
        # Acceptable responses: 400 (bad request), 422 (validation), 401 (auth), 200 (success)
        assert response.status_code in [400, 401, 422, 200]
