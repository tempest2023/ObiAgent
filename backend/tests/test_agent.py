#!/usr/bin/env python3
"""
Test script for the PocketFlow General Agent System

This script demonstrates how the agent system works by simulating
a flight booking request and showing the workflow design and execution.
"""

import asyncio
import json
from agent.flow import create_general_agent_flow
from agent.utils.node_registry import node_registry
from agent.utils.workflow_store import workflow_store
from agent.utils.permission_manager import permission_manager

class MockWebSocket:
    """Mock WebSocket for testing"""
    
    def __init__(self):
        self.messages = []
    
    async def send_text(self, message):
        """Mock send_text method"""
        data = json.loads(message)
        self.messages.append(data)
        print(f"📤 {data['type']}: {data.get('content', '')[:100]}...")
    
    def get_messages(self):
        """Get all sent messages"""
        return self.messages

async def test_flight_booking():
    """Test the flight booking workflow"""
    print("🚀 Testing PocketFlow General Agent System")
    print("=" * 50)
    
    # Create mock WebSocket
    websocket = MockWebSocket()
    
    # Create shared store
    shared_store = {
        "websocket": websocket,
        "conversation_history": [],
        "user_message": "Help book a flight ticket from Los Angeles to Shanghai with high cost performance, preferably departing in the afternoon."
    }
    
    print(f"📝 User Question: {shared_store['user_message']}")
    print()
    
    # Create and run the agent flow
    flow = create_general_agent_flow()
    
    try:
        await flow.run_async(shared_store)
        print("\n✅ Workflow completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
    
    # Show results
    print("\n📊 Results:")
    print("-" * 30)
    
    if "workflow_design" in shared_store:
        design = shared_store["workflow_design"]
        print(f"🎯 Workflow Name: {design.get('workflow', {}).get('name', 'Unknown')}")
        print(f"📋 Estimated Steps: {design.get('estimated_steps', 'Unknown')}")
        print(f"🔐 Requires Permission: {design.get('requires_permission', False)}")
    
    if "workflow_results" in shared_store:
        results = shared_store["workflow_results"]
        print(f"📈 Nodes Executed: {len(results)}")
        for node_name, result in results.items():
            if isinstance(result, dict):
                print(f"  - {node_name}: {result.get('recommendation', str(result))}")
            else:
                print(f"  - {node_name}: {str(result)[:50]}...")
    
    # Show workflow store statistics
    print("\n📚 Workflow Store Statistics:")
    print("-" * 30)
    stats = workflow_store.get_statistics()
    print(f"Total Workflows: {stats['total_workflows']}")
    print(f"Total Usage: {stats['total_usage']}")
    print(f"Average Success Rate: {stats['average_success_rate']:.2%}")
    
    # Show permission statistics
    print("\n🔐 Permission Statistics:")
    print("-" * 30)
    perm_stats = permission_manager.get_permission_summary()
    print(f"Pending Requests: {perm_stats['pending_requests']}")
    print(f"Completed Requests: {perm_stats['completed_requests']}")
    print(f"Success Rate: {perm_stats['success_rate']:.2%}")

async def test_node_registry():
    """Test the node registry functionality"""
    print("\n🔧 Testing Node Registry")
    print("=" * 30)
    
    # Get all nodes
    all_nodes = node_registry.get_all_nodes()
    print(f"Total Nodes: {len(all_nodes)}")
    
    # Get nodes by category
    from agent.utils.node_registry import NodeCategory
    search_nodes = node_registry.get_nodes_by_category(NodeCategory.SEARCH)
    print(f"Search Nodes: {len(search_nodes)}")
    
    # Get nodes for a specific question
    question = "book a flight"
    relevant_nodes = node_registry.get_nodes_for_question(question)
    print(f"Relevant Nodes for '{question}': {len(relevant_nodes)}")
    
    for node in relevant_nodes[:3]:  # Show first 3
        print(f"  - {node.name}: {node.description}")

async def test_workflow_store():
    """Test the workflow store functionality"""
    print("\n💾 Testing Workflow Store")
    print("=" * 30)
    
    # Get all workflows
    workflows = workflow_store.get_all_workflows()
    print(f"Stored Workflows: {len(workflows)}")
    
    if workflows:
        # Show first workflow
        workflow = workflows[0]
        print(f"Sample Workflow: {workflow.metadata.name}")
        print(f"Success Rate: {workflow.metadata.success_rate:.2%}")
        print(f"Usage Count: {workflow.metadata.usage_count}")
        print(f"Tags: {workflow.metadata.tags}")

async def main():
    """Main test function"""
    print("🧪 PocketFlow General Agent System Test Suite")
    print("=" * 60)
    
    # Test node registry
    await test_node_registry()
    
    # Test workflow store
    await test_workflow_store()
    
    # Test flight booking workflow
    await test_flight_booking()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
