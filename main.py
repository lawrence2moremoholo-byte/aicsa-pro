from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from infrastructure.database import init_db, get_db, Client
from core.agent_controller import AgentController
import uuid

app = FastAPI(title="AICSA Pro", description="AI Customer Success Automation")

# Initialize database
init_db()

# Initialize agent controller
agent_controller = AgentController()

class ClientMetrics(BaseModel):
    domain: str
    metrics: Dict[str, float]

class RSIRequest(BaseModel):
    client_name: str
    domain: str
    metrics: Dict[str, float]

# API Key security
def get_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if auth_header.startswith("Bearer "):
        api_key = auth_header.replace("Bearer ", "")
    else:
        api_key = auth_header
    
    # Check if client exists with this API key
    db = next(get_db())
    client = db.query(Client).filter(Client.api_key == api_key).first()
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return client

@app.post("/register-client")
def register_client(client_data: RSIRequest):
    """Register a new client"""
    db = next(get_db())
    
    # Generate API key for client
    api_key = f"acs_{str(uuid.uuid4())[:16]}"
    
    client = Client(
        name=client_data.client_name,
        domain=client_data.domain,
        api_key=api_key
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return {
        "client_id": client.id,
        "api_key": api_key,
        "message": "Client registered successfully"
    }

@app.post("/analyze-performance")
def analyze_performance(metrics: ClientMetrics, client: Client = Depends(get_api_key)):
    """Main RSI analysis endpoint"""
    try:
        result = agent_controller.analyze_client_performance(
            client_id=client.id,
            domain=metrics.domain,
            metrics=metrics.metrics
        )
        
        return {
            "status": "success",
            "client": client.name,
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AICSA Pro"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)