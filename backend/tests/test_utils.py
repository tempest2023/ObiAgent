"""
Tests for utility functions and helper modules.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from agent.utils.stream_llm import call_llm, call_gemini
from agent.utils.node_registry import node_registry, NodeCategory, PermissionLevel
from agent.utils.workflow_store import workflow_store, WorkflowMetadata
from agent.utils.permission_manager import permission_manager, PermissionRequest
from agent.utils.node_loader import node_loader

class TestStreamLLM:
    """Test streaming LLM functionality"""
    
    def test_successful_stream_call(self, mock_openai_client, monkeypatch):
        """Test successful streaming LLM call"""
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            result = call_llm("Test prompt")
            
            # Should return a response
            assert result is not None
            assert isinstance(result, str)
    
    def test_missing_api_key(self, monkeypatch):
        """Test handling of missing API key"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            call_llm("Test prompt")
    
    def test_api_error_handling(self, monkeypatch):
        """Test handling of API errors"""
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('openai.OpenAI', return_value=mock_client):
            with pytest.raises(Exception, match="API Error"):
                call_llm("Test prompt")
    
    def test_empty_prompt(self, mock_openai_client, monkeypatch):
        """Test handling of empty prompt"""
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            with pytest.raises(ValueError, match="Prompt cannot be empty"):
                call_llm("")

class TestGeminiLLM:
    """Test Gemini LLM functionality"""
    
    def test_successful_gemini_call(self, mock_gemini_client, monkeypatch):
        """Test successful Gemini LLM call"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_client):
            result = call_gemini("Test prompt")
            
            # Should return a response
            assert result is not None
            assert isinstance(result, str)
    
    def test_missing_api_key(self, monkeypatch):
        """Test handling of missing API key"""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
            call_gemini("Test prompt")
    
    def test_api_error_handling(self, monkeypatch):
        """Test handling of API errors"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        mock_client = Mock()
        mock_client.generate_content.side_effect = Exception("API Error")
        
        with patch('google.generativeai.GenerativeModel', return_value=mock_client):
            with pytest.raises(Exception, match="API Error"):
                call_gemini("Test prompt")

class TestNodeRegistry:
    """Test node registry functionality"""
    
    def test_get_all_nodes(self):
        """Test getting all nodes from registry"""
        nodes = node_registry.get_all_nodes()
        
        # Should return a list
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        
        # Each node should have required attributes
        for node in nodes:
            assert hasattr(node, 'name')
            assert hasattr(node, 'description')
            assert hasattr(node, 'category')
            assert hasattr(node, 'permission_level')
            assert hasattr(node, 'module_path')
            assert hasattr(node, 'class_name')
    
    def test_get_node_by_name(self):
        """Test getting specific node by name"""
        # Test getting web_search node
        web_search_node = node_registry.get_node("web_search")
        assert web_search_node is not None
        assert web_search_node.name == "web_search"
        assert web_search_node.category == NodeCategory.SEARCH
    
    def test_get_nonexistent_node(self):
        """Test getting non-existent node"""
        nonexistent_node = node_registry.get_node("nonexistent_node")
        assert nonexistent_node is None
    
    def test_get_nodes_by_category(self):
        """Test getting nodes by category"""
        search_nodes = node_registry.get_nodes_by_category(NodeCategory.SEARCH)
        assert isinstance(search_nodes, list)
        
        for node in search_nodes:
            assert node.category == NodeCategory.SEARCH
    
    def test_get_nodes_by_permission_level(self):
        """Test getting nodes by permission level"""
        low_permission_nodes = node_registry.get_nodes_by_permission_level(PermissionLevel.LOW)
        assert isinstance(low_permission_nodes, list)
        
        for node in low_permission_nodes:
            assert node.permission_level == PermissionLevel.LOW
    
    def test_get_nodes_for_question(self):
        """Test getting relevant nodes for a question"""
        question = "book a flight"
        relevant_nodes = node_registry.get_nodes_for_question(question)
        
        assert isinstance(relevant_nodes, list)
        assert len(relevant_nodes) > 0
        
        # Should include flight-related nodes
        node_names = [node.name for node in relevant_nodes]
        assert any("flight" in name.lower() for name in node_names)
    
    def test_node_metadata_validation(self):
        """Test validation of node metadata"""
        nodes = node_registry.get_all_nodes()
        
        for node in nodes:
            # Required fields should not be empty
            assert node.name and len(node.name.strip()) > 0
            assert node.description and len(node.description.strip()) > 0
            assert node.module_path and len(node.module_path.strip()) > 0
            assert node.class_name and len(node.class_name.strip()) > 0
            
            # Category should be valid
            assert isinstance(node.category, NodeCategory)
            
            # Permission level should be valid
            assert isinstance(node.permission_level, PermissionLevel)

class TestWorkflowStore:
    """Test workflow store functionality"""
    
    def test_add_workflow(self):
        """Test adding workflow to store"""
        workflow_id = "test_workflow"
        metadata = WorkflowMetadata(
            name="Test Workflow",
            description="Test workflow description",
            tags=["test", "workflow"],
            success_rate=0.8,
            usage_count=0
        )
        
        workflow_store.add_workflow(
            workflow_id=workflow_id,
            metadata=metadata,
            nodes=[],
            success_rate=0.8
        )
        
        # Verify workflow was added
        stored_workflow = workflow_store.get_workflow(workflow_id)
        assert stored_workflow is not None
        assert stored_workflow.metadata.name == "Test Workflow"
        
        # Clean up
        workflow_store.remove_workflow(workflow_id)
    
    def test_get_workflow(self):
        """Test getting workflow from store"""
        workflow_id = "test_get_workflow"
        metadata = Mock(name="Test Get Workflow")
        
        workflow_store.add_workflow(
            workflow_id=workflow_id,
            metadata=metadata,
            nodes=[],
            success_rate=0.9
        )
        
        # Get workflow
        workflow = workflow_store.get_workflow(workflow_id)
        assert workflow is not None
        assert workflow.metadata.name == "Test Get Workflow"
        
        # Clean up
        workflow_store.remove_workflow(workflow_id)
    
    def test_get_nonexistent_workflow(self):
        """Test getting non-existent workflow"""
        workflow = workflow_store.get_workflow("nonexistent_workflow")
        assert workflow is None
    
    def test_update_workflow_success_rate(self):
        """Test updating workflow success rate"""
        workflow_id = "test_update_workflow"
        metadata = Mock(name="Test Update Workflow")
        
        workflow_store.add_workflow(
            workflow_id=workflow_id,
            metadata=metadata,
            nodes=[],
            success_rate=0.5
        )
        
        # Update success rate
        workflow_store.update_workflow_success_rate(workflow_id, 0.9)
        
        # Verify update
        workflow = workflow_store.get_workflow(workflow_id)
        assert workflow.metadata.success_rate == 0.9
        
        # Clean up
        workflow_store.remove_workflow(workflow_id)
    
    def test_remove_workflow(self):
        """Test removing workflow from store"""
        workflow_id = "test_remove_workflow"
        metadata = Mock(name="Test Remove Workflow")
        
        workflow_store.add_workflow(
            workflow_id=workflow_id,
            metadata=metadata,
            nodes=[],
            success_rate=0.8
        )
        
        # Verify workflow exists
        assert workflow_store.get_workflow(workflow_id) is not None
        
        # Remove workflow
        workflow_store.remove_workflow(workflow_id)
        
        # Verify workflow was removed
        assert workflow_store.get_workflow(workflow_id) is None
    
    def test_get_all_workflows(self):
        """Test getting all workflows"""
        # Add some test workflows
        workflow_ids = []
        for i in range(3):
            workflow_id = f"test_all_workflows_{i}"
            metadata = Mock(name=f"Test Workflow {i}")
            
            workflow_store.add_workflow(
                workflow_id=workflow_id,
                metadata=metadata,
                nodes=[],
                success_rate=0.8
            )
            workflow_ids.append(workflow_id)
        
        # Get all workflows
        all_workflows = workflow_store.get_all_workflows()
        assert isinstance(all_workflows, list)
        assert len(all_workflows) >= 3
        
        # Clean up
        for workflow_id in workflow_ids:
            workflow_store.remove_workflow(workflow_id)
    
    def test_get_statistics(self):
        """Test getting workflow store statistics"""
        stats = workflow_store.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total_workflows" in stats
        assert "total_usage" in stats
        assert "average_success_rate" in stats
        
        assert isinstance(stats["total_workflows"], int)
        assert isinstance(stats["total_usage"], int)
        assert isinstance(stats["average_success_rate"], float)
        assert 0 <= stats["average_success_rate"] <= 1

class TestPermissionManager:
    """Test permission manager functionality"""
    
    def test_create_permission_request(self):
        """Test creating permission request"""
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        assert request_id is not None
        assert isinstance(request_id, str)
        assert len(request_id) > 0
        
        # Clean up
        permission_manager.remove_request(request_id)
    
    def test_get_permission_request(self):
        """Test getting permission request"""
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        # Get request
        request = permission_manager.get_request(request_id)
        assert request is not None
        assert request.user_id == "test_user"
        assert request.operation == "payment"
        assert request.amount == 100
        
        # Clean up
        permission_manager.remove_request(request_id)
    
    def test_get_nonexistent_request(self):
        """Test getting non-existent request"""
        request = permission_manager.get_request("nonexistent_request")
        assert request is None
    
    def test_authorize_request(self):
        """Test authorizing permission request"""
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        # Should not be authorized initially
        assert not permission_manager.is_authorized(request_id)
        
        # Authorize request
        permission_manager.authorize_request(request_id, "admin_user")
        
        # Should now be authorized
        assert permission_manager.is_authorized(request_id)
        
        # Clean up
        permission_manager.remove_request(request_id)
    
    def test_deny_request(self):
        """Test denying permission request"""
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        # Deny request
        permission_manager.deny_request(request_id, "admin_user", "Insufficient funds")
        
        # Should be denied
        request = permission_manager.get_request(request_id)
        assert request.status == "denied"
        assert request.denial_reason == "Insufficient funds"
        
        # Clean up
        permission_manager.remove_request(request_id)
    
    def test_get_user_requests(self):
        """Test getting requests for a specific user"""
        # Create requests for different users
        request1_id = permission_manager.create_permission_request(
            user_id="user1",
            operation="payment",
            details="Payment 1",
            amount=100
        )
        
        request2_id = permission_manager.create_permission_request(
            user_id="user2",
            operation="payment",
            details="Payment 2",
            amount=200
        )
        
        # Get requests for user1
        user1_requests = permission_manager.get_user_requests("user1")
        assert len(user1_requests) >= 1
        
        # Verify user1 only sees their requests
        for request in user1_requests:
            assert request.user_id == "user1"
        
        # Clean up
        permission_manager.remove_request(request1_id)
        permission_manager.remove_request(request2_id)
    
    def test_get_permission_summary(self):
        """Test getting permission summary"""
        summary = permission_manager.get_permission_summary()
        
        assert isinstance(summary, dict)
        assert "pending_requests" in summary
        assert "completed_requests" in summary
        assert "success_rate" in summary
        
        assert isinstance(summary["pending_requests"], int)
        assert isinstance(summary["completed_requests"], int)
        assert isinstance(summary["success_rate"], float)
        assert 0 <= summary["success_rate"] <= 1
    
    def test_remove_request(self):
        """Test removing permission request"""
        request_id = permission_manager.create_permission_request(
            user_id="test_user",
            operation="payment",
            details="Test payment",
            amount=100
        )
        
        # Verify request exists
        assert permission_manager.get_request(request_id) is not None
        
        # Remove request
        permission_manager.remove_request(request_id)
        
        # Verify request was removed
        assert permission_manager.get_request(request_id) is None

class TestNodeLoader:
    """Test node loader functionality"""
    
    def test_load_node_class(self):
        """Test loading node class"""
        # Test loading web_search node class
        node_class = node_loader.load_node_class(
            "agent.function_nodes.web_search",
            "WebSearchNode"
        )
        
        assert node_class is not None
        assert hasattr(node_class, 'prep')
        assert hasattr(node_class, 'exec')
        assert hasattr(node_class, 'post')
    
    def test_load_nonexistent_class(self):
        """Test loading non-existent class"""
        node_class = node_loader.load_node_class(
            "agent.function_nodes.nonexistent",
            "NonexistentNode"
        )
        
        assert node_class is None
    
    def test_create_node_instance(self):
        """Test creating node instance"""
        node_config = {
            "module_path": "agent.function_nodes.web_search",
            "class_name": "WebSearchNode"
        }
        
        node_instance = node_loader.create_node_instance(node_config)
        
        assert node_instance is not None
        assert hasattr(node_instance, 'prep')
        assert hasattr(node_instance, 'exec')
        assert hasattr(node_instance, 'post')
    
    def test_create_node_instance_with_invalid_config(self):
        """Test creating node instance with invalid config"""
        node_config = {
            "module_path": "agent.function_nodes.nonexistent",
            "class_name": "NonexistentNode"
        }
        
        node_instance = node_loader.create_node_instance(node_config)
        
        assert node_instance is None

class TestHelperFunctions:
    """Test helper functions"""
    
    def test_assert_dict_structure(self):
        """Test dictionary structure assertion helper"""
        from tests.conftest import assert_dict_structure
        
        # Valid dictionary
        data = {"key1": "value1", "key2": "value2"}
        assert_dict_structure(data, ["key1", "key2"])
        
        # Missing required key
        with pytest.raises(AssertionError, match="Required key 'key3' not found"):
            assert_dict_structure(data, ["key1", "key2", "key3"])
        
        # Optional keys
        assert_dict_structure(data, ["key1"], ["key2"])
        
        # Optional key that is None
        data_with_none = {"key1": "value1", "key2": None}
        with pytest.raises(AssertionError, match="Optional key 'key2' is None when present"):
            assert_dict_structure(data_with_none, ["key1"], ["key2"])
    
    def test_assert_list_structure(self):
        """Test list structure assertion helper"""
        from tests.conftest import assert_list_structure
        
        # Valid list
        data = [1, 2, 3]
        assert_list_structure(data, min_length=3)
        
        # List too short
        with pytest.raises(AssertionError, match="Expected at least 5 items"):
            assert_list_structure(data, min_length=5)
        
        # Invalid type
        with pytest.raises(AssertionError, match="Expected list"):
            assert_list_structure("not a list", min_length=0)
        
        # With item validator
        def validate_int(item):
            if not isinstance(item, int):
                raise ValueError("Item must be int")
        
        assert_list_structure(data, min_length=3, item_validator=validate_int)
        
        # Invalid item
        invalid_data = [1, 2, "not int"]
        with pytest.raises(AssertionError, match="Item 2 failed validation"):
            assert_list_structure(invalid_data, min_length=3, item_validator=validate_int)
    
    def test_create_mock_llm_response(self):
        """Test mock LLM response creation helper"""
        from tests.conftest import create_mock_llm_response
        
        mock_response = create_mock_llm_response("Test response")
        
        assert mock_response is not None
        assert hasattr(mock_response, 'choices')
        assert len(mock_response.choices) == 1
        assert hasattr(mock_response.choices[0], 'message')
        assert hasattr(mock_response.choices[0].message, 'content')
        assert mock_response.choices[0].message.content == "Test response" 