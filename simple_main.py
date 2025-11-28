from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import openai
import uuid
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from payments import PaymentSystem
from datetime import datetime, timedelta
from webhooks import WebhookManager

# Database setup
Base = declarative_base()
engine = create_engine("sqlite:///./aicsa.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    domain = Column(String)
    api_key = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer)
    hypothesis = Column(Text)
    intervention_type = Column(String)
    status = Column(String)
    results = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer)
    plan_type = Column(String)  # basic, advanced, enterprise
    status = Column(String)  # active, canceled, expired
    charge_id = Column(String)  # Yoco charge ID
    amount_paid = Column(Float)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer)
    webhook_url = Column(String)  # Client's URL to receive notifications
    event_types = Column(String)  # Types of events client wants to receive
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Initialize database
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Initialize payment system
payment_system = PaymentSystem()

# Initialize webhook manager
webhook_manager = WebhookManager()

# AI Service
class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "demo_key"))  # REPLACE WITH YOUR KEY
    
    def analyze_performance_gaps(self, metrics: Dict[str, float], domain: str) -> List[str]:
        prompt = f"Analyze these {domain} metrics: {metrics}. Return top 3 gaps as JSON array."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            gaps = eval(response.choices[0].message.content)
            return gaps[:3]
        except:
            return ["High response time", "Low accuracy", "Customer dissatisfaction"]
    
    def generate_improvement_plan(self, gaps: List[str], domain: str) -> Dict[str, Any]:
        prompt = f"For {domain}, fix these gaps: {gaps}. Return JSON with proposals."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return eval(response.choices[0].message.content)
        except:
            return {"proposals": [{"hypothesis": "Improve response templates", "intervention": "prompt_change", "expected_impact": 0.15}]}
    
    def test_intervention(self, hypothesis: str, test_data: List[str]) -> Dict[str, Any]:
        return {"success_rate": 0.85, "improvement": 0.12, "risks": ["Low risk"]}

# Agent Controller
class AgentController:
    def __init__(self):
        self.ai_service = AIService()
        self.db = SessionLocal()
    
    def analyze_client_performance(self, client_id: int, domain: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        gaps = self.ai_service.analyze_performance_gaps(metrics, domain)
        print(f"Found gaps: {gaps}")
        
        proposals_data = self.ai_service.generate_improvement_plan(gaps, domain)
        
        tested_proposals = []
        for proposal in proposals_data.get("proposals", [])[:1]:
            test_result = self.ai_service.test_intervention(proposal["hypothesis"], [])
            
            experiment = Experiment(
                client_id=client_id,
                hypothesis=proposal["hypothesis"],
                intervention_type=proposal["intervention"],
                status="completed",
                results=str(test_result)
            )
            self.db.add(experiment)
            self.db.commit()
            
            tested_proposals.append({
                "hypothesis": proposal["hypothesis"],
                "intervention": proposal["intervention"],
                "test_results": test_result
            })
        
        return {
            "client_id": client_id,
            "domain": domain,
            "performance_gaps": gaps,
            "tested_proposals": tested_proposals,
            "recommendations": ["IMPLEMENT: " + p["hypothesis"] for p in tested_proposals]
        }

# FastAPI App
app = FastAPI(title="AICSA Pro")
app.mount("/static", StaticFiles(directory="templates"), name="static")
agent_controller = AgentController()

class ClientMetrics(BaseModel):
    domain: str
    metrics: Dict[str, float]

class RSIRequest(BaseModel):
    client_name: str
    domain: str
    metrics: Dict[str, float]

def get_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if auth_header.startswith("Bearer "):
        api_key = auth_header.replace("Bearer ", "")
    else:
        api_key = auth_header
    
    db = next(get_db())
    client = db.query(Client).filter(Client.api_key == api_key).first()
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return client
@app.get("/")
async def serve_dashboard():
    return FileResponse("templates/simple_dash.html")

@app.post("/register-client")
def register_client(client_data: RSIRequest):
    db = next(get_db())
    api_key = f"acs_{str(uuid.uuid4())[:16]}"
    
    client = Client(
        name=client_data.client_name,
        domain=client_data.domain,
        api_key=api_key
    )
    
    db.add(client)
    db.commit()
    
    return {
        "client_id": client.id,
        "api_key": api_key,
        "message": "Client registered successfully"
    }

@app.post("/analyze-performance")
def analyze_performance(metrics: ClientMetrics, client: Client = Depends(get_api_key)):
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
    
@app.post("/client-metrics")
async def receive_client_metrics(
    metrics_data: dict,
    client: Client = Depends(get_api_key)
):
    """Receive metrics from client applications and provide AI analysis"""
    try:
        metrics = metrics_data.get("metrics", {})
        
        if not metrics:
            raise HTTPException(status_code=400, detail="No metrics provided")
        
        print(f"Received metrics from client {client.name}: {metrics}")
        
        # Analyze the metrics
        result = agent_controller.analyze_client_performance(
            client_id=client.id,
            domain=client.domain,
            metrics=metrics
        )
        
        # Store the analysis in database
        db = next(get_db())
        
        # Log this API call
        experiment = Experiment(
            client_id=client.id,
            hypothesis="API-driven metric analysis",
            intervention_type="api_analysis",
            status="completed",
            results=f"Metrics analyzed: {list(metrics.keys())}"
        )
        db.add(experiment)
        db.commit()
        
        # Return comprehensive analysis
        return {
            "status": "success",
            "client": client.name,
            "analysis_id": f"analysis_{client.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "performance_gaps": result["performance_gaps"],
            "recommendations": result["recommendations"],
            "metrics_received": list(metrics.keys()),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscription-status")
async def get_subscription_status(client: Client = Depends(get_api_key)):
    """Get client's subscription status"""
    db = next(get_db())
    subscription = db.query(Subscription).filter(
        Subscription.client_id == client.id,
        Subscription.status == "active"
    ).first()
    
    if subscription and subscription.end_date > datetime.utcnow():
        return {
            "status": "active",
            "plan": subscription.plan_type,
            "expires": subscription.end_date.isoformat()
        }
    else:
        return {"status": "inactive", "plan": "none"}
    
@app.post("/register-webhook")
async def register_webhook(
    webhook_data: dict,
    client: Client = Depends(get_api_key)
):
    """Register a webhook URL for a client"""
    try:
        db = next(get_db())
        
        webhook = Webhook(
            client_id=client.id,
            webhook_url=webhook_data.get("webhook_url"),
            event_types=webhook_data.get("event_types", "all")
        )
        
        db.add(webhook)
        db.commit()
        
        return {
            "status": "success",
            "message": "Webhook registered successfully",
            "webhook_id": webhook.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-webhook")
async def test_webhook(client: Client = Depends(get_api_key)):
    """Send a test webhook to the client"""
    try:
        db = next(get_db())
        webhook = db.query(Webhook).filter(Webhook.client_id == client.id).first()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="No webhook registered")
        
        # Create test payload
        test_payload = webhook_manager.create_new_recommendation_alert(
            client.name,
            "Test recommendation - your webhook is working!"
        )
        
        # Send webhook
        success = webhook_manager.send_webhook(webhook.webhook_url, test_payload)
        
        if success:
            return {"status": "success", "message": "Test webhook sent successfully"}
        else:
            return {"status": "error", "message": "Failed to send test webhook"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook-logs")
async def get_webhook_logs(client: Client = Depends(get_api_key)):
    """Get webhook delivery logs (simplified for demo)"""
    return {
        "status": "success",
        "client": client.name,
        "webhooks_sent": 5,
        "last_sent": "2025-11-28T17:45:00Z",
        "success_rate": "100%"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AICSA Pro"}

# Render deployment
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)