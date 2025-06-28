"""
Pytest configuration file for the backend tests.
Provides fixtures and test utilities for all test modules.
"""

import sys
import os
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Add the current directory to Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockWebSocket:
    """Mock WebSocket for testing"""
    
    def __init__(self):
        self.messages = []
        self.closed = False
    
    async def send_text(self, message):
        """Mock send_text method"""
        if self.closed:
            raise Exception("WebSocket is closed")
        data = json.loads(message)
        self.messages.append(data)
    
    async def close(self):
        """Mock close method"""
        self.closed = True
    
    def get_messages(self):
        """Get all sent messages"""
        return self.messages
    
    def get_message_by_type(self, message_type: str):
        """Get messages by type"""
        return [msg for msg in self.messages if msg.get('type') == message_type]

@pytest.fixture
def mock_websocket():
    """Fixture for mock WebSocket"""
    return MockWebSocket()

@pytest.fixture
def sample_shared_store():
    """Fixture for sample shared store"""
    return {
        "websocket": MockWebSocket(),
        "conversation_history": [],
        "user_message": "Test message",
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }

@pytest.fixture
def mock_openai_client():
    """Fixture for mock OpenAI client"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Mock OpenAI response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client

@pytest.fixture
def mock_gemini_client():
    """Fixture for mock Gemini client"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = "Mock Gemini response"
    mock_client.generate_content.return_value = mock_response
    return mock_client

@pytest.fixture
def sample_flight_data():
    """Fixture for sample flight data"""
    return {
        "flight_search_results": [
            {
                "airline": "UA",
                "flight_number": "UA123",
                "departure_time": "14:30",
                "arrival_time": "18:45",
                "price": 850,
                "duration": "4h 15m",
                "stops": 0
            },
            {
                "airline": "AA",
                "flight_number": "AA456",
                "departure_time": "16:00",
                "arrival_time": "20:15",
                "price": 920,
                "duration": "4h 15m",
                "stops": 0
            }
        ],
        "user_preferences": {
            "departure_time": "afternoon",
            "max_price": 1000,
            "max_stops": 1
        }
    }

@pytest.fixture
def sample_web_search_results():
    """Fixture for sample web search results"""
    return [
        {
            "title": "Test Article 1",
            "snippet": "This is a test snippet for article 1",
            "link": "https://example1.com",
            "source": "example1.com"
        },
        {
            "title": "Test Article 2", 
            "snippet": "This is a test snippet for article 2",
            "link": "https://example2.com",
            "source": "example2.com"
        }
    ]

@pytest.fixture
def mock_requests_response():
    """Fixture for mock requests response"""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "success",
        "data": {"test": "data"}
    }
    mock_response.text = "Mock response text"
    return mock_response

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment with required environment variables"""
    # Set required environment variables for testing
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test_firecrawl_key")
    monkeypatch.setenv("DUCKDUCKGO_API_KEY", "test_duckduckgo_key")
    
    # Mock external API calls to avoid real network requests
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        mock_post.return_value = Mock(
            raise_for_status=Mock(),
            json=lambda: {"status": "success", "data": {}},
            text="Mock response"
        )
        mock_get.return_value = Mock(
            raise_for_status=Mock(),
            json=lambda: {"status": "success", "data": {}},
            text="Mock response"
        )
        yield

def assert_dict_structure(data: Dict[str, Any], expected_keys: list, optional_keys: list = None):
    """Helper function to assert dictionary structure"""
    optional_keys = optional_keys or []
    for key in expected_keys:
        assert key in data, f"Required key '{key}' not found in data"
    
    for key in optional_keys:
        if key in data:
            assert data[key] is not None, f"Optional key '{key}' is None when present"

def assert_list_structure(data: list, min_length: int = 0, item_validator=None):
    """Helper function to assert list structure"""
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) >= min_length, f"Expected at least {min_length} items, got {len(data)}"
    
    if item_validator:
        for i, item in enumerate(data):
            try:
                item_validator(item)
            except Exception as e:
                raise AssertionError(f"Item {i} failed validation: {e}")

def create_mock_llm_response(response_text: str):
    """Helper function to create mock LLM response"""
    return Mock(
        choices=[Mock(message=Mock(content=response_text))]
    ) 