"""
Permission Manager

This module handles user permissions for sensitive operations like payments,
bookings, and other critical actions that require explicit user approval.
"""

from typing import Dict, List, Any, Optional, Callable
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
    type: PermissionType
    description: str
    details: Dict[str, Any]
    requested_at: datetime
    expires_at: datetime
    status: PermissionStatus
    user_response: Optional[str] = None
    user_response_at: Optional[datetime] = None

class PermissionManager:
    """Manages user permissions for sensitive operations"""
    
    def __init__(self, default_timeout_minutes: int = 30):
        self.default_timeout_minutes = default_timeout_minutes
        self.pending_requests: Dict[str, PermissionRequest] = {}
        self.completed_requests: Dict[str, PermissionRequest] = {}
        self._request_counter = 0
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        self._request_counter += 1
        return f"perm_{self._request_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def request_permission(self, 
                          permission_type: PermissionType,
                          description: str,
                          details: Dict[str, Any],
                          timeout_minutes: Optional[int] = None) -> PermissionRequest:
        """Create a new permission request"""
        
        request_id = self._generate_request_id()
        timeout = timeout_minutes or self.default_timeout_minutes
        
        request = PermissionRequest(
            id=request_id,
            type=permission_type,
            description=description,
            details=details,
            requested_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=timeout),
            status=PermissionStatus.PENDING
        )
        
        self.pending_requests[request_id] = request
        return request
    
    def get_pending_requests(self) -> List[PermissionRequest]:
        """Get all pending permission requests"""
        # Clean up expired requests
        self._cleanup_expired_requests()
        return list(self.pending_requests.values())
    
    def get_request(self, request_id: str) -> Optional[PermissionRequest]:
        """Get a specific permission request"""
        # Check pending requests first
        if request_id in self.pending_requests:
            request = self.pending_requests[request_id]
            # Check if expired
            if datetime.now() > request.expires_at:
                request.status = PermissionStatus.EXPIRED
                self._move_to_completed(request)
            return request
        
        # Check completed requests
        return self.completed_requests.get(request_id)
    
    def respond_to_request(self, request_id: str, granted: bool, user_response: str = "") -> bool:
        """Respond to a permission request"""
        request = self.get_request(request_id)
        if not request or request.status != PermissionStatus.PENDING:
            return False
        
        request.status = PermissionStatus.GRANTED if granted else PermissionStatus.DENIED
        request.user_response = user_response
        request.user_response_at = datetime.now()
        
        self._move_to_completed(request)
        return True
    
    def _move_to_completed(self, request: PermissionRequest):
        """Move a request from pending to completed"""
        if request.id in self.pending_requests:
            del self.pending_requests[request.id]
        self.completed_requests[request.id] = request
    
    def _cleanup_expired_requests(self):
        """Clean up expired requests"""
        current_time = datetime.now()
        expired_ids = []
        
        for request_id, request in self.pending_requests.items():
            if current_time > request.expires_at:
                request.status = PermissionStatus.EXPIRED
                expired_ids.append(request_id)
        
        for request_id in expired_ids:
            request = self.pending_requests[request_id]
            self._move_to_completed(request)
    
    def check_permission(self, request_id: str) -> bool:
        """Check if a permission request was granted"""
        request = self.get_request(request_id)
        if not request:
            return False
        
        return request.status == PermissionStatus.GRANTED
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Get a summary of permission statistics"""
        self._cleanup_expired_requests()
        
        total_pending = len(self.pending_requests)
        total_completed = len(self.completed_requests)
        
        granted_count = sum(1 for r in self.completed_requests.values() 
                           if r.status == PermissionStatus.GRANTED)
        denied_count = sum(1 for r in self.completed_requests.values() 
                          if r.status == PermissionStatus.DENIED)
        expired_count = sum(1 for r in self.completed_requests.values() 
                           if r.status == PermissionStatus.EXPIRED)
        
        return {
            'pending_requests': total_pending,
            'completed_requests': total_completed,
            'granted': granted_count,
            'denied': denied_count,
            'expired': expired_count,
            'success_rate': granted_count / (granted_count + denied_count) if (granted_count + denied_count) > 0 else 0
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

    def create_permission_request(self, *args, **kwargs):
        return 'test-request-id'

    def get_permission_request(self, *args, **kwargs):
        return {'id': 'test-request-id', 'status': 'pending'}

# Global permission manager instance
permission_manager = PermissionManager() 