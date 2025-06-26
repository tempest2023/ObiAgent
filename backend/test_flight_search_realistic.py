#!/usr/bin/env python3
"""
Test FlightSearchNode with realistic search results to demonstrate parsing capabilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.function_nodes.flight_search import FlightSearchNode
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_with_realistic_search_results():
    """Test FlightSearchNode with realistic search results containing flight prices."""
    
    print("🧪 Testing FlightSearchNode with Realistic Search Results")
    print("=" * 60)
    
    # Simulate realistic search results that would come from a real web search
    realistic_search_results = [
        {
            "title": "Cheap Flights from Los Angeles (LAX) to London Heathrow (LHR) - $450",
            "snippet": "Find the best deals on flights from LAX to LHR. British Airways offers direct flights starting at $450. Book now and save!",
            "link": "https://www.expedia.com/flights/lax-lhr"
        },
        {
            "title": "$389 CHEAP FLIGHTS from Los Angeles to London (LAX - LHR)",
            "snippet": "Compare prices from United Airlines, Virgin Atlantic, and American Airlines. Flights from $389 roundtrip.",
            "link": "https://www.kayak.com/flights/LAX-LHR"
        },
        {
            "title": "Delta Air Lines - LAX to LHR from $520 | Book Direct",
            "snippet": "Delta offers comfortable flights from Los Angeles to London Heathrow. Premium economy available from $520.",
            "link": "https://www.delta.com/flights"
        },
        {
            "title": "Lufthansa Flights LAX-LHR Starting at $675",
            "snippet": "Experience German engineering and hospitality. Lufthansa flights from Los Angeles to London starting at $675.",
            "link": "https://www.lufthansa.com/flights"
        }
    ]
    
    shared = {
        "search_results": realistic_search_results,
        "from": "LAX",
        "to": "LHR",
        "date": "2024-08-15",
        "preferences": "afternoon departure"
    }
    
    print("📊 Input Search Results:")
    for i, result in enumerate(realistic_search_results, 1):
        print(f"  {i}. {result['title']}")
        print(f"     {result['snippet'][:60]}...")
    
    print("\n✈️ FlightSearchNode - Parsing flight information")
    
    flight_search_node = FlightSearchNode()
    flight_prep = flight_search_node.prep(shared)
    flights = flight_search_node.exec(flight_prep)
    flight_search_node.post(shared, flight_prep, flights)
    
    print(f"\n📋 Parsed {len(flights)} flights:")
    print("-" * 50)
    
    for i, flight in enumerate(flights, 1):
        print(f"{i}. {flight['airline']} {flight['flight_number']}")
        print(f"   Route: {flight['from']} → {flight['to']} on {flight['date']}")
        print(f"   Time: {flight['departure']} → {flight['arrival']} ({flight['duration']})")
        print(f"   Price: ${flight['price']}")
        print(f"   Source: {flight['source']}")
        print(f"   Based on: {flight['search_result']['title'][:50]}...")
        print()
    
    # Show summary
    if 'flight_search_summary' in shared:
        summary = shared['flight_search_summary']
        print("📊 Flight Search Summary:")
        print(f"  Total flights: {summary['total_flights']}")
        print(f"  Price range: ${summary['price_range']['min']} - ${summary['price_range']['max']}")
        print(f"  Average price: ${summary['price_range']['avg']}")
        print(f"  Airlines: {', '.join(summary['airlines'])}")
        print(f"  Search type: {summary['search_type']}")

def test_preference_filtering():
    """Test preference-based filtering."""
    
    print("\n🧪 Testing Preference-Based Filtering")
    print("=" * 60)
    
    # Test with budget preference
    shared = {
        "search_results": [],  # Will use mock data
        "from": "JFK",
        "to": "CDG",
        "date": "2024-09-01",
        "preferences": "budget cheap morning departure"
    }
    
    print("🔍 Testing preferences: 'budget cheap morning departure'")
    
    flight_search_node = FlightSearchNode()
    flight_prep = flight_search_node.prep(shared)
    flights = flight_search_node.exec(flight_prep)
    flight_search_node.post(shared, flight_prep, flights)
    
    print(f"📋 Generated {len(flights)} flights with preferences applied:")
    print("-" * 50)
    
    for i, flight in enumerate(flights, 1):
        dep_hour = int(flight['departure'].split(':')[0])
        time_period = "Morning" if dep_hour < 12 else "Afternoon" if dep_hour < 18 else "Evening"
        print(f"{i}. {flight['airline']} - ${flight['price']} - {flight['departure']} ({time_period})")
    
    # Verify morning departures
    morning_flights = [f for f in flights if int(f['departure'].split(':')[0]) < 12]
    print(f"\n✅ Preference filtering results:")
    print(f"  Morning departures: {len(morning_flights)}/{len(flights)}")
    print(f"  Sorted by price: {flights == sorted(flights, key=lambda x: x['price'])}")

if __name__ == "__main__":
    test_with_realistic_search_results()
    test_preference_filtering()
    
    print("\n" + "=" * 60)
    print("✅ Realistic FlightSearchNode testing completed!")
    print("\n💡 Key Capabilities Demonstrated:")
    print("• Price extraction from search result titles and snippets")
    print("• Airline detection from search content")
    print("• Realistic flight number generation")
    print("• Time and duration calculations")
    print("• Preference-based filtering (time, budget)")
    print("• Structured output with search result references")
    print("• Summary statistics generation")