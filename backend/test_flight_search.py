#!/usr/bin/env python3
"""
Test script for the FlightSearchNode implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.function_nodes.flight_search import FlightSearchNode
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_flight_search():
    """Test the FlightSearchNode with various scenarios."""
    
    print("🧪 Testing FlightSearchNode Implementation")
    print("=" * 50)
    
    # Create node instance
    node = FlightSearchNode()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Basic LAX to PVG search",
            "shared": {
                "from": "LAX",
                "to": "PVG", 
                "date": "2024-07-15",
                "num_results": 3
            }
        },
        {
            "name": "Afternoon preference search",
            "shared": {
                "from": "JFK",
                "to": "LHR",
                "date": "2024-08-01",
                "preferences": "afternoon departure",
                "num_results": 4
            }
        },
        {
            "name": "Budget-conscious search",
            "shared": {
                "from": "SFO",
                "to": "NRT",
                "date": "2024-09-10",
                "preferences": "cheap budget affordable",
                "num_results": 5
            }
        },
        {
            "name": "Direct flight preference",
            "shared": {
                "from": "ORD",
                "to": "CDG",
                "date": "2024-10-05",
                "preferences": "direct nonstop",
                "num_results": 3
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        shared = test_case["shared"].copy()
        
        # Run the node
        try:
            # Prep phase
            prep_result = node.prep(shared)
            print(f"📋 Prep result: {prep_result}")
            
            # Exec phase
            exec_result = node.exec(prep_result)
            print(f"✈️ Found {len(exec_result)} flights:")
            
            # Display results
            for j, flight in enumerate(exec_result, 1):
                print(f"  {j}. {flight['airline']} {flight['flight_number']}")
                print(f"     {flight['from']} → {flight['to']} on {flight['date']}")
                print(f"     Departure: {flight['departure']}, Arrival: {flight['arrival']}")
                print(f"     Duration: {flight['duration']}, Price: ${flight['price']}")
                if 'stops' in flight:
                    print(f"     Stops: {flight['stops']}")
                print(f"     Source: {flight['source']}")
                if 'search_result' in flight:
                    print(f"     Search title: {flight['search_result']['title'][:60]}...")
                print()
            
            # Post phase
            post_result = node.post(shared, prep_result, exec_result)
            print(f"💾 Post result: {post_result}")
            
            # Check shared data
            if 'flight_search_summary' in shared:
                summary = shared['flight_search_summary']
                print(f"📊 Summary: {summary['total_flights']} flights, "
                      f"${summary['price_range']['min']}-${summary['price_range']['max']}, "
                      f"avg: ${summary['price_range']['avg']}")
                print(f"🏢 Airlines: {', '.join(summary['airlines'][:3])}{'...' if len(summary['airlines']) > 3 else ''}")
                print(f"🔍 Search type: {summary['search_type']}")
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 Flight search testing completed!")
    
    # Test search query construction
    print("\n🔍 Testing search query construction:")
    test_queries = [
        ("LAX", "PVG", "2024-07-15", ""),
        ("JFK", "LHR", "2024-08-01", "afternoon departure"),
        ("SFO", "NRT", "2024-09-10", "cheap budget"),
    ]
    
    for from_airport, to_airport, date, preferences in test_queries:
        query = node._construct_search_query(from_airport, to_airport, date, preferences)
        print(f"  {from_airport} → {to_airport}: {query}")

if __name__ == "__main__":
    test_flight_search()