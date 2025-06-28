"""
Security tests for the backend system.
Tests for API key handling, input validation, CORS, and other security concerns.
"""

import pytest
import os
import json
from unittest.mock import patch, Mock
from agent.utils.stream_llm import call_llm, call_gemini
from agent.utils.permission_manager import permission_manager
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.firecrawl_scrape import FirecrawlScrapeNode

class TestAPIKeySecurity:
    """Test API key security handling"""
    
    def test_openai_api_key_missing(self, monkeypatch):
        """Test that missing OpenAI API key raises proper error"""
        # Remove API key
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            call_llm("test prompt")
    
    def test_gemini_api_key_missing(self, monkeypatch):
        """Test that missing Gemini API key raises proper error"""
        # Remove API key
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
            call_gemini("test prompt")
    
    def test_firecrawl_api_key_missing(self, monkeypatch):
        """Test that missing Firecrawl API key raises proper error"""
        # Remove API key
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        
        node = FirecrawlScrapeNode()
        shared = {"url": "https://example.com"}
        
        with pytest.raises(ValueError, match="FIRECRAWL_API_KEY environment variable is required"):
            node.prep(shared)
    
    def test_api_key_not_exposed_in_logs(self, caplog, monkeypatch):
        """Test that API keys are not logged"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123456789")
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            try:
                call_llm("test prompt")
            except:
                pass
        
        # Check that API key is not in logs
        log_text = caplog.text
        assert "sk-test123456789" not in log_text
        assert "test123456789" not in log_text

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are handled safely"""
        malicious_input = "'; DROP TABLE users; --"
        
        # Test with web search node
        node = WebSearchNode()
        shared = {"query": malicious_input}
        
        # Should not crash or execute malicious code
        prep_res = node.prep(shared)
        assert prep_res == malicious_input  # Should be treated as plain text
    
    def test_xss_prevention(self):
        """Test that XSS attempts are handled safely"""
        malicious_input = "<script>alert('xss')</script>"
        
        node = WebSearchNode()
        shared = {"query": malicious_input}
        
        prep_res = node.prep(shared)
        assert prep_res == malicious_input  # Should be treated as plain text
    
    def test_url_validation(self):
        """Test URL validation in web scraping"""
        node = FirecrawlScrapeNode()
        
        # Valid URL
        shared = {"url": "https://example.com"}
        prep_res = node.prep(shared)
        assert prep_res["url"] == "https://example.com"
        
        # Invalid URL should raise error
        shared = {"url": "not-a-url"}
        with pytest.raises(ValueError, match="Invalid URL"):
            node.prep(shared)
    
    def test_input_length_limits(self):
        """Test input length limits"""
        node = WebSearchNode()
        
        # Very long input should be handled gracefully
        long_input = "a" * 10000
        shared = {"query": long_input}
        
        prep_res = node.prep(shared)
        assert len(prep_res) <= 10000  # Should have reasonable limits

class TestPermissionSecurity:
    """Test permission system security"""
    
    def test_permission_request_validation(self):
        """Test that permission requests are properly validated"""
        # Valid permission request
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Book flight for $500",
            amount=500
        )
        assert request_id is not None
        
        # Invalid amount should be rejected
        with pytest.raises(ValueError, match="Invalid amount"):
            permission_manager.create_permission_request(
                user_id="test_user",
                operation="payment",
                details="Book flight",
                amount=-100
            )
    
    def test_permission_authorization(self):
        """Test that permissions are properly checked"""
        # Create a permission request
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        # Should not be authorized initially
        assert not permission_manager.is_authorized(request_id)
        
        # Authorize the request
        permission_manager.authorize_request(request_id, "admin_user")
        
        # Should now be authorized
        assert permission_manager.is_authorized(request_id)
    
    def test_permission_request_isolation(self):
        """Test that permission requests are isolated between users"""
        # Create requests for different users
        request1 = permission_manager.create_permission_request(
            user_id="user1",
            operation="payment",
            details="Payment 1",
            amount=100
        )
        
        request2 = permission_manager.create_permission_request(
            user_id="user2", 
            operation="payment",
            details="Payment 2",
            amount=200
        )
        
        # Requests should be different
        assert request1 != request2
        
        # User should only see their own requests
        user1_requests = permission_manager.get_user_requests("user1")
        user2_requests = permission_manager.get_user_requests("user2")
        
        assert len(user1_requests) == 1
        assert len(user2_requests) == 1
        assert user1_requests[0].request_id == request1
        assert user2_requests[0].request_id == request2

class TestWebSocketSecurity:
    """Test WebSocket security"""
    
    @pytest.mark.asyncio
    async def test_websocket_message_validation(self, mock_websocket):
        """Test that WebSocket messages are properly validated"""
        # Valid message
        valid_message = json.dumps({
            "type": "user_message",
            "content": "Hello world"
        })
        
        # Should not raise exception
        await mock_websocket.send_text(valid_message)
        assert len(mock_websocket.messages) == 1
        
        # Invalid JSON should be handled
        with pytest.raises(json.JSONDecodeError):
            await mock_websocket.send_text("invalid json")
    
    @pytest.mark.asyncio
    async def test_websocket_connection_limits(self):
        """Test WebSocket connection limits"""
        # This would be implemented in the actual WebSocket handler
        # For now, we test the mock behavior
        from tests.conftest import MockWebSocket
        websocket = MockWebSocket()
        
        # Should be able to send messages when open
        await websocket.send_text('{"type": "test"}')
        assert len(websocket.messages) == 1
        
        # Should not be able to send when closed
        await websocket.close()
        with pytest.raises(Exception, match="WebSocket is closed"):
            await websocket.send_text('{"type": "test"}')

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_api_call_rate_limiting(self, monkeypatch):
        """Test that API calls are rate limited"""
        # Mock time to control rate limiting
        import time
        original_time = time.time
        current_time = 0
        
        def mock_time():
            return current_time
        
        monkeypatch.setattr(time, "time", mock_time)
        
        # This would test actual rate limiting implementation
        # For now, we verify the concept
        assert True  # Placeholder for actual rate limiting tests

class TestDataSanitization:
    """Test data sanitization"""
    
    def test_user_input_sanitization(self):
        """Test that user inputs are properly sanitized"""
        # Test various types of malicious input
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for malicious_input in malicious_inputs:
            # Should not crash or execute malicious code
            node = WebSearchNode()
            shared = {"query": malicious_input}
            
            prep_res = node.prep(shared)
            assert isinstance(prep_res, str)
            assert malicious_input in prep_res  # Should be treated as plain text
    
    def test_output_sanitization(self):
        """Test that outputs are properly sanitized"""
        # Test that outputs don't contain executable code
        node = WebSearchNode()
        shared = {"query": "test query"}
        
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        node.post(shared, prep_res, exec_res)
        
        # Check that results are properly structured
        assert "search_results" in shared
        results = shared["search_results"]
        
        if isinstance(results, list) and len(results) > 0:
            for result in results:
                # Should not contain executable code
                assert "<script>" not in str(result)
                assert "javascript:" not in str(result)

class TestErrorHandling:
    """Test error handling security"""
    
    def test_error_messages_dont_expose_sensitive_data(self, caplog):
        """Test that error messages don't expose sensitive information"""
        # Test with missing API key
        with pytest.raises(ValueError) as exc_info:
            call_llm("test prompt")
        
        error_message = str(exc_info.value)
        
        # Should not contain API keys or internal paths
        assert "sk-" not in error_message
        assert "api_key" not in error_message.lower()
        assert "/etc/" not in error_message
        assert "password" not in error_message.lower()
    
    def test_exception_handling_doesnt_leak_info(self):
        """Test that exception handling doesn't leak sensitive information"""
        # This would test actual exception handling in the application
        # For now, we verify the concept
        assert True  # Placeholder for actual exception handling tests 