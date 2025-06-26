from pocketflow import Node
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataFormatterNode(Node):
    """
    Node to format workflow results for presentation.
    Example:
        >>> node = DataFormatterNode()
        >>> shared = {"workflow_results": {...}, "format_type": "comparison_table"}
        >>> node.prep(shared)
        # Returns (workflow_results, format_type)
        >>> node.exec((..., "comparison_table"))
        # Returns formatted string
    """
    def prep(self, shared: Dict[str, Any]):
        raw_data, format_type = shared.get("workflow_results", {}), shared.get("format_type", "text")
        logger.info(f"🔄 DataFormatterNode: prep - format_type='{format_type}', data_keys={list(raw_data.keys()) if isinstance(raw_data, dict) else type(raw_data)}")
        return raw_data, format_type

    def exec(self, inputs):
        raw_data, format_type = inputs
        logger.info(f"🔄 DataFormatterNode: exec - format_type='{format_type}', data_keys={list(raw_data.keys()) if isinstance(raw_data, dict) else type(raw_data)}")
        if format_type == "comparison_table":
            logger.info("📋 DataFormatterNode: Formatting as comparison table")
            return "Formatted comparison table would be displayed here"
        else:
            logger.info("📋 DataFormatterNode: Formatting as text")
            return str(raw_data)

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 DataFormatterNode: post - Storing formatted results in shared['formatted_results']")
        shared["formatted_results"] = exec_res
        return "default" 