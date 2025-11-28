import requests
import json
from typing import Dict, List

class WebhookManager:
    def __init__(self):
        self.webhook_types = {
            "performance_alert": "Your performance score dropped significantly",
            "new_recommendation": "New AI recommendation available", 
            "subscription_expiring": "Your subscription is expiring soon",
            "system_update": "System update completed successfully"
        }
    
    def send_webhook(self, client_webhook_url: str, payload: Dict) -> bool:
        """Send a webhook to a client's URL"""
        try:
            response = requests.post(
                client_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5  # 5 second timeout
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Webhook delivered to {client_webhook_url}")
                return True
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return False
    
    def create_performance_alert(self, client_name: str, old_score: int, new_score: int) -> Dict:
        """Create a performance drop alert"""
        return {
            "event_type": "performance_alert",
            "title": "📉 Performance Alert",
            "message": f"Your AI performance score dropped from {old_score}% to {new_score}%",
            "client": client_name,
            "old_score": old_score,
            "new_score": new_score,
            "priority": "high",
            "timestamp": "2025-11-28T17:45:00Z"
        }
    
    def create_new_recommendation_alert(self, client_name: str, recommendation: str) -> Dict:
        """Create a new recommendation alert"""
        return {
            "event_type": "new_recommendation", 
            "title": "🎯 New AI Recommendation",
            "message": f"New optimization available: {recommendation}",
            "client": client_name,
            "recommendation": recommendation,
            "priority": "medium",
            "timestamp": "2025-11-28T17:45:00Z"
        }
    
    def create_subscription_alert(self, client_name: str, days_remaining: int) -> Dict:
        """Create subscription expiration alert"""
        return {
            "event_type": "subscription_expiring",
            "title": "⏰ Subscription Reminder",
            "message": f"Your subscription expires in {days_remaining} days",
            "client": client_name,
            "days_remaining": days_remaining,
            "priority": "medium",
            "timestamp": "2025-11-28T17:45:00Z"
        }