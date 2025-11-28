from fastapi import FastAPI, Request
import uvicorn

# This is a test server that receives webhooks
app = FastAPI(title="Webhook Test Receiver")

@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive webhooks from AICSA Pro"""
    payload = await request.json()
    
    print("🎯 WEBHOOK RECEIVED!")
    print(f"Title: {payload.get('title')}")
    print(f"Message: {payload.get('message')}")
    print(f"Event: {payload.get('event_type')}")
    print(f"Client: {payload.get('client')}")
    print("---")
    
    return {"status": "success", "message": "Webhook received"}

@app.get("/")
async def home():
    return {"message": "Webhook test server is running"}

if __name__ == "__main__":
    print("🚀 Starting webhook test server on http://127.0.0.1:8001")
    print("This will receive webhooks from your AICSA Pro system")
    uvicorn.run(app, host="127.0.0.1", port=8001)