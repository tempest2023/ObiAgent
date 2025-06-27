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

# Configure logging
logger = logging.getLogger(__name__)

class UserResponseRequiredException(Exception):
    """Exception raised when a workflow needs user input to continue"""
    def __init__(self, node_name: str, question: str, node_index: int):
        self.node_name = node_name
        self.question = question
        self.node_index = node_index
        super().__init__(f"User response required for node {node_name} at index {node_index}")

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
        
        logger.info(f"🔧 WorkflowDesignerNode: Found {len(available_nodes.get('nodes', {}))} available nodes")
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
        
        # 检查是否需要从特定节点继续执行
        start_index = shared.get("current_node_index", 0)
        if start_index > 0:
            logger.info(f"🔄 WorkflowExecutorNode: Resuming from node index {start_index}")
        
        logger.info(f"🚀 WorkflowExecutorNode: Starting execution of {len(nodes)} nodes from index {start_index}")
        logger.info(f"📋 WorkflowExecutorNode: Execution order: {execution_order}")
        results = {}
        
        for i, node_name in enumerate(execution_order):
            # 如果从特定索引开始，跳过之前的节点
            if i < start_index:
                logger.info(f"⏭️ WorkflowExecutorNode: Skipping node {i}: {node_name}")
                continue
                
            node_config = next(n for n in nodes if n["name"] == node_name)
            logger.info(f"⚡ WorkflowExecutorNode: Executing node {i+1}/{len(execution_order)}: {node_name}")
            logger.info(f"📝 WorkflowExecutorNode: Node description: {node_config.get('description', 'No description')}")
            
            # --- BEGIN PATCH: user_query question improvement ---
            if node_name == "user_query":
                # Try to generate a meaningful question
                question = None
                # Prefer explicit question in node_config
                if "question" in node_config and node_config["question"]:
                    question = node_config["question"]
                # Otherwise, use description to form a question
                elif node_config.get("description"):
                    question = node_config["description"]
                # If still no question, try to compose from inputs
                elif node_config.get("inputs"):
                    # Compose a question from inputs
                    inputs = node_config["inputs"]
                    if isinstance(inputs, list) and len(inputs) > 0:
                        question = f"Please provide the following information: {', '.join(inputs)}"
                # If no meaningful question found, raise an error
                if not question:
                    raise ValueError(f"UserQueryNode '{node_name}' has no meaningful question. Node config: {node_config}")
                shared["question"] = question
                logger.info(f"🔧 WorkflowExecutorNode: Set question for user_query node: '{question}'")
            # --- END PATCH ---

            # --- BEGIN PATCH: web_search query auto-fill ---
            if node_name == "web_search":
                if not shared.get("query"):
                    # 优先用 shared["user_message"]
                    if shared.get("user_message"):
                        shared["query"] = shared["user_message"]
                    # 其次用 workflow_design["user_question"]
                    elif workflow_design.get("user_question"):
                        shared["query"] = workflow_design["user_question"]
                    # 兼容 workflow 节点 inputs 字段
                    elif node_config.get("inputs"):
                        for input_key in node_config["inputs"]:
                            if shared.get(input_key):
                                shared["query"] = shared[input_key]
                                break
                logger.info(f"🔧 WorkflowExecutorNode: Set query for web_search node: '{shared.get('query')}'")
            # --- END PATCH ---

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
                                # 在生产环境中，我们暂停执行并等待服务器重新启动流程
                                logger.info("⏸️ WorkflowExecutorNode: Pausing execution, waiting for server to resume")
                                shared["waiting_for_user_response"] = True
                                shared["current_node_index"] = i  # 保存当前节点索引
                                shared["current_node_name"] = node_name
                                
                                # 抛出特殊异常来暂停执行
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
                # 这是预期的异常，用于暂停执行
                logger.info(f"⏸️ WorkflowExecutorNode: Paused for user response: {e}")
                # 清除当前节点索引，因为我们已经处理了这个异常
                shared.pop("current_node_index", None)
                shared.pop("current_node_name", None)
                raise  # 重新抛出异常，让上层处理
                
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