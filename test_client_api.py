import requests
import json

# Configuration
BASE_URL = "https://aicsa.org.za"
API_KEY = "acs_7a88f7a9-371f-45"  # Use your actual API key

def test_client_api():
    """Test the client API with sample metrics"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_metrics = {
        "response_accuracy": 0.75,
        "resolution_time": 3.2,
        "customer_satisfaction": 3.8
    }
    
    print("🧪 Testing AICSA Pro Client API...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/client-metrics",
            headers=headers,
            json={"metrics": test_metrics}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Call Successful!")
            print(f"Client: {result.get('client')}")
            print(f"Analysis ID: {result.get('analysis_id')}")
            print("Performance Gaps:")
            for gap in result.get('performance_gaps', []):
                print(f"  - {gap}")
            print("Recommendations:")
            for rec in result.get('recommendations', []):
                print(f"  - {rec}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    test_client_api()