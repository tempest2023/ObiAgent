import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from agent.flow import create_streaming_chat_flow


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App with OpenAPI Customization
app = FastAPI(
    title="PocketFlow Agent API",
    description="Real-time chat backend with streaming LLM responses.",
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

# Health Check Endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

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
    logger.info("Server startup: initializing resources...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Server shutdown: cleaning up resources...")

# Main API Endpoints (Versioned)
@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
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
        logger.info("WebSocket disconnected")
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
