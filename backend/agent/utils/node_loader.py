"""
Dynamic Node Loader

This module provides functionality to dynamically load and instantiate
function nodes based on JSON configuration metadata.
"""

import importlib
import logging
from typing import Dict, Any, Optional, Type
from pocketflow import Node

logger = logging.getLogger(__name__)

class NodeLoader:
    """Dynamic loader for function nodes based on JSON configuration"""
    
    def __init__(self):
        self._node_cache: Dict[str, Type[Node]] = {}
    
    def load_node_class(self, module_path: str, class_name: str) -> Optional[Type[Node]]:
        """
        Dynamically load a node class from a module.
        
        Args:
            module_path: Full module path (e.g., "agent.function_nodes.web_search")
            class_name: Name of the class to load (e.g., "WebSearchNode")
            
        Returns:
            The node class if successfully loaded, None otherwise
        """
        cache_key = f"{module_path}.{class_name}"
        
        # Check cache first
        if cache_key in self._node_cache:
            logger.debug(f"📦 NodeLoader: Using cached node class: {cache_key}")
            return self._node_cache[cache_key]
        
        try:
            logger.info(f"🔄 NodeLoader: Loading node class: {cache_key}")
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class from the module
            node_class = getattr(module, class_name)
            
            # Verify it's a Node subclass
            if not issubclass(node_class, Node):
                logger.error(f"❌ NodeLoader: {class_name} is not a Node subclass")
                return None
            
            # Cache the class
            self._node_cache[cache_key] = node_class
            
            logger.info(f"✅ NodeLoader: Successfully loaded node class: {cache_key}")
            return node_class
            
        except ImportError as e:
            logger.error(f"❌ NodeLoader: Failed to import module {module_path}: {e}")
            return None
        except AttributeError as e:
            logger.error(f"❌ NodeLoader: Failed to get class {class_name} from module {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ NodeLoader: Unexpected error loading node class {cache_key}: {e}")
            return None
    
    def create_node_instance(self, node_metadata: Dict[str, Any]) -> Optional[Node]:
        """
        Create a node instance from metadata.
        
        Args:
            node_metadata: Node metadata dictionary containing module_path and class_name
            
        Returns:
            Node instance if successfully created, None otherwise
        """
        module_path = node_metadata.get("module_path")
        class_name = node_metadata.get("class_name")
        
        if not module_path or not class_name:
            logger.error(f"❌ NodeLoader: Missing module_path or class_name in metadata: {node_metadata}")
            return None
        
        # Load the node class
        node_class = self.load_node_class(module_path, class_name)
        if not node_class:
            return None
        
        try:
            # Create an instance
            node_instance = node_class()
            logger.info(f"✅ NodeLoader: Created node instance: {node_metadata.get('name', 'unknown')}")
            return node_instance
            
        except Exception as e:
            logger.error(f"❌ NodeLoader: Failed to create node instance for {node_metadata.get('name', 'unknown')}: {e}")
            return None
    
    def get_available_nodes(self) -> Dict[str, Type[Node]]:
        """Get all cached node classes"""
        return self._node_cache.copy()
    
    def clear_cache(self):
        """Clear the node cache"""
        self._node_cache.clear()
        logger.info("🧹 NodeLoader: Cleared node cache")

# Global node loader instance
node_loader = NodeLoader() 