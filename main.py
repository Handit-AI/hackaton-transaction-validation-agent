#!/usr/bin/env python3
"""
FastAPI application for risk_manager (LangGraph)
Following FastAPI best practices for production deployment
"""

import os
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from handit_ai import configure, tracing

# Load environment variables
load_dotenv()

# Configure Handit
configure(HANDIT_API_KEY=os.getenv("HANDIT_API_KEY"))

from src.agent import LangGraphAgent

# Global agent instance
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent
    
    # Startup
    print(f"🚀 Starting risk_manager (LangGraph + FastAPI)")
    
    # Initialize agent
    agent = LangGraphAgent()
    
    # Print graph information
    graph_info = agent.get_graph_info()
    print(f"✅ risk_manager initialized successfully")
    
    yield
    
    # Shutdown
    print(f"🔄 Shutting down risk_manager")

# Create FastAPI app with lifespan
app = FastAPI(
    title="risk_manager",
    description="LangGraph-powered AI agent API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware - Commented out to allow all connections
# Cloud Run handles security at the infrastructure level
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
# )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response Models
class ProcessRequest(BaseModel):
    # Accept either a string or a dictionary for flexible input
    input_data: Any = Field(None, description="Input data to process (optional for compatibility)")
    
    # Accept array of transactions for batch processing
    transactions: List[Dict[str, Any]] = Field(None, description="Array of transactions to process")

    # Allow direct transaction fields (fraud detection)
    transaction: Dict[str, Any] = Field(None, description="Transaction details")
    financial: Dict[str, Any] = Field(None, description="Financial information")
    card: Dict[str, Any] = Field(None, description="Card details")
    merchant: Dict[str, Any] = Field(None, description="Merchant information")
    customer: Dict[str, Any] = Field(None, description="Customer details")
    device: Dict[str, Any] = Field(None, description="Device information")
    location: Dict[str, Any] = Field(None, description="Location data")
    behavioral_profile: Dict[str, Any] = Field(None, description="Behavioral profile")
    velocity_counters: Dict[str, Any] = Field(None, description="Velocity metrics")
    risk_signals: Dict[str, Any] = Field(None, description="Risk signals")
    session: Dict[str, Any] = Field(None, description="Session data")
    channel: Dict[str, Any] = Field(None, description="Channel information")
    authentication: Dict[str, Any] = Field(None, description="Authentication data")

    # Simple transaction fields for basic testing
    user_id: str = Field(None, description="User ID")
    user_age_days: int = Field(None, description="Account age in days")
    total_transactions: int = Field(None, description="Total transaction count")
    amount: float = Field(None, description="Transaction amount")
    time: str = Field(None, description="Transaction time (HH:MM format)")
    merchant_name: str = Field(None, description="Merchant name")
    merchant_category: str = Field(None, description="Merchant category")
    currency: str = Field(None, description="Transaction currency code")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")

    class Config:
        schema_extra = {
            "example": {
                "transaction": {
                    "transaction_id": "TXN-001",
                    "transaction_type": "PURCHASE"
                },
                "financial": {
                    "amount": 150.00,
                    "currency": "USD"
                },
                "merchant": {
                    "merchant_name": "Amazon",
                    "merchant_category_code": "5732"
                },
                "customer": {
                    "customer_id": "CUST-001",
                    "age_of_account_days": 365
                }
            }
        }

class ProcessResponse(BaseModel):
    result: Any = Field(..., description="Processing result")
    success: bool = Field(..., description="Whether processing was successful")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "result": "I can help you with various tasks...",
                "success": True,
                "metadata": {
                    "agent": "risk_manager",
                    "framework": "langgraph",
                    "processing_time_ms": 150
                }
            }
        }

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    agent: str = Field(..., description="Agent name")
    framework: str = Field(..., description="Framework used")
    uptime: str = Field(..., description="Application uptime")

class GraphInfoResponse(BaseModel):
    graph_info: Dict[str, Any] = Field(..., description="Graph structure information")

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# API Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to risk_manager API",
        "framework": "langgraph",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/process", response_model=ProcessResponse, tags=["Agent"])
@tracing(agent="risk_manager")
async def process_endpoint(request: ProcessRequest):
    """
    Main processing endpoint - sends input through the LangGraph agent
    This is the main entry point for agent execution, so it has tracing.
    Accepts flexible transaction data in multiple formats.
    Can process single transactions or arrays of transactions.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        import time
        import uuid
        start_time = time.time()

        # Check if this is a batch request (array of transactions)
        if request.transactions:
            # Process multiple transactions
            results = []
            for idx, tx in enumerate(request.transactions):
                try:
                    # Ensure transaction has an ID
                    if "transaction_id" not in tx:
                        tx["transaction_id"] = f"TXN-{uuid.uuid4().hex[:12].upper()}"
                    
                    # Process through the agent
                    result = await agent.process(tx)
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e), "transaction_id": tx.get("transaction_id", "unknown")})
            
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessResponse(
                result=results,
                success=True,
                metadata={
                    "agent": "risk_manager",
                    "framework": "langgraph",
                    "processing_time_ms": round(processing_time, 2),
                    "transaction_count": len(request.transactions),
                    **request.metadata
                }
            )

        # Single transaction processing (existing logic)
        # Build transaction data from whatever format is provided
        transaction_data = {}

        # Option 1: If input_data is provided (backwards compatibility)
        if request.input_data:
            if isinstance(request.input_data, dict):
                transaction_data = request.input_data
            elif isinstance(request.input_data, str):
                # Try to parse as JSON if it's a string
                try:
                    import json
                    transaction_data = json.loads(request.input_data)
                except:
                    # If not JSON, create a simple transaction
                    transaction_data = {"raw_input": request.input_data}

        # Option 2: Build from structured fields (complex transaction)
        elif request.transaction or request.financial or request.merchant:
            # Complex transaction format
            if request.transaction:
                transaction_data.update(request.transaction)
            if request.financial and "amount" in request.financial:
                transaction_data["amount"] = request.financial["amount"]
                transaction_data["currency"] = request.financial.get("currency", "USD")
            if request.card:
                transaction_data["card_info"] = request.card
            if request.merchant:
                if "merchant_name" in request.merchant:
                    transaction_data["merchant"] = request.merchant["merchant_name"]
                    transaction_data["merchant_category_code"] = request.merchant.get("merchant_category_code")
                transaction_data["merchant_data"] = request.merchant
            if request.customer:
                if "customer_id" in request.customer:
                    transaction_data["user_id"] = request.customer["customer_id"]
                if "age_of_account_days" in request.customer:
                    transaction_data["user_age_days"] = request.customer["age_of_account_days"]
                transaction_data["customer_data"] = request.customer
            if request.device:
                transaction_data["device_data"] = request.device
            if request.location:
                if "transaction_city" in request.location:
                    transaction_data["location"] = f"{request.location.get('transaction_city', '')}, {request.location.get('transaction_country', '')}"
                transaction_data["location_data"] = request.location
            if request.behavioral_profile:
                transaction_data["behavioral_profile"] = request.behavioral_profile
            if request.velocity_counters:
                transaction_data["velocity_counters"] = request.velocity_counters
            if request.risk_signals:
                transaction_data["risk_signals"] = request.risk_signals
            if request.session:
                transaction_data["session_data"] = request.session
            if request.channel:
                transaction_data["channel_data"] = request.channel
            if request.authentication:
                transaction_data["authentication_data"] = request.authentication

        # Option 3: Build from simple fields (basic transaction)
        elif request.user_id or request.amount:
            transaction_data = {
                "user_id": request.user_id or f"user_{uuid.uuid4().hex[:8]}",
                "user_age_days": request.user_age_days or 180,
                "total_transactions": request.total_transactions or 10,
                "amount": request.amount or 100.0,
                "time": request.time or "14:00",
                "merchant": request.merchant_name or "Unknown Merchant",
                "merchant_category": request.merchant_category or "General",
                "currency": request.currency or "USD",
                "location": "Unknown",
                "previous_location": "Unknown"
            }

        # Option 4: Use the raw request dict if nothing else works
        else:
            # Get all non-None fields from the request
            request_dict = request.dict(exclude_none=True, exclude={"metadata"})
            if request_dict:
                transaction_data = request_dict
            else:
                # Default minimal transaction
                transaction_data = {
                    "user_id": f"user_{uuid.uuid4().hex[:8]}",
                    "amount": 100.0,
                    "merchant": "Test Merchant",
                    "user_age_days": 180,
                    "total_transactions": 10
                }

        # Ensure transaction has an ID
        if "transaction_id" not in transaction_data:
            transaction_data["transaction_id"] = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        # Process through the agent
        result = await agent.process(transaction_data)

        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Extract only analyzer results and final decision
        final_output = {}

        # If result is a dict containing 'results' (from graph execution)
        if isinstance(result, dict):
            # Get the results section which contains analyzer outputs
            if 'results' in result:
                analyzer_results = result['results']

                # Include all analyzer outputs
                for analyzer in ['pattern_detector', 'behavioral_analizer', 'velocity_checker',
                               'merchant_risk_analizer', 'geographic_analizer']:
                    if analyzer in analyzer_results:
                        final_output[analyzer] = analyzer_results[analyzer]

                # Include the decision aggregator (final decision)
                if 'decision_aggregator' in analyzer_results:
                    final_output['decision'] = analyzer_results['decision_aggregator']

            # Alternative: Check if analyzers are directly in result
            else:
                for key in ['pattern_detector', 'behavioral_analizer', 'velocity_checker',
                           'merchant_risk_analizer', 'geographic_analizer', 'decision_aggregator']:
                    if key in result:
                        if key == 'decision_aggregator':
                            final_output['decision'] = result[key]
                        else:
                            final_output[key] = result[key]

        # If no analyzers found, return the raw result
        if not final_output:
            final_output = result

        return ProcessResponse(
            result=final_output,
            success=True,
            metadata={
                "agent": "risk_manager",
                "framework": "langgraph",
                "processing_time_ms": round(processing_time, 2),
                **request.metadata
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    import time
    uptime = time.time() - start_time if 'start_time' in globals() else 0
    
    return HealthResponse(
        status="healthy",
        agent="risk_manager",
        framework="langgraph",
        uptime=f"{uptime:.2f} seconds"
    )

@app.get("/graph/info", response_model=GraphInfoResponse, tags=["Graph"])
async def graph_info():
    """Get graph structure information"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return GraphInfoResponse(
        graph_info=agent.get_graph_info()
    )

# Development server
if __name__ == "__main__":
    import time
    start_time = time.time()
    
    port = 8001
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🌐 Starting risk_manager FastAPI server")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Alternative docs: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
