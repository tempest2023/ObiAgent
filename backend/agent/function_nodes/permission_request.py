from pocketflow import Node
from typing import Dict, Any
from agent.utils.permission_manager import permission_manager
import logging

logger = logging.getLogger(__name__)

# Define supported permission types and their matching keywords
PERMISSION_TYPES = {
    "payment": ["payment", "pay", "purchase", "transaction"],
    "booking": ["book", "booking", "reservation", "reserve"],
    "data_access": ["data", "access", "read", "write", "database"],
    "external_api": ["api", "external", "third-party", "service"],
    # Add more types as needed
}

def infer_permission_type(operation: str) -> str:
    op = operation.lower()
    for ptype, keywords in PERMISSION_TYPES.items():
        if any(kw in op for kw in keywords):
            return ptype
    return "general"

class PermissionRequestNode(Node):
    """
    Node to request user permission for sensitive operations of various types.
    Supported permission types: payment, booking, data_access, external_api, general.
    Example:
        >>> node = PermissionRequestNode()
        >>> shared = {"operation": "access database", "details": "Read user table", "permission_type": "data_access"}
        >>> node.prep(shared)
        # Returns (permission_type, operation, details)
        >>> node.exec(("data_access", "access database", "Read user table"))
        # Returns detailed permission request message
    """
    def prep(self, shared: Dict[str, Any]):
        operation = shared.get("operation", "unknown")
        details = shared.get("details", "No details provided")
        # Allow explicit permission_type, else infer
        permission_type = shared.get("permission_type") or infer_permission_type(operation)
        logger.info(f"🔄 PermissionRequestNode: prep - type='{permission_type}', operation='{operation}', details='{details}'")
        return permission_type, operation, details

    def exec(self, inputs):
        permission_type, operation, details = inputs
        logger.info(f"🔄 PermissionRequestNode: exec - type='{permission_type}', operation='{operation}', details='{details}'")
        # Build a detailed, user-facing description
        user_message = (
            f"Permission required: [{permission_type.upper()}]\n"
            f"Operation: {operation}\n"
            f"Details: {details}\n\n"
            f"Please review and grant permission if you approve this action."
        )
        request = permission_manager.request_permission(
            permission_type=permission_type,
            description=f"Permission for {operation}",
            details={"operation": operation, "details": details, "user_message": user_message}
        )
        logger.info(f"✅ PermissionRequestNode: Created permission request {request.id}")
        return user_message + f"\nRequest ID: {request.id}"

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 PermissionRequestNode: post - Storing pending permission request in shared['pending_permission_request']")
        # Extract request ID from the exec_res (last line after 'Request ID: ')
        request_id = exec_res.strip().split("Request ID: ")[-1]
        shared["pending_permission_request"] = request_id
        shared["waiting_for_permission"] = True
        return "wait_for_permission" 