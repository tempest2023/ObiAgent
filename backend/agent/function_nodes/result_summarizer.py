from pocketflow import Node
from typing import Dict, Any
from agent.utils.stream_llm import call_llm
import logging

logger = logging.getLogger(__name__)

class ResultSummarizerNode(Node):
    """
    Summarize results and provide recommendations using LLM.
    Example:
        >>> node = ResultSummarizerNode()
        >>> shared = {"user_message": "Analyze my options...", "analysis": {...}}
        >>> node.prep(shared)
        # Returns (user_message, analysis)
        >>> node.exec(("Analyze my options...", {...}))
        # Returns summary string
    """
    def prep(self, shared: Dict[str, Any]):
        user_message = shared.get("user_message", "")
        analysis = shared.get("analysis", {})
        logger.info(f"🔄 ResultSummarizerNode: prep - user_message='{user_message[:30]}...', analysis keys={list(analysis.keys())}")
        return user_message, analysis

    def exec(self, inputs):
        user_message, analysis = inputs
        logger.info(f"🔄 ResultSummarizerNode: exec - user_message='{user_message[:30]}...', analysis keys={list(analysis.keys())}")
        prompt = f"""
You are an expert assistant. Summarize the following analysis for the user and provide clear, actionable recommendations.

User request: {user_message}

Analysis:
{analysis}

Provide a concise summary and, if appropriate, a clear recommendation for the best option or next steps.
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