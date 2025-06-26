#!/usr/bin/env python3
"""
Demo script showing the FlightSearchNode with real DuckDuckGo search.
This demonstrates how the node can find real flight information from booking sites.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.function_nodes.flight_search import FlightSearchNode
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def demo_flight_search():
    """Demonstrate flight search with real data."""
    
    print("🛫 Flight Search Demo - Real DuckDuckGo Integration")
    print("=" * 60)
    print("This demo shows how the FlightSearchNode finds real flight")
    print("information from booking websites using DuckDuckGo search.")
    print("=" * 60)
    
    # Create node instance
    node = FlightSearchNode()
    
    # Demo search
    print("\n🔍 Searching for flights: LAX → LHR (Los Angeles to London)")
    print("Date: 2024-08-15")
    print("Preferences: afternoon departure")
    print("-" * 40)
    
    shared = {
        "from": "LAX",
        "to": "LHR",
        "date": "2024-08-15",
        "preferences": "afternoon departure",
        "num_results": 3
    }
    
    try:
        # Run the search
        prep_result = node.prep(shared)
        print(f"📋 Search parameters: {prep_result}")
        
        print("\n🌐 Performing DuckDuckGo search...")
        flights = node.exec(prep_result)
        
        print(f"\n✈️ Found {len(flights)} flights:")
        print("=" * 60)
        
        for i, flight in enumerate(flights, 1):
            print(f"\n{i}. {flight['airline']} {flight['flight_number']}")
            print(f"   Route: {flight['from']} → {flight['to']}")
            print(f"   Date: {flight['date']}")
            print(f"   Departure: {flight['departure']}")
            print(f"   Arrival: {flight['arrival']}")
            print(f"   Duration: {flight['duration']}")
            print(f"   Price: ${flight['price']}")
            print(f"   Source: {flight['source']}")
            
            if flight['source'] == 'web_search' and 'search_result' in flight:
                result = flight['search_result']
                print(f"   📄 Found on: {result['title'][:50]}...")
                print(f"   🔗 Link: {result['link'][:50]}...")
        
        # Post processing
        node.post(shared, prep_result, flights)
        
        if 'flight_search_summary' in shared:
            summary = shared['flight_search_summary']
            print(f"\n📊 Search Summary:")
            print(f"   Total flights: {summary['total_flights']}")
            print(f"   Price range: ${summary['price_range']['min']} - ${summary['price_range']['max']}")
            print(f"   Average price: ${summary['price_range']['avg']}")
            print(f"   Airlines: {', '.join(summary['airlines'][:3])}{'...' if len(summary['airlines']) > 3 else ''}")
            print(f"   Search type: {summary['search_type']}")
        
        print("\n" + "=" * 60)
        if flights and flights[0]['source'] == 'web_search':
            print("✅ SUCCESS: Real flight data found from booking websites!")
            print("The FlightSearchNode successfully used DuckDuckGo to find")
            print("actual flight information from travel booking sites.")
        else:
            print("ℹ️  INFO: Using enhanced mock data (search may be rate limited)")
            print("The FlightSearchNode gracefully fell back to realistic mock data.")
        
        print("\n💡 Key Features Demonstrated:")
        print("• Real web search using DuckDuckGo (no API key required)")
        print("• Intelligent search query construction")
        print("• Price and airline extraction from search results")
        print("• Preference-based filtering (afternoon departure)")
        print("• Graceful fallback to enhanced mock data")
        print("• Comprehensive flight information structure")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_flight_search()