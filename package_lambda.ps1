#!/usr/bin/env pwsh
# package_lambda.ps1

Write-Host "Creating deployment package for AWS Lambda..."

# Ensure we are in the root directory
if (!(Test-Path "backend/main.py")) {
    Write-Error "Please run this script from the root directory (d:\BharatBuilds)"
    exit 1
}

# Create a temporary directory for the build
$buildDir = "build_lambda"
if (Test-Path $buildDir) { Remove-Item -Recurse -Force $buildDir }
New-Item -ItemType Directory -Path $buildDir | Out-Null

# Install dependencies into the build directory
Write-Host "Installing dependencies..."
pip install -r backend/requirements.txt -t $buildDir

# Copy the backend code into the build directory
Write-Host "Copying backend code..."
Copy-Item -Path "backend" -Destination "$buildDir/backend" -Recurse

# Copy config and .env if needed (be careful not to expose secrets in the repo, but Lambda needs them)
if (Test-Path ".env") {
    Copy-Item -Path ".env" -Destination "$buildDir/.env"
}

# Create the zip file
$zipFile = "backend_lambda_deploy.zip"
if (Test-Path $zipFile) { Remove-Item -Force $zipFile }
Write-Host "Zipping everything up to $zipFile..."
Compress-Archive -Path "$buildDir\*" -DestinationPath $zipFile

# Cleanup
Remove-Item -Recurse -Force $buildDir

Write-Host "Done! You can now upload $zipFile to AWS Lambda."
Write-Host "Set the Lambda Handler to: backend.main.handler"
