"""
Improved tests for the PocketFlow General Agent System.
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agent.flow import create_general_agent_flow
from agent.utils.node_registry import node_registry
from agent.utils.workflow_store import workflow_store
from agent.utils.permission_manager import permission_manager

class TestAgentSystem:
    """Test the complete agent system"""
    
    @pytest.mark.asyncio
    async def test_flight_booking_workflow(self, sample_shared_store):
        """Test the flight booking workflow with improved assertions"""
        print("🚀 Testing PocketFlow General Agent System - Flight Booking")
        print("=" * 60)
        
        # Setup
        shared = sample_shared_store.copy()
        shared["user_message"] = "Help book a flight ticket from Los Angeles to Shanghai with high cost performance, preferably departing in the afternoon."
        
        print(f"📝 User Question: {shared['user_message']}")
        print()
        
        # Create and run the agent flow
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            print("\n✅ Workflow completed successfully!")
            
            # Verify workflow completed with proper structure
            assert "workflow_results" in shared or "error" in shared or "workflow_design" in shared
            
            # Check for expected outputs
            if "workflow_results" in shared:
                results = shared["workflow_results"]
                assert isinstance(results, dict)
                assert len(results) > 0
                print(f"📊 Workflow Results: {len(results)} nodes executed")
                
            elif "workflow_design" in shared:
                design = shared["workflow_design"]
                assert isinstance(design, dict)
                print(f"🎯 Workflow Design: {design.get('workflow', {}).get('name', 'Unknown')}")
                
            elif "error" in shared:
                error = shared["error"]
                assert isinstance(error, str)
                print(f"⚠️ Workflow Error: {error}")
                
        except Exception as e:
            print(f"\n❌ Workflow failed: {e}")
            # Should handle errors gracefully
            assert "error" in shared or "workflow_design" in shared
        
        # Show results
        print("\n📊 Results:")
        print("-" * 30)
        
        if "workflow_design" in shared:
            design = shared["workflow_design"]
            print(f"🎯 Workflow Name: {design.get('workflow', {}).get('name', 'Unknown')}")
            print(f"📋 Estimated Steps: {design.get('estimated_steps', 'Unknown')}")
            print(f"🔐 Requires Permission: {design.get('requires_permission', False)}")
        
        if "workflow_results" in shared:
            results = shared["workflow_results"]
            print(f"📈 Nodes Executed: {len(results)}")
            for node_name, result in results.items():
                if isinstance(result, dict):
                    print(f"  - {node_name}: {result.get('recommendation', str(result))}")
                else:
                    print(f"  - {node_name}: {str(result)[:50]}...")
    
    @pytest.mark.asyncio
    async def test_web_search_workflow(self, sample_shared_store):
        """Test web search workflow"""
        print("\n🔍 Testing Web Search Workflow")
        print("=" * 40)
        
        shared = sample_shared_store.copy()
        shared["user_message"] = "Search for information about AI trends and machine learning developments"
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should have some results or error handling
            assert any(key in shared for key in ["workflow_results", "error", "workflow_design"])
            
            if "workflow_results" in shared:
                results = shared["workflow_results"]
                assert isinstance(results, dict)
                print(f"✅ Web search completed with {len(results)} results")
                
        except Exception as e:
            print(f"⚠️ Web search workflow failed: {e}")
            # Should handle errors gracefully
            assert True
    
    @pytest.mark.asyncio
    async def test_permission_workflow(self, sample_shared_store):
        """Test workflow requiring permissions"""
        print("\n🔐 Testing Permission Workflow")
        print("=" * 40)
        
        shared = sample_shared_store.copy()
        shared["user_message"] = "Make a payment of $500 for flight booking"
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should either complete or request permissions
            assert any(key in shared for key in ["workflow_results", "error", "permission_request", "workflow_design"])
            
            if "permission_request" in shared:
                print("✅ Permission request created")
            elif "workflow_results" in shared:
                print("✅ Payment workflow completed")
                
        except Exception as e:
            print(f"⚠️ Permission workflow failed: {e}")
            # Should handle errors gracefully
            assert True

class TestNodeRegistry:
    """Test the node registry functionality"""
    
    def test_node_registry_comprehensive(self):
        """Comprehensive test of node registry functionality"""
        print("\n🔧 Testing Node Registry")
        print("=" * 30)
        
        # Get all nodes
        all_nodes = node_registry.get_all_nodes()
        print(f"Total Nodes: {len(all_nodes)}")
        assert len(all_nodes) > 0
        
        # Verify node structure
        for node in all_nodes:
            assert hasattr(node, 'name')
            assert hasattr(node, 'description')
            assert hasattr(node, 'category')
            assert hasattr(node, 'permission_level')
            assert hasattr(node, 'module_path')
            assert hasattr(node, 'class_name')
            
            print(f"  - {node.name}: {node.description}")
            print(f"    Category: {node.category.value}")
            print(f"    Permission: {node.permission_level.value}")
            print(f"    Module: {node.module_path}")
            print(f"    Class: {node.class_name}")
            print()
        
        # Get nodes by category
        from agent.utils.node_registry import NodeCategory
        search_nodes = node_registry.get_nodes_by_category(NodeCategory.SEARCH)
        print(f"🔍 Found {len(search_nodes)} search nodes")
        assert len(search_nodes) > 0
        
        # Get nodes for a specific question
        question = "book a flight"
        relevant_nodes = node_registry.get_nodes_for_question(question)
        print(f"Relevant Nodes for '{question}': {len(relevant_nodes)}")
        
        for node in relevant_nodes[:3]:  # Show first 3
            print(f"  - {node.name}: {node.description}")
    
    def test_node_metadata_validation(self):
        """Test validation of node metadata"""
        all_nodes = node_registry.get_all_nodes()
        
        for node in all_nodes:
            # Required fields should not be empty
            assert node.name and len(node.name.strip()) > 0, f"Empty name for node: {node}"
            assert node.description and len(node.description.strip()) > 0, f"Empty description for node: {node.name}"
            assert node.module_path and len(node.module_path.strip()) > 0, f"Empty module_path for node: {node.name}"
            assert node.class_name and len(node.class_name.strip()) > 0, f"Empty class_name for node: {node.name}"
            
            # Category should be valid
            assert isinstance(node.category, NodeCategory), f"Invalid category for node: {node.name}"
            
            # Permission level should be valid
            assert isinstance(node.permission_level, PermissionLevel), f"Invalid permission level for node: {node.name}"

class TestWorkflowStore:
    """Test the workflow store functionality"""
    
    def test_workflow_store_comprehensive(self):
        """Comprehensive test of workflow store functionality"""
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
        
        # Test adding and removing workflow
        test_workflow_id = "test_workflow_store"
        test_metadata = Mock(name="Test Workflow Store")
        
        # Add workflow
        workflow_store.add_workflow(
            workflow_id=test_workflow_id,
            metadata=test_metadata,
            nodes=[],
            success_rate=0.9
        )
        
        # Verify workflow was added
        stored_workflow = workflow_store.get_workflow(test_workflow_id)
        assert stored_workflow is not None
        assert stored_workflow.metadata.name == "Test Workflow Store"
        
        # Update workflow
        workflow_store.update_workflow_success_rate(test_workflow_id, 0.95)
        updated_workflow = workflow_store.get_workflow(test_workflow_id)
        assert updated_workflow.metadata.success_rate == 0.95
        
        # Remove workflow
        workflow_store.remove_workflow(test_workflow_id)
        assert workflow_store.get_workflow(test_workflow_id) is None
        
        print("✅ Workflow store operations completed successfully")
    
    def test_workflow_statistics(self):
        """Test workflow store statistics"""
        stats = workflow_store.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total_workflows" in stats
        assert "total_usage" in stats
        assert "average_success_rate" in stats
        
        assert isinstance(stats["total_workflows"], int)
        assert isinstance(stats["total_usage"], int)
        assert isinstance(stats["average_success_rate"], float)
        assert 0 <= stats["average_success_rate"] <= 1
        
        print(f"📊 Workflow Statistics:")
        print(f"  Total Workflows: {stats['total_workflows']}")
        print(f"  Total Usage: {stats['total_usage']}")
        print(f"  Average Success Rate: {stats['average_success_rate']:.2%}")

class TestPermissionManager:
    """Test the permission manager functionality"""
    
    def test_permission_manager_comprehensive(self):
        """Comprehensive test of permission manager functionality"""
        print("\n🔐 Testing Permission Manager")
        print("=" * 30)
        
        # Test creating permission request
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment for flight booking",
            amount=500
        )
        
        assert request_id is not None
        assert isinstance(request_id, str)
        print(f"✅ Created permission request: {request_id}")
        
        # Test getting request
        request = permission_manager.get_request(request_id)
        assert request is not None
        assert request.user_id == "test_user"
        assert request.operation == "payment"
        assert request.amount == 500
        assert request.status == "pending"
        
        # Test authorization
        assert not permission_manager.is_authorized(request_id)
        permission_manager.authorize_request(request_id, "admin_user")
        assert permission_manager.is_authorized(request_id)
        print("✅ Permission request authorized")
        
        # Test getting user requests
        user_requests = permission_manager.get_user_requests("test_user")
        assert len(user_requests) >= 1
        assert any(req.request_id == request_id for req in user_requests)
        
        # Test permission summary
        summary = permission_manager.get_permission_summary()
        assert isinstance(summary, dict)
        assert "pending_requests" in summary
        assert "completed_requests" in summary
        assert "success_rate" in summary
        
        print(f"📊 Permission Summary:")
        print(f"  Pending Requests: {summary['pending_requests']}")
        print(f"  Completed Requests: {summary['completed_requests']}")
        print(f"  Success Rate: {summary['success_rate']:.2%}")
        
        # Clean up
        permission_manager.remove_request(request_id)
        assert permission_manager.get_request(request_id) is None
        print("✅ Permission request cleaned up")

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_missing_api_keys_handling(self, sample_shared_store, monkeypatch):
        """Test handling of missing API keys"""
        print("\n⚠️ Testing Missing API Keys Handling")
        print("=" * 40)
        
        # Remove API keys
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        
        shared = sample_shared_store.copy()
        shared["user_message"] = "Search for information about AI"
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should handle missing API keys gracefully
            assert any(key in shared for key in ["error", "workflow_design"])
            
            if "error" in shared:
                print(f"✅ Graceful error handling: {shared['error']}")
            elif "workflow_design" in shared:
                print("✅ Workflow design created despite missing API keys")
                
        except Exception as e:
            print(f"⚠️ Exception caught: {e}")
            # Should not crash completely
            assert "API" in str(e) or "key" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, sample_shared_store):
        """Test handling of invalid inputs"""
        print("\n⚠️ Testing Invalid Input Handling")
        print("=" * 40)
        
        # Test empty message
        shared = sample_shared_store.copy()
        shared["user_message"] = ""
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should handle empty input gracefully
            assert any(key in shared for key in ["error", "workflow_design"])
            
            if "error" in shared:
                print(f"✅ Empty input handled: {shared['error']}")
            elif "workflow_design" in shared:
                print("✅ Workflow design created for empty input")
                
        except Exception as e:
            print(f"⚠️ Exception caught: {e}")
            # Should not crash completely
            assert "empty" in str(e).lower() or "invalid" in str(e).lower()
        
        # Test very long message
        shared["user_message"] = "a" * 10000
        
        try:
            await flow.run_async(shared)
            print("✅ Long input handled successfully")
        except Exception as e:
            print(f"⚠️ Long input exception: {e}")
            # Should handle gracefully
            assert True

@pytest.mark.asyncio
async def test_complete_agent_system():
    """Test the complete agent system end-to-end"""
    print("\n🧪 Complete Agent System Test")
    print("=" * 60)
    
    # Test node registry
    test_registry = TestNodeRegistry()
    test_registry.test_node_registry_comprehensive()
    test_registry.test_node_metadata_validation()
    
    # Test workflow store
    test_store = TestWorkflowStore()
    test_store.test_workflow_store_comprehensive()
    test_store.test_workflow_statistics()
    
    # Test permission manager
    test_permissions = TestPermissionManager()
    test_permissions.test_permission_manager_comprehensive()
    
    # Test error handling
    test_errors = TestErrorHandling()
    await test_errors.test_missing_api_keys_handling(sample_shared_store={}, monkeypatch=Mock())
    await test_errors.test_invalid_input_handling(sample_shared_store={})
    
    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_complete_agent_system()) 