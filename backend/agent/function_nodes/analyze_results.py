from pocketflow import Node
from typing import Dict, List, Any
from agent.utils.stream_llm import call_llm
import yaml
import logging

logger = logging.getLogger(__name__)

class AnalyzeResultsNode(Node):
    """
    Node to analyze search results using LLM.
    Example:
        >>> node = AnalyzeResultsNode()
        >>> shared = {"query": "best LLM frameworks", "search_results": [{...}]}
        >>> node.prep(shared)
        # Returns (query, search_results)
        >>> node.exec(("best LLM frameworks", [{...}]))
        # Returns dict with summary, key_points, follow_up_queries
    """
    def prep(self, shared: Dict[str, Any]):
        query, results = shared.get("query"), shared.get("search_results", [])
        logger.info(f"🔄 AnalyzeResultsNode: prep - query='{query}', results_count={len(results)}")
        return query, results

    def exec(self, inputs):
        query, results = inputs
        logger.info(f"🔄 AnalyzeResultsNode: exec - query='{query}', results_count={len(results)}")
        if not results:
            logger.warning("⚠️ AnalyzeResultsNode: No search results to analyze")
            return {
                "summary": "No search results to analyze",
                "key_points": [],
                "follow_up_queries": []
            }
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(f"""
Result {i}:
Title: {result.get('title', '')}
Snippet: {result.get('snippet', '')}
URL: {result.get('link', '')}
""")
        prompt = f"""
Analyze these search results for the query: \"{query}\"

{chr(10).join(formatted_results)}

Please provide:
1. A concise summary of the findings (2-3 sentences)
2. Key points or facts (up to 5 bullet points)
3. Suggested follow-up queries (2-3)

Output in YAML format:
```yaml
summary: >
    brief summary here
key_points:
    - point 1
    - point 2
follow_up_queries:
    - query 1
    - query 2
```
"""
        try:
            logger.info("🤖 AnalyzeResultsNode: Calling LLM for analysis")
            response = call_llm(prompt)
            yaml_str = response.split("```yaml")[1].split("```", 1)[0].strip()
            analysis = yaml.safe_load(yaml_str)
            logger.info("✅ AnalyzeResultsNode: Successfully parsed LLM response")
            assert "summary" in analysis
            assert "key_points" in analysis
            assert "follow_up_queries" in analysis
            assert isinstance(analysis["key_points"], list)
            assert isinstance(analysis["follow_up_queries"], list)
            return analysis
        except Exception as e:
            logger.error(f"❌ AnalyzeResultsNode: Error analyzing results: {e}")
            return {
                "summary": f"Error analyzing results: {str(e)}",
                "key_points": [],
                "follow_up_queries": []
            }

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 AnalyzeResultsNode: post - Storing analysis in shared['analysis']")
        shared["analysis"] = exec_res
        return "default" 