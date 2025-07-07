import logging
import os
import json
from pocketflow import Node
from typing import Dict, Any
import httpx

logger = logging.getLogger(__name__)

class FirecrawlScrapeNode(Node):
    """
    Node to scrape a website using the Firecrawl API.
    Example:
        >>> node = FirecrawlScrapeNode()
        >>> shared = {"url": "https://www.example.com"}
        >>> node.prep(shared)
        # Returns url
        >>> node.exec("https://www.example.com")
        # Returns dict with markdown, json, etc.
    """
    def prep(self, shared: Dict[str, Any]):
        url = shared.get("url")
        logger.info(f"🔄 FirecrawlScrapeNode: prep - url='{url}'")
        return url

    def exec(self, url: str):
        logger.info(f"🔄 FirecrawlScrapeNode: exec - url='{url}'")
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            logger.error("❌ FirecrawlScrapeNode: FIRECRAWL_API_KEY not set in environment")
            return {"error": "FIRECRAWL_API_KEY not set"}
        if not url:
            logger.error("❌ FirecrawlScrapeNode: No URL provided")
            return {"error": "No URL provided"}
        endpoint = "https://api.firecrawl.dev/scrape"
        payload = {"url": url}
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            response = httpx.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ FirecrawlScrapeNode: Scrape successful, keys: {list(data.keys())}")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ FirecrawlScrapeNode: HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            logger.error(f"❌ FirecrawlScrapeNode: Request error: {e}")
            return {"error": f"Request error: {e}"}
        except Exception as e:
            logger.error(f"❌ FirecrawlScrapeNode: Scrape failed: {e}")
            return {"error": str(e)}

    def post(self, shared, prep_res, exec_res):
        shared["firecrawl_scrape_result"] = exec_res
        logger.info(f"💾 FirecrawlScrapeNode: post - Stored scrape result in shared['firecrawl_scrape_result']") 