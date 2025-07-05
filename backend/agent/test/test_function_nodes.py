import os
import importlib
import importlib.util
import unittest
from unittest.mock import Mock, patch

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

class TestFunctionNodes(unittest.TestCase):
    """Test cases for all function nodes"""

    def setUp(self):
        """Set up test environment"""
        # Set dummy environment variables
        os.environ['FIRECRAWL_API_KEY'] = 'dummy-key'

    def test_firecrawl_scrape(self):
        """Test FirecrawlScrapeNode"""
        node = FirecrawlScrapeNode()
        shared = {"url": "https://example.com"}
        
        # Mock urllib.request.urlopen
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = b'{"markdown": "# Title", "json": {"title": "Title"}}'
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=None)
            mock_urlopen.return_value = mock_response
            
            prep_res = node.prep(shared)
            self.assertIsNotNone(prep_res)
            result = node.exec(prep_res)
            self.assertIn("markdown", result)
            node.post(shared, prep_res, result)
            self.assertIn("firecrawl_scrape_result", shared)

    def test_flight_booking(self):
        """Test FlightBookingNode"""
        node = FlightBookingNode()
        shared = {"selected_flight": {"airline": "UA", "flight_number": "UA123"}, "user_info": {"name": "Alice"}}
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        self.assertEqual(result["status"], "success")
        node.post(shared, prep_res, result)
        self.assertIn("booking_confirmation", shared)

    def test_preference_matcher(self):
        """Test PreferenceMatcherNode"""
        node = PreferenceMatcherNode()
        shared = {"flight_search_results": [{"departure_time": "afternoon"}, {"departure_time": "morning"}], "user_preferences": {"departure_time": "afternoon"}}
        prep_res = node.prep(shared)
        matched, summary = node.exec(prep_res)
        self.assertIsInstance(matched, list)
        self.assertIn("afternoon", summary)
        node.post(shared, prep_res, (matched, summary))
        self.assertIn("matched_flights", shared)

    def test_data_formatter(self):
        """Test DataFormatterNode"""
        node = DataFormatterNode()
        shared = {"workflow_results": {"a": 1, "b": 2}, "format_type": "comparison_table"}
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        self.assertIsInstance(result, str)
        node.post(shared, prep_res, result)

    def test_permission_request(self):
        """Test PermissionRequestNode"""
        node = PermissionRequestNode()
        shared = {"operation": "payment", "details": "Book flight"}
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Permission request created:"))
        node.post(shared, prep_res, result)

    def test_user_query(self):
        """Test UserQueryNode"""
        node = UserQueryNode()
        shared = {"question": "What is your name?"}
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        self.assertIn("Waiting for user response", result)
        node.post(shared, prep_res, result)
        self.assertIn("pending_user_question", shared)

    def test_result_summarizer(self):
        """Test ResultSummarizerNode"""
        node = ResultSummarizerNode()
        shared = {"user_message": "Book a flight", "cost_analysis": {"cheapest": {}, "best_value": {}, "recommendation": ""}}
        
        # Patch call_llm
        with patch("agent.function_nodes.result_summarizer.call_llm", return_value="Summary text"):
            prep_res = node.prep(shared)
            result = node.exec(prep_res)
            self.assertIsInstance(result, str)
            node.post(shared, prep_res, result)
            self.assertIn("result_summary", shared)

    def test_cost_analysis(self):
        """Test CostAnalysisNode"""
        node = CostAnalysisNode()
        shared = {"flight_search_results": [{"price": 100, "duration": "2h", "airline": "UA", "flight_number": "UA1", "departure_time": "afternoon"}]}
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        self.assertIn("cheapest", result)
        node.post(shared, prep_res, result)
        self.assertIn("cost_analysis", shared)

    def test_flight_search(self):
        """Test FlightSearchNode"""
        node = FlightSearchNode()
        shared = {"from": "LAX", "to": "PVG", "date": "2024-07-01"}
        prep_res = node.prep(shared)
        result = node.exec(prep_res)
        self.assertIsInstance(result, list)
        node.post(shared, prep_res, result)
        self.assertIn("flight_search_results", shared)

    def test_analyze_results(self):
        """Test AnalyzeResultsNode"""
        node = AnalyzeResultsNode()
        shared = {"query": "best LLM frameworks", "search_results": [{"title": "A"}]}
        
        # Patch call_llm
        with patch("agent.function_nodes.analyze_results.call_llm", return_value="summary: test\nkey_points: [a]\nfollow_up_queries: []"):
            prep_res = node.prep(shared)
            result = node.exec(prep_res)
            self.assertIsInstance(result, dict)
            node.post(shared, prep_res, result)
            self.assertIn("analysis", shared)

    def test_web_search(self):
        """Test web search with mocked DuckDuckGo to avoid rate limits in CI"""
        if importlib.util.find_spec("duckduckgo_search") is None:
            self.skipTest("duckduckgo_search not installed")
        
        # Import DDGS if available
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            self.skipTest("duckduckgo_search not available")
        
        # Mock DDGS at the module level
        with patch('duckduckgo_search.DDGS') as mock_ddgs_class:
            # Mock the search results
            mock_ddgs_instance = Mock()
            mock_ddgs_instance.text.return_value = [
                {
                    'title': 'OpenAI GPT-4 Overview',
                    'body': 'GPT-4 is a powerful language model by OpenAI',
                    'href': 'https://openai.com/gpt-4'
                },
                {
                    'title': 'GPT-4 Technical Details',
                    'body': 'Technical specifications and capabilities of GPT-4',
                    'href': 'https://openai.com/research/gpt-4'
                }
            ]
            mock_ddgs_class.return_value = mock_ddgs_instance
            
            # Ensure DDGS is available in the web_search module
            with patch('agent.function_nodes.web_search.DDGS_AVAILABLE', True):
                with patch('agent.function_nodes.web_search.DDGS', mock_ddgs_class):
                    node = WebSearchNode()
                    shared = {"query": "OpenAI GPT-4", "num_results": 2}
                    prep_res = node.prep(shared)
                    result = node.exec(prep_res)
                    
                    # Verify results structure
                    self.assertIsInstance(result, list)
                    self.assertEqual(len(result), 2)
                    for item in result:
                        self.assertIn("title", item)
                        self.assertIn("snippet", item)
                        self.assertIn("link", item)
                    
                    # Verify specific content
                    self.assertEqual(result[0]["title"], "OpenAI GPT-4 Overview")
                    self.assertEqual(result[0]["snippet"], "GPT-4 is a powerful language model by OpenAI")
                    self.assertEqual(result[0]["link"], "https://openai.com/gpt-4")
                    
                    node.post(shared, prep_res, result)
                    self.assertIn("search_results", shared)

if __name__ == '__main__':
    unittest.main() 