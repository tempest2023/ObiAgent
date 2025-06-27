import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from agent.flow import create_general_agent_flow, create_streaming_chat_flow
from agent.utils.node_registry import node_registry
from agent.utils.workflow_store import workflow_store
from agent.utils.permission_manager import permission_manager
from agent.nodes import UserResponseRequiredException

# Setup standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI App with OpenAPI Customization
app = FastAPI(
    title="PocketFlow General Agent API",
    description="General agent system that can design and execute workflows to solve complex problems.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health Check Endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "service": "PocketFlow General Agent"}

# Serve the main page
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# Node Registry Endpoints
@app.get("/api/v1/nodes")
async def get_nodes():
    """Get all available nodes in the registry"""
    return node_registry.to_dict()

@app.get("/api/v1/nodes/{node_name}")
async def get_node(node_name: str):
    """Get a specific node by name"""
    node = node_registry.get_node(node_name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_name} not found")
    return node

@app.get("/api/v1/nodes/category/{category}")
async def get_nodes_by_category(category: str):
    """Get nodes by category"""
    from agent.utils.node_registry import NodeCategory
    try:
        node_category = NodeCategory(category)
        nodes = node_registry.get_nodes_by_category(node_category)
        return {"nodes": [node.__dict__ for node in nodes]}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

# Workflow Store Endpoints
@app.get("/api/v1/workflows")
async def get_workflows():
    """Get all stored workflows"""
    workflows = workflow_store.get_all_workflows()
    return {
        "workflows": [
            {
                "id": w.metadata.id,
                "name": w.metadata.name,
                "description": w.metadata.description,
                "success_rate": w.metadata.success_rate,
                "usage_count": w.metadata.usage_count,
                "tags": w.metadata.tags
            }
            for w in workflows
        ]
    }

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID"""
    workflow = workflow_store.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return workflow

@app.get("/api/v1/workflows/similar")
async def find_similar_workflows(question: str, limit: int = 5):
    """Find workflows similar to a question"""
    workflows = workflow_store.find_similar_workflows(question, limit)
    return {
        "question": question,
        "workflows": [
            {
                "id": w.metadata.id,
                "name": w.metadata.name,
                "description": w.metadata.description,
                "success_rate": w.metadata.success_rate,
                "nodes_used": w.metadata.nodes_used
            }
            for w in workflows
        ]
    }

@app.delete("/api/v1/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    success = workflow_store.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return {"message": f"Workflow {workflow_id} deleted successfully"}

@app.get("/api/v1/workflows/stats")
async def get_workflow_stats():
    """Get workflow store statistics"""
    return workflow_store.get_statistics()

# Permission Management Endpoints
@app.get("/api/v1/permissions")
async def get_pending_permissions():
    """Get all pending permission requests"""
    requests = permission_manager.get_pending_requests()
    return {
        "pending_requests": [
            permission_manager.format_permission_request_for_user(req)
            for req in requests
        ]
    }

@app.get("/api/v1/permissions/{request_id}")
async def get_permission_request(request_id: str):
    """Get a specific permission request"""
    request = permission_manager.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Permission request {request_id} not found")
    return permission_manager.format_permission_request_for_user(request)

@app.post("/api/v1/permissions/{request_id}/respond")
async def respond_to_permission(request_id: str, granted: bool, response: str = ""):
    """Respond to a permission request"""
    success = permission_manager.respond_to_request(request_id, granted, response)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid permission request or already responded")
    return {"message": f"Permission {'granted' if granted else 'denied'} successfully"}

@app.get("/api/v1/permissions/stats")
async def get_permission_stats():
    """Get permission management statistics"""
    return permission_manager.get_permission_summary()

# Exception Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    logger.info("Server startup: initializing general agent system...")
    logger.info(f"Loaded {len(node_registry.get_all_nodes())} nodes")
    logger.info(f"Loaded {len(workflow_store.get_all_workflows())} workflows")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Server shutdown: cleaning up resources...")

# Main WebSocket Endpoint for Agent Interaction
@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    shared_store = {
        "websocket": websocket,
        "conversation_history": [],
        "session_id": f"session_{websocket.client.port}_{websocket.client.host}",
        "waiting_for_user_response": False,
        "waiting_for_permission": False,
        "pending_user_question": None,
        "pending_permission_request": None
    }
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type", "chat")
            
            if message_type == "chat":
                # Standard chat message - use general agent flow
                if not shared_store.get("waiting_for_user_response") and not shared_store.get("waiting_for_permission"):
                    shared_store["user_message"] = message.get("content", "")
                    flow = create_general_agent_flow()
                    shared_store["current_flow"] = flow
                    try:
                        await flow.run_async(shared_store)
                    except UserResponseRequiredException as e:
                        logger.info(f"⏸️ Workflow paused for user response: {e}")
                        # 保存暂停状态，等待用户响应
                        shared_store["paused_workflow"] = {
                            "flow": flow,
                            "exception": e,
                            "node_name": e.node_name,
                            "question": e.question,
                            "node_index": e.node_index
                        }
                    except Exception as e:
                        logger.error(f"❌ Workflow execution failed: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "content": f"Workflow execution failed: {str(e)}"
                        }))
                else:
                    # Still waiting for user input, ignore new chat messages
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": "Please respond to the current question or permission request first."
                    }))
                
            elif message_type == "user_response":
                # User response to a question
                question_id = message.get("question_id")
                response_content = message.get("content", "")
                
                logger.info(f"📥 Received user response: {response_content[:50]}...")
                
                # Store the user response
                shared_store["user_response"] = response_content
                shared_store["waiting_for_user_response"] = False
                shared_store["pending_user_question"] = None
                
                # Add to conversation history
                shared_store["conversation_history"].append({
                    "role": "user",
                    "content": response_content,
                    "type": "response"
                })
                
                logger.info("✅ User response processed, continuing workflow execution")
                
                # 检查是否有暂停的 workflow 需要继续执行
                if shared_store.get("paused_workflow"):
                    logger.info("🔄 Continuing paused workflow execution")
                    try:
                        paused_workflow = shared_store["paused_workflow"]
                        flow = paused_workflow["flow"]
                        exception = paused_workflow["exception"]
                        
                        # 设置从下一个节点开始执行
                        shared_store["current_node_index"] = exception.node_index + 1
                        
                        # 继续执行 workflow
                        await flow.run_async(shared_store)
                        
                        # 清除暂停状态
                        shared_store.pop("paused_workflow", None)
                        shared_store.pop("current_node_index", None)
                        
                        logger.info("✅ Workflow execution completed successfully")
                        
                    except UserResponseRequiredException as e:
                        logger.info(f"⏸️ Workflow paused again for user response: {e}")
                        # 更新暂停状态
                        shared_store["paused_workflow"] = {
                            "flow": flow,
                            "exception": e,
                            "node_name": e.node_name,
                            "question": e.question,
                            "node_index": e.node_index
                        }
                    except Exception as e:
                        logger.error(f"❌ Failed to continue workflow: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "content": f"Failed to continue workflow: {str(e)}"
                        }))
                        # 清除暂停状态
                        shared_store.pop("paused_workflow", None)
                else:
                    logger.info("ℹ️ No paused workflow to continue")
                
            elif message_type == "permission_response":
                # User response to permission request
                request_id = message.get("request_id")
                granted = message.get("granted", False)
                response = message.get("response", "")
                
                logger.info(f"📥 Received permission response: {granted} for {request_id}")
                
                if request_id:
                    # Update permission manager
                    permission_manager.respond_to_request(request_id, granted, response)
                    
                    # Update shared store
                    shared_store["waiting_for_permission"] = False
                    shared_store["pending_permission_request"] = None
                    shared_store["permission_response"] = {
                        "request_id": request_id,
                        "granted": granted,
                        "response": response
                    }
                    
                    # Add to conversation history
                    shared_store["conversation_history"].append({
                        "role": "user",
                        "content": f"Permission {'granted' if granted else 'denied'} for {request_id}",
                        "type": "permission_response"
                    })
                    
                    logger.info("✅ Permission response processed, workflow should continue automatically")
                    # Note: The workflow will continue automatically when waiting_for_permission becomes False
                
            elif message_type == "feedback":
                # User feedback for workflow optimization
                shared_store["user_feedback"] = message.get("content", "")
                
            else:
                # Unknown message type
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": f"Unknown message type: {message_type}"
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": f"Server error: {str(e)}"
        }))

# Legacy WebSocket endpoint for backward compatibility
@app.websocket("/api/v1/ws/chat")
async def legacy_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    shared_store = {
        "websocket": websocket,
        "conversation_history": []
    }
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            shared_store["user_message"] = message.get("content", "")
            flow = create_streaming_chat_flow()
            await flow.run_async(shared_store)
    except WebSocketDisconnect:
        logger.info("Legacy WebSocket disconnected")
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)