from pocketflow import AsyncFlow
from .nodes import (
    WorkflowDesignerNode, 
    WorkflowExecutorNode, 
    UserInteractionNode, 
    WorkflowOptimizerNode,
    StreamingChatNode,
    WorkflowEndNode,
    RethinkingWorkflowNode
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
    rethinking = RethinkingWorkflowNode()
    executor = WorkflowExecutorNode()
    interaction = UserInteractionNode()
    optimizer = WorkflowOptimizerNode()
    end_node = WorkflowEndNode()
    
    # Connect the workflow design flow
    designer - "designed" >> rethinking
    rethinking - "needs_revision" >> designer
    rethinking - "ready_to_execute" >> executor
    executor - "workflow_complete" >> optimizer
    executor - "wait_for_response" >> interaction
    executor - "wait_for_permission" >> interaction
    
    # Connect user interaction flow
    interaction - "wait_for_response" >> interaction  # Loop until response
    interaction - "wait_for_permission" >> interaction  # Loop until permission
    interaction - "continue_workflow" >> executor
    
    # Connect optimization flow
    optimizer - "optimize_workflow" >> designer  # Go back to design with improvements
    optimizer - "workflow_success" >> end_node  # End flow with completion node
    
    return AsyncFlow(start=designer)

def create_simple_agent_flow():
    """
    Create a simpler agent flow for basic questions
    """
    designer = WorkflowDesignerNode()
    rethinking = RethinkingWorkflowNode()
    executor = WorkflowExecutorNode()
    end_node = WorkflowEndNode()
    
    designer - "designed" >> rethinking
    rethinking - "needs_revision" >> designer
    rethinking - "ready_to_execute" >> executor
    executor - "workflow_complete" >> end_node
    
    return AsyncFlow(start=designer) 