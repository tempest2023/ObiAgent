#!/usr/bin/env python3
"""
Simple test for the new FlightSearchNode that follows PocketFlow architecture.
This tests the node's ability to parse flight information from search results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.web_search import WebSearchNode
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_flight_search_with_web_search():
    """Test FlightSearchNode using results from WebSearchNode."""
    
    print("🧪 Testing FlightSearchNode with WebSearchNode Integration")
    print("=" * 60)
    
    # Simulate a workflow where WebSearchNode provides search results
    shared = {
        "query": "flights from LAX to LHR 2024-08-15 afternoon departure",
        "from": "LAX",
        "to": "LHR", 
        "date": "2024-08-15",
        "preferences": "afternoon departure"
    }
    
    print("🔍 Step 1: WebSearchNode - Searching for flights")
    print(f"Query: {shared['query']}")
    
    # Use WebSearchNode to get search results
    web_search_node = WebSearchNode()
    web_prep = web_search_node.prep(shared)
    search_results = web_search_node.exec(web_prep)
    web_search_node.post(shared, web_prep, search_results)
    
    print(f"📊 WebSearchNode found {len(search_results)} search results")
    for i, result in enumerate(search_results[:2], 1):
        print(f"  {i}. {result.get('title', 'No title')[:50]}...")
    
    print("\n✈️ Step 2: FlightSearchNode - Parsing flight information")
    
    # Use FlightSearchNode to parse flight information
    flight_search_node = FlightSearchNode()
    flight_prep = flight_search_node.prep(shared)
    flights = flight_search_node.exec(flight_prep)
    flight_search_node.post(shared, flight_prep, flights)
    
    print(f"📋 FlightSearchNode parsed {len(flights)} flights:")
    print("-" * 40)
    
    for i, flight in enumerate(flights, 1):
        print(f"{i}. {flight['airline']} {flight['flight_number']}")
        print(f"   Route: {flight['from']} → {flight['to']}")
        print(f"   Date: {flight['date']}")
        print(f"   Departure: {flight['departure']}")
        print(f"   Arrival: {flight['arrival']}")
        print(f"   Duration: {flight['duration']}")
        print(f"   Price: ${flight['price']}")
        print(f"   Source: {flight['source']}")
        if flight.get('search_result'):
            print(f"   Based on: {flight['search_result']['title'][:40]}...")
        print()
    
    # Check shared store
    print("📊 Shared Store Contents:")
    print(f"  search_results: {len(shared.get('search_results', []))} items")
    print(f"  flight_search_results: {len(shared.get('flight_search_results', []))} items")
    
    if 'flight_search_summary' in shared:
        summary = shared['flight_search_summary']
        print(f"  flight_search_summary:")
        print(f"    total_flights: {summary['total_flights']}")
        print(f"    price_range: ${summary['price_range']['min']} - ${summary['price_range']['max']}")
        print(f"    airlines: {', '.join(summary['airlines'][:3])}{'...' if len(summary['airlines']) > 3 else ''}")
        print(f"    search_type: {summary['search_type']}")

def test_flight_search_with_mock_data():
    """Test FlightSearchNode with no search results (mock data)."""
    
    print("\n🧪 Testing FlightSearchNode with Mock Data")
    print("=" * 60)
    
    # Simulate empty search results
    shared = {
        "search_results": [],  # Empty search results
        "from": "SFO",
        "to": "NRT",
        "date": "2024-09-10",
        "preferences": "budget morning departure"
    }
    
    print("✈️ FlightSearchNode - Generating mock flights")
    print(f"Route: {shared['from']} → {shared['to']}")
    print(f"Preferences: {shared['preferences']}")
    
    flight_search_node = FlightSearchNode()
    flight_prep = flight_search_node.prep(shared)
    flights = flight_search_node.exec(flight_prep)
    flight_search_node.post(shared, flight_prep, flights)
    
    print(f"📋 Generated {len(flights)} mock flights:")
    print("-" * 40)
    
    for i, flight in enumerate(flights, 1):
        print(f"{i}. {flight['airline']} {flight['flight_number']}")
        print(f"   Departure: {flight['departure']} | Price: ${flight['price']}")
        print(f"   Source: {flight['source']}")

if __name__ == "__main__":
    test_flight_search_with_web_search()
    test_flight_search_with_mock_data()
    
    print("\n" + "=" * 60)
    print("✅ FlightSearchNode testing completed!")
    print("\n💡 Key Features Demonstrated:")
    print("• Proper PocketFlow node architecture")
    print("• Integration with WebSearchNode results")
    print("• Flight information parsing from search results")
    print("• Preference-based filtering")
    print("• Graceful fallback to mock data")
    print("• Structured data storage in shared store")