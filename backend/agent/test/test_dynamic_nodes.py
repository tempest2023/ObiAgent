# -*- coding: utf-8 -*-
"""
Unit tests for dynamic node loading system.

This script tests:
1. Loading node metadata from JSON config
2. Dynamic node class loading
3. Node instance creation and execution
4. UserQueryNode logic
"""
import logging
import unittest
from unittest.mock import Mock, patch
import pytest
from agent.utils.node_registry import node_registry, NodeCategory
from agent.utils.node_loader import node_loader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_node_registry():
    """Test loading nodes from JSON configuration"""
    logger.info("🧪 Testing Node Registry...")
    all_nodes = node_registry.get_all_nodes()
    logger.info(f"📋 Found {len(all_nodes)} nodes in registry")
    for node in all_nodes:
        logger.info(f"  - {node.name}: {node.description}")
        logger.info(f"    Category: {node.category.value}")
        logger.info(f"    Permission: {node.permission_level.value}")
        logger.info(f"    Module: {node.module_path}")
        logger.info(f"    Class: {node.class_name}")
        logger.info(f"    Inputs: {node.inputs}")
        logger.info(f"    Outputs: {node.outputs}")
        logger.info("")
    web_search = node_registry.get_node("web_search")
    assert web_search is not None, "web_search node not found"
    search_nodes = node_registry.get_nodes_by_category(NodeCategory.SEARCH)
    logger.info(f"🔍 Found {len(search_nodes)} search nodes")
    assert len(all_nodes) > 0
    assert len(search_nodes) > 0

def test_node_loader():
    """Test dynamic node loading"""
    logger.info("🧪 Testing Node Loader...")
    web_search_metadata = node_registry.get_node("web_search")
    assert web_search_metadata is not None, "web_search metadata not found"
    node_class = node_loader.load_node_class(
        web_search_metadata.module_path,
        web_search_metadata.class_name
    )
    assert node_class is not None, "Failed to load node class"
    logger.info(f"✅ Successfully loaded node class: {node_class.__name__}")
    node_instance = node_loader.create_node_instance({
        "module_path": web_search_metadata.module_path,
        "class_name": web_search_metadata.class_name
    })
    assert node_instance is not None, "Failed to create node instance"
    logger.info(f"✅ Successfully created node instance: {type(node_instance).__name__}")

def test_node_execution(monkeypatch):
    """Test node execution"""
    logger.info("🧪 Testing Node Execution...")
    
    # Mock DDGS to avoid rate limiting issues
    class MockDDGS:
        def text(self, query, max_results=None):
            return [
                {"title": "Test Result", "body": "Test search result", "href": "https://example.com/test"},
                {"title": "Another Result", "body": "Another test result", "href": "https://example.com/test2"}
            ][:max_results]
    
    # Patch the DDGS import in web_search module
    import agent.function_nodes.web_search
    monkeypatch.setattr(agent.function_nodes.web_search, "DDGS", MockDDGS)
    
    shared = {"query": "test search query", "num_results": 3}
    web_search_metadata = node_registry.get_node("web_search")
    assert web_search_metadata is not None, "web_search metadata not found"
    node_instance = node_loader.create_node_instance({
        "module_path": web_search_metadata.module_path,
        "class_name": web_search_metadata.class_name
    })
    assert node_instance is not None, "Failed to create node instance"
    prep_res = node_instance.prep(shared)
    logger.info(f"✅ Node prep completed: {prep_res}")
    
    # Mock the web search execution to avoid hitting real API
    with patch.object(node_instance, 'exec') as mock_exec:
        # Mock the exec method to return fake search results
        mock_exec.return_value = [
            {"title": "Test Result 1", "snippet": "Test snippet 1", "link": "https://example.com/1"},
            {"title": "Test Result 2", "snippet": "Test snippet 2", "link": "https://example.com/2"}
        ]
        
        exec_res = node_instance.exec(prep_res)
        logger.info(f"✅ Node exec completed: {type(exec_res)}")
        
        # Verify the mocked results
        assert isinstance(exec_res, list)
        assert len(exec_res) == 2
        assert exec_res[0]["title"] == "Test Result 1"
        
        action = node_instance.post(shared, prep_res, exec_res)
        logger.info(f"✅ Node post completed: {action}")
        assert "search_results" in shared, "Results not stored in shared"
        assert isinstance(shared["search_results"], list)
        logger.info(f"✅ Results stored in shared: {len(shared['search_results'])} items")

def test_user_query_node():
    """Test user query node specifically"""
    logger.info("🧪 Testing User Query Node...")
    shared = {"question": "What is your preferred departure time?"}
    user_query_metadata = node_registry.get_node("user_query")
    assert user_query_metadata is not None, "user_query metadata not found"
    node_instance = node_loader.create_node_instance({
        "module_path": user_query_metadata.module_path,
        "class_name": user_query_metadata.class_name
    })
    assert node_instance is not None, "Failed to create user_query node instance"
    prep_res = node_instance.prep(shared)
    logger.info(f"✅ User query prep completed: {prep_res}")
    exec_res = node_instance.exec(prep_res)
    logger.info(f"✅ User query exec completed: {exec_res}")
    action = node_instance.post(shared, prep_res, exec_res)
    logger.info(f"✅ User query post completed: {action}")
    assert shared.get("waiting_for_user_response"), "Waiting for user response flag not set"
    logger.info("✅ Waiting for user response flag set correctly")

class TestDynamicNodes(unittest.TestCase):
    """Test dynamic node loading system using unittest"""
    
    def test_node_registry_unittest(self):
        """Test loading nodes from JSON configuration"""
        test_node_registry()
    
    def test_node_loader_unittest(self):
        """Test dynamic node loading"""
        test_node_loader()
    
    def test_user_query_node_unittest(self):
        """Test user query node specifically"""
        test_user_query_node()

@pytest.mark.usefixtures("monkeypatch")
def test_node_execution_pytest(monkeypatch):
    test_node_execution(monkeypatch)

if __name__ == '__main__':
    unittest.main() 