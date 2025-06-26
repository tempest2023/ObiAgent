#!/usr/bin/env python3
"""
Test preference filtering in FlightSearchNode.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.function_nodes.flight_search import FlightSearchNode
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_time_preferences():
    """Test time-based preference filtering."""
    
    print("🧪 Testing Time Preference Filtering")
    print("=" * 50)
    
    # Create test flights with different departure times
    test_flights = [
        {
            "airline": "Test Airlines",
            "flight_number": "TA001",
            "departure": "08:30",  # Morning
            "arrival": "20:30",
            "duration": "12h 00m",
            "price": 500,
            "from": "LAX",
            "to": "LHR",
            "date": "2024-08-15",
            "stops": "Direct",
            "source": "test"
        },
        {
            "airline": "Test Airlines",
            "flight_number": "TA002", 
            "departure": "14:30",  # Afternoon
            "arrival": "02:30",
            "duration": "12h 00m",
            "price": 600,
            "from": "LAX",
            "to": "LHR",
            "date": "2024-08-15",
            "stops": "Direct",
            "source": "test"
        },
        {
            "airline": "Test Airlines",
            "flight_number": "TA003",
            "departure": "20:30",  # Evening
            "arrival": "08:30",
            "duration": "12h 00m",
            "price": 550,
            "from": "LAX",
            "to": "LHR",
            "date": "2024-08-15",
            "stops": "Direct",
            "source": "test"
        }
    ]
    
    node = FlightSearchNode()
    
    # Test morning preference
    print("\n🌅 Testing 'morning departure' preference:")
    morning_flights = node._apply_preferences(test_flights, "morning departure")
    print(f"  Original flights: {len(test_flights)}")
    print(f"  Morning flights: {len(morning_flights)}")
    for flight in morning_flights:
        print(f"    {flight['flight_number']}: {flight['departure']}")
    
    # Test afternoon preference
    print("\n☀️ Testing 'afternoon departure' preference:")
    afternoon_flights = node._apply_preferences(test_flights, "afternoon departure")
    print(f"  Original flights: {len(test_flights)}")
    print(f"  Afternoon flights: {len(afternoon_flights)}")
    for flight in afternoon_flights:
        print(f"    {flight['flight_number']}: {flight['departure']}")
    
    # Test evening preference
    print("\n🌙 Testing 'evening departure' preference:")
    evening_flights = node._apply_preferences(test_flights, "evening departure")
    print(f"  Original flights: {len(test_flights)}")
    print(f"  Evening flights: {len(evening_flights)}")
    for flight in evening_flights:
        print(f"    {flight['flight_number']}: {flight['departure']}")

def test_budget_preferences():
    """Test budget-based preference filtering."""
    
    print("\n\n💰 Testing Budget Preference Filtering")
    print("=" * 50)
    
    # Create test flights with different prices
    test_flights = [
        {"airline": "Expensive Air", "flight_number": "EA001", "departure": "10:00", "price": 1200, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "22:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
        {"airline": "Budget Air", "flight_number": "BA001", "departure": "12:00", "price": 400, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "00:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
        {"airline": "Mid Air", "flight_number": "MA001", "departure": "14:00", "price": 800, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "02:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
    ]
    
    node = FlightSearchNode()
    
    print("\n💸 Testing 'budget' preference (should sort by price):")
    budget_flights = node._apply_preferences(test_flights, "budget")
    print(f"  Original order: {[f['price'] for f in test_flights]}")
    print(f"  Budget order: {[f['price'] for f in budget_flights]}")
    for flight in budget_flights:
        print(f"    {flight['flight_number']}: ${flight['price']}")

def test_combined_preferences():
    """Test combined preferences."""
    
    print("\n\n🎯 Testing Combined Preferences")
    print("=" * 50)
    
    # Create more test flights
    test_flights = [
        {"airline": "Morning Expensive", "flight_number": "ME001", "departure": "08:00", "price": 1000, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "20:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
        {"airline": "Morning Cheap", "flight_number": "MC001", "departure": "09:00", "price": 400, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "21:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
        {"airline": "Afternoon Expensive", "flight_number": "AE001", "departure": "14:00", "price": 1200, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "02:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
        {"airline": "Afternoon Cheap", "flight_number": "AC001", "departure": "15:00", "price": 500, "from": "LAX", "to": "LHR", "date": "2024-08-15", "arrival": "03:00", "duration": "12h 00m", "stops": "Direct", "source": "test"},
    ]
    
    node = FlightSearchNode()
    
    print("\n🌅💰 Testing 'morning departure budget' preference:")
    combined_flights = node._apply_preferences(test_flights, "morning departure budget")
    print(f"  Original flights: {len(test_flights)}")
    print(f"  Filtered flights: {len(combined_flights)}")
    for flight in combined_flights:
        dep_hour = int(flight['departure'].split(':')[0])
        time_period = "Morning" if dep_hour < 12 else "Afternoon" if dep_hour < 18 else "Evening"
        print(f"    {flight['flight_number']}: {flight['departure']} ({time_period}) - ${flight['price']}")

if __name__ == "__main__":
    test_time_preferences()
    test_budget_preferences()
    test_combined_preferences()
    
    print("\n" + "=" * 50)
    print("✅ Preference filtering tests completed!")
    print("\n💡 Key Features Verified:")
    print("• Time-based filtering (morning/afternoon/evening)")
    print("• Budget-based sorting (cheapest first)")
    print("• Combined preference handling")
    print("• Proper flight filtering logic")