"""
Permission Manager

This module handles user permissions for sensitive operations like payments,
bookings, and other critical actions that require explicit user approval.
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

class PermissionStatus(Enum):
    """Status of a permission request"""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"

class PermissionType(Enum):
    """Types of permissions"""
    PAYMENT = "payment"
    BOOKING = "booking"
    DATA_ACCESS = "data_access"
    SYSTEM_ACTION = "system_action"

@dataclass
class PermissionRequest:
    """A permission request"""
    id: str
    user_id: Optional[str] = None
    operation: Optional[str] = None
    details: Union[str, Dict[str, Any]] = None
    amount: Optional[float] = None
    requested_at: datetime = None
    expires_at: datetime = None
    status: str = "pending"  # always string
    admin_user: Optional[str] = None
    denial_reason: Optional[str] = None
    permission_type: Optional[str] = None

    @property
    def request_id(self):
        return self.id
    @property
    def status_str(self):
        return str(self.status)

class PermissionManager:
    """Manages user permissions for sensitive operations"""
    
    def __init__(self, default_timeout_minutes: int = 30):
        self.default_timeout_minutes = default_timeout_minutes
        self.requests: Dict[str, PermissionRequest] = {}
        self._request_counter = 0
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        self._request_counter += 1
        return f"perm_{self._request_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def request_permission(self, *args, return_object: bool = False, **kwargs) -> str:
        # Accept both legacy and new signatures
        # Legacy: permission_type, description, details, amount, user_id, operation
        # New: user_id, operation, details, amount
        if 'permission_type' in kwargs:
            permission_type = kwargs.get('permission_type')
            description = kwargs.get('description', None)
            details = kwargs.get('details', None)
            amount = kwargs.get('amount', None)
            user_id = kwargs.get('user_id', None)
            operation = kwargs.get('operation', None)
        else:
            # Try to infer from args or kwargs
            user_id = kwargs.get('user_id', None)
            operation = kwargs.get('operation', None)
            details = kwargs.get('details', None)
            amount = kwargs.get('amount', None)
            permission_type = None
            description = None
            if len(args) >= 4:
                user_id, operation, details, amount = args[:4]
            elif len(args) >= 1:
                user_id = args[0]
        request_id = self._generate_request_id()
        req = PermissionRequest(
            id=request_id,
            user_id=user_id,
            operation=operation,
            details=details,
            amount=amount,
            requested_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=self.default_timeout_minutes),
            status="pending",
            permission_type=permission_type
        )
        self.requests[request_id] = req
        if return_object:
            return req
        return request_id
    
    def create_permission_request(self, user_id: str, operation: str, details: Union[str, Dict[str, Any]], amount: Optional[float] = None, return_object: bool = False) -> str:
        return self.request_permission(user_id=user_id, operation=operation, details=details, amount=amount, return_object=return_object)
    
    def get_request(self, request_id: str):
        req = self.requests.get(request_id)
        if req is None:
            return None
        # Always return a PermissionRequest with all expected fields
        return req
    
    def remove_request(self, request_id: str):
        if request_id in self.requests:
            del self.requests[request_id]
    
    def is_authorized(self, request_id: str) -> bool:
        req = self.requests.get(request_id)
        return req is not None and req.status == "granted"
    
    def authorize_request(self, request_id: str, admin_user: str):
        req = self.requests.get(request_id)
        if req and req.status == "pending":
            req.status = "granted"
            req.admin_user = admin_user
    
    def deny_request(self, request_id: str, admin_user: str, reason: str):
        req = self.requests.get(request_id)
        if req and req.status == "pending":
            req.status = "denied"
            req.admin_user = admin_user
            req.denial_reason = reason
    
    def get_user_requests(self, user_id: str):
        return [r for r in self.requests.values() if r.user_id == user_id]
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Get a summary of permission statistics"""
        pending = sum(1 for r in self.requests.values() if r.status == "pending")
        completed = sum(1 for r in self.requests.values() if r.status in ("granted", "denied"))
        granted = sum(1 for r in self.requests.values() if r.status == "granted")
        denied = sum(1 for r in self.requests.values() if r.status == "denied")
        total = granted + denied
        return {
            "pending_requests": pending,
            "completed_requests": completed,
            "success_rate": float(granted) / total if total > 0 else 0.0
        }
    
    def create_payment_permission_request(self, amount: float, currency: str, description: str, 
                                        payment_method: str = "credit_card") -> PermissionRequest:
        """Create a payment permission request"""
        details = {
            'amount': amount,
            'currency': currency,
            'description': description,
            'payment_method': payment_method
        }
        
        return self.request_permission(
            permission_type=PermissionType.PAYMENT,
            description=f"Payment request: {amount} {currency} for {description}",
            details=details,
            timeout_minutes=15  # Shorter timeout for payments
        )
    
    def create_booking_permission_request(self, booking_type: str, details: Dict[str, Any]) -> PermissionRequest:
        """Create a booking permission request"""
        return self.request_permission(
            permission_type=PermissionType.BOOKING,
            description=f"Booking request: {booking_type}",
            details=details,
            timeout_minutes=30
        )
    
    def format_permission_request_for_user(self, request: PermissionRequest) -> Dict[str, Any]:
        """Format a permission request for user display"""
        return {
            'id': request.id,
            'type': request.type.value,
            'description': request.description,
            'details': request.details,
            'requested_at': request.requested_at.isoformat(),
            'expires_at': request.expires_at.isoformat(),
            'status': request.status.value,
            'time_remaining': max(0, (request.expires_at - datetime.now()).total_seconds())
        }

# Global permission manager instance
permission_manager = PermissionManager() 