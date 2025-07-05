import os
import pytest
import importlib

from agent.function_nodes.firecrawl_scrape import FirecrawlScrapeNode
from agent.function_nodes.data_formatter import DataFormatterNode
from agent.function_nodes.permission_request import PermissionRequestNode
from agent.function_nodes.user_query import UserQueryNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode
from agent.function_nodes.analyze_results import AnalyzeResultsNode
from agent.function_nodes.web_search import WebSearchNode

# --- FirecrawlScrapeNode ---
def test_firecrawl_scrape(monkeypatch):
    node = FirecrawlScrapeNode()
    shared = {"url": "https://example.com"}
    monkeypatch.setenv("FIRECRAWL_API_KEY", "dummy-key")
    # Mock requests.post
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


# --- DataFormatterNode ---
def test_data_formatter():
    node = DataFormatterNode()
    shared = {"workflow_results": {"a": 1, "b": 2}, "format_type": "comparison_table"}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, str)
    node.post(shared, prep_res, result)

# --- PermissionRequestNode ---
def test_permission_request_infer_type():
    node = PermissionRequestNode()
    shared = {"operation": "access database", "details": "Read user table"}
    prep_res = node.prep(shared)
    assert prep_res[0] == "data_access"  # inferred type
    result = node.exec(prep_res)
    assert isinstance(result, str)
    assert "Permission required: [DATA_ACCESS]" in result
    assert "Request ID:" in result
    node.post(shared, prep_res, result)
    assert "pending_permission_request" in shared
    assert shared["waiting_for_permission"] is True

def test_permission_request_explicit_type():
    node = PermissionRequestNode()
    shared = {"operation": "external API call", "details": "Send data to third-party service", "permission_type": "external_api"}
    prep_res = node.prep(shared)
    assert prep_res[0] == "external_api"  # explicit type
    result = node.exec(prep_res)
    assert "Permission required: [EXTERNAL_API]" in result
    assert "Request ID:" in result
    node.post(shared, prep_res, result)
    assert "pending_permission_request" in shared
    assert shared["waiting_for_permission"] is True

# --- UserQueryNode ---
def test_user_query():
    node = UserQueryNode()
    shared = {"question": "What is your name?"}
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert "Waiting for user response" in result
    node.post(shared, prep_res, result)
    assert "pending_user_question" in shared

# --- ResultSummarizerNode ---
def test_result_summarizer(monkeypatch):
    node = ResultSummarizerNode()
    shared = {"user_message": "Book a flight"}
    # Patch call_llm
    monkeypatch.setattr("agent.function_nodes.result_summarizer.call_llm", lambda *a, **k: "Summary text")
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, str)
    node.post(shared, prep_res, result)
    assert "result_summary" in shared

# --- AnalyzeResultsNode ---
def test_analyze_results(monkeypatch):
    node = AnalyzeResultsNode()
    shared = {"query": "best LLM frameworks", "search_results": [{"title": "A"}]}
    # Patch call_llm
    monkeypatch.setattr("agent.function_nodes.analyze_results.call_llm", lambda *a, **k: """summary: test\nkey_points: [a]\nfollow_up_queries: []""")
    prep_res = node.prep(shared)
    result = node.exec(prep_res)
    assert isinstance(result, dict)
    node.post(shared, prep_res, result)
    assert "analysis" in shared

# --- WebSearchNode ---
def test_web_search(monkeypatch):
    if importlib.util.find_spec("duckduckgo_search") is None:
        pytest.skip("duckduckgo_search not installed")
    
    # Mock DDGS to avoid rate limiting issues
    class MockDDGS:
        def text(self, query, max_results=None):
            return [
                {"title": "OpenAI GPT-4", "body": "GPT-4 is a large language model", "href": "https://openai.com/gpt-4"},
                {"title": "GPT-4 Features", "body": "Advanced AI capabilities", "href": "https://example.com/gpt4"}
            ][:max_results]
    
    # Patch the DDGS import in web_search module
    import agent.function_nodes.web_search
    monkeypatch.setattr(agent.function_nodes.web_search, "DDGS", MockDDGS)
    
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