import logging
from pocketflow import Node
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PreferenceMatcherNode(Node):
    """
    Node to match user preferences with available flight options.
    Example:
        >>> node = PreferenceMatcherNode()
        >>> shared = {
        ...     "flight_search_results": [{...}, {...}],
        ...     "user_preferences": {"departure_time": "afternoon"}
        ... }
        >>> node.prep(shared)
        # Returns (flights, preferences)
        >>> node.exec(([{...}, {...}], {"departure_time": "afternoon"}))
        # Returns (matched_flights, summary)
    """
    def prep(self, shared: Dict[str, Any]):
        flights = shared.get("flight_search_results", [])
        preferences = shared.get("user_preferences", {})
        logger.info(f"🔄 PreferenceMatcherNode: prep - {len(flights)} flights, preferences={preferences}")
        return flights, preferences

    def exec(self, inputs):
        flights, preferences = inputs
        logger.info(f"🔄 PreferenceMatcherNode: exec - {len(flights)} flights, preferences={preferences}")
        if not flights:
            logger.warning("⚠️ PreferenceMatcherNode: No flights to match")
            return [], "No flights to match"
        # Example: match by departure time (e.g., 'afternoon')
        dep_pref = preferences.get("departure_time", "any").lower()
        matched = []
        for f in flights:
            dep_time = f.get("departure_time", "").lower()
            if dep_pref == "any" or dep_pref in dep_time:
                matched.append(f)
        summary = f"Found {len(matched)} flights matching preference: departure_time={dep_pref}"
        logger.info(f"✅ PreferenceMatcherNode: {summary}")
        return matched, summary

    def post(self, shared, prep_res, exec_res):
        matched, summary = exec_res
        shared["matched_flights"] = matched
        shared["preference_match_summary"] = summary
        logger.info(f"💾 PreferenceMatcherNode: post - Stored {len(matched)} matched flights and summary") 