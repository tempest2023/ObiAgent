"""
Agent Nodes for General Problem Solving

This module contains nodes for the general agent system that can:
1. Analyze user questions and design workflows
2. Execute workflows dynamically
3. Handle user interactions and permissions
4. Learn from successful workflows
"""

import asyncio
import json
import yaml
import logging
from typing import Dict, List, Any, Optional
from pocketflow import AsyncNode, Node
from .utils.stream_llm import stream_llm, call_llm
from .utils.node_registry import node_registry
from .utils.workflow_store import workflow_store
from .utils.permission_manager import permission_manager
from .utils.node_loader import node_loader
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.analyze_results import AnalyzeResultsNode
from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.cost_analysis import CostAnalysisNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode
from agent.function_nodes.user_query import UserQueryNode
from agent.function_nodes.permission_request import PermissionRequestNode
from agent.function_nodes.data_formatter import DataFormatterNode

# Configure logging
logger = logging.getLogger(__name__)

class UserResponseRequiredException(Exception):
    """Exception raised when a node requires user response"""
    
    def __init__(self, node_name: str, question: str, node_index: int):
        self.node_name = node_name
        self.question = question
        self.node_index = node_index
        super().__init__(f"User response required for node {node_name}")

class WorkflowDesignerNode(AsyncNode):
    """
    Node that designs workflows based on user questions.
    Example:
        >>> node = WorkflowDesignerNode()
        >>> shared = {"user_message": "Book a flight from LA to NY"}
        >>> await node.prep_async(shared)
        # Prepares workflow design context
        >>> result = await node.exec_async(prep_res)
        # Returns workflow design
        >>> action = await node.post_async(shared, prep_res, result)
        # Stores workflow design in shared store
    """
    
    async def prep_async(self, shared):
        """Prepare workflow design context"""
        logger.info("🔄 WorkflowDesignerNode: Starting prep_async")
        
        user_message = shared.get("user_message", "")
        if not user_message:
            raise ValueError("User message is required")
        
        # Get relevant nodes for the question
        relevant_nodes = node_registry.get_nodes_for_question(user_message)
        
        # Create workflow design context
        workflow_context = {
            "user_message": user_message,
            "relevant_nodes": [node.name for node in relevant_nodes],
            "node_details": [
                {
                    "name": node.name,
                    "description": node.description,
                    "category": node.category.value,
                    "permission_level": node.permission_level.value
                }
                for node in relevant_nodes
            ]
        }
        
        logger.info(f"📋 WorkflowDesignerNode: Found {len(relevant_nodes)} relevant nodes")
        logger.info("✅ WorkflowDesignerNode: prep_async completed")
        return workflow_context
    
    async def exec_async(self, prep_res):
        """Design workflow based on user question"""
        logger.info("🔄 WorkflowDesignerNode: Starting exec_async")
        
        user_message = prep_res["user_message"]
        relevant_nodes = prep_res["relevant_nodes"]
        
        # Create workflow design
        workflow_design = {
            "workflow": {
                "name": f"Workflow for: {user_message[:50]}...",
                "description": f"Automated workflow to handle: {user_message}",
                "nodes": relevant_nodes,
                "connections": self._create_connections(relevant_nodes),
                "shared_store_schema": self._create_schema(relevant_nodes),
                "estimated_steps": len(relevant_nodes),
                "requires_permission": self._check_permission_requirements(relevant_nodes)
            },
            "execution_order": relevant_nodes,
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "version": "1.0",
                "tags": self._extract_tags(user_message)
            }
        }
        
        logger.info(f"🎯 WorkflowDesignerNode: Created workflow with {len(relevant_nodes)} nodes")
        logger.info("✅ WorkflowDesignerNode: exec_async completed")
        return workflow_design
    
    def _create_connections(self, nodes):
        """Create connections between nodes"""
        connections = []
        for i in range(len(nodes) - 1):
            connections.append({
                "from": nodes[i],
                "to": nodes[i + 1],
                "condition": "default"
            })
        return connections
    
    def _create_schema(self, nodes):
        """Create shared store schema based on nodes"""
        schema = {
            "user_message": "User's original question",
            "workflow_results": "Results from workflow execution"
        }
        
        # Add node-specific schemas
        for node_name in nodes:
            schema[f"{node_name}_result"] = f"Result from {node_name} node"
        
        return schema
    
    def _check_permission_requirements(self, nodes):
        """Check if workflow requires permissions"""
        for node_name in nodes:
            node_metadata = node_registry.get_node(node_name)
            if node_metadata and node_metadata.permission_level.value in ["MEDIUM", "HIGH"]:
                return True
        return False
    
    def _extract_tags(self, user_message):
        """Extract tags from user message"""
        tags = []
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["flight", "book", "airline", "ticket"]):
            tags.append("flight_booking")
        if any(word in message_lower for word in ["search", "find", "look"]):
            tags.append("search")
        if any(word in message_lower for word in ["cost", "price", "budget"]):
            tags.append("cost_analysis")
        if any(word in message_lower for word in ["payment", "pay", "money"]):
            tags.append("payment")
        
        return tags
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store workflow design in shared store"""
        logger.info("🔄 WorkflowDesignerNode: Starting post_async")
        
        # Store workflow design
        shared["workflow_design"] = exec_res
        
        logger.info("💾 WorkflowDesignerNode: Stored workflow design in shared store")
        logger.info("✅ WorkflowDesignerNode: post_async completed, returning 'default'")
        return "default"

class WorkflowExecutorNode(AsyncNode):
    """
    Node that executes workflows.
    Example:
        >>> node = WorkflowExecutorNode()
        >>> shared = {"workflow_design": {...}, "websocket": ws}
        >>> await node.prep_async(shared)
        # Prepares execution context
        >>> result = await node.exec_async(prep_res)
        # Returns execution results
        >>> action = await node.post_async(shared, prep_res, result)
        # Stores results in shared store
    """
    
    async def prep_async(self, shared):
        """Prepare workflow execution context"""
        logger.info("🔄 WorkflowExecutorNode: Starting prep_async")
        
        workflow_design = shared.get("workflow_design")
        if not workflow_design:
            raise ValueError("Workflow design is required")
        
        execution_order = workflow_design.get("execution_order", [])
        if not execution_order:
            raise ValueError("Execution order is required")
        
        logger.info(f"📋 WorkflowExecutorNode: Prepared execution for {len(execution_order)} nodes")
        logger.info("✅ WorkflowExecutorNode: prep_async completed")
        return {"execution_order": execution_order, "workflow_design": workflow_design}
    
    async def exec_async(self, prep_res):
        """Execute workflow nodes"""
        logger.info("🔄 WorkflowExecutorNode: Starting exec_async")
        
        execution_order = prep_res["execution_order"]
        workflow_design = prep_res["workflow_design"]
        websocket = workflow_design.get("websocket")
        
        results = {}
        
        for i, node_name in enumerate(execution_order):
            logger.info(f"🔄 WorkflowExecutorNode: Executing node {i+1}/{len(execution_order)}: {node_name}")
            
            try:
                # Get node metadata from registry
                node_metadata = node_registry.get_node(node_name)
                if not node_metadata:
                    logger.warning(f"⚠️ WorkflowExecutorNode: No metadata found for {node_name}, returning mock result")
                    result = f"Mock result for {node_name}"
                else:
                    # Create node instance using dynamic loader
                    node_instance = node_loader.create_node_instance({
                        "module_path": node_metadata.module_path,
                        "class_name": node_metadata.class_name
                    })
                    
                    if node_instance is None:
                        logger.warning(f"⚠️ WorkflowExecutorNode: Failed to create instance for {node_name}, returning mock result")
                        result = f"Mock result for {node_name}"
                    else:
                        # Execute the node
                        prep_res_node = node_instance.prep(shared)
                        result = node_instance.exec(prep_res_node)
                        action = node_instance.post(shared, prep_res_node, result)
                        
                        # Special handling for user_query node
                        if node_name == "user_query" and action == "wait_for_response":
                            logger.info("⏳ WorkflowExecutorNode: User query node requires response, pausing execution")
                            
                            # Send question to user via websocket
                            if websocket:
                                try:
                                    await websocket.send_text(json.dumps({
                                        "type": "user_question",
                                        "content": {
                                            "question": prep_res_node,
                                            "requires_response": True
                                        }
                                    }))
                                    logger.info("📤 WorkflowExecutorNode: Sent user question via websocket")
                                except Exception as e:
                                    logger.error(f"❌ WorkflowExecutorNode: Failed to send user question: {e}")
                            
                            # Check if this is a demo environment (DemoWebSocket)
                            is_demo = hasattr(websocket, 'get_auto_response')
                            
                            if is_demo:
                                logger.info("🎭 WorkflowExecutorNode: Demo environment detected, using auto-response")
                                # Get auto response from demo websocket
                                auto_response = websocket.get_auto_response(prep_res_node)
                                shared["user_response"] = auto_response
                                shared["waiting_for_user_response"] = False
                                logger.info(f"🤖 WorkflowExecutorNode: Auto response: {auto_response[:50]}...")
                            else:
                                # In production, pause execution and wait for server to resume
                                logger.info("⏸️ WorkflowExecutorNode: Pausing execution, waiting for server to resume")
                                shared["waiting_for_user_response"] = True
                                shared["current_node_index"] = i  # Save current node index
                                shared["current_node_name"] = node_name
                                
                                # Raise special exception to pause execution
                                raise UserResponseRequiredException(
                                    node_name=node_name,
                                    question=prep_res_node,
                                    node_index=i
                                )
                            
                            # Get the user response
                            user_response = shared.get("user_response", "")
                            logger.info(f"✅ WorkflowExecutorNode: Received user response: {user_response[:50]}...")
                            
                            # Update the result with user response
                            result = user_response
                            shared[f"{node_name}_result"] = user_response
                            
                            # Clear the waiting flag
                            shared["waiting_for_user_response"] = False
                            shared["user_response"] = None
                        
                        # Special handling for permission_request node
                        elif node_name == "permission_request" and action == "wait_for_permission":
                            logger.info("⏳ WorkflowExecutorNode: Permission request node requires response, pausing execution")
                            
                            # Wait for permission response
                            waiting_logged = False
                            while shared.get("waiting_for_permission", False):
                                if not waiting_logged:
                                    logger.info("⏳ WorkflowExecutorNode: Waiting for permission response...")
                                    waiting_logged = True
                                await asyncio.sleep(0.1)
                            
                            # Get the permission response
                            permission_response = shared.get("permission_response", {})
                            logger.info(f"✅ WorkflowExecutorNode: Received permission response: {permission_response}")
                            
                            # Update the result with permission response
                            result = permission_response
                            shared[f"{node_name}_result"] = permission_response
                            
                            # Clear the waiting flag
                            shared["waiting_for_permission"] = False
                            shared["permission_response"] = None
                
                results[node_name] = result
                logger.info(f"✅ WorkflowExecutorNode: Node {node_name} completed successfully")
                
                if websocket:
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "node_complete",
                            "content": {
                                "node": node_name,
                                "result": result
                            }
                        }))
                        logger.info(f"📤 WorkflowExecutorNode: Sent completion message for {node_name}")
                    except Exception as e:
                        logger.error(f"❌ WorkflowExecutorNode: Failed to send completion message: {e}")
                        
            except UserResponseRequiredException as e:
                # This is an expected exception to pause execution
                logger.info(f"⏸️ WorkflowExecutorNode: Paused for user response: {e}")
                # Clear current node index since we've handled this exception
                shared.pop("current_node_index", None)
                shared.pop("current_node_name", None)
                raise  # Re-raise exception for upper layer to handle
                
            except Exception as e:
                logger.error(f"❌ WorkflowExecutorNode: Node {node_name} failed with error: {e}")
                if websocket:
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "node_error",
                            "content": {
                                "node": node_name,
                                "error": str(e)
                            }
                        }))
                        logger.info(f"📤 WorkflowExecutorNode: Sent error message for {node_name}")
                    except Exception as send_error:
                        logger.error(f"❌ WorkflowExecutorNode: Failed to send error message: {send_error}")
                raise
        
        logger.info(f"🎉 WorkflowExecutorNode: All {len(execution_order)} nodes completed successfully")
        logger.info("✅ WorkflowExecutorNode: exec_async completed")
        return results
    
    async def post_async(self, shared, prep_res, exec_res):
        logger.info("🔄 WorkflowExecutorNode: Starting post_async")
        
        # Store workflow results
        shared["workflow_results"] = exec_res
        
        logger.info(f"💾 WorkflowExecutorNode: Stored {len(exec_res)} workflow results in shared store")
        
        # Save successful workflow to store
        workflow_design = prep_res["workflow_design"]
        
        # Safely extract workflow components with fallbacks
        workflow = workflow_design.get("workflow", {})
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", [])
        shared_store_schema = workflow.get("shared_store_schema", {})
        
        # If shared_store_schema is not available, create a basic one
        if not shared_store_schema:
            logger.warning("⚠️ WorkflowExecutorNode: No shared_store_schema found, creating basic schema")
            shared_store_schema = {
                "user_message": "User's original question",
                "workflow_results": "Results from workflow execution"
            }
        
        workflow_store.save_workflow(
            question=shared.get("user_message", ""),
            nodes=nodes,
            connections=connections,
            shared_store_schema=shared_store_schema,
            success=True,
            tags=["flight_booking", "cost_analysis"]
        )
        
        logger.info("💾 WorkflowExecutorNode: Saved workflow to workflow store")
        logger.info("✅ WorkflowExecutorNode: post_async completed, returning 'workflow_complete'")
        return "workflow_complete"

class UserInteractionNode(AsyncNode):
    """
    Node that handles user interactions and responses (questions, permissions).
    Example:
        >>> node = UserInteractionNode()
        >>> shared = {"pending_user_question": "What is your budget?", "websocket": ws}
        >>> await node.prep_async(shared)
        # Prepares interaction context
        >>> result = await node.exec_async(prep_res)
        # Returns interaction result
        >>> action = await node.post_async(shared, prep_res, result)
        # Stores interaction result in shared store
    """
    
    async def prep_async(self, shared):
        """Prepare user interaction context"""
        logger.info("🔄 UserInteractionNode: Starting prep_async")
        
        # Check for pending user questions or permission requests
        pending_question = shared.get("pending_user_question")
        pending_permission = shared.get("pending_permission_request")
        
        if not pending_question and not pending_permission:
            raise ValueError("No pending user interaction found")
        
        interaction_context = {
            "type": "question" if pending_question else "permission",
            "content": pending_question or pending_permission,
            "websocket": shared.get("websocket")
        }
        
        logger.info(f"📋 UserInteractionNode: Prepared {interaction_context['type']} interaction")
        logger.info("✅ UserInteractionNode: prep_async completed")
        return interaction_context
    
    async def exec_async(self, prep_res):
        """Handle user interaction"""
        logger.info("🔄 UserInteractionNode: Starting exec_async")
        
        interaction_type = prep_res["type"]
        content = prep_res["content"]
        websocket = prep_res["websocket"]
        
        if interaction_type == "question":
            # Handle user question
            logger.info("❓ UserInteractionNode: Processing user question")
            
            # Send question to user
            if websocket:
                try:
                    await websocket.send_text(json.dumps({
                        "type": "user_question",
                        "content": {
                            "question": content,
                            "requires_response": True
                        }
                    }))
                    logger.info("📤 UserInteractionNode: Sent question to user")
                except Exception as e:
                    logger.error(f"❌ UserInteractionNode: Failed to send question: {e}")
            
            # Wait for response (in demo mode, use auto-response)
            if hasattr(websocket, 'get_auto_response'):
                response = websocket.get_auto_response(content)
                logger.info(f"🤖 UserInteractionNode: Auto response: {response[:50]}...")
            else:
                # In production, this would wait for actual user response
                response = "User response placeholder"
                logger.info("⏳ UserInteractionNode: Waiting for user response...")
            
            result = {
                "type": "question_response",
                "question": content,
                "response": response
            }
            
        else:  # permission
            # Handle permission request
            logger.info("🔐 UserInteractionNode: Processing permission request")
            
            # Send permission request to user
            if websocket:
                try:
                    await websocket.send_text(json.dumps({
                        "type": "permission_request",
                        "content": content
                    }))
                    logger.info("📤 UserInteractionNode: Sent permission request to user")
                except Exception as e:
                    logger.error(f"❌ UserInteractionNode: Failed to send permission request: {e}")
            
            # Wait for permission response (in demo mode, auto-approve)
            if hasattr(websocket, 'get_auto_permission'):
                permission_response = websocket.get_auto_permission(content)
                logger.info(f"🤖 UserInteractionNode: Auto permission: {permission_response}")
            else:
                # In production, this would wait for actual permission response
                permission_response = {"approved": True, "reason": "Auto-approved"}
                logger.info("⏳ UserInteractionNode: Waiting for permission response...")
            
            result = {
                "type": "permission_response",
                "request": content,
                "response": permission_response
            }
        
        logger.info("✅ UserInteractionNode: exec_async completed")
        return result
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store interaction result in shared store"""
        logger.info("🔄 UserInteractionNode: Starting post_async")
        
        result_type = exec_res["type"]
        
        if result_type == "question_response":
            # Store question response
            shared["user_response"] = exec_res["response"]
            shared["pending_user_question"] = None
            shared["waiting_for_user_response"] = False
            
        else:  # permission_response
            # Store permission response
            shared["permission_response"] = exec_res["response"]
            shared["pending_permission_request"] = None
            shared["waiting_for_permission"] = False
        
        logger.info(f"💾 UserInteractionNode: Stored {result_type} in shared store")
        logger.info("✅ UserInteractionNode: post_async completed, returning 'default'")
        return "default"

class WorkflowOptimizerNode(AsyncNode):
    """
    Node that optimizes workflows based on execution results.
    Example:
        >>> node = WorkflowOptimizerNode()
        >>> shared = {"workflow_results": {...}, "execution_metrics": {...}}
        >>> await node.prep_async(shared)
        # Prepares optimization context
        >>> result = await node.exec_async(prep_res)
        # Returns optimization suggestions
        >>> action = await node.post_async(shared, prep_res, result)
        # Stores optimization results in shared store
    """
    
    async def prep_async(self, shared):
        """Prepare workflow optimization context"""
        logger.info("🔄 WorkflowOptimizerNode: Starting prep_async")
        
        workflow_results = shared.get("workflow_results", {})
        execution_metrics = shared.get("execution_metrics", {})
        
        if not workflow_results:
            raise ValueError("Workflow results are required for optimization")
        
        optimization_context = {
            "workflow_results": workflow_results,
            "execution_metrics": execution_metrics,
            "optimization_targets": ["performance", "accuracy", "user_satisfaction"]
        }
        
        logger.info("📋 WorkflowOptimizerNode: Prepared optimization context")
        logger.info("✅ WorkflowOptimizerNode: prep_async completed")
        return optimization_context
    
    async def exec_async(self, prep_res):
        """Optimize workflow based on results"""
        logger.info("🔄 WorkflowOptimizerNode: Starting exec_async")
        
        workflow_results = prep_res["workflow_results"]
        execution_metrics = prep_res["execution_metrics"]
        
        # Analyze workflow performance
        optimization_suggestions = []
        
        # Check for failed nodes
        failed_nodes = [node for node, result in workflow_results.items() 
                       if isinstance(result, str) and "error" in result.lower()]
        
        if failed_nodes:
            optimization_suggestions.append({
                "type": "error_fix",
                "nodes": failed_nodes,
                "suggestion": "Review and fix failed nodes",
                "priority": "high"
            })
        
        # Check for performance issues
        if execution_metrics.get("total_time", 0) > 30:  # More than 30 seconds
            optimization_suggestions.append({
                "type": "performance",
                "suggestion": "Consider parallel execution or caching",
                "priority": "medium"
            })
        
        # Check for user satisfaction
        if execution_metrics.get("user_satisfaction", 0) < 0.7:
            optimization_suggestions.append({
                "type": "user_experience",
                "suggestion": "Improve result quality and user interaction",
                "priority": "high"
            })
        
        optimization_result = {
            "suggestions": optimization_suggestions,
            "metrics": execution_metrics,
            "workflow_health": "good" if not failed_nodes else "needs_attention"
        }
        
        logger.info(f"🎯 WorkflowOptimizerNode: Generated {len(optimization_suggestions)} optimization suggestions")
        logger.info("✅ WorkflowOptimizerNode: exec_async completed")
        return optimization_result
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store optimization results in shared store"""
        logger.info("🔄 WorkflowOptimizerNode: Starting post_async")
        
        # Store optimization results
        shared["workflow_optimization"] = exec_res
        
        logger.info("💾 WorkflowOptimizerNode: Stored optimization results in shared store")
        logger.info("✅ WorkflowOptimizerNode: post_async completed, returning 'default'")
        return "default"

class StreamingChatNode(AsyncNode):
    """
    Node that handles streaming chat responses.
    Example:
        >>> node = StreamingChatNode()
        >>> shared = {"user_message": "Hello", "websocket": ws}
        >>> await node.prep_async(shared)
        # Prepares streaming context
        >>> result = await node.exec_async(prep_res)
        # Returns streaming response
        >>> action = await node.post_async(shared, prep_res, result)
        # Streams response to user
    """
    
    async def prep_async(self, shared):
        """Prepare streaming chat context"""
        logger.info("🔄 StreamingChatNode: Starting prep_async")
        
        user_message = shared.get("user_message", "")
        websocket = shared.get("websocket")
        
        if not user_message:
            raise ValueError("User message is required")
        
        if not websocket:
            raise ValueError("WebSocket connection is required for streaming")
        
        streaming_context = {
            "user_message": user_message,
            "websocket": websocket,
            "streaming_config": {
                "chunk_size": 50,
                "delay": 0.1
            }
        }
        
        logger.info("📋 StreamingChatNode: Prepared streaming context")
        logger.info("✅ StreamingChatNode: prep_async completed")
        return streaming_context
    
    async def exec_async(self, prep_res):
        """Generate and stream chat response"""
        logger.info("🔄 StreamingChatNode: Starting exec_async")
        
        user_message = prep_res["user_message"]
        websocket = prep_res["websocket"]
        config = prep_res["streaming_config"]
        
        # Generate response (in real implementation, this would call LLM)
        response = f"Hello! I received your message: '{user_message}'. How can I help you today?"
        
        # Stream response in chunks
        chunks = [response[i:i+config["chunk_size"]] 
                 for i in range(0, len(response), config["chunk_size"])]
        
        for i, chunk in enumerate(chunks):
            try:
                await websocket.send_text(json.dumps({
                    "type": "stream_chunk",
                    "content": {
                        "chunk": chunk,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                }))
                logger.info(f"📤 StreamingChatNode: Sent chunk {i+1}/{len(chunks)}")
                await asyncio.sleep(config["delay"])
            except Exception as e:
                logger.error(f"❌ StreamingChatNode: Failed to send chunk {i}: {e}")
                break
        
        logger.info("✅ StreamingChatNode: exec_async completed")
        return {"response": response, "chunks_sent": len(chunks)}
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store streaming results in shared store"""
        logger.info("🔄 StreamingChatNode: Starting post_async")
        
        # Store streaming results
        shared["streaming_response"] = exec_res["response"]
        shared["chunks_sent"] = exec_res["chunks_sent"]
        
        logger.info(f"💾 StreamingChatNode: Stored streaming response ({exec_res['chunks_sent']} chunks)")
        logger.info("✅ StreamingChatNode: post_async completed, returning 'default'")
        return "default"

class WorkflowEndNode(AsyncNode):
    """
    Node that finalizes workflow execution and provides summary.
    Example:
        >>> node = WorkflowEndNode()
        >>> shared = {"workflow_results": {...}, "user_message": "..."}
        >>> await node.prep_async(shared)
        # Prepares summary context
        >>> result = await node.exec_async(prep_res)
        # Returns workflow summary
        >>> action = await node.post_async(shared, prep_res, result)
        # Stores final results in shared store
    """
    
    async def prep_async(self, shared):
        """Prepare workflow summary context"""
        logger.info("🔄 WorkflowEndNode: Starting prep_async")
        
        workflow_results = shared.get("workflow_results", {})
        user_message = shared.get("user_message", "")
        
        if not workflow_results:
            raise ValueError("Workflow results are required for summary")
        
        summary_context = {
            "workflow_results": workflow_results,
            "user_message": user_message,
            "execution_summary": {
                "total_nodes": len(workflow_results),
                "successful_nodes": len([r for r in workflow_results.values() 
                                       if not isinstance(r, str) or "error" not in r.lower()]),
                "failed_nodes": len([r for r in workflow_results.values() 
                                   if isinstance(r, str) and "error" in r.lower()])
            }
        }
        
        logger.info("📋 WorkflowEndNode: Prepared summary context")
        logger.info("✅ WorkflowEndNode: prep_async completed")
        return summary_context
    
    async def exec_async(self, prep_res):
        """Generate workflow summary"""
        logger.info("🔄 WorkflowEndNode: Starting exec_async")
        
        workflow_results = prep_res["workflow_results"]
        user_message = prep_res["user_message"]
        execution_summary = prep_res["execution_summary"]
        
        # Generate summary
        summary = {
            "user_question": user_message,
            "execution_summary": execution_summary,
            "key_results": {},
            "recommendations": [],
            "next_steps": []
        }
        
        # Extract key results
        for node_name, result in workflow_results.items():
            if isinstance(result, dict) and "recommendation" in result:
                summary["key_results"][node_name] = result["recommendation"]
            elif isinstance(result, str) and len(result) < 100:
                summary["key_results"][node_name] = result
        
        # Generate recommendations
        if execution_summary["failed_nodes"] > 0:
            summary["recommendations"].append("Review failed nodes and retry workflow")
        
        if execution_summary["successful_nodes"] > 0:
            summary["recommendations"].append("Workflow completed successfully")
        
        # Generate next steps
        summary["next_steps"].append("Review results and take action")
        summary["next_steps"].append("Optimize workflow if needed")
        
        logger.info(f"📊 WorkflowEndNode: Generated summary with {len(summary['key_results'])} key results")
        logger.info("✅ WorkflowEndNode: exec_async completed")
        return summary
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store final results in shared store"""
        logger.info("🔄 WorkflowEndNode: Starting post_async")
        
        # Store final results
        shared["workflow_summary"] = exec_res
        shared["workflow_completed"] = True
        
        logger.info("💾 WorkflowEndNode: Stored final results in shared store")
        logger.info("✅ WorkflowEndNode: post_async completed, returning 'workflow_end'")
        return "workflow_end" 