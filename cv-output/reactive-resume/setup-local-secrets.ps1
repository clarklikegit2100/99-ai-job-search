$ErrorActionPreference = "Stop"

$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path -LiteralPath $envFile) {
    Write-Host ".env already exists; keeping the current encryption secret."
    exit 0
}

$bytes = [byte[]]::new(48)
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
$secret = [Convert]::ToBase64String($bytes)
[System.IO.File]::WriteAllText($envFile, "ENCRYPTION_SECRET=$secret`n", [System.Text.UTF8Encoding]::new($false))
Write-Host "Created a local .env containing ENCRYPTION_SECRET. Keep this file private and backed up."
