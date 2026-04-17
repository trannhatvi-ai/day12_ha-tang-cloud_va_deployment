$resp = Invoke-RestMethod -Uri 'http://localhost:8000/auth/token' -Method POST -Headers @{'Content-Type'='application/json'} -Body '{"username": "student", "password": "demo123"}'
$TOKEN = $resp.access_token
Write-Host "Got token: $($TOKEN.Substring(0,20))..."

for ($i=1; $i -le 15; $i++) {
    try {
        $body = '{"question": "Test ' + $i + '"}'
        $r = Invoke-RestMethod -Uri 'http://localhost:8000/ask' -Method POST `
            -Headers @{'Authorization' = "Bearer $TOKEN"; 'Content-Type' = 'application/json'} `
            -Body $body
        Write-Host "Req $i OK - remaining=$($r.usage.requests_remaining)" -ForegroundColor Green
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        Write-Host "Req $i FAILED - HTTP $status (Rate limit hit!)" -ForegroundColor Red
    }
}
