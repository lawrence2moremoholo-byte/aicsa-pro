# AICSA Pro API Documentation

## Base URL
`https://aicsa.org.za` 

## How to Use:

1. **Get your API Key:**
   - Go to the dashboard
   - Register a client
   - Copy the API key

2. **Send metrics like this:**
```bash
curl -X POST "https://aicsa.org.za/client-metrics" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {
      "response_accuracy": 0.84,
      "resolution_time": 2.1
    }
  }'