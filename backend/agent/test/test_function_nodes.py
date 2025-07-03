import os
import pytest
import importlib
import json

from agent.function_nodes.permission_request import PermissionRequestNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode
from agent.function_nodes.user_query import UserQueryNode
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.analyze_results import AnalyzeResultsNode
from agent.function_nodes.cost_analysis import CostAnalysisNode
from agent.function_nodes.data_formatter import DataFormatterNode
from agent.function_nodes.firecrawl_scrape import FirecrawlScrapeNode


# --- PermissionRequestNode ---
def test_permission_request():
    node = PermissionRequestNode()
    shared = {"operation": "payment", "details": "Book flight"}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, str)
    assert result.startswith("Permission request created:")
    node.post(shared, prep_res, result)

# --- ResultSummarizerNode ---
def test_result_summarizer(monkeypatch):
    node = ResultSummarizerNode()
    shared = {"user_message": "Book a flight", "cost_analysis": {"cheapest": {}, "best_value": {}, "recommendation": ""}}
    monkeypatch.setattr("agent.function_nodes.result_summarizer.call_llm", lambda *a, **k: "Summary text")
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, str)
    node.post(shared, prep_res, result)
    assert "result_summary" in shared

# --- UserQueryNode ---
def test_user_query():
    node = UserQueryNode()
    shared = {"question": "What is your name?"}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert "Waiting for user response" in result
    node.post(shared, prep_res, result)
    assert "pending_user_question" in shared

# --- WebSearchNode ---
def test_web_search():
    if importlib.util.find_spec("duckduckgo_search") is None:
        pytest.skip("duckduckgo_search not installed")
    node = WebSearchNode()
    shared = {"query": "OpenAI GPT-4", "num_results": 2}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, list)
    assert len(result) > 0
    for item in result:
        assert "title" in item
        assert "snippet" in item
        assert "link" in item
    node.post(shared, prep_res, result)
    assert "search_results" in shared

# --- AnalyzeResultsNode ---
def test_analyze_results(monkeypatch):
    node = AnalyzeResultsNode()
    shared = {"query": "best LLM frameworks", "search_results": [{"title": "A"}]}
    monkeypatch.setattr("agent.function_nodes.analyze_results.call_llm", lambda *a, **k: """summary: test\nkey_points: [a]\nfollow_up_queries: []""")
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, dict)
    node.post(shared, prep_res, result)
    assert "analysis" in shared

# --- CostAnalysisNode ---
def test_cost_analysis():
    node = CostAnalysisNode()
    shared = {"flight_search_results": [{"price": 100, "duration": "2h", "airline": "UA", "flight_number": "UA1", "departure_time": "afternoon"}]}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert "cheapest" in result
    node.post(shared, prep_res, result)
    assert "cost_analysis" in shared

# --- DataFormatterNode ---
def test_data_formatter():
    node = DataFormatterNode()
    shared = {"workflow_results": {"a": 1, "b": 2}, "format_type": "comparison_table"}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, str)
    node.post(shared, prep_res, result)

# --- FirecrawlScrapeNode ---
def test_firecrawl_scrape(monkeypatch):
    node = FirecrawlScrapeNode()
    shared = {"url": "https://example.com"}
    monkeypatch.setenv("FIRECRAWL_API_KEY", "dummy-key")
    import requests
    class DummyResp:
        def raise_for_status(self): pass
        def json(self): return {"markdown": "# Title", "json": {"title": "Title"}}
    monkeypatch.setattr(requests, "post", lambda *a, **k: DummyResp())
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert "markdown" in result
    node.post(shared, prep_res, result)
    assert "firecrawl_scrape_result" in shared 