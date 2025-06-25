from pocketflow import Node
from typing import Dict, Any
from agent.utils.stream_llm import call_llm
import logging

logger = logging.getLogger(__name__)

class ResultSummarizerNode(Node):
    """
    Node to summarize results and provide recommendations using LLM.
    Example:
        >>> node = ResultSummarizerNode()
        >>> shared = {"user_message": "Book a flight...", "cost_analysis": {...}}
        >>> node.prep(shared)
        # Returns (user_message, cost_analysis)
        >>> node.exec(("Book a flight...", {...}))
        # Returns summary string
    """
    def prep(self, shared: Dict[str, Any]):
        user_message, cost_analysis = shared.get("user_message", ""), shared.get("cost_analysis", {})
        logger.info(f"🔄 ResultSummarizerNode: prep - user_message='{user_message[:30]}...', cost_analysis keys={list(cost_analysis.keys())}")
        return user_message, cost_analysis

    def exec(self, inputs):
        user_message, cost_analysis = inputs
        logger.info(f"🔄 ResultSummarizerNode: exec - user_message='{user_message[:30]}...', cost_analysis keys={list(cost_analysis.keys())}")
        prompt = f"""
You are a travel assistant. Summarize the following flight booking analysis for the user:

User request: {user_message}

Analysis:
{cost_analysis}

Provide a concise summary and a clear recommendation for the best flight option.
"""
        try:
            logger.info("🤖 ResultSummarizerNode: Calling LLM for summary")
            summary = call_llm(prompt)
            logger.info("✅ ResultSummarizerNode: LLM summary generated")
            return summary
        except Exception as e:
            logger.error(f"❌ ResultSummarizerNode: Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 ResultSummarizerNode: post - Storing summary in shared['result_summary']")
        shared["result_summary"] = exec_res
        return "default" 