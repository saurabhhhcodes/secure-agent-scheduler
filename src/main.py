from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import our services and models
from .services.orchestrator import Orchestrator
from .models.schedule import ScheduleEvent
from .utils.audit_log import get_audit_log

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Secure Agent Scheduler",
    description="A secure multi-agent system for scheduling and notifications",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = Orchestrator()

# Initialize templates
templates = Jinja2Templates(directory="templates")

class ScheduleRequest(BaseModel):
    """Request model for scheduling an event."""
    user_request: str = Field(..., description="Natural language request for scheduling")
    user_id: str = Field(..., description="ID of the user making the request")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional metadata for the request"
    )

class ScheduleResponse(BaseModel):
    """Response model for scheduling requests."""
    success: bool
    event: Optional[Dict[str, Any]] = None
    notification: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root(request: Request):
    """Root endpoint that serves the frontend application."""
    audit_log = get_audit_log(limit=100)
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "audit_log": audit_log}
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "secure-agent-scheduler"
    }

@app.get("/api/audit", summary="Get audit log", tags=["Audit"])
async def audit_log(limit: int = 100):
    """Return the last N audit log entries."""
    return {"audit_log": get_audit_log(limit=limit)}

@app.post(
    "/api/schedule",
    response_model=ScheduleResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Schedule a new event",
    response_description="The scheduled event details"
)
async def schedule_event(request: ScheduleRequest):
    """
    Schedule a new event based on natural language input.
    
    This endpoint processes a natural language request to schedule an event,
    creates the event, and sets up any necessary notifications.
    """
    try:
        logger.info(f"Processing schedule request from user {request.user_id}")
        
        # Process the request through our orchestrator
        result = await orchestrator.process_request(
            user_request=request.user_request,
            user_id=request.user_id
        )
        
        # Return appropriate response
        if result["success"]:
            return ScheduleResponse(
                success=True,
                event=result.get("event"),
                notification=result.get("notification")
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ScheduleResponse(
                    success=False,
                    error=result.get("error", "Unknown error occurred")
                ).dict()
            )
            
    except Exception as e:
        logger.error(f"Error processing schedule request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ScheduleResponse(
                success=False,
                error=f"Internal server error: {str(e)}"
            ).dict()
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ScheduleResponse(
            success=False,
            error=exc.detail
        ).dict()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ScheduleResponse(
            success=False,
            error="An unexpected error occurred"
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
