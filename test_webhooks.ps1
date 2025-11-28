Write-Host "Testing AICSA Pro Webhooks..." -ForegroundColor Cyan

# Configuration
$baseUrl = "https://aicsa.org.za"
$apiKey = "acs_7a88f7a9-371f-45"
$webhookUrl = "http://127.0.0.1:8001/webhook"

$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

# 1. Register webhook
Write-Host "`n1. Registering webhook..." -ForegroundColor Yellow

$webhookBody = @{
    webhook_url = $webhookUrl
    event_types = "all"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/register-webhook" -Method Post -Body $webhookBody -Headers $headers
    Write-Host "✅ Webhook registered: $($registerResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Webhook registration failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Test webhook
Write-Host "`n2. Testing webhook..." -ForegroundColor Yellow

try {
    $testResponse = Invoke-RestMethod -Uri "$baseUrl/test-webhook" -Method Post -Headers $headers
    Write-Host "✅ Webhook test: $($testResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Webhook test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Check webhook logs
Write-Host "`n3. Checking webhook logs..." -ForegroundColor Yellow

try {
    $logsResponse = Invoke-RestMethod -Uri "$baseUrl/webhook-logs" -Method Get -Headers $headers
    Write-Host "✅ Webhook logs:" -ForegroundColor Green
    $logsResponse | Format-List
} catch {
    Write-Host "❌ Failed to get logs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nWebhook testing complete!" -ForegroundColor Cyan