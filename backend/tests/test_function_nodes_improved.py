"""
Improved tests for function nodes with better coverage and assertions.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from agent.function_nodes.firecrawl_scrape import FirecrawlScrapeNode
from agent.function_nodes.flight_booking import FlightBookingNode
from agent.function_nodes.preference_matcher import PreferenceMatcherNode
from agent.function_nodes.data_formatter import DataFormatterNode
from agent.function_nodes.permission_request import PermissionRequestNode
from agent.function_nodes.user_query import UserQueryNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode
from agent.function_nodes.cost_analysis import CostAnalysisNode
from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.analyze_results import AnalyzeResultsNode
from agent.function_nodes.web_search import WebSearchNode

class TestFirecrawlScrapeNode:
    """Test FirecrawlScrapeNode functionality"""
    
    def test_valid_url_processing(self, mock_requests_response, monkeypatch):
        """Test processing of valid URLs"""
        node = FirecrawlScrapeNode()
        shared = {"url": "https://example.com"}
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "markdown": "# Test Title\n\nTest content",
            "json": {"title": "Test Title", "content": "Test content"}
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.post', return_value=mock_response):
            prep_res = node.prep(shared)
            result = node.exec(prep_res)
            action = node.post(shared, prep_res, result)
        
        # Verify results
        assert "firecrawl_scrape_result" in shared
        assert "markdown" in result
        assert "json" in result
        assert result["markdown"].startswith("# Test Title")
        assert action == "default"
    
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        node = FirecrawlScrapeNode()
        
        # Test with invalid URL
        shared = {"url": "not-a-valid-url"}
        
        with pytest.raises(ValueError, match="Invalid URL"):
            node.prep(shared)
    
    def test_api_error_handling(self, monkeypatch):
        """Test handling of API errors"""
        node = FirecrawlScrapeNode()
        shared = {"url": "https://example.com"}
        
        # Mock API error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        
        with patch('requests.post', return_value=mock_response):
            prep_res = node.prep(shared)
            
            with pytest.raises(Exception, match="API Error"):
                node.exec(prep_res)

class TestFlightBookingNode:
    """Test FlightBookingNode functionality"""
    
    def test_successful_booking(self, sample_flight_data):
        """Test successful flight booking"""
        node = FlightBookingNode()
        shared = {
            "selected_flight": {
                "airline": "UA",
                "flight_number": "UA123",
                "price": 500,
                "departure_time": "14:30"
            },
            "user_info": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify booking results
        assert "booking_confirmation" in shared
        assert result["status"] == "success"
        assert "booking_id" in result
        assert action == "default"
    
    def test_missing_flight_data(self):
        """Test handling of missing flight data"""
        node = FlightBookingNode()
        shared = {"user_info": {"name": "John Doe"}}
        
        with pytest.raises(KeyError, match="selected_flight"):
            node.prep(shared)
    
    def test_missing_user_info(self):
        """Test handling of missing user info"""
        node = FlightBookingNode()
        shared = {"selected_flight": {"airline": "UA", "flight_number": "UA123"}}
        
        with pytest.raises(KeyError, match="user_info"):
            node.prep(shared)

class TestPreferenceMatcherNode:
    """Test PreferenceMatcherNode functionality"""
    
    def test_preference_matching(self, sample_flight_data):
        """Test matching flights to user preferences"""
        node = PreferenceMatcherNode()
        shared = {
            "flight_search_results": sample_flight_data["flight_search_results"],
            "user_preferences": sample_flight_data["user_preferences"]
        }
        
        prep_res = node.prep(shared)
        matched, summary = node.exec(prep_res)
        action = node.post(shared, prep_res, (matched, summary))
        
        # Verify matching results
        assert "matched_flights" in shared
        assert isinstance(matched, list)
        assert isinstance(summary, str)
        assert "afternoon" in summary.lower()
        assert action == "default"
    
    def test_no_matches(self):
        """Test handling when no flights match preferences"""
        node = PreferenceMatcherNode()
        shared = {
            "flight_search_results": [
                {"departure_time": "morning", "price": 400}
            ],
            "user_preferences": {"departure_time": "afternoon"}
        }
        
        prep_res = node.prep(shared)
        matched, summary = node.exec(prep_res)
        node.post(shared, prep_res, (matched, summary))
        
        # Should handle no matches gracefully
        assert len(matched) == 0
        assert "no matches" in summary.lower() or "no flights" in summary.lower()
    
    def test_empty_results(self):
        """Test handling of empty search results"""
        node = PreferenceMatcherNode()
        shared = {
            "flight_search_results": [],
            "user_preferences": {"departure_time": "afternoon"}
        }
        
        prep_res = node.prep(shared)
        matched, summary = node.exec(prep_res)
        node.post(shared, prep_res, (matched, summary))
        
        # Should handle empty results gracefully
        assert len(matched) == 0
        assert "no results" in summary.lower() or "empty" in summary.lower()

class TestDataFormatterNode:
    """Test DataFormatterNode functionality"""
    
    def test_comparison_table_formatting(self):
        """Test formatting data as comparison table"""
        node = DataFormatterNode()
        shared = {
            "workflow_results": {
                "option1": {"price": 500, "duration": "2h"},
                "option2": {"price": 600, "duration": "1.5h"}
            },
            "format_type": "comparison_table"
        }
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify formatting results
        assert isinstance(result, str)
        assert "option1" in result
        assert "option2" in result
        assert "500" in result
        assert "600" in result
        assert action == "default"
    
    def test_json_formatting(self):
        """Test formatting data as JSON"""
        node = DataFormatterNode()
        shared = {
            "workflow_results": {"key": "value"},
            "format_type": "json"
        }
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        node.post(shared, prep_res, result)
        
        # Verify JSON formatting
        assert isinstance(result, str)
        parsed_json = json.loads(result)
        assert parsed_json["key"] == "value"
    
    def test_invalid_format_type(self):
        """Test handling of invalid format type"""
        node = DataFormatterNode()
        shared = {
            "workflow_results": {"key": "value"},
            "format_type": "invalid_format"
        }
        
        prep_res = node.prep(shared)
        
        with pytest.raises(ValueError, match="Unsupported format type"):
            node.exec(prep_res)

class TestPermissionRequestNode:
    """Test PermissionRequestNode functionality"""
    
    def test_permission_request_creation(self):
        """Test creating permission requests"""
        node = PermissionRequestNode()
        shared = {
            "operation": "payment",
            "details": "Book flight for $500",
            "amount": 500
        }
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify permission request
        assert "permission_request" in shared
        assert result.startswith("Permission request created:")
        assert "request_id" in result
        assert action == "wait_for_permission"
    
    def test_invalid_amount(self):
        """Test handling of invalid amounts"""
        node = PermissionRequestNode()
        shared = {
            "operation": "payment",
            "details": "Book flight",
            "amount": -100
        }
        
        prep_res = node.prep(shared)
        
        with pytest.raises(ValueError, match="Invalid amount"):
            node.exec(prep_res)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        node = PermissionRequestNode()
        shared = {"operation": "payment"}  # Missing details and amount
        
        with pytest.raises(KeyError, match="details"):
            node.prep(shared)

class TestUserQueryNode:
    """Test UserQueryNode functionality"""
    
    def test_user_query_handling(self):
        """Test handling of user queries"""
        node = UserQueryNode()
        shared = {"question": "What is your preferred departure time?"}
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify user query handling
        assert "pending_user_question" in shared
        assert "Waiting for user response" in result
        assert action == "wait_for_user"
    
    def test_empty_question(self):
        """Test handling of empty questions"""
        node = UserQueryNode()
        shared = {"question": ""}
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        node.post(shared, prep_res, result)
        
        # Should handle empty question gracefully
        assert "pending_user_question" in shared
        assert "Please provide a question" in result

class TestResultSummarizerNode:
    """Test ResultSummarizerNode functionality"""
    
    def test_result_summarization(self, monkeypatch):
        """Test summarizing workflow results"""
        node = ResultSummarizerNode()
        shared = {
            "user_message": "Book a flight",
            "cost_analysis": {
                "cheapest": {"price": 400, "airline": "UA"},
                "best_value": {"price": 500, "airline": "AA"},
                "recommendation": "Choose UA for best price"
            }
        }
        
        # Mock LLM response
        mock_llm_response = "Based on the analysis, I recommend choosing UA for the best price."
        monkeypatch.setattr("agent.function_nodes.result_summarizer.call_llm", 
                           lambda *args, **kwargs: mock_llm_response)
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify summarization
        assert "result_summary" in shared
        assert isinstance(result, str)
        assert "UA" in result
        assert action == "default"
    
    def test_empty_results_summarization(self, monkeypatch):
        """Test summarizing empty results"""
        node = ResultSummarizerNode()
        shared = {
            "user_message": "Book a flight",
            "cost_analysis": {}
        }
        
        # Mock LLM response for empty results
        mock_llm_response = "No results found for your query."
        monkeypatch.setattr("agent.function_nodes.result_summarizer.call_llm", 
                           lambda *args, **kwargs: mock_llm_response)
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        node.post(shared, prep_res, result)
        
        # Should handle empty results gracefully
        assert "result_summary" in shared
        assert "No results" in result

class TestCostAnalysisNode:
    """Test CostAnalysisNode functionality"""
    
    def test_cost_analysis(self, sample_flight_data):
        """Test analyzing flight costs"""
        node = CostAnalysisNode()
        shared = {"flight_search_results": sample_flight_data["flight_search_results"]}
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify cost analysis
        assert "cost_analysis" in shared
        assert "cheapest" in result
        assert "best_value" in result
        assert "recommendation" in result
        assert action == "default"
    
    def test_single_flight_analysis(self):
        """Test analyzing single flight"""
        node = CostAnalysisNode()
        shared = {
            "flight_search_results": [
                {"price": 500, "duration": "2h", "airline": "UA", "flight_number": "UA123"}
            ]
        }
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        node.post(shared, prep_res, result)
        
        # Should handle single flight
        assert result["cheapest"]["price"] == 500
        assert result["best_value"]["price"] == 500
    
    def test_empty_flight_results(self):
        """Test handling of empty flight results"""
        node = CostAnalysisNode()
        shared = {"flight_search_results": []}
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        node.post(shared, prep_res, result)
        
        # Should handle empty results gracefully
        assert result["cheapest"] is None
        assert result["best_value"] is None
        assert "No flights found" in result["recommendation"]

class TestFlightSearchNode:
    """Test FlightSearchNode functionality"""
    
    def test_flight_search(self):
        """Test searching for flights"""
        node = FlightSearchNode()
        shared = {"from": "LAX", "to": "JFK", "date": "2024-07-01"}
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify flight search
        assert "flight_search_results" in shared
        assert isinstance(result, list)
        assert action == "default"
    
    def test_missing_search_parameters(self):
        """Test handling of missing search parameters"""
        node = FlightSearchNode()
        shared = {"from": "LAX"}  # Missing 'to' and 'date'
        
        with pytest.raises(KeyError, match="to"):
            node.prep(shared)
    
    def test_invalid_date_format(self):
        """Test handling of invalid date format"""
        node = FlightSearchNode()
        shared = {"from": "LAX", "to": "JFK", "date": "invalid-date"}
        
        prep_res = node.prep(shared)
        
        with pytest.raises(ValueError, match="Invalid date format"):
            node.exec(prep_res)

class TestAnalyzeResultsNode:
    """Test AnalyzeResultsNode functionality"""
    
    def test_results_analysis(self, monkeypatch):
        """Test analyzing search results"""
        node = AnalyzeResultsNode()
        shared = {
            "query": "best LLM frameworks",
            "search_results": [
                {"title": "Top 10 LLM Frameworks", "snippet": "Comprehensive guide..."},
                {"title": "LLM Framework Comparison", "snippet": "Detailed analysis..."}
            ]
        }
        
        # Mock LLM response
        mock_response = """summary: Analysis of LLM frameworks
key_points: [Framework comparison, Performance metrics, Use cases]
follow_up_queries: [What are the latest trends?, How to choose the right framework?]"""
        
        monkeypatch.setattr("agent.function_nodes.analyze_results.call_llm", 
                           lambda *args, **kwargs: mock_response)
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify analysis
        assert "analysis" in shared
        assert isinstance(result, dict)
        assert "summary" in result
        assert "key_points" in result
        assert "follow_up_queries" in result
        assert action == "default"
    
    def test_empty_results_analysis(self, monkeypatch):
        """Test analyzing empty search results"""
        node = AnalyzeResultsNode()
        shared = {
            "query": "test query",
            "search_results": []
        }
        
        # Mock LLM response for empty results
        mock_response = "summary: No results found\nkey_points: []\nfollow_up_queries: []"
        monkeypatch.setattr("agent.function_nodes.analyze_results.call_llm", 
                           lambda *args, **kwargs: mock_response)
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        node.post(shared, prep_res, result)
        
        # Should handle empty results gracefully
        assert result["summary"] == "No results found"
        assert len(result["key_points"]) == 0
        assert len(result["follow_up_queries"]) == 0

class TestWebSearchNode:
    """Test WebSearchNode functionality"""
    
    def test_web_search(self, sample_web_search_results, monkeypatch):
        """Test web search functionality"""
        node = WebSearchNode()
        shared = {"query": "OpenAI GPT-4", "num_results": 2}
        
        # Mock search results
        monkeypatch.setattr("agent.function_nodes.web_search.search_web", 
                           lambda *args, **kwargs: sample_web_search_results)
        
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        action = node.post(shared, prep_res, result)
        
        # Verify search results
        assert "search_results" in shared
        assert isinstance(result, list)
        assert len(result) == 2
        
        for item in result:
            assert "title" in item
            assert "snippet" in item
            assert "link" in item
        
        assert action == "default"
    
    def test_empty_query(self):
        """Test handling of empty query"""
        node = WebSearchNode()
        shared = {"query": "", "num_results": 5}
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            node.prep(shared)
    
    def test_invalid_num_results(self):
        """Test handling of invalid number of results"""
        node = WebSearchNode()
        shared = {"query": "test query", "num_results": -1}
        
        with pytest.raises(ValueError, match="Number of results must be positive"):
            node.prep(shared)
    
    def test_search_error_handling(self, monkeypatch):
        """Test handling of search errors"""
        node = WebSearchNode()
        shared = {"query": "test query", "num_results": 5}
        
        # Mock search error
        monkeypatch.setattr("agent.function_nodes.web_search.search_web", 
                           lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Search failed")))
        
        prep_res = node.prep(shared)
        
        with pytest.raises(Exception, match="Search failed"):
            node.exec(prep_res) 