from typing import Dict, Any
import requests
import json
import os

class PaymentSystem:
    def __init__(self):
        # Your Yoco secret key (keep this safe!)
        self.secret_key = os.getenv("YOCO_SECRET_KEY", "demo_key_for_testing")  # Replace with your actual secret key
        
        # Pricing plans
        self.plans = {
            "basic": {
                "name": "Basic",
                "price": 14900,  # in cents (R149)
                "features": ["1000 AI analyses/month", "Basic dashboard", "Email support"]
            },
            "advanced": {
                "name": "Advanced", 
                "price": 49900,  # in cents (R499)
                "features": ["5000 AI analyses/month", "Advanced dashboard", "Priority support", "API access"]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 99900,  # in cents (R999)
                "features": ["Unlimited analyses", "Full dashboard", "24/7 support", "Custom integrations"]
            }
        }
    
    def create_payment(self, plan_type: str, token: str, email: str) -> Dict[str, Any]:
        """Process a payment with Yoco"""
        try:
            plan = self.plans.get(plan_type)
            if not plan:
                return {"success": False, "error": "Invalid plan type"}
            
            # For demo purposes, we'll simulate successful payment
            # In production, you'd make actual API call to Yoco:
            # headers = {'Authorization': f'Bearer {self.secret_key}'}
            # data = {
            #     'token': token,
            #     'amountInCents': plan["price"],
            #     'currency': 'ZAR'
            # }
            # response = requests.post('https://payments.yoco.com/api/charges', headers=headers, json=data)
            
            # Simulate payment processing
            print(f"DEMO: Processing {plan['name']} plan payment for {email}")
            print(f"DEMO: Amount: R{plan['price'] / 100}")
            print(f"DEMO: Token: {token}")
            
            # Simulate successful payment
            return {
                "success": True,
                "charge_id": f"ch_demo_{plan_type}_{email}",
                "amount": plan["price"] / 100,  # Convert to Rands
                "plan": plan_type,
                "email": email
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_plans(self) -> Dict[str, Any]:
        """Return available pricing plans"""
        return self.plans