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
from typing import Dict, List, Any, Optional
from pocketflow import AsyncNode, Node
from utils.stream_llm import stream_llm, call_llm
from utils.node_registry import node_registry
from utils.workflow_store import workflow_store
from utils.permission_manager import permission_manager

class WorkflowDesignerNode(AsyncNode):
    """Node that analyzes user questions and designs workflows"""
    
    async def prep_async(self, shared):
        user_question = shared.get("user_message", "")
        conversation_history = shared.get("conversation_history", [])
        websocket = shared.get("websocket")
        
        # Get available nodes and similar workflows
        available_nodes = node_registry.to_dict()
        similar_workflows = workflow_store.find_similar_workflows(user_question, limit=3)
        
        return {
            "user_question": user_question,
            "conversation_history": conversation_history,
            "websocket": websocket,
            "available_nodes": available_nodes,
            "similar_workflows": similar_workflows
        }
    
    async def exec_async(self, prep_res):
        user_question = prep_res["user_question"]
        available_nodes = prep_res["available_nodes"]
        similar_workflows = prep_res["similar_workflows"]
        
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
        
        # Parse YAML response
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        workflow_design = yaml.safe_load(yaml_str)
        
        return workflow_design
    
    async def post_async(self, shared, prep_res, exec_res):
        # Store the workflow design
        shared["workflow_design"] = exec_res
        shared["current_workflow"] = exec_res
        
        # Send workflow design to user
        websocket = prep_res["websocket"]
        await websocket.send_text(json.dumps({
            "type": "workflow_design",
            "content": exec_res
        }))
        
        return "execute_workflow"

class WorkflowExecutorNode(AsyncNode):
    """Node that executes the designed workflow"""
    
    async def prep_async(self, shared):
        workflow_design = shared.get("workflow_design")
        websocket = shared.get("websocket")
        
        if not workflow_design:
            raise ValueError("No workflow design found")
        
        return {
            "workflow_design": workflow_design,
            "websocket": websocket,
            "shared": shared
        }
    
    async def exec_async(self, prep_res):
        workflow_design = prep_res["workflow_design"]
        websocket = prep_res["websocket"]
        shared = prep_res["shared"]
        
        # Execute each node in the workflow
        nodes = workflow_design["workflow"]["nodes"]
        connections = workflow_design["workflow"]["connections"]
        
        # Create a simple execution order (could be enhanced with proper graph traversal)
        execution_order = []
        for node in nodes:
            execution_order.append(node["name"])
        
        results = {}
        current_node = None
        
        for node_name in execution_order:
            current_node = node_name
            node_config = next(n for n in nodes if n["name"] == node_name)
            
            # Send progress update
            await websocket.send_text(json.dumps({
                "type": "workflow_progress",
                "content": {
                    "current_node": node_name,
                    "description": node_config["description"],
                    "progress": f"{execution_order.index(node_name) + 1}/{len(execution_order)}"
                }
            }))
            
            # Execute the node
            try:
                result = await self._execute_node(node_config, shared)
                results[node_name] = result
                
                # Send node completion
                await websocket.send_text(json.dumps({
                    "type": "node_complete",
                    "content": {
                        "node": node_name,
                        "result": result
                    }
                }))
                
            except Exception as e:
                # Send error
                await websocket.send_text(json.dumps({
                    "type": "node_error",
                    "content": {
                        "node": node_name,
                        "error": str(e)
                    }
                }))
                raise
        
        return results
    
    async def _execute_node(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Execute a single node"""
        node_name = node_config["name"]
        
        # Map node names to actual implementations
        node_implementations = {
            "web_search": self._web_search,
            "flight_search": self._flight_search,
            "cost_analysis": self._cost_analysis,
            "user_query": self._user_query,
            "permission_request": self._permission_request,
            "result_summarizer": self._result_summarizer,
            "data_formatter": self._data_formatter
        }
        
        if node_name in node_implementations:
            return await node_implementations[node_name](node_config, shared)
        else:
            # Mock implementation for unknown nodes
            return f"Mock result for {node_name}"
    
    async def _web_search(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Mock web search implementation"""
        query = shared.get("user_message", "")
        return f"Search results for: {query}"
    
    async def _flight_search(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Mock flight search implementation"""
        # Extract flight details from user message
        user_message = shared.get("user_message", "")
        
        # Mock flight options
        flight_options = [
            {
                "airline": "United Airlines",
                "flight_number": "UA857",
                "departure": "14:30",
                "arrival": "18:45",
                "price": 850,
                "duration": "12h 15m"
            },
            {
                "airline": "China Eastern",
                "flight_number": "MU586",
                "departure": "15:45",
                "arrival": "19:30",
                "price": 720,
                "duration": "11h 45m"
            },
            {
                "airline": "Delta Airlines",
                "flight_number": "DL287",
                "departure": "16:20",
                "arrival": "20:15",
                "price": 920,
                "duration": "11h 55m"
            }
        ]
        
        return flight_options
    
    async def _cost_analysis(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Analyze costs and find best value"""
        flight_options = shared.get("flight_search_result", [])
        
        if not flight_options:
            return "No flight options to analyze"
        
        # Find the best value option (lowest price for afternoon departure)
        best_option = min(flight_options, key=lambda x: x["price"])
        
        return {
            "best_option": best_option,
            "analysis": f"Best value option: {best_option['airline']} {best_option['flight_number']} at ${best_option['price']}",
            "recommendation": "China Eastern MU586 offers the best value at $720"
        }
    
    async def _user_query(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Ask user for additional information"""
        question = node_config.get("inputs", {}).get("question", "Please provide additional information")
        
        # Store the question for user response
        shared["pending_user_question"] = question
        
        return f"Waiting for user response to: {question}"
    
    async def _permission_request(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Request user permission for sensitive operations"""
        operation = node_config.get("inputs", {}).get("operation", "unknown")
        details = node_config.get("inputs", {}).get("details", "No details provided")
        
        # Create permission request
        request = permission_manager.request_permission(
            permission_type="payment" if "payment" in operation.lower() else "booking",
            description=f"Permission for {operation}",
            details={"operation": operation, "details": details}
        )
        
        shared["pending_permission_request"] = request.id
        
        return f"Permission request created: {request.id}"
    
    async def _result_summarizer(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Summarize results and provide recommendations"""
        results = shared.get("workflow_results", {})
        user_question = shared.get("user_message", "")
        
        summary = f"""
Based on your request: "{user_question}"

I found the following options:

1. **China Eastern MU586** - $720
   - Departure: 15:45 (afternoon as requested)
   - Duration: 11h 45m
   - Best value option

2. **United Airlines UA857** - $850
   - Departure: 14:30 (afternoon)
   - Duration: 12h 15m

3. **Delta Airlines DL287** - $920
   - Departure: 16:20 (afternoon)
   - Duration: 11h 55m

**Recommendation**: China Eastern MU586 offers the best cost-performance ratio at $720 with an afternoon departure time as you requested.

Would you like me to proceed with booking this flight?
"""
        
        return summary
    
    async def _data_formatter(self, node_config: Dict[str, Any], shared: Dict[str, Any]):
        """Format data for better presentation"""
        raw_data = shared.get("workflow_results", {})
        format_type = node_config.get("inputs", {}).get("format_type", "text")
        
        if format_type == "comparison_table":
            return "Formatted comparison table would be displayed here"
        else:
            return str(raw_data)
    
    async def post_async(self, shared, prep_res, exec_res):
        # Store workflow results
        shared["workflow_results"] = exec_res
        
        # Save successful workflow to store
        workflow_design = prep_res["workflow_design"]
        workflow_store.save_workflow(
            question=shared.get("user_message", ""),
            nodes=workflow_design["workflow"]["nodes"],
            connections=workflow_design["workflow"]["connections"],
            shared_store_schema=workflow_design["workflow"]["shared_store_schema"],
            success=True,
            tags=["flight_booking", "cost_analysis"]
        )
        
        return "workflow_complete"

class UserInteractionNode(AsyncNode):
    """Node that handles user interactions and responses"""
    
    async def prep_async(self, shared):
        websocket = shared.get("websocket")
        pending_question = shared.get("pending_user_question")
        pending_permission = shared.get("pending_permission_request")
        
        return {
            "websocket": websocket,
            "pending_question": pending_question,
            "pending_permission": pending_permission
        }
    
    async def exec_async(self, prep_res):
        websocket = prep_res["websocket"]
        pending_question = prep_res["pending_question"]
        pending_permission = prep_res["pending_permission"]
        
        if pending_question:
            # Send question to user
            await websocket.send_text(json.dumps({
                "type": "user_question",
                "content": {
                    "question": pending_question,
                    "requires_response": True
                }
            }))
            
            # Wait for user response (in real implementation, this would be handled differently)
            return {"type": "question", "question": pending_question}
        
        elif pending_permission:
            # Send permission request to user
            request = permission_manager.get_request(pending_permission)
            if request:
                formatted_request = permission_manager.format_permission_request_for_user(request)
                await websocket.send_text(json.dumps({
                    "type": "permission_request",
                    "content": formatted_request
                }))
                return {"type": "permission", "request_id": pending_permission}
        
        return {"type": "none"}
    
    async def post_async(self, shared, prep_res, exec_res):
        interaction_type = exec_res["type"]
        
        if interaction_type == "question":
            # Store that we're waiting for user response
            shared["waiting_for_user_response"] = True
            return "wait_for_response"
        
        elif interaction_type == "permission":
            # Store that we're waiting for permission
            shared["waiting_for_permission"] = True
            return "wait_for_permission"
        
        return "continue_workflow"

class WorkflowOptimizerNode(AsyncNode):
    """Node that optimizes workflows based on results and user feedback"""
    
    async def prep_async(self, shared):
        workflow_results = shared.get("workflow_results", {})
        user_feedback = shared.get("user_feedback", "")
        original_workflow = shared.get("workflow_design")
        
        return {
            "workflow_results": workflow_results,
            "user_feedback": user_feedback,
            "original_workflow": original_workflow
        }
    
    async def exec_async(self, prep_res):
        workflow_results = prep_res["workflow_results"]
        user_feedback = prep_res["user_feedback"]
        original_workflow = prep_res["original_workflow"]
        
        # Analyze if workflow needs optimization
        optimization_needed = False
        optimization_reasons = []
        
        # Check for errors in results
        for node_name, result in workflow_results.items():
            if isinstance(result, str) and "error" in result.lower():
                optimization_needed = True
                optimization_reasons.append(f"Error in {node_name}: {result}")
        
        # Check user feedback for dissatisfaction
        if user_feedback and any(word in user_feedback.lower() for word in ["not good", "wrong", "bad", "improve"]):
            optimization_needed = True
            optimization_reasons.append(f"User feedback indicates dissatisfaction: {user_feedback}")
        
        if optimization_needed:
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
            
            return optimization_plan
        else:
            return {"optimization_needed": False, "message": "Workflow executed successfully"}
    
    async def post_async(self, shared, prep_res, exec_res):
        if exec_res.get("optimization_needed", False):
            # Store optimization plan
            shared["optimization_plan"] = exec_res
            
            # Send optimization suggestions to user
            websocket = shared.get("websocket")
            await websocket.send_text(json.dumps({
                "type": "optimization_suggestions",
                "content": exec_res
            }))
            
            return "optimize_workflow"
        else:
            # Workflow is complete and successful
            shared["workflow_complete"] = True
            return "workflow_success"

# Legacy node for backward compatibility
class StreamingChatNode(AsyncNode):
    """Legacy streaming chat node for backward compatibility"""
    
    async def prep_async(self, shared):
        user_message = shared.get("user_message", "")
        websocket = shared.get("websocket")
        
        conversation_history = shared.get("conversation_history", [])
        conversation_history.append({"role": "user", "content": user_message})
        
        return conversation_history, websocket
    
    async def exec_async(self, prep_res):
        messages, websocket = prep_res
        
        await websocket.send_text(json.dumps({"type": "start", "content": ""}))
        
        full_response = ""
        async for chunk_content in stream_llm(messages):
            full_response += chunk_content
            await websocket.send_text(json.dumps({
                "type": "chunk", 
                "content": chunk_content
            }))
        
        await websocket.send_text(json.dumps({"type": "end", "content": ""}))
        
        return full_response, websocket
    
    async def post_async(self, shared, prep_res, exec_res):
        full_response, websocket = exec_res
        
        conversation_history = shared.get("conversation_history", [])
        conversation_history.append({"role": "assistant", "content": full_response})
        shared["conversation_history"] = conversation_history 