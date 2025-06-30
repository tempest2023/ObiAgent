from pocketflow import Node
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FlightSearchNode(Node):
    """
    Node to search for flights (mock implementation for demo).
    Example:
        >>> node = FlightSearchNode()
        >>> shared = {"from": "LAX", "to": "PVG", "date": "2024-07-01"}
        >>> node.prep(shared)
        # Returns (from, to, date)
        >>> node.exec(("LAX", "PVG", "2024-07-01"))
        # Returns list of flight dicts
    """
    def prep(self, shared: Dict[str, Any]):
        from_airport, to_airport, date = shared.get("from", "LAX"), shared.get("to", "PVG"), shared.get("date", "2024-07-01")
        logger.info(f"🔄 FlightSearchNode: prep - from='{from_airport}', to='{to_airport}', date='{date}'")
        return from_airport, to_airport, date

    def exec(self, inputs):
        from_airport, to_airport, date = inputs
        logger.info(f"🔄 FlightSearchNode: exec - from='{from_airport}', to='{to_airport}', date='{date}'")
        # Mock flight data
        flights = [
            {
                "airline": "United Airlines",
                "flight_number": "UA857",
                "departure": "14:30",
                "arrival": "18:45",
                "duration": "12h 15m",
                "price": 850,
                "from": from_airport,
                "to": to_airport,
                "date": date
            },
            {
                "airline": "China Eastern",
                "flight_number": "MU586",
                "departure": "15:45",
                "arrival": "19:30",
                "duration": "11h 45m",
                "price": 720,
                "from": from_airport,
                "to": to_airport,
                "date": date
            },
            {
                "airline": "Delta Airlines",
                "flight_number": "DL287",
                "departure": "16:20",
                "arrival": "20:15",
                "duration": "11h 55m",
                "price": 920,
                "from": from_airport,
                "to": to_airport,
                "date": date
            }
        ]
        logger.info(f"✅ FlightSearchNode: Returning {len(flights)} mock flights")
        return flights

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 FlightSearchNode: post - Storing {len(exec_res)} flights in shared['flight_search_results']")
        shared["flight_search_results"] = exec_res
        return "default" 