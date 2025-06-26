from pocketflow import Node
from typing import List, Dict, Any
import os
import logging

try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

class WebSearchNode(Node):
    """
    Node to perform web search using SerpAPI (or mock if unavailable).
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

    def exec(self, inputs):
        query, num_results = inputs
        logger.info(f"🔄 WebSearchNode: exec - query='{query}', num_results={num_results}")
        if not query:
            logger.warning("⚠️ WebSearchNode: No query provided")
            return []
        if SERPAPI_AVAILABLE:
            api_key = os.getenv("SERPAPI_API_KEY")
            if not api_key:
                logger.warning("⚠️ WebSearchNode: No SERPAPI_API_KEY found")
                return [{"title": "No API key", "snippet": "Set SERPAPI_API_KEY env var.", "link": ""}]
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": num_results
            }
            try:
                logger.info("🔍 WebSearchNode: Performing real web search via SerpAPI")
                search = GoogleSearch(params)
                results = search.get_dict()
                if "organic_results" not in results:
                    logger.warning("⚠️ WebSearchNode: No organic_results in SerpAPI response")
                    return []
                processed = []
                for result in results["organic_results"][:num_results]:
                    processed.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", "")
                    })
                logger.info(f"✅ WebSearchNode: Found {len(processed)} results")
                return processed
            except Exception as e:
                logger.error(f"❌ WebSearchNode: Search error: {e}")
                return [{"title": "Search error", "snippet": str(e), "link": ""}]
        else:
            logger.info("🔧 WebSearchNode: Returning mock search results")
            return [
                {"title": f"Result {i+1} for {query}", "snippet": f"Snippet {i+1}", "link": f"https://example.com/{i+1}"}
                for i in range(num_results)
            ]

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 WebSearchNode: post - Storing {len(exec_res)} results in shared['search_results']")
        shared["search_results"] = exec_res
        return "default" 