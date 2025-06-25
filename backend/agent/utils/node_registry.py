"""
Node Registry System

This module provides a registry of available nodes that the agent can use
to design workflows. Each node has metadata describing its purpose, inputs,
outputs, and whether it requires user permission.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class NodeCategory(Enum):
    """Categories for different types of nodes"""
    SEARCH = "search"
    ANALYSIS = "analysis"
    CREATION = "creation"
    TRANSFORMATION = "transformation"
    COMMUNICATION = "communication"
    PAYMENT = "payment"
    BOOKING = "booking"
    UTILITY = "utility"

class PermissionLevel(Enum):
    """Permission levels for nodes"""
    NONE = "none"
    BASIC = "basic"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"

@dataclass
class NodeMetadata:
    """Metadata for a node in the registry"""
    name: str
    description: str
    category: NodeCategory
    permission_level: PermissionLevel
    inputs: List[str]
    outputs: List[str]
    examples: List[Dict[str, Any]]
    estimated_cost: Optional[float] = None
    estimated_time: Optional[int] = None  # in seconds

class NodeRegistry:
    """Registry of available nodes for workflow design"""
    
    def __init__(self):
        self.nodes: Dict[str, NodeMetadata] = {}
        self._initialize_default_nodes()
    
    def _initialize_default_nodes(self):
        """Initialize the registry with default nodes"""
        
        # Search and Information Nodes
        self.register_node(NodeMetadata(
            name="web_search",
            description="Search the web for current information",
            category=NodeCategory.SEARCH,
            permission_level=PermissionLevel.NONE,
            inputs=["query"],
            outputs=["search_results"],
            examples=[
                {"query": "flight prices Los Angeles to Shanghai", "output": "Current flight prices and options"}
            ]
        ))
        
        self.register_node(NodeMetadata(
            name="flight_search",
            description="Search for flight options and prices",
            category=NodeCategory.SEARCH,
            permission_level=PermissionLevel.BASIC,
            inputs=["origin", "destination", "date", "preferences"],
            outputs=["flight_options"],
            examples=[
                {"origin": "LAX", "destination": "PVG", "date": "2024-03-15", "preferences": "afternoon departure"}
            ]
        ))
        
        self.register_node(NodeMetadata(
            name="hotel_search", 
            description="Search for hotel options and prices",
            category=NodeCategory.SEARCH,
            permission_level=PermissionLevel.BASIC,
            inputs=["location", "check_in", "check_out", "preferences"],
            outputs=["hotel_options"],
            examples=[
                {"location": "Shanghai", "check_in": "2024-03-15", "check_out": "2024-03-20", "preferences": "budget friendly"}
            ]
        ))
        
        # Analysis Nodes
        self.register_node(NodeMetadata(
            name="cost_analysis",
            description="Analyze costs and find best value options",
            category=NodeCategory.ANALYSIS,
            permission_level=PermissionLevel.NONE,
            inputs=["options", "criteria"],
            outputs=["analysis_result"],
            examples=[
                {"options": "flight_options", "criteria": "cost_performance"}
            ]
        ))
        
        self.register_node(NodeMetadata(
            name="preference_matcher",
            description="Match user preferences with available options",
            category=NodeCategory.ANALYSIS,
            permission_level=PermissionLevel.NONE,
            inputs=["options", "preferences"],
            outputs=["matched_options"],
            examples=[
                {"options": "flight_options", "preferences": "afternoon departure, budget friendly"}
            ]
        ))
        
        # Communication Nodes
        self.register_node(NodeMetadata(
            name="user_query",
            description="Ask user for additional information or clarification",
            category=NodeCategory.COMMUNICATION,
            permission_level=PermissionLevel.NONE,
            inputs=["question"],
            outputs=["user_response"],
            examples=[
                {"question": "What is your budget range for this flight?"}
            ]
        ))
        
        self.register_node(NodeMetadata(
            name="permission_request",
            description="Request user permission for sensitive operations",
            category=NodeCategory.COMMUNICATION,
            permission_level=PermissionLevel.NONE,
            inputs=["operation", "details"],
            outputs=["permission_granted"],
            examples=[
                {"operation": "payment", "details": "Book flight for $850 using saved payment method"}
            ]
        ))
        
        # Booking and Payment Nodes
        self.register_node(NodeMetadata(
            name="flight_booking",
            description="Book a flight ticket",
            category=NodeCategory.BOOKING,
            permission_level=PermissionLevel.CRITICAL,
            inputs=["flight_option", "passenger_info", "payment_info"],
            outputs=["booking_confirmation"],
            examples=[
                {"flight_option": "selected_flight", "passenger_info": "user_details", "payment_info": "payment_method"}
            ]
        ))
        
        self.register_node(NodeMetadata(
            name="payment_processing",
            description="Process payment for booking",
            category=NodeCategory.PAYMENT,
            permission_level=PermissionLevel.CRITICAL,
            inputs=["amount", "payment_method", "description"],
            outputs=["payment_confirmation"],
            examples=[
                {"amount": 850.00, "payment_method": "credit_card", "description": "Flight booking LAX-PVG"}
            ]
        ))
        
        # Utility Nodes
        self.register_node(NodeMetadata(
            name="data_formatter",
            description="Format data for better presentation",
            category=NodeCategory.TRANSFORMATION,
            permission_level=PermissionLevel.NONE,
            inputs=["raw_data", "format_type"],
            outputs=["formatted_data"],
            examples=[
                {"raw_data": "flight_options", "format_type": "comparison_table"}
            ]
        ))
        
        self.register_node(NodeMetadata(
            name="result_summarizer",
            description="Summarize results and provide recommendations",
            category=NodeCategory.ANALYSIS,
            permission_level=PermissionLevel.NONE,
            inputs=["results", "user_question"],
            outputs=["summary"],
            examples=[
                {"results": "analysis_results", "user_question": "Help book a flight ticket from Los Angeles to Shanghai"}
            ]
        ))
    
    def register_node(self, metadata: NodeMetadata):
        """Register a new node in the registry"""
        self.nodes[metadata.name] = metadata
    
    def get_node(self, name: str) -> Optional[NodeMetadata]:
        """Get a node by name"""
        return self.nodes.get(name)
    
    def get_nodes_by_category(self, category: NodeCategory) -> List[NodeMetadata]:
        """Get all nodes in a specific category"""
        return [node for node in self.nodes.values() if node.category == category]
    
    def get_nodes_by_permission_level(self, level: PermissionLevel) -> List[NodeMetadata]:
        """Get all nodes with a specific permission level"""
        return [node for node in self.nodes.values() if node.permission_level == level]
    
    def get_all_nodes(self) -> List[NodeMetadata]:
        """Get all registered nodes"""
        return list(self.nodes.values())
    
    def get_nodes_for_question(self, question: str) -> List[NodeMetadata]:
        """Get relevant nodes for a specific question"""
        # Simple keyword-based matching - could be enhanced with embeddings
        question_lower = question.lower()
        relevant_nodes = []
        
        for node in self.nodes.values():
            # Check if question contains keywords related to the node
            if any(keyword in question_lower for keyword in node.description.lower().split()):
                relevant_nodes.append(node)
            elif any(keyword in question_lower for keyword in node.name.lower().split('_')):
                relevant_nodes.append(node)
        
        return relevant_nodes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary for LLM consumption"""
        return {
            "nodes": {
                name: {
                    "name": metadata.name,
                    "description": metadata.description,
                    "category": metadata.category.value,
                    "permission_level": metadata.permission_level.value,
                    "inputs": metadata.inputs,
                    "outputs": metadata.outputs,
                    "examples": metadata.examples
                }
                for name, metadata in self.nodes.items()
            }
        }

# Global registry instance
node_registry = NodeRegistry() 