# Flight Search Node Usage Guide

The `FlightSearchNode` provides intelligent flight search capabilities with both real web search integration and enhanced mock data fallback.

## Features

### 🌐 Real Web Search Integration
- Uses SerpAPI to search flight booking websites (Expedia, Kayak, Google Flights, Skyscanner)
- Parses real flight information from search results
- Extracts prices, airlines, times, and durations automatically

### 🎯 Smart Preferences Support
- **Time Preferences**: "morning departure", "afternoon departure"
- **Budget Preferences**: "cheap", "budget", "affordable", "low cost"
- **Route Preferences**: "direct", "nonstop"

### 🏢 Comprehensive Data
- 80+ major airports worldwide with city mappings
- 30+ major airlines with proper IATA codes
- Realistic pricing based on route distance and type
- Accurate flight durations for common routes

## Usage Examples

### Basic Flight Search
```python
from agent.function_nodes.flight_search import FlightSearchNode

node = FlightSearchNode()
shared = {
    "from": "LAX",
    "to": "PVG", 
    "date": "2024-07-15",
    "num_results": 5
}

prep_result = node.prep(shared)
flights = node.exec(prep_result)
node.post(shared, prep_result, flights)
```

### Search with Preferences
```python
# Afternoon departure preference
shared = {
    "from": "JFK",
    "to": "LHR",
    "date": "2024-08-01",
    "preferences": "afternoon departure",
    "num_results": 3
}

# Budget-conscious search
shared = {
    "from": "SFO",
    "to": "NRT", 
    "date": "2024-09-10",
    "preferences": "cheap budget affordable",
    "num_results": 5
}

# Direct flights only
shared = {
    "from": "ORD",
    "to": "CDG",
    "date": "2024-10-05", 
    "preferences": "direct nonstop",
    "num_results": 3
}
```

## Configuration

### Environment Variables
- `SERPAPI_API_KEY`: Required for real web search functionality
  - Get your API key from [SerpAPI](https://serpapi.com/)
  - Without this, the node falls back to enhanced mock data

### Dependencies
```bash
pip install google-search-results
```

## Response Format

Each flight result includes:

```python
{
    "airline": "United Airlines",
    "flight_number": "UA857", 
    "departure": "14:30",
    "arrival": "18:45",
    "duration": "12h 15m",
    "price": 850,
    "from": "LAX",
    "to": "PVG",
    "date": "2024-07-15",
    "stops": "Direct",  # or "1 stop"
    "source": "web_search",  # or "enhanced_mock"
    "search_result": {  # Only for web_search source
        "title": "Flight search result title",
        "snippet": "Search result snippet...",
        "link": "https://booking-site.com/..."
    }
}
```

## Shared Data

After execution, the following data is stored in `shared`:

- `flight_search_results`: List of flight dictionaries
- `flight_search_summary`: Summary statistics including:
  - `total_flights`: Number of flights found
  - `price_range`: Min, max, and average prices
  - `airlines`: List of airlines found
  - `search_type`: "web_search" or "enhanced_mock"

## Testing

Run the included test script to verify functionality:

```bash
cd backend
python test_flight_search.py
```

This will test various scenarios including:
- Basic searches
- Preference-based filtering
- Search query construction
- Mock data generation

## Supported Airports

Major airports supported include:
- **US**: LAX, JFK, SFO, ORD, DFW, SEA, MIA, BOS, ATL, etc.
- **Asia**: PVG, PEK, NRT, HND, ICN, HKG, SIN, BKK, etc.
- **Europe**: LHR, CDG, FRA, AMS, ZUR, FCO, MAD, etc.
- **Others**: DXB, SYD, YVR, GRU, etc.

## Error Handling

The node gracefully handles:
- Missing SerpAPI credentials (falls back to mock data)
- Network errors during search
- Invalid airport codes
- Missing or malformed preferences
- Empty search results

All errors are logged with appropriate emoji indicators for easy debugging.