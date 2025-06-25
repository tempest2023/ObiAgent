from pocketflow import Node
from typing import Dict, Any
from agent.utils.permission_manager import permission_manager
import logging

logger = logging.getLogger(__name__)

class PermissionRequestNode(Node):
    """
    Node to request user permission for sensitive operations.
    Example:
        >>> node = PermissionRequestNode()
        >>> shared = {"operation": "payment", "details": "Book flight for $720"}
        >>> node.prep(shared)
        # Returns (operation, details)
        >>> node.exec(("payment", "Book flight for $720"))
        # Returns permission request message
    """
    def prep(self, shared: Dict[str, Any]):
        operation, details = shared.get("operation", "unknown"), shared.get("details", "No details provided")
        logger.info(f"🔄 PermissionRequestNode: prep - operation='{operation}', details='{details}'")
        return operation, details

    def exec(self, inputs):
        operation, details = inputs
        logger.info(f"🔄 PermissionRequestNode: exec - operation='{operation}', details='{details}'")
        request = permission_manager.request_permission(
            permission_type="payment" if "payment" in operation.lower() else "booking",
            description=f"Permission for {operation}",
            details={"operation": operation, "details": details}
        )
        logger.info(f"✅ PermissionRequestNode: Created permission request {request.id}")
        return f"Permission request created: {request.id}"

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 PermissionRequestNode: post - Storing pending permission request in shared['pending_permission_request']")
        shared["pending_permission_request"] = prep_res
        return "wait_for_permission" 