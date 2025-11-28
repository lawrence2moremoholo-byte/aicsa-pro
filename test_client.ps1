# AICSA Pro Test Client
Write-Host "=== AICSA Pro Testing ===" -ForegroundColor Cyan

# Test data for different business domains
$customerSupportMetrics = @{
    response_accuracy = 0.72
    resolution_time = 4.5
    customer_satisfaction = 3.8
    first_contact_resolution = 0.65
}

$technicalSupportMetrics = @{
    issue_resolution_rate = 0.68
    first_call_resolution = 0.62
    escalation_rate = 0.25
    average_handle_time = 8.2
}

$salesMetrics = @{
    lead_conversion_rate = 0.15
    qualification_accuracy = 0.70
    response_time = 2.1
    deal_size = 2500
}

# API configuration
$baseUrl = "https://aicsa.org.za"
$apiKey = ""  # Will be filled after registration

# Function to make API calls
function Invoke-AICSARequest {
    param($Uri, $Method, $Body, $ContentType = "application/json")
    
    $headers = @{
        "Content-Type" = $ContentType
    }
    
    if ($apiKey) {
        $headers["Authorization"] = "Bearer $apiKey"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Body $Body -Headers $headers
        return $response
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
        return $null
    }
}

# 1. Register a new client
Write-Host "`n1. Registering new client..." -ForegroundColor Yellow
$registerBody = @{
    client_name = "Test Corporation"
    domain = "customer_support"
    metrics = $customerSupportMetrics
} | ConvertTo-Json -Compress

$registration = Invoke-AICSARequest -Uri "$baseUrl/register-client" -Method "POST" -Body $registerBody

if ($registration) {
    $apiKey = $registration.api_key
    Write-Host "✅ Client registered successfully!" -ForegroundColor Green
    Write-Host "   Client ID: $($registration.client_id)" -ForegroundColor Gray
    Write-Host "   API Key: $apiKey" -ForegroundColor Gray
} else {
    Write-Host "❌ Client registration failed" -ForegroundColor Red
    exit
}

# 2. Test performance analysis
Write-Host "`n2. Testing performance analysis..." -ForegroundColor Yellow
$analysisBody = @{
    domain = "customer_support"
    metrics = $customerSupportMetrics
} | ConvertTo-Json -Compress

$analysis = Invoke-AICSARequest -Uri "$baseUrl/analyze-performance" -Method "POST" -Body $analysisBody

if ($analysis) {
    Write-Host "✅ Performance analysis completed!" -ForegroundColor Green
    Write-Host "   Client: $($analysis.client)" -ForegroundColor Gray
    Write-Host "   Status: $($analysis.status)" -ForegroundColor Gray
    
    # Display analysis results
    $analysis.analysis | ConvertTo-Json -Depth 4 | Write-Host -ForegroundColor White
} else {
    Write-Host "❌ Performance analysis failed" -ForegroundColor Red
}

# 3. Test with different domain
Write-Host "`n3. Testing technical support domain..." -ForegroundColor Yellow
$techBody = @{
    domain = "technical_support"
    metrics = $technicalSupportMetrics
} | ConvertTo-Json -Compress

$techAnalysis = Invoke-AICSARequest -Uri "$baseUrl/analyze-performance" -Method "POST" -Body $techBody

if ($techAnalysis) {
    Write-Host "✅ Technical analysis completed!" -ForegroundColor Green
    
    # Show recommendations
    $recommendations = $techAnalysis.analysis.recommendations
    Write-Host "   Recommendations:" -ForegroundColor Cyan
    foreach ($rec in $recommendations) {
        Write-Host "   - $rec" -ForegroundColor Gray
    }
}

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan