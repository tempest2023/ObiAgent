#!/usr/bin/env python3
"""
Demo of a complete flight search workflow using PocketFlow nodes.
This demonstrates how WebSearchNode and FlightSearchNode work together.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.cost_analysis import CostAnalysisNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def demo_flight_search_workflow():
    """Demonstrate a complete flight search workflow."""
    
    print("🚀 Flight Search Workflow Demo")
    print("=" * 60)
    print("This demo shows how multiple PocketFlow nodes work together")
    print("to solve a flight search task.\n")
    
    # Shared store - this is passed between all nodes
    shared = {
        "user_message": "Find flights from Los Angeles to London on August 15th, prefer afternoon departure",
        "from": "LAX",
        "to": "LHR", 
        "date": "2024-08-15",
        "preferences": "afternoon departure"
    }
    
    print("📋 User Request:")
    print(f"  {shared['user_message']}")
    print(f"  Route: {shared['from']} → {shared['to']}")
    print(f"  Date: {shared['date']}")
    print(f"  Preferences: {shared['preferences']}")
    
    # Step 1: Web Search
    print("\n🔍 Step 1: WebSearchNode - Searching for flight information")
    print("-" * 40)
    
    # Construct search query
    shared["query"] = f"flights from {shared['from']} to {shared['to']} {shared['date']} {shared['preferences']}"
    shared["num_results"] = 5
    
    web_search_node = WebSearchNode()
    web_prep = web_search_node.prep(shared)
    search_results = web_search_node.exec(web_prep)
    web_search_node.post(shared, web_prep, search_results)
    
    print(f"✅ Found {len(shared['search_results'])} search results")
    
    # Step 2: Flight Search (Parse flight info from search results)
    print("\n✈️ Step 2: FlightSearchNode - Parsing flight information")
    print("-" * 40)
    
    flight_search_node = FlightSearchNode()
    flight_prep = flight_search_node.prep(shared)
    flights = flight_search_node.exec(flight_prep)
    flight_search_node.post(shared, flight_prep, flights)
    
    print(f"✅ Parsed {len(shared['flight_search_results'])} flights")
    
    # Step 3: Cost Analysis
    print("\n💰 Step 3: CostAnalysisNode - Analyzing flight options")
    print("-" * 40)
    
    cost_analysis_node = CostAnalysisNode()
    cost_prep = cost_analysis_node.prep(shared)
    analysis = cost_analysis_node.exec(cost_prep)
    cost_analysis_node.post(shared, cost_prep, analysis)
    
    print(f"✅ Analysis complete")
    
    # Step 4: Result Summary
    print("\n📊 Step 4: ResultSummarizerNode - Creating summary")
    print("-" * 40)
    
    result_summarizer_node = ResultSummarizerNode()
    summary_prep = result_summarizer_node.prep(shared)
    summary = result_summarizer_node.exec(summary_prep)
    result_summarizer_node.post(shared, summary_prep, summary)
    
    print(f"✅ Summary generated")
    
    # Display Results
    print("\n" + "=" * 60)
    print("📋 WORKFLOW RESULTS")
    print("=" * 60)
    
    # Show flights
    if shared.get('flight_search_results'):
        print("\n✈️ Available Flights:")
        for i, flight in enumerate(shared['flight_search_results'], 1):
            print(f"  {i}. {flight['airline']} {flight['flight_number']}")
            print(f"     {flight['departure']} → {flight['arrival']} ({flight['duration']})")
            print(f"     Price: ${flight['price']}")
            if flight.get('search_result'):
                print(f"     Source: {flight['search_result']['title'][:50]}...")
            print()
    
    # Show cost analysis
    if shared.get('cost_analysis'):
        analysis = shared['cost_analysis']
        print("💰 Cost Analysis:")
        if 'cheapest' in analysis:
            cheapest = analysis['cheapest']
            print(f"  Cheapest: {cheapest['airline']} {cheapest['flight_number']} - ${cheapest['price']}")
        if 'best_value' in analysis:
            best_value = analysis['best_value']
            print(f"  Best Value: {best_value['airline']} {best_value['flight_number']} - ${best_value['price']}")
        if 'recommendation' in analysis:
            print(f"  Recommendation: {analysis['recommendation']}")
        print()
    
    # Show summary
    if shared.get('summary'):
        print("📊 Summary:")
        print(f"  {shared['summary']}")
        print()
    
    # Show shared store contents
    print("🗄️ Shared Store Contents:")
    for key, value in shared.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        elif isinstance(value, dict):
            print(f"  {key}: {type(value).__name__} with {len(value)} keys")
        else:
            print(f"  {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")

def demo_with_realistic_data():
    """Demo with realistic search results to show real parsing."""
    
    print("\n\n🎯 Realistic Data Demo")
    print("=" * 60)
    
    # Simulate realistic search results
    realistic_results = [
        {
            "title": "British Airways LAX to LHR - Book from $450",
            "snippet": "Direct flights from Los Angeles to London Heathrow. Premium service starting at $450.",
            "link": "https://www.britishairways.com"
        },
        {
            "title": "United Airlines - LAX-LHR flights from $389",
            "snippet": "Compare United Airlines flights from Los Angeles to London. Book now from $389.",
            "link": "https://www.united.com"
        }
    ]
    
    shared = {
        "search_results": realistic_results,
        "from": "LAX",
        "to": "LHR",
        "date": "2024-08-15",
        "preferences": "afternoon departure"
    }
    
    print("📊 Using realistic search results with actual prices")
    
    # Parse flights
    flight_search_node = FlightSearchNode()
    flight_prep = flight_search_node.prep(shared)
    flights = flight_search_node.exec(flight_prep)
    flight_search_node.post(shared, flight_prep, flights)
    
    print(f"\n✈️ Parsed {len(flights)} flights from realistic data:")
    for flight in flights:
        print(f"  • {flight['airline']} {flight['flight_number']} - ${flight['price']}")
        print(f"    Based on: {flight['search_result']['title']}")

if __name__ == "__main__":
    demo_flight_search_workflow()
    demo_with_realistic_data()
    
    print("\n" + "=" * 60)
    print("✅ Flight Search Workflow Demo Complete!")
    print("\n💡 Architecture Benefits Demonstrated:")
    print("• Modular design - each node has a single responsibility")
    print("• Reusable components - WebSearchNode can be used for any search")
    print("• Data flow - shared store passes data between nodes")
    print("• Composable workflows - nodes can be combined in different ways")
    print("• Testable - each node can be tested independently")
    print("• Extensible - new nodes can be added easily")