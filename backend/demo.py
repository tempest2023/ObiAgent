#!/usr/bin/env python3
"""Demo script for the PocketFlow General Agent System"""

import asyncio
import json
from agent.flow import create_general_agent_flow
from agent.utils.node_registry import node_registry
from agent.utils.workflow_store import workflow_store

class DemoWebSocket:
    def __init__(self):
        self.messages = []
    
    async def send_text(self, message):
        data = json.loads(message)
        self.messages.append(data)
        
        if data['type'] == 'workflow_design':
            content = data['content']
            print(f"\n🎯 Workflow: {content.get('workflow', {}).get('name', 'Unknown')}")
            print(f"   Steps: {content.get('estimated_steps', 'Unknown')}")
            
        elif data['type'] == 'workflow_progress':
            print(f"⚡ {data['content']['current_node']} ({data['content']['progress']})")
            
        elif data['type'] == 'node_complete':
            result = data['content']['result']
            if isinstance(result, dict) and 'recommendation' in result:
                print(f"✅ {data['content']['node']}: {result['recommendation']}")
            else:
                print(f"✅ {data['content']['node']}: {str(result)[:50]}...")

async def demo_flight_booking():
    print("🚀 DEMO: Flight Booking Workflow")
    print("=" * 50)
    
    websocket = DemoWebSocket()
    shared_store = {
        "websocket": websocket,
        "conversation_history": [],
        "user_message": "Help book a flight ticket from Los Angeles to Shanghai with high cost performance, preferably departing in the afternoon."
    }
    
    print(f"📝 Question: {shared_store['user_message']}")
    
    flow = create_general_agent_flow()
    try:
        await flow.run_async(shared_store)
        print("\n✅ Workflow completed!")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

async def main():
    print("🎭 PocketFlow General Agent System Demo")
    print("=" * 50)
    
    # Show system info
    all_nodes = node_registry.get_all_nodes()
    print(f"🔧 Available Nodes: {len(all_nodes)}")
    
    stats = workflow_store.get_statistics()
    print(f"💾 Stored Workflows: {stats['total_workflows']}")
    
    # Run demo
    await demo_flight_booking()
    
    print("\n🎉 Demo completed!")
    print("To run interactive version: python server.py")

if __name__ == "__main__":
    asyncio.run(main()) 