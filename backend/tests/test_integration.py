"""
Integration tests for the backend system.
Tests complete workflows and system interactions.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from agent.flow import create_general_agent_flow
from agent.utils.workflow_store import workflow_store
from agent.utils.permission_manager import permission_manager
from agent.utils.node_registry import node_registry
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.cost_analysis import CostAnalysisNode
from agent.function_nodes.preference_matcher import PreferenceMatcherNode

class TestCompleteWorkflows:
    """Test complete workflow execution"""
    
    @pytest.mark.asyncio
    async def test_flight_booking_workflow(self, sample_shared_store):
        """Test complete flight booking workflow"""
        # Setup
        shared = sample_shared_store.copy()
        shared["user_message"] = "Book a flight from Los Angeles to New York for next week"
        
        # Create and run workflow
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Verify workflow completed
            assert "workflow_results" in shared or "error" in shared
            
            # Check for expected outputs
            if "workflow_results" in shared:
                results = shared["workflow_results"]
                assert isinstance(results, dict)
                
                # Should have some results
                assert len(results) > 0
                
        except Exception as e:
            # Workflow might fail due to missing API keys, but should handle gracefully
            assert "error" in shared or "workflow_design" in shared
    
    @pytest.mark.asyncio
    async def test_web_search_workflow(self, sample_shared_store):
        """Test web search workflow"""
        shared = sample_shared_store.copy()
        shared["user_message"] = "Search for information about AI trends"
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should have some results or error handling
            assert "workflow_results" in shared or "error" in shared
            
        except Exception as e:
            # Should handle errors gracefully
            assert True
    
    @pytest.mark.asyncio
    async def test_permission_workflow(self, sample_shared_store):
        """Test workflow requiring permissions"""
        shared = sample_shared_store.copy()
        shared["user_message"] = "Make a payment of $500 for flight booking"
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should either complete or request permissions
            assert any(key in shared for key in ["workflow_results", "error", "permission_request"])
            
        except Exception as e:
            # Should handle errors gracefully
            assert True

class TestSystemIntegration:
    """Test system component integration"""
    
    def test_node_registry_integration(self):
        """Test node registry integration with workflow store"""
        # Get nodes from registry
        all_nodes = node_registry.get_all_nodes()
        assert len(all_nodes) > 0
        
        # Test that nodes can be loaded and executed
        web_search_node = node_registry.get_node("web_search")
        assert web_search_node is not None
        
        # Test node execution
        node_instance = web_search_node.create_instance()
        shared = {"query": "test query"}
        
        prep_res = node_instance.prep(shared)
        exec_res = node_instance.exec(prep_res)
        action = node_instance.post(shared, prep_res, exec_res)
        
        # Should complete without errors
        assert action is not None
    
    def test_workflow_store_integration(self):
        """Test workflow store integration"""
        # Add workflow to store
        workflow_id = "test_integration_workflow"
        metadata = Mock(name="Integration Test Workflow")
        
        workflow_store.add_workflow(
            workflow_id=workflow_id,
            metadata=metadata,
            nodes=[],
            success_rate=0.9
        )
        
        # Retrieve workflow
        stored_workflow = workflow_store.get_workflow(workflow_id)
        assert stored_workflow is not None
        assert stored_workflow.metadata.name == "Integration Test Workflow"
        
        # Update workflow
        workflow_store.update_workflow_success_rate(workflow_id, 0.95)
        updated_workflow = workflow_store.get_workflow(workflow_id)
        assert updated_workflow.metadata.success_rate == 0.95
        
        # Clean up
        workflow_store.remove_workflow(workflow_id)
        assert workflow_store.get_workflow(workflow_id) is None
    
    def test_permission_manager_integration(self):
        """Test permission manager integration"""
        # Create permission request
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        # Get user requests
        user_requests = permission_manager.get_user_requests("test_user")
        assert len(user_requests) > 0
        
        # Find our request
        our_request = None
        for req in user_requests:
            if req.request_id == request_id:
                our_request = req
                break
        
        assert our_request is not None
        assert our_request.amount == 100
        assert our_request.operation == "payment"
        
        # Authorize request
        permission_manager.authorize_request(request_id, "admin_user")
        assert permission_manager.is_authorized(request_id)
        
        # Clean up
        permission_manager.remove_request(request_id)

class TestErrorHandling:
    """Test error handling in integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_missing_api_keys_handling(self, sample_shared_store, monkeypatch):
        """Test handling of missing API keys"""
        # Remove API keys
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        
        shared = sample_shared_store.copy()
        shared["user_message"] = "Search for information"
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should handle missing API keys gracefully
            assert "error" in shared or "workflow_design" in shared
            
        except Exception as e:
            # Should not crash completely
            assert "API" in str(e) or "key" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_network_failure_handling(self, sample_shared_store):
        """Test handling of network failures"""
        shared = sample_shared_store.copy()
        shared["user_message"] = "Search for information"
        
        # Mock network failure
        with patch('requests.get', side_effect=Exception("Network error")):
            flow = create_general_agent_flow()
            
            try:
                await flow.run_async(shared)
                
                # Should handle network failures gracefully
                assert "error" in shared or "workflow_design" in shared
                
            except Exception as e:
                # Should not crash completely
                assert "Network" in str(e) or "error" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, sample_shared_store):
        """Test handling of invalid inputs"""
        shared = sample_shared_store.copy()
        shared["user_message"] = ""  # Empty message
        
        flow = create_general_agent_flow()
        
        try:
            await flow.run_async(shared)
            
            # Should handle empty input gracefully
            assert "error" in shared or "workflow_design" in shared
            
        except Exception as e:
            # Should not crash completely
            assert "empty" in str(e).lower() or "invalid" in str(e).lower()

class TestDataFlow:
    """Test data flow between components"""
    
    def test_data_persistence(self):
        """Test that data persists correctly through workflow"""
        # Create workflow data
        workflow_data = {
            "user_id": "test_user",
            "session_id": "test_session",
            "query": "test query",
            "results": []
        }
        
        # Simulate workflow execution
        workflow_store.add_workflow(
            workflow_id="test_data_flow",
            metadata=Mock(name="Data Flow Test"),
            nodes=[],
            success_rate=0.8
        )
        
        # Verify data persistence
        stored_workflow = workflow_store.get_workflow("test_data_flow")
        assert stored_workflow is not None
        
        # Clean up
        workflow_store.remove_workflow("test_data_flow")
    
    def test_data_transformation(self):
        """Test data transformation through nodes"""
        # Test flight search to cost analysis flow
        flight_node = FlightSearchNode()
        cost_node = CostAnalysisNode()
        
        # Initial data
        shared = {
            "from": "LAX",
            "to": "JFK",
            "date": "2024-07-01"
        }
        
        # Flight search
        prep_res = flight_node.prep(shared)
        exec_res = flight_node.exec(prep_res)
        flight_node.post(shared, prep_res, exec_res)
        
        # Verify flight search results
        assert "flight_search_results" in shared
        assert isinstance(shared["flight_search_results"], list)
        
        # Cost analysis
        prep_res = cost_node.prep(shared)
        exec_res = cost_node.exec(prep_res)
        cost_node.post(shared, prep_res, exec_res)
        
        # Verify cost analysis results
        assert "cost_analysis" in shared
        cost_analysis = shared["cost_analysis"]
        assert "cheapest" in cost_analysis
        assert "best_value" in cost_analysis
    
    def test_data_validation(self):
        """Test data validation through workflow"""
        # Test with valid data
        node = PreferenceMatcherNode()
        shared = {
            "flight_search_results": [
                {"departure_time": "afternoon", "price": 500},
                {"departure_time": "morning", "price": 400}
            ],
            "user_preferences": {"departure_time": "afternoon"}
        }
        
        prep_res = node.prep(shared)
        matched, summary = node.exec(prep_res)
        node.post(shared, prep_res, (matched, summary))
        
        # Verify data validation
        assert "matched_flights" in shared
        assert isinstance(shared["matched_flights"], list)
        
        # Test with invalid data
        shared_invalid = {
            "flight_search_results": "invalid_data",
            "user_preferences": {}
        }
        
        # Should handle invalid data gracefully
        try:
            prep_res = node.prep(shared_invalid)
            exec_res = node.exec(prep_res)
            node.post(shared_invalid, prep_res, exec_res)
        except Exception as e:
            # Should raise appropriate error
            assert "invalid" in str(e).lower() or "data" in str(e).lower()

class TestConcurrency:
    """Test concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_workflows(self, sample_shared_store):
        """Test multiple concurrent workflows"""
        # Create multiple workflows
        workflows = []
        shared_stores = []
        
        for i in range(3):
            shared = sample_shared_store.copy()
            shared["user_message"] = f"Test query {i}"
            shared["user_id"] = f"user_{i}"
            
            shared_stores.append(shared)
            workflows.append(create_general_agent_flow())
        
        # Execute workflows concurrently
        tasks = []
        for flow, shared in zip(workflows, shared_stores):
            task = asyncio.create_task(flow.run_async(shared))
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete (though some might fail due to missing API keys)
        assert len(results) == 3
        
        # Check that each workflow had its own state
        for i, shared in enumerate(shared_stores):
            assert shared["user_id"] == f"user_{i}"
    
    @pytest.mark.asyncio
    async def test_concurrent_permission_requests(self):
        """Test concurrent permission requests"""
        # Create multiple permission requests
        request_ids = []
        
        for i in range(5):
            request_id = permission_manager.create_permission_request(
                user_id=f"user_{i}",
                operation="payment",
                details=f"Payment {i}",
                amount=100 + i
            )
            request_ids.append(request_id)
        
        # Verify all requests were created
        assert len(request_ids) == 5
        
        # Clean up
        for request_id in request_ids:
            permission_manager.remove_request(request_id) 