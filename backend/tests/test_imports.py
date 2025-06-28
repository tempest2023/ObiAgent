#!/usr/bin/env python3
"""
Test script to verify that all function node imports work correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all function nodes can be imported successfully."""
    try:
        from agent.function_nodes.firecrawl_scrape import FirecrawlScrapeNode
        print("✅ FirecrawlScrapeNode imported successfully")
        
        from agent.function_nodes.flight_booking import FlightBookingNode
        print("✅ FlightBookingNode imported successfully")
        
        from agent.function_nodes.preference_matcher import PreferenceMatcherNode
        print("✅ PreferenceMatcherNode imported successfully")
        
        from agent.function_nodes.data_formatter import DataFormatterNode
        print("✅ DataFormatterNode imported successfully")
        
        from agent.function_nodes.permission_request import PermissionRequestNode
        print("✅ PermissionRequestNode imported successfully")
        
        from agent.function_nodes.user_query import UserQueryNode
        print("✅ UserQueryNode imported successfully")
        
        from agent.function_nodes.result_summarizer import ResultSummarizerNode
        print("✅ ResultSummarizerNode imported successfully")
        
        from agent.function_nodes.cost_analysis import CostAnalysisNode
        print("✅ CostAnalysisNode imported successfully")
        
        from agent.function_nodes.flight_search import FlightSearchNode
        print("✅ FlightSearchNode imported successfully")
        
        from agent.function_nodes.analyze_results import AnalyzeResultsNode
        print("✅ AnalyzeResultsNode imported successfully")
        
        from agent.function_nodes.web_search import WebSearchNode
        print("✅ WebSearchNode imported successfully")
        
        print("\n🎉 All imports successful!")
        assert True, "All imports completed successfully"
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        assert False, f"Import failed: {e}"
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        assert False, f"Unexpected error: {e}"

if __name__ == "__main__":
    test_imports()
