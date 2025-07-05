import logging
import os
import urllib.request
import urllib.parse
import urllib.error
import json
from pocketflow import Node
from typing import Dict, Any

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
            # Convert payload to JSON bytes
            data = json.dumps(payload).encode('utf-8')
            
            # Create request
            request = urllib.request.Request(endpoint, data=data, headers=headers)
            request.get_method = lambda: 'POST'
            
            # Make request
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
                logger.info(f"✅ FirecrawlScrapeNode: Scrape successful, keys: {list(data.keys())}")
                return data
        except urllib.error.HTTPError as e:
            logger.error(f"❌ FirecrawlScrapeNode: HTTP error: {e}")
            return {"error": f"HTTP error: {e}"}
        except urllib.error.URLError as e:
            logger.error(f"❌ FirecrawlScrapeNode: URL error: {e}")
            return {"error": f"URL error: {e}"}
        except Exception as e:
            logger.error(f"❌ FirecrawlScrapeNode: Scrape failed: {e}")
            return {"error": str(e)}

    def post(self, shared, prep_res, exec_res):
        shared["firecrawl_scrape_result"] = exec_res
        logger.info(f"💾 FirecrawlScrapeNode: post - Stored scrape result in shared['firecrawl_scrape_result']") 