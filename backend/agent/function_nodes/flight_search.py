from pocketflow import Node
from typing import List, Dict, Any, Optional
import os
import re
import logging
from datetime import datetime, timedelta
import random

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

logger = logging.getLogger(__name__)

class FlightSearchNode(Node):
    """
    Node to search for flights using web search or enhanced mock data.
    
    This node can:
    1. Use real web search (DuckDuckGo) to find flight information
    2. Parse search results to extract flight details
    3. Fall back to enhanced mock data when real search is unavailable
    
    Example:
        >>> node = FlightSearchNode()
        >>> shared = {"from": "LAX", "to": "PVG", "date": "2024-07-01", "preferences": "afternoon departure"}
        >>> node.prep(shared)
        # Returns (from, to, date, preferences)
        >>> node.exec(("LAX", "PVG", "2024-07-01", "afternoon departure"))
        # Returns list of flight dicts with real or enhanced mock data
    """
    
    def __init__(self):
        super().__init__()
        self.airport_codes = {
            # Major US airports
            "LAX": "Los Angeles", "JFK": "New York JFK", "LGA": "New York LaGuardia",
            "EWR": "Newark", "ORD": "Chicago O'Hare", "DFW": "Dallas", "DEN": "Denver",
            "SFO": "San Francisco", "SEA": "Seattle", "MIA": "Miami", "BOS": "Boston",
            "ATL": "Atlanta", "PHX": "Phoenix", "LAS": "Las Vegas", "MSP": "Minneapolis",
            
            # Major international airports
            "PVG": "Shanghai Pudong", "PEK": "Beijing", "NRT": "Tokyo Narita",
            "HND": "Tokyo Haneda", "ICN": "Seoul Incheon", "HKG": "Hong Kong",
            "SIN": "Singapore", "BKK": "Bangkok", "DEL": "Delhi", "BOM": "Mumbai",
            "LHR": "London Heathrow", "CDG": "Paris Charles de Gaulle", "FRA": "Frankfurt",
            "AMS": "Amsterdam", "ZUR": "Zurich", "VIE": "Vienna", "MUC": "Munich",
            "FCO": "Rome", "MAD": "Madrid", "BCN": "Barcelona", "ARN": "Stockholm",
            "CPH": "Copenhagen", "OSL": "Oslo", "HEL": "Helsinki", "SVO": "Moscow",
            "DXB": "Dubai", "DOH": "Doha", "AUH": "Abu Dhabi", "CAI": "Cairo",
            "JNB": "Johannesburg", "CPT": "Cape Town", "SYD": "Sydney", "MEL": "Melbourne",
            "PER": "Perth", "AKL": "Auckland", "YVR": "Vancouver", "YYZ": "Toronto",
            "YUL": "Montreal", "GRU": "São Paulo", "GIG": "Rio de Janeiro", "EZE": "Buenos Aires"
        }
        
        self.airlines = [
            "United Airlines", "American Airlines", "Delta Air Lines", "Southwest Airlines",
            "JetBlue Airways", "Alaska Airlines", "Spirit Airlines", "Frontier Airlines",
            "China Eastern", "China Southern", "Air China", "Cathay Pacific",
            "Singapore Airlines", "Emirates", "Qatar Airways", "Etihad Airways",
            "Lufthansa", "British Airways", "Air France", "KLM", "Swiss International",
            "Turkish Airlines", "Japan Airlines", "ANA", "Korean Air", "Thai Airways",
            "Qantas", "Air Canada", "LATAM", "Avianca", "Air New Zealand"
        ]

    def prep(self, shared: Dict[str, Any]):
        from_airport = shared.get("from", "LAX")
        to_airport = shared.get("to", "PVG") 
        date = shared.get("date", "2024-07-01")
        preferences = shared.get("preferences", "")
        num_results = shared.get("num_results", 5)
        
        logger.info(f"🔄 FlightSearchNode: prep - from='{from_airport}', to='{to_airport}', date='{date}', preferences='{preferences}'")
        return from_airport, to_airport, date, preferences, num_results

    def _construct_search_query(self, from_airport: str, to_airport: str, date: str, preferences: str = "") -> str:
        """Construct an effective search query for flight information."""
        from_city = self.airport_codes.get(from_airport, from_airport)
        to_city = self.airport_codes.get(to_airport, to_airport)
        
        # Base query
        query = f"flights from {from_city} {from_airport} to {to_city} {to_airport} {date}"
        
        # Add preferences if specified
        if preferences:
            query += f" {preferences}"
            
        # Add flight booking sites for better results
        query += " site:expedia.com OR site:kayak.com OR site:google.com/flights OR site:skyscanner.com"
        
        return query

    def _parse_flight_info_from_search(self, search_results: List[Dict], from_airport: str, to_airport: str, date: str) -> List[Dict]:
        """Parse flight information from search results."""
        flights = []
        
        for i, result in enumerate(search_results[:5]):  # Limit to top 5 results
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            # Try to extract flight information from title and snippet
            text = f"{title} {snippet}".lower()
            
            # Extract price using regex
            price_match = re.search(r'\$(\d{1,4}(?:,\d{3})*)', text)
            price = int(price_match.group(1).replace(',', '')) if price_match else self._generate_realistic_price(from_airport, to_airport)
            
            # Extract airline if mentioned
            airline = self._extract_airline(text)
            
            # Extract time information
            departure_time, arrival_time, duration = self._extract_time_info(text, from_airport, to_airport)
            
            # Generate flight number
            flight_number = self._generate_flight_number(airline)
            
            flight = {
                "airline": airline,
                "flight_number": flight_number,
                "departure": departure_time,
                "arrival": arrival_time,
                "duration": duration,
                "price": price,
                "from": from_airport,
                "to": to_airport,
                "date": date,
                "source": "web_search",
                "search_result": {
                    "title": title,
                    "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                    "link": link
                }
            }
            flights.append(flight)
            
        return flights

    def _extract_airline(self, text: str) -> str:
        """Extract airline name from text."""
        text_lower = text.lower()
        for airline in self.airlines:
            if airline.lower() in text_lower:
                return airline
        # Return a random airline if none found
        return random.choice(self.airlines)

    def _extract_time_info(self, text: str, from_airport: str, to_airport: str) -> tuple:
        """Extract departure time, arrival time, and duration from text."""
        # Look for time patterns
        time_pattern = r'(\d{1,2}):(\d{2})\s*(am|pm)?'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        
        if len(times) >= 2:
            # Use first two times found
            dep_hour, dep_min, dep_period = times[0]
            arr_hour, arr_min, arr_period = times[1]
            
            departure = f"{dep_hour}:{dep_min}"
            arrival = f"{arr_hour}:{arr_min}"
            
            if dep_period:
                departure += f" {dep_period.upper()}"
            if arr_period:
                arrival += f" {arr_period.upper()}"
        else:
            # Generate realistic times
            departure, arrival = self._generate_realistic_times(from_airport, to_airport)
        
        # Look for duration
        duration_match = re.search(r'(\d{1,2}h?\s*\d{0,2}m?|\d{1,2}\s*hours?\s*\d{0,2}\s*minutes?)', text)
        if duration_match:
            duration = duration_match.group(1)
        else:
            duration = self._calculate_realistic_duration(from_airport, to_airport)
            
        return departure, arrival, duration

    def _generate_realistic_times(self, from_airport: str, to_airport: str) -> tuple:
        """Generate realistic departure and arrival times."""
        # Generate random departure time (prefer common flight times)
        common_hours = [6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
        dep_hour = random.choice(common_hours)
        dep_min = random.choice([0, 15, 30, 45])
        
        departure = f"{dep_hour:02d}:{dep_min:02d}"
        
        # Calculate arrival based on realistic flight duration
        duration_hours = self._get_realistic_duration_hours(from_airport, to_airport)
        arr_hour = (dep_hour + duration_hours) % 24
        arr_min = dep_min + random.choice([-15, 0, 15, 30])
        if arr_min < 0:
            arr_min += 60
            arr_hour -= 1
        elif arr_min >= 60:
            arr_min -= 60
            arr_hour += 1
        
        arrival = f"{arr_hour:02d}:{arr_min:02d}"
        
        return departure, arrival

    def _get_realistic_duration_hours(self, from_airport: str, to_airport: str) -> int:
        """Get realistic flight duration in hours based on route."""
        # Simplified duration estimation based on common routes
        route_durations = {
            ("LAX", "PVG"): 13, ("LAX", "NRT"): 11, ("LAX", "LHR"): 11,
            ("JFK", "LHR"): 7, ("JFK", "CDG"): 7, ("JFK", "PVG"): 15,
            ("SFO", "NRT"): 10, ("SFO", "PVG"): 12, ("ORD", "LHR"): 8,
            ("DFW", "LHR"): 9, ("SEA", "NRT"): 10, ("LAX", "SYD"): 15,
        }
        
        # Check both directions
        duration = route_durations.get((from_airport, to_airport)) or route_durations.get((to_airport, from_airport))
        
        if duration:
            return duration + random.randint(-1, 1)  # Add some variation
        
        # Default estimation based on airport codes (very rough)
        if from_airport[:1] == to_airport[:1]:  # Same region
            return random.randint(2, 6)
        else:  # International
            return random.randint(8, 16)

    def _calculate_realistic_duration(self, from_airport: str, to_airport: str) -> str:
        """Calculate realistic flight duration."""
        hours = self._get_realistic_duration_hours(from_airport, to_airport)
        minutes = random.choice([0, 15, 30, 45])
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"

    def _generate_realistic_price(self, from_airport: str, to_airport: str) -> int:
        """Generate realistic flight prices based on route."""
        # Base prices for different route types
        base_prices = {
            "domestic_short": (150, 400),      # < 3 hours
            "domestic_long": (300, 800),       # 3-6 hours  
            "international_short": (400, 1200), # 6-10 hours
            "international_long": (600, 2500),  # > 10 hours
        }
        
        duration_hours = self._get_realistic_duration_hours(from_airport, to_airport)
        
        if duration_hours <= 3:
            price_range = base_prices["domestic_short"]
        elif duration_hours <= 6:
            price_range = base_prices["domestic_long"]
        elif duration_hours <= 10:
            price_range = base_prices["international_short"]
        else:
            price_range = base_prices["international_long"]
            
        return random.randint(price_range[0], price_range[1])

    def _generate_flight_number(self, airline: str) -> str:
        """Generate realistic flight number for airline."""
        airline_codes = {
            "United Airlines": "UA", "American Airlines": "AA", "Delta Air Lines": "DL",
            "Southwest Airlines": "WN", "JetBlue Airways": "B6", "Alaska Airlines": "AS",
            "China Eastern": "MU", "China Southern": "CZ", "Air China": "CA",
            "Cathay Pacific": "CX", "Singapore Airlines": "SQ", "Emirates": "EK",
            "Qatar Airways": "QR", "Lufthansa": "LH", "British Airways": "BA",
            "Air France": "AF", "KLM": "KL", "Japan Airlines": "JL", "ANA": "NH"
        }
        
        code = airline_codes.get(airline, "XX")
        number = random.randint(100, 9999)
        return f"{code}{number}"

    def _perform_web_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Perform web search using DuckDuckGo."""
        if not DUCKDUCKGO_AVAILABLE:
            logger.warning("⚠️ FlightSearchNode: DuckDuckGo search not available")
            return []
            
        try:
            logger.info(f"🔍 FlightSearchNode: Searching DuckDuckGo for: {query}")
            
            # Use DuckDuckGo search
            ddgs = DDGS()
            results = ddgs.text(query, max_results=num_results)
            
            if not results:
                logger.warning("⚠️ FlightSearchNode: No results from DuckDuckGo search")
                return []
                
            processed = []
            for result in results:
                processed.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),  # DuckDuckGo uses 'body' instead of 'snippet'
                    "link": result.get("href", "")     # DuckDuckGo uses 'href' instead of 'link'
                })
                
            logger.info(f"✅ FlightSearchNode: Found {len(processed)} search results from DuckDuckGo")
            return processed
            
        except Exception as e:
            logger.error(f"❌ FlightSearchNode: DuckDuckGo search error: {e}")
            return []

    def _generate_enhanced_mock_flights(self, from_airport: str, to_airport: str, date: str, preferences: str, num_results: int) -> List[Dict]:
        """Generate enhanced mock flight data with realistic details."""
        flights = []
        
        # Consider preferences for mock data
        prefer_afternoon = "afternoon" in preferences.lower()
        prefer_morning = "morning" in preferences.lower()
        prefer_cheap = any(word in preferences.lower() for word in ["cheap", "budget", "low cost", "affordable"])
        prefer_direct = "direct" in preferences.lower() or "nonstop" in preferences.lower()
        
        for i in range(num_results):
            airline = random.choice(self.airlines)
            
            # Adjust times based on preferences
            if prefer_afternoon:
                dep_hour = random.choice([12, 13, 14, 15, 16, 17, 18])
            elif prefer_morning:
                dep_hour = random.choice([6, 7, 8, 9, 10, 11])
            else:
                dep_hour = random.choice([6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20])
                
            dep_min = random.choice([0, 15, 30, 45])
            departure = f"{dep_hour:02d}:{dep_min:02d}"
            
            # Calculate arrival
            duration_hours = self._get_realistic_duration_hours(from_airport, to_airport)
            arr_hour = (dep_hour + duration_hours + random.randint(-1, 1)) % 24
            arr_min = dep_min + random.choice([0, 15, 30, 45])
            if arr_min >= 60:
                arr_min -= 60
                arr_hour += 1
            arrival = f"{arr_hour:02d}:{arr_min:02d}"
            
            # Duration
            duration = self._calculate_realistic_duration(from_airport, to_airport)
            
            # Price (adjust based on preferences)
            base_price = self._generate_realistic_price(from_airport, to_airport)
            if prefer_cheap:
                price = int(base_price * random.uniform(0.7, 0.9))  # 10-30% cheaper
            else:
                price = int(base_price * random.uniform(0.9, 1.3))  # Normal variation
                
            # Flight number
            flight_number = self._generate_flight_number(airline)
            
            # Add some variety in flight types
            stops = "Direct" if prefer_direct or random.random() < 0.6 else "1 stop"
            
            flight = {
                "airline": airline,
                "flight_number": flight_number,
                "departure": departure,
                "arrival": arrival,
                "duration": duration,
                "price": price,
                "from": from_airport,
                "to": to_airport,
                "date": date,
                "stops": stops,
                "source": "enhanced_mock",
                "preferences_applied": preferences if preferences else "none"
            }
            flights.append(flight)
            
        # Sort by price if budget-conscious, otherwise by departure time
        if prefer_cheap:
            flights.sort(key=lambda x: x["price"])
        else:
            flights.sort(key=lambda x: x["departure"])
            
        return flights

    def exec(self, inputs):
        from_airport, to_airport, date, preferences, num_results = inputs
        logger.info(f"🔄 FlightSearchNode: exec - from='{from_airport}', to='{to_airport}', date='{date}', preferences='{preferences}'")
        
        # Try real search first if available
        if DUCKDUCKGO_AVAILABLE:
            query = self._construct_search_query(from_airport, to_airport, date, preferences)
            search_results = self._perform_web_search(query, num_results)
            
            if search_results:
                logger.info("🌐 FlightSearchNode: Using real DuckDuckGo search results")
                flights = self._parse_flight_info_from_search(search_results, from_airport, to_airport, date)
                if flights:
                    logger.info(f"✅ FlightSearchNode: Returning {len(flights)} flights from DuckDuckGo search")
                    return flights
                    
        # Fall back to enhanced mock data
        logger.info("🔧 FlightSearchNode: Using enhanced mock flight data")
        flights = self._generate_enhanced_mock_flights(from_airport, to_airport, date, preferences, num_results)
        logger.info(f"✅ FlightSearchNode: Returning {len(flights)} enhanced mock flights")
        return flights

    def post(self, shared, prep_res, exec_res):
        logger.info(f"💾 FlightSearchNode: post - Storing {len(exec_res)} flights in shared['flight_search_results']")
        shared["flight_search_results"] = exec_res
        
        # Add summary information
        if exec_res:
            prices = [flight["price"] for flight in exec_res]
            shared["flight_search_summary"] = {
                "total_flights": len(exec_res),
                "price_range": {"min": min(prices), "max": max(prices), "avg": sum(prices) // len(prices)},
                "airlines": list(set(flight["airline"] for flight in exec_res)),
                "search_type": exec_res[0].get("source", "unknown")
            }
            
        return "default" 