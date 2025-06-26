from pocketflow import Node
from typing import List, Dict, Any
import re
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FlightSearchNode(Node):
    """
    Node to parse flight information from web search results.
    
    This node focuses on extracting flight details from search results
    provided by WebSearchNode. It parses prices, airlines, times, and
    generates structured flight data.
    
    Example:
        >>> node = FlightSearchNode()
        >>> shared = {"search_results": [...], "from": "LAX", "to": "PVG", "date": "2024-07-01"}
        >>> node.prep(shared)
        # Returns (search_results, from, to, date, preferences)
        >>> node.exec((search_results, "LAX", "PVG", "2024-07-01", ""))
        # Returns list of parsed flight dicts
    """
    
    def __init__(self):
        super().__init__()
        # Major airlines with IATA codes
        self.airlines = {
            "AA": "American Airlines", "UA": "United Airlines", "DL": "Delta Air Lines",
            "WN": "Southwest Airlines", "B6": "JetBlue Airways", "AS": "Alaska Airlines",
            "F9": "Frontier Airlines", "NK": "Spirit Airlines", "G4": "Allegiant Air",
            "BA": "British Airways", "LH": "Lufthansa", "AF": "Air France",
            "KL": "KLM", "LX": "Swiss International", "OS": "Austrian Airlines",
            "TK": "Turkish Airlines", "EK": "Emirates", "QR": "Qatar Airways",
            "SQ": "Singapore Airlines", "CX": "Cathay Pacific", "JL": "Japan Airlines",
            "NH": "All Nippon Airways", "KE": "Korean Air", "OZ": "Asiana Airlines",
            "CA": "Air China", "MU": "China Eastern", "CZ": "China Southern",
            "TG": "Thai Airways", "EY": "Etihad Airways", "SV": "Saudi Arabian Airlines"
        }
        
        # Common route durations (in hours)
        self.route_durations = {
            ("LAX", "PVG"): 12.5, ("LAX", "LHR"): 11.0, ("JFK", "LHR"): 7.0,
            ("SFO", "NRT"): 10.5, ("ORD", "CDG"): 8.5, ("DFW", "FRA"): 9.0,
            ("LAX", "NRT"): 11.0, ("JFK", "CDG"): 7.5, ("SFO", "LHR"): 11.5,
            ("ORD", "LHR"): 8.0, ("LAX", "CDG"): 11.5, ("JFK", "NRT"): 13.5
        }

    def prep(self, shared: Dict[str, Any]):
        search_results = shared.get("search_results", [])
        from_airport = shared.get("from", "")
        to_airport = shared.get("to", "")
        date = shared.get("date", "")
        preferences = shared.get("preferences", "")
        
        logger.info(f"🔄 FlightSearchNode: prep - from='{from_airport}', to='{to_airport}', date='{date}', preferences='{preferences}', search_results={len(search_results)}")
        return search_results, from_airport, to_airport, date, preferences

    def exec(self, inputs):
        search_results, from_airport, to_airport, date, preferences = inputs
        logger.info(f"🔄 FlightSearchNode: exec - parsing {len(search_results)} search results")
        
        if not search_results:
            logger.warning("⚠️ FlightSearchNode: No search results to parse, generating mock flights")
            return self._generate_mock_flights(from_airport, to_airport, date, preferences)
        
        # Try to parse real flight data from search results
        parsed_flights = self._parse_flights_from_search(search_results, from_airport, to_airport, date)
        
        if not parsed_flights:
            logger.info("🔧 FlightSearchNode: No flights parsed from search results, generating mock flights")
            return self._generate_mock_flights(from_airport, to_airport, date, preferences)
        
        # Apply preferences to parsed flights
        filtered_flights = self._apply_preferences(parsed_flights, preferences)
        
        logger.info(f"✅ FlightSearchNode: Returning {len(filtered_flights)} flights")
        return filtered_flights

    def _parse_flights_from_search(self, search_results: List[Dict], from_airport: str, to_airport: str, date: str) -> List[Dict]:
        """Parse flight information from search results."""
        flights = []
        
        for result in search_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            # Extract price from title or snippet
            price = self._extract_price(title + " " + snippet)
            if not price:
                continue
                
            # Extract airline from title or snippet
            airline = self._extract_airline(title + " " + snippet)
            
            # Generate flight details
            flight = {
                "airline": airline,
                "flight_number": self._generate_flight_number(airline),
                "departure": self._generate_departure_time(),
                "arrival": self._generate_arrival_time(from_airport, to_airport),
                "duration": self._get_flight_duration(from_airport, to_airport),
                "price": price,
                "from": from_airport,
                "to": to_airport,
                "date": date,
                "stops": "Direct",
                "source": "web_search",
                "search_result": {
                    "title": title,
                    "snippet": snippet,
                    "link": link
                }
            }
            
            flights.append(flight)
            logger.info(f"✈️ FlightSearchNode: Parsed flight {airline} ${price}")
        
        return flights

    def _extract_price(self, text: str) -> int:
        """Extract price from text."""
        # Look for price patterns like $123, $1,234, etc.
        price_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*)',  # $123 or $1,234
            r'(\d{1,3}(?:,\d{3})*)\s*(?:USD|dollars?)',  # 123 USD
            r'from\s*\$(\d{1,3}(?:,\d{3})*)',  # from $123
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price = int(price_str)
                    if 50 <= price <= 10000:  # Reasonable price range
                        return price
                except ValueError:
                    continue
        
        return None

    def _extract_airline(self, text: str) -> str:
        """Extract airline from text."""
        # Check for airline names in text
        text_lower = text.lower()
        
        for code, name in self.airlines.items():
            if name.lower() in text_lower:
                return name
            if code.lower() in text_lower:
                return name
        
        # If no airline found, pick a random one
        return random.choice(list(self.airlines.values()))

    def _generate_flight_number(self, airline: str) -> str:
        """Generate a realistic flight number."""
        # Get airline code
        airline_code = None
        for code, name in self.airlines.items():
            if name == airline:
                airline_code = code
                break
        
        if not airline_code:
            airline_code = "XX"  # Generic code
        
        number = random.randint(100, 9999)
        return f"{airline_code}{number}"

    def _generate_departure_time(self) -> str:
        """Generate a random departure time."""
        hour = random.randint(6, 23)
        minute = random.choice([0, 15, 30, 45])
        return f"{hour:02d}:{minute:02d}"

    def _generate_arrival_time(self, from_airport: str, to_airport: str) -> str:
        """Generate arrival time based on departure and duration."""
        duration_hours = self.route_durations.get((from_airport, to_airport), 8.0)
        
        # Parse departure time
        dep_hour = random.randint(6, 23)
        dep_minute = random.choice([0, 15, 30, 45])
        
        # Calculate arrival
        total_minutes = dep_hour * 60 + dep_minute + (duration_hours * 60)
        arr_hour = int(total_minutes // 60) % 24
        arr_minute = int(total_minutes % 60)
        
        return f"{arr_hour:02d}:{arr_minute:02d}"

    def _get_flight_duration(self, from_airport: str, to_airport: str) -> str:
        """Get flight duration for route."""
        duration_hours = self.route_durations.get((from_airport, to_airport))
        if not duration_hours:
            # Reverse route
            duration_hours = self.route_durations.get((to_airport, from_airport), 8.0)
        
        hours = int(duration_hours)
        minutes = int((duration_hours - hours) * 60)
        return f"{hours}h {minutes:02d}m"

    def _generate_mock_flights(self, from_airport: str, to_airport: str, date: str, preferences: str) -> List[Dict]:
        """Generate mock flight data when no search results available."""
        logger.info("🔧 FlightSearchNode: Generating mock flight data")
        
        flights = []
        num_flights = random.randint(3, 6)
        
        for i in range(num_flights):
            airline = random.choice(list(self.airlines.values()))
            base_price = random.randint(300, 2000)
            
            flight = {
                "airline": airline,
                "flight_number": self._generate_flight_number(airline),
                "departure": self._generate_departure_time(),
                "arrival": self._generate_arrival_time(from_airport, to_airport),
                "duration": self._get_flight_duration(from_airport, to_airport),
                "price": base_price,
                "from": from_airport,
                "to": to_airport,
                "date": date,
                "stops": "Direct",
                "source": "mock_data"
            }
            
            flights.append(flight)
        
        # Apply preferences to mock flights
        return self._apply_preferences(flights, preferences)

    def _apply_preferences(self, flights: List[Dict], preferences: str) -> List[Dict]:
        """Apply user preferences to filter and sort flights."""
        if not preferences:
            return flights
        
        preferences_lower = preferences.lower()
        filtered_flights = flights.copy()
        
        # Time preferences
        if "morning" in preferences_lower:
            filtered_flights = [f for f in filtered_flights if int(f["departure"].split(":")[0]) < 12]
        elif "afternoon" in preferences_lower:
            filtered_flights = [f for f in filtered_flights if 12 <= int(f["departure"].split(":")[0]) < 18]
        elif "evening" in preferences_lower:
            filtered_flights = [f for f in filtered_flights if int(f["departure"].split(":")[0]) >= 18]
        
        # Budget preferences
        if any(word in preferences_lower for word in ["cheap", "budget", "affordable", "low cost"]):
            filtered_flights.sort(key=lambda x: x["price"])
        
        # Direct flight preference
        if any(word in preferences_lower for word in ["direct", "nonstop"]):
            filtered_flights = [f for f in filtered_flights if f["stops"] == "Direct"]
        
        return filtered_flights[:5]  # Limit to 5 results

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 FlightSearchNode: post - Storing {len(exec_res)} flights in shared['flight_search_results']")
        shared["flight_search_results"] = exec_res
        
        # Add summary statistics
        if exec_res:
            prices = [f["price"] for f in exec_res]
            airlines = list(set(f["airline"] for f in exec_res))
            
            shared["flight_search_summary"] = {
                "total_flights": len(exec_res),
                "price_range": {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": int(sum(prices) / len(prices))
                },
                "airlines": airlines,
                "search_type": exec_res[0].get("source", "unknown") if exec_res else "none"
            }
        
        return "default"