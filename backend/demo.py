#!/usr/bin/env python3
"""Demo script for the PocketFlow General Agent System"""

import asyncio
import json
from agent.flow import create_general_agent_flow
from agent.utils.node_registry import node_registry
from agent.utils.workflow_store import workflow_store
from logging_config import setup_logging, get_logger

# Setup logging
setup_logging('INFO')  # Use INFO level for demo
logger = get_logger(__name__)

class DemoWebSocket:
    def __init__(self):
        self.messages = []
        self.user_responses = {
            "Ask the user for additional information such as preferred date and passenger details.": 
                "My preferred date is July 15th, 2024, and I need 2 adult passengers.",
            "Please provide the following information: preferred_date, passenger_details": 
                "Preferred date: July 15th, 2024. Passengers: 2 adults, 1 child.",
            "What is your budget for this flight?": 
                "My budget is around $800 per person.",
            "Do you have any specific airline preferences?": 
                "I prefer direct flights and would like to avoid budget airlines."
        }
    
    async def send_text(self, message):
        data = json.loads(message)
        self.messages.append(data)
        
        if data['type'] == 'workflow_design':
            content = data['content']
            print(f"\n🎯 Workflow: {content.get('workflow', {}).get('name', 'Unknown')}")
            print(f"   Steps: {content.get('estimated_steps', 'Unknown')}")
            
        elif data['type'] == 'workflow_progress':
            print(f"⚡ {data['content']['current_node']} ({data['content']['progress']})")
            
        elif data['type'] == 'user_question':
            question = data['content']['question']
            print(f"\n❓ User Question: {question}")
            
            # Auto-respond based on question content
            response = self.get_auto_response(question)
            print(f"🤖 Auto Response: {response}")
            
            # Simulate user response by setting the response in the shared store
            # This will be handled by the workflow executor
            return {
                'type': 'user_response',
                'content': response
            }
            
        elif data['type'] == 'node_complete':
            result = data['content']['result']
            if isinstance(result, dict) and 'recommendation' in result:
                print(f"✅ {data['content']['node']}: {result['recommendation']}")
            else:
                print(f"✅ {data['content']['node']}: {str(result)[:50]}...")
    
    def get_auto_response(self, question):
        """Get automatic response based on question content"""
        # Try exact match first
        if question in self.user_responses:
            return self.user_responses[question]
        
        # Try partial match
        for key, response in self.user_responses.items():
            if key.lower() in question.lower() or question.lower() in key.lower():
                return response
        
        # Default response
        return "I prefer afternoon flights, budget around $800 per person, and need 2 adult passengers."

class DemoSharedStore(dict):
    def __init__(self, websocket, user_message):
        super().__init__()
        self.websocket = websocket
        self.conversation_history = []
        self.user_message = user_message
        self.waiting_for_user_response = False
        self.user_response = None
        self.waiting_for_permission = False
        self.permission_response = None
        
        # Initialize dict with required keys
        self.update({
            "websocket": websocket,
            "conversation_history": self.conversation_history,
            "user_message": self.user_message,
            "waiting_for_user_response": self.waiting_for_user_response,
            "user_response": self.user_response,
            "waiting_for_permission": self.waiting_for_permission,
            "permission_response": self.permission_response
        })
    
    def __getitem__(self, key):
        if key == "websocket":
            return self.websocket
        elif key == "conversation_history":
            return self.conversation_history
        elif key == "user_message":
            return self.user_message
        elif key == "waiting_for_user_response":
            return self.waiting_for_user_response
        elif key == "user_response":
            return self.user_response
        elif key == "waiting_for_permission":
            return self.waiting_for_permission
        elif key == "permission_response":
            return self.permission_response
        else:
            return super().__getitem__(key)
    
    def __setitem__(self, key, value):
        if key == "websocket":
            self.websocket = value
        elif key == "conversation_history":
            self.conversation_history = value
        elif key == "user_message":
            self.user_message = value
        elif key == "waiting_for_user_response":
            self.waiting_for_user_response = value
        elif key == "user_response":
            self.user_response = value
        elif key == "waiting_for_permission":
            self.waiting_for_permission = value
        elif key == "permission_response":
            self.permission_response = value
        
        super().__setitem__(key, value)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

async def demo_flight_booking():
    print("🚀 DEMO: Flight Booking Workflow with User Interaction")
    print("=" * 60)
    
    websocket = DemoWebSocket()
    shared_store = DemoSharedStore(
        websocket, 
        "Help book a flight ticket from Los Angeles to Shanghai with high cost performance, preferably departing in the afternoon."
    )
    
    print(f"📝 Question: {shared_store.user_message}")
    
    # Create a custom flow that can handle user interactions
    flow = create_general_agent_flow()
    
    try:
        # Run the flow with custom handling for user questions
        await flow.run_async(shared_store)
        print("\n✅ Workflow completed!")
        
        # Show final results
        if hasattr(shared_store, 'workflow_results'):
            print("\n📊 Final Results:")
            for node, result in shared_store.workflow_results.items():
                if isinstance(result, dict):
                    print(f"  {node}: {list(result.keys())}")
                else:
                    print(f"  {node}: {str(result)[:100]}...")
                    
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()

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