from pocketflow import AsyncFlow
from .nodes import (
    WorkflowDesignerNode, 
    WorkflowExecutorNode, 
    UserInteractionNode, 
    WorkflowOptimizerNode,
    StreamingChatNode
)

def create_streaming_chat_flow():
    """Create the legacy streaming chat flow for backward compatibility"""
    chat_node = StreamingChatNode()
    return AsyncFlow(start=chat_node)

def create_general_agent_flow():
    """
    Create the general agent flow that can:
    1. Design workflows based on user questions
    2. Execute workflows dynamically
    3. Handle user interactions and permissions
    4. Optimize workflows based on results
    """
    # Create nodes
    designer = WorkflowDesignerNode()
    executor = WorkflowExecutorNode()
    interaction = UserInteractionNode()
    optimizer = WorkflowOptimizerNode()
    
    # Connect the workflow design flow
    designer - "execute_workflow" >> executor
    executor - "workflow_complete" >> optimizer
    executor - "wait_for_response" >> interaction
    executor - "wait_for_permission" >> interaction
    
    # Connect user interaction flow
    interaction - "wait_for_response" >> interaction  # Loop until response
    interaction - "wait_for_permission" >> interaction  # Loop until permission
    interaction - "continue_workflow" >> executor
    
    # Connect optimization flow
    optimizer - "optimize_workflow" >> designer  # Go back to design with improvements
    optimizer - "workflow_success" >> None  # End flow
    
    return AsyncFlow(start=designer)

def create_simple_agent_flow():
    """
    Create a simpler agent flow for basic questions
    """
    designer = WorkflowDesignerNode()
    executor = WorkflowExecutorNode()
    
    designer - "execute_workflow" >> executor
    executor - "workflow_complete" >> None
    
    return AsyncFlow(start=designer) 