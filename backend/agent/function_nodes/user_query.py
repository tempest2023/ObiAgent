from pocketflow import Node
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class UserQueryNode(Node):
    """
    Node to ask the user for additional information.
    Example:
        >>> node = UserQueryNode()
        >>> shared = {"question": "What is your preferred departure date?"}
        >>> node.prep(shared)
        # Returns question string
        >>> node.exec("What is your preferred departure date?")
        # Returns waiting message
    """
    def prep(self, shared: Dict[str, Any]):
        question = shared.get("question", "Please provide additional information")
        logger.info(f"🔄 UserQueryNode: prep - question='{question}'")
        return question

    def exec(self, question: str):
        logger.info(f"🔄 UserQueryNode: exec - question='{question}'")
        return f"Waiting for user response to: {question}"

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 UserQueryNode: post - Storing pending question in shared['pending_user_question']")
        shared["pending_user_question"] = prep_res
        shared["waiting_for_user_response"] = True
        return "wait_for_response" 