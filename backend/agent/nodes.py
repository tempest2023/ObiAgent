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

class WorkflowDesignerNode(AsyncNode):
    """
    Node that analyzes user questions and designs workflows.
    Example:
        >>> node = WorkflowDesignerNode()
        >>> shared = {"user_message": "Book a flight from LA to Shanghai"}
        >>> await node.prep_async(shared)
        # Returns context for LLM to design a workflow
    """
    
    async def prep_async(self, shared):
        logger.info("🔄 WorkflowDesignerNode: Starting prep_async")
        
        # Ensure shared is a dictionary
        if not isinstance(shared, dict):
            shared = {}
            logger.warning("WorkflowDesignerNode: shared parameter is not a dictionary, using empty dict")
        
        user_question = shared.get("user_message", "")
        conversation_history = shared.get("conversation_history", [])
        websocket = shared.get("websocket")
        
        logger.info(f"📝 WorkflowDesignerNode: Processing question: {user_question[:50]}...")
        logger.info(f"💬 WorkflowDesignerNode: Conversation history length: {len(conversation_history)}")
        
        # Get available nodes and similar workflows
        available_nodes = node_registry.to_dict()
        similar_workflows = workflow_store.find_similar_workflows(user_question, limit=3)
        
        logger.info(f"🔧 WorkflowDesignerNode: Found {len(available_nodes)} available nodes")
        logger.info(f"💾 WorkflowDesignerNode: Found {len(similar_workflows)} similar workflows")
        
        result = {
            "user_question": user_question,
            "conversation_history": conversation_history,
            "websocket": websocket,
            "available_nodes": available_nodes,
            "similar_workflows": similar_workflows
        }
        
        logger.info("✅ WorkflowDesignerNode: prep_async completed")
        return result
    
    async def exec_async(self, prep_res):
        logger.info("🔄 WorkflowDesignerNode: Starting exec_async")
        
        user_question = prep_res["user_question"]
        available_nodes = prep_res["available_nodes"]
        similar_workflows = prep_res["similar_workflows"]
        
        logger.info(f"🤖 WorkflowDesignerNode: Calling LLM to design workflow for: {user_question[:50]}...")
        
        # Create prompt for workflow design
        prompt = f"""
You are a workflow designer agent. Your task is to analyze the user's question and design a workflow to solve it.

USER QUESTION: {user_question}

AVAILABLE NODES:
{json.dumps(available_nodes, indent=2)}

SIMILAR WORKFLOWS (for reference):
{json.dumps([{
    'description': w.metadata.description,
    'nodes_used': w.metadata.nodes_used,
    'success_rate': w.metadata.success_rate
} for w in similar_workflows], indent=2)}

Design a workflow to solve the user's question. Consider:
1. What information do we need to gather?
2. What analysis or processing is required?
3. What actions need user permission?
4. How can we present the results?

Return your response in YAML format:

```yaml
thinking: |
    <your step-by-step reasoning about how to solve this problem>

workflow:
  name: <workflow name>
  description: <brief description>
  nodes:
    - name: <node_name>
      description: <what this node does>
      inputs: <list of inputs>
      outputs: <list of outputs>
      requires_permission: <true/false>
    - name: <node_name>
      ...
  
  connections:
    - from: <node_name>
      to: <node_name>
      action: <action_name>
    - from: <node_name>
      to: <node_name>
      action: <action_name>
  
  shared_store_schema:
    <key>: <description>
    <key>: <description>

estimated_steps: <number of steps>
requires_user_input: <true/false>
requires_permission: <true/false>
```

IMPORTANT: Use only the available nodes listed above. If you need a node that doesn't exist, use the closest available one or ask for user input.
"""
        
        # Get workflow design from LLM
        response = call_llm(prompt)
        logger.info("🤖 WorkflowDesignerNode: Received LLM response")
        
        # Parse YAML response with error handling
        try:
            yaml_str = response.split("```yaml")[1].split("```")[0].strip()
            workflow_design = yaml.safe_load(yaml_str)
            logger.info("✅ WorkflowDesignerNode: Successfully parsed YAML response")
        except (IndexError, yaml.YAMLError) as e:
            logger.error(f"❌ WorkflowDesignerNode: Failed to parse YAML response: {e}")
            logger.error(f"📄 WorkflowDesignerNode: Raw response: {response}")
            # Create a fallback workflow design
            workflow_design = {
                "thinking": "Failed to parse LLM response, using fallback workflow",
                "workflow": {
                    "name": "Fallback Workflow",
                    "description": "A simple fallback workflow",
                    "nodes": [
                        {
                            "name": "user_query",
                            "description": "Ask user for more information",
                            "inputs": ["user_message"],
                            "outputs": ["clarified_question"],
                            "requires_permission": False
                        }
                    ],
                    "connections": [],
                    "shared_store_schema": {
                        "user_message": "User's original question",
                        "clarified_question": "Clarified question from user"
                    }
                },
                "estimated_steps": 1,
                "requires_user_input": True,
                "requires_permission": False
            }
            logger.info("🔄 WorkflowDesignerNode: Using fallback workflow design")
        
        logger.info(f"🎯 WorkflowDesignerNode: Designed workflow '{workflow_design.get('workflow', {}).get('name', 'Unknown')}' with {workflow_design.get('estimated_steps', 0)} steps")
        logger.info("✅ WorkflowDesignerNode: exec_async completed")
        return workflow_design
    
    async def post_async(self, shared, prep_res, exec_res):
        logger.info("🔄 WorkflowDesignerNode: Starting post_async")
        
        # Store the workflow design
        shared["workflow_design"] = exec_res
        shared["current_workflow"] = exec_res
        
        logger.info(f"💾 WorkflowDesignerNode: Stored workflow design in shared store")
        
        # Send workflow design to user
        websocket = prep_res["websocket"]
        if websocket:
            try:
                await websocket.send_text(json.dumps({
                    "type": "workflow_design",
                    "content": exec_res
                }))
                logger.info("📤 WorkflowDesignerNode: Sent workflow design to websocket")
            except Exception as e:
                logger.error(f"❌ WorkflowDesignerNode: Failed to send workflow design to websocket: {e}")
        else:
            logger.warning("⚠️ WorkflowDesignerNode: No websocket available to send workflow design")
        
        logger.info("✅ WorkflowDesignerNode: post_async completed, returning 'execute_workflow'")
        return "execute_workflow"

class WorkflowExecutorNode(AsyncNode):
    """
    Node that executes the designed workflow step by step.
    Example:
        >>> node = WorkflowExecutorNode()
        >>> shared = {"workflow_design": <workflow_dict>}
        >>> await node.prep_async(shared)
        # Prepares execution context
        >>> await node.exec_async(prep_res)
        # Executes workflow nodes in order
    """
    
    node_class_map = {
        "web_search": WebSearchNode,
        "analyze_results": AnalyzeResultsNode,
        "flight_search": FlightSearchNode,
        "cost_analysis": CostAnalysisNode,
        "result_summarizer": ResultSummarizerNode,
        "user_query": UserQueryNode,
        "permission_request": PermissionRequestNode,
        "data_formatter": DataFormatterNode,
    }

    async def prep_async(self, shared):
        logger.info("🔄 WorkflowExecutorNode: Starting prep_async")
        
        # Ensure shared is a dictionary
        if not isinstance(shared, dict):
            shared = {}
            logger.warning("WorkflowExecutorNode: shared parameter is not a dictionary, using empty dict")
        
        workflow_design = shared.get("workflow_design")
        websocket = shared.get("websocket")
        
        if not workflow_design:
            logger.error("❌ WorkflowExecutorNode: No workflow design found")
            raise ValueError("No workflow design found")
        
        logger.info(f"📋 WorkflowExecutorNode: Found workflow design: {workflow_design.get('workflow', {}).get('name', 'Unknown')}")
        logger.info(f"🔧 WorkflowExecutorNode: Workflow has {len(workflow_design.get('workflow', {}).get('nodes', []))} nodes")
        
        result = {
            "workflow_design": workflow_design,
            "websocket": websocket,
            "shared": shared
        }
        
        logger.info("✅ WorkflowExecutorNode: prep_async completed")
        return result
    
    async def exec_async(self, prep_res):
        logger.info("🔄 WorkflowExecutorNode: Starting exec_async")
        
        workflow_design = prep_res["workflow_design"]
        websocket = prep_res["websocket"]
        shared = prep_res["shared"]
        nodes = workflow_design["workflow"]["nodes"]
        execution_order = [node["name"] for node in nodes]
        logger.info(f"🚀 WorkflowExecutorNode: Starting execution of {len(nodes)} nodes")
        logger.info(f"📋 WorkflowExecutorNode: Execution order: {execution_order}")
        results = {}
        for i, node_name in enumerate(execution_order):
            node_config = next(n for n in nodes if n["name"] == node_name)
            logger.info(f"⚡ WorkflowExecutorNode: Executing node {i+1}/{len(execution_order)}: {node_name}")
            logger.info(f"📝 WorkflowExecutorNode: Node description: {node_config.get('description', 'No description')}")
            if websocket:
                try:
                    await websocket.send_text(json.dumps({
                        "type": "workflow_progress",
                        "content": {
                            "current_node": node_name,
                            "description": node_config["description"],
                            "progress": f"{i+1}/{len(execution_order)}"
                        }
                    }))
                    logger.info(f"📤 WorkflowExecutorNode: Sent progress update for {node_name}")
                except Exception as e:
                    logger.error(f"❌ WorkflowExecutorNode: Failed to send progress update: {e}")
            try:
                # Use real function node
                node_cls = self.node_class_map.get(node_name)
                if node_cls is None:
                    logger.warning(f"⚠️ WorkflowExecutorNode: No implementation found for {node_name}, returning mock result")
                    result = f"Mock result for {node_name}"
                else:
                    node = node_cls()
                    prep_res_node = node.prep(shared)
                    result = node.exec(prep_res_node)
                    node.post(shared, prep_res_node, result)
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
        >>> await node.exec_async(prep_res)
        # Sends question to user via websocket
    """
    
    async def prep_async(self, shared):
        logger.info("🔄 UserInteractionNode: Starting prep_async")
        
        # Ensure shared is a dictionary
        if not isinstance(shared, dict):
            shared = {}
            logger.warning("UserInteractionNode: shared parameter is not a dictionary, using empty dict")
        
        websocket = shared.get("websocket")
        pending_question = shared.get("pending_user_question")
        pending_permission = shared.get("pending_permission_request")
        
        logger.info(f"❓ UserInteractionNode: Pending question: {pending_question is not None}")
        logger.info(f"🔐 UserInteractionNode: Pending permission: {pending_permission is not None}")
        
        result = {
            "websocket": websocket,
            "pending_question": pending_question,
            "pending_permission": pending_permission
        }
        
        logger.info("✅ UserInteractionNode: prep_async completed")
        return result
    
    async def exec_async(self, prep_res):
        logger.info("🔄 UserInteractionNode: Starting exec_async")
        
        websocket = prep_res["websocket"]
        pending_question = prep_res["pending_question"]
        pending_permission = prep_res["pending_permission"]
        
        if pending_question:
            logger.info(f"❓ UserInteractionNode: Sending question to user: {pending_question[:50]}...")
            # Send question to user
            if websocket:
                try:
                    await websocket.send_text(json.dumps({
                        "type": "user_question",
                        "content": {
                            "question": pending_question,
                            "requires_response": True
                        }
                    }))
                    logger.info("📤 UserInteractionNode: Sent question to websocket")
                except Exception as e:
                    logger.error(f"❌ UserInteractionNode: Failed to send question: {e}")
            
            # Wait for user response (in real implementation, this would be handled differently)
            result = {"type": "question", "question": pending_question}
            logger.info("✅ UserInteractionNode: Question sent, waiting for response")
            return result
        
        elif pending_permission:
            logger.info(f"🔐 UserInteractionNode: Processing permission request: {pending_permission}")
            # Send permission request to user
            request = permission_manager.get_request(pending_permission)
            if request:
                formatted_request = permission_manager.format_permission_request_for_user(request)
                if websocket:
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "permission_request",
                            "content": formatted_request
                        }))
                        logger.info("📤 UserInteractionNode: Sent permission request to websocket")
                    except Exception as e:
                        logger.error(f"❌ UserInteractionNode: Failed to send permission request: {e}")
                result = {"type": "permission", "request_id": pending_permission}
                logger.info("✅ UserInteractionNode: Permission request sent")
                return result
        
        logger.info("✅ UserInteractionNode: No pending interactions")
        return {"type": "none"}
    
    async def post_async(self, shared, prep_res, exec_res):
        logger.info("🔄 UserInteractionNode: Starting post_async")
        
        interaction_type = exec_res["type"]
        logger.info(f"🔄 UserInteractionNode: Processing interaction type: {interaction_type}")
        
        if interaction_type == "question":
            # Store that we're waiting for user response
            shared["waiting_for_user_response"] = True
            logger.info("✅ UserInteractionNode: Set waiting_for_user_response flag")
            return "wait_for_response"
        
        elif interaction_type == "permission":
            # Store that we're waiting for permission
            shared["waiting_for_permission"] = True
            logger.info("✅ UserInteractionNode: Set waiting_for_permission flag")
            return "wait_for_permission"
        
        logger.info("✅ UserInteractionNode: Continuing workflow")
        return "continue_workflow"

class WorkflowOptimizerNode(AsyncNode):
    """
    Node that optimizes workflows based on results and user feedback.
    Example:
        >>> node = WorkflowOptimizerNode()
        >>> shared = {"workflow_results": {...}, "user_feedback": "Not good"}
        >>> await node.prep_async(shared)
        # Prepares optimization context
        >>> await node.exec_async(prep_res)
        # Suggests improvements if needed
    """
    
    async def prep_async(self, shared):
        logger.info("🔄 WorkflowOptimizerNode: Starting prep_async")
        
        # Ensure shared is a dictionary
        if not isinstance(shared, dict):
            shared = {}
            logger.warning("WorkflowOptimizerNode: shared parameter is not a dictionary, using empty dict")
        
        workflow_results = shared.get("workflow_results", {})
        user_feedback = shared.get("user_feedback", "")
        original_workflow = shared.get("workflow_design")
        
        logger.info(f"📊 WorkflowOptimizerNode: Analyzing {len(workflow_results)} workflow results")
        logger.info(f"💬 WorkflowOptimizerNode: User feedback length: {len(user_feedback)}")
        
        result = {
            "workflow_results": workflow_results,
            "user_feedback": user_feedback,
            "original_workflow": original_workflow
        }
        
        logger.info("✅ WorkflowOptimizerNode: prep_async completed")
        return result
    
    async def exec_async(self, prep_res):
        logger.info("🔄 WorkflowOptimizerNode: Starting exec_async")
        
        workflow_results = prep_res["workflow_results"]
        user_feedback = prep_res["user_feedback"]
        original_workflow = prep_res["original_workflow"]
        
        # Analyze if workflow needs optimization
        optimization_needed = False
        optimization_reasons = []
        
        logger.info("🔍 WorkflowOptimizerNode: Analyzing workflow results for optimization needs")
        
        # Check for errors in results
        for node_name, result in workflow_results.items():
            if isinstance(result, str) and "error" in result.lower():
                optimization_needed = True
                optimization_reasons.append(f"Error in {node_name}: {result}")
                logger.warning(f"⚠️ WorkflowOptimizerNode: Found error in {node_name}: {result}")
        
        # Check user feedback for dissatisfaction
        if user_feedback and any(word in user_feedback.lower() for word in ["not good", "wrong", "bad", "improve"]):
            optimization_needed = True
            optimization_reasons.append(f"User feedback indicates dissatisfaction: {user_feedback}")
            logger.info(f"💬 WorkflowOptimizerNode: User feedback indicates dissatisfaction: {user_feedback}")
        
        if optimization_needed:
            logger.info("🔧 WorkflowOptimizerNode: Optimization needed, calling LLM for suggestions")
            # Create optimization prompt
            prompt = f"""
The workflow execution had issues that need optimization:

ORIGINAL WORKFLOW:
{json.dumps(original_workflow, indent=2)}

ISSUES FOUND:
{chr(10).join(optimization_reasons)}

WORKFLOW RESULTS:
{json.dumps(workflow_results, indent=2)}

USER FEEDBACK:
{user_feedback}

Please suggest improvements to the workflow. Return in YAML format:

```yaml
optimization_needed: true
issues:
  - <issue description>
  - <issue description>

suggested_improvements:
  - <improvement description>
  - <improvement description>

revised_workflow:
  <revised workflow structure>
```
"""
            
            response = call_llm(prompt)
            yaml_str = response.split("```yaml")[1].split("```")[0].strip()
            optimization_plan = yaml.safe_load(yaml_str)
            
            logger.info("✅ WorkflowOptimizerNode: Generated optimization plan")
            return optimization_plan
        else:
            logger.info("✅ WorkflowOptimizerNode: No optimization needed, workflow executed successfully")
            return {"optimization_needed": False, "message": "Workflow executed successfully"}
    
    async def post_async(self, shared, prep_res, exec_res):
        logger.info("🔄 WorkflowOptimizerNode: Starting post_async")
        
        if exec_res.get("optimization_needed", False):
            logger.info("🔧 WorkflowOptimizerNode: Optimization needed, storing plan and sending suggestions")
            # Store optimization plan
            shared["optimization_plan"] = exec_res
            
            # Send optimization suggestions to user
            websocket = shared.get("websocket")
            if websocket:
                try:
                    await websocket.send_text(json.dumps({
                        "type": "optimization_suggestions",
                        "content": exec_res
                    }))
                    logger.info("📤 WorkflowOptimizerNode: Sent optimization suggestions to websocket")
                except Exception as e:
                    logger.error(f"❌ WorkflowOptimizerNode: Failed to send optimization suggestions: {e}")
            
            logger.info("✅ WorkflowOptimizerNode: Returning 'optimize_workflow'")
            return "optimize_workflow"
        else:
            logger.info("✅ WorkflowOptimizerNode: Workflow successful, returning 'workflow_success'")
            # Workflow is complete and successful
            shared["workflow_complete"] = True
            return "workflow_success"

# Legacy node for backward compatibility
class StreamingChatNode(AsyncNode):
    """
    Legacy streaming chat node for backward compatibility (streams LLM output).
    Example:
        >>> node = StreamingChatNode()
        >>> shared = {"user_message": "Hello", "websocket": ws}
        >>> await node.prep_async(shared)
        # Prepares chat context
        >>> await node.exec_async(prep_res)
        # Streams LLM response to websocket
    """
    
    async def prep_async(self, shared):
        logger.info("🔄 StreamingChatNode: Starting prep_async")
        
        # Ensure shared is a dictionary
        if not isinstance(shared, dict):
            shared = {}
            logger.warning("StreamingChatNode: shared parameter is not a dictionary, using empty dict")
        
        user_message = shared.get("user_message", "")
        websocket = shared.get("websocket")
        
        conversation_history = shared.get("conversation_history", [])
        conversation_history.append({"role": "user", "content": user_message})
        
        logger.info(f"💬 StreamingChatNode: Processing message: {user_message[:50]}...")
        logger.info(f"📚 StreamingChatNode: Conversation history length: {len(conversation_history)}")
        
        result = conversation_history, websocket
        logger.info("✅ StreamingChatNode: prep_async completed")
        return result
    
    async def exec_async(self, prep_res):
        logger.info("🔄 StreamingChatNode: Starting exec_async")
        
        messages, websocket = prep_res
        
        logger.info("📤 StreamingChatNode: Sending start message")
        await websocket.send_text(json.dumps({"type": "start", "content": ""}))
        
        logger.info("🤖 StreamingChatNode: Starting LLM streaming")
        full_response = ""
        async for chunk_content in stream_llm(messages):
            full_response += chunk_content
            await websocket.send_text(json.dumps({
                "type": "chunk", 
                "content": chunk_content
            }))
        
        logger.info("📤 StreamingChatNode: Sending end message")
        await websocket.send_text(json.dumps({"type": "end", "content": ""}))
        
        logger.info(f"✅ StreamingChatNode: Generated response length: {len(full_response)}")
        logger.info("✅ StreamingChatNode: exec_async completed")
        return full_response, websocket
    
    async def post_async(self, shared, prep_res, exec_res):
        logger.info("🔄 StreamingChatNode: Starting post_async")
        
        full_response, websocket = exec_res
        
        conversation_history = shared.get("conversation_history", [])
        conversation_history.append({"role": "assistant", "content": full_response})
        shared["conversation_history"] = conversation_history
        
        logger.info("💾 StreamingChatNode: Updated conversation history")
        logger.info("✅ StreamingChatNode: post_async completed")

class WorkflowEndNode(AsyncNode):
    """
    Node that marks the end of a workflow and notifies the user.
    Example:
        >>> node = WorkflowEndNode()
        >>> shared = {"workflow_results": {...}, "websocket": ws}
        >>> await node.prep_async(shared)
        # Prepares completion context
        >>> await node.exec_async(prep_res)
        # Sends completion message to websocket
    """
    
    async def prep_async(self, shared):
        logger.info("🔄 WorkflowEndNode: Starting prep_async")
        
        # Ensure shared is a dictionary
        if not isinstance(shared, dict):
            shared = {}
            logger.warning("WorkflowEndNode: shared parameter is not a dictionary, using empty dict")
        
        websocket = shared.get("websocket")
        workflow_results = shared.get("workflow_results", {})
        
        logger.info(f"📊 WorkflowEndNode: Workflow has {len(workflow_results)} results")
        
        result = {
            "websocket": websocket,
            "workflow_results": workflow_results
        }
        
        logger.info("✅ WorkflowEndNode: prep_async completed")
        return result
    
    async def exec_async(self, prep_res):
        logger.info("🔄 WorkflowEndNode: Starting exec_async")
        
        # Send completion message
        websocket = prep_res["websocket"]
        if websocket:
            try:
                await websocket.send_text(json.dumps({
                    "type": "workflow_complete",
                    "content": {
                        "message": "Workflow completed successfully!",
                        "results": prep_res["workflow_results"]
                    }
                }))
                logger.info("📤 WorkflowEndNode: Sent workflow completion message to websocket")
            except Exception as e:
                logger.error(f"❌ WorkflowEndNode: Failed to send workflow completion message: {e}")
        else:
            logger.warning("⚠️ WorkflowEndNode: No websocket available to send completion message")
        
        result = "Workflow completed successfully"
        logger.info("✅ WorkflowEndNode: exec_async completed")
        return result
    
    async def post_async(self, shared, prep_res, exec_res):
        logger.info("🔄 WorkflowEndNode: Starting post_async")
        
        # Mark workflow as complete
        shared["workflow_complete"] = True
        shared["workflow_status"] = "success"
        
        logger.info("✅ WorkflowEndNode: Marked workflow as complete")
        logger.info("🎉 WorkflowEndNode: Workflow execution finished successfully")
        return None  # End the flow 