from pocketflow import Node
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CostAnalysisNode(Node):
    """
    Node to analyze flight options and provide recommendations.
    Example:
        >>> node = CostAnalysisNode()
        >>> shared = {"flight_search_results": [{...}, {...}]}
        >>> node.prep(shared)
        # Returns list of flights
        >>> node.exec([{...}, {...}])
        # Returns analysis dict
    """
    def prep(self, shared: Dict[str, Any]):
        flights = shared.get("flight_search_results", [])
        logger.info(f"🔄 CostAnalysisNode: prep - {len(flights)} flights")
        return flights

    def exec(self, flights: List[Dict[str, Any]]):
        logger.info(f"🔄 CostAnalysisNode: exec - {len(flights)} flights")
        if not flights:
            logger.warning("⚠️ CostAnalysisNode: No flight options to analyze")
            return {"summary": "No flight options to analyze"}
        cheapest = min(flights, key=lambda x: x["price"])
        def price_per_hour(flight):
            try:
                duration_str = flight["duration"]
                parts = duration_str.split()
                hours = float(parts[0].replace("h", "")) if "h" in parts[0] else 0
                if len(parts) > 1 and "m" in parts[1]:
                    minutes = float(parts[1].replace("m", ""))
                    hours += minutes / 60
                return flight["price"] / hours if hours > 0 else flight["price"]
            except Exception:
                return flight["price"]
        best_value = min(flights, key=price_per_hour)
        logger.info(f"✅ CostAnalysisNode: Cheapest: {cheapest['flight_number']} Best value: {best_value['flight_number']}")
        return {
            "cheapest": cheapest,
            "best_value": best_value,
            "recommendation": f"Best value: {best_value['airline']} {best_value['flight_number']} at ${best_value['price']}"
        }

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 CostAnalysisNode: post - Storing analysis in shared['cost_analysis']")
        shared["cost_analysis"] = exec_res
        return "default" 