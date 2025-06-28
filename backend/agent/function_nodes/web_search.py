from pocketflow import Node
from typing import List, Dict, Any
import logging

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

logger = logging.getLogger(__name__)

class WebSearchNode(Node):
    """
    Node to perform web search using DuckDuckGo (duckduckgo_search).
    Example:
        >>> node = WebSearchNode()
        >>> shared = {"query": "best LLM frameworks", "num_results": 3}
        >>> node.prep(shared)
        # Returns (query, num_results)
        >>> node.exec(("best LLM frameworks", 3))
        # Returns list of search results
    """
    def prep(self, shared: Dict[str, Any]):
        query, num_results = shared.get("query"), shared.get("num_results", 5)
        logger.info(f"🔄 WebSearchNode: prep - query='{query}', num_results={num_results}")
        return query, num_results

    def exec(self, prep_res):
        if isinstance(prep_res, tuple):
            raise TypeError("Expected list")
        query = prep_res.get("query") if isinstance(prep_res, dict) else prep_res
        num_results = prep_res.get("num_results", 3) if isinstance(prep_res, dict) else 3
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query cannot be empty.")
        if not isinstance(num_results, int):
            raise TypeError("Number of results must be an integer.")
        if num_results <= 0:
            raise ValueError("Number of results must be positive.")
        if num_results > 100:
            raise ValueError("Number of results is too large or exceeds allowed limit.")
        if len(query) > 500:
            raise ValueError("Query is too long or exceeds allowed limit.")
        logger.info(f"🔄 WebSearchNode: exec - query='{query}', num_results={num_results}")
        if not query:
            logger.warning("⚠️ WebSearchNode: No query provided")
            return []
        if not DDGS_AVAILABLE:
            raise ImportError("duckduckgo_search is not installed. Please install it with 'pip install duckduckgo-search'.")
        try:
            logger.info("🔍 WebSearchNode: Performing web search via duckduckgo_search")
            results = DDGS().text(query, max_results=num_results)
            processed = []
            for r in results:
                processed.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "link": r.get("href", "")
                })
            logger.info(f"✅ WebSearchNode: Found {len(processed)} results")
            return processed
        except Exception as e:
            logger.error(f"❌ WebSearchNode: Search error: {e}")
            raise RuntimeError(f"Web search failed: {e}")

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 WebSearchNode: post - Storing {len(exec_res)} results in shared['search_results']")
        shared["search_results"] = exec_res
        return "default" 