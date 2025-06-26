import logging
from pocketflow import Node
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FlightBookingNode(Node):
    """
    Node to simulate booking a flight ticket based on selected flight and user info.
    Example:
        >>> node = FlightBookingNode()
        >>> shared = {
        ...     "selected_flight": {...},
        ...     "user_info": {"name": "Alice", "passport": "E12345678"}
        ... }
        >>> node.prep(shared)
        # Returns (selected_flight, user_info)
        >>> node.exec((..., ...))
        # Returns booking confirmation dict
    """
    def prep(self, shared: Dict[str, Any]):
        flight = shared.get("selected_flight")
        user_info = shared.get("user_info", {})
        logger.info(f"🔄 FlightBookingNode: prep - flight={flight}, user_info={user_info}")
        return flight, user_info

    def exec(self, inputs):
        flight, user_info = inputs
        logger.info(f"🔄 FlightBookingNode: exec - flight={flight}, user_info={user_info}")
        if not flight or not user_info:
            logger.warning("⚠️ FlightBookingNode: Missing flight or user info")
            return {"status": "failed", "reason": "Missing flight or user info"}
        # Simulate booking
        confirmation = {
            "status": "success",
            "message": f"Flight booked for {user_info.get('name', 'Unknown')} on {flight.get('airline', 'Unknown')} {flight.get('flight_number', '')}",
            "flight": flight,
            "user": user_info,
            "booking_id": "BK" + str(hash(str(flight) + str(user_info)))[:8]
        }
        logger.info(f"✅ FlightBookingNode: Booking successful: {confirmation['booking_id']}")
        return confirmation

    def post(self, shared, prep_res, exec_res):
        shared["booking_confirmation"] = exec_res
        logger.info(f"💾 FlightBookingNode: post - Stored booking confirmation in shared['booking_confirmation']") 