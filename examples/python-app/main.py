#!/usr/bin/env python3
"""
Example Python application with AI-integrated CI/CD pipeline
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GenAI CICD Example",
    description="Example Python application with AI-integrated CI/CD pipeline",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to GenAI CICD Example",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID - example endpoint"""
    if user_id < 1:
        raise HTTPException(status_code=400, detail="User ID must be positive")
    
    # Simulate user data
    user_data = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": datetime.now().isoformat()
    }
    
    logger.info(f"Retrieved user data for ID: {user_id}")
    return user_data

@app.post("/api/users")
async def create_user(user_data: dict):
    """Create new user - example endpoint"""
    required_fields = ["name", "email"]
    
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Simulate user creation
    new_user = {
        "id": 12345,  # Would be generated in real app
        "name": user_data["name"],
        "email": user_data["email"],
        "created_at": datetime.now().isoformat()
    }
    
    logger.info(f"Created new user: {new_user['name']}")
    return new_user

@app.get("/api/metrics")
async def get_metrics():
    """Get application metrics"""
    return {
        "requests_total": 1000,
        "response_time_avg": 0.125,
        "error_rate": 0.01,
        "uptime_seconds": 86400,
        "memory_usage_mb": 256,
        "cpu_usage_percent": 15.5
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)