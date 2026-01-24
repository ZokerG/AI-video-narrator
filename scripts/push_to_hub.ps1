param(
    [Parameter(Mandatory=$true)]
    [string]$DockerUser,

    [Parameter(Mandatory=$true)]
    [string]$Ec2Address
)

# Backend
Write-Host "🚀 Building Backend..."
docker build -t $DockerUser/quinesis-backend:latest .
if ($LASTEXITCODE -ne 0) { Write-Error "Backend build failed"; exit 1 }

Write-Host "⬆️ Pushing Backend..."
docker push $DockerUser/quinesis-backend:latest

# Frontend
Write-Host "🚀 Building Frontend (Proxy Mode)..."
# No URL baked in, using relative /api path
docker build --no-cache -t $DockerUser/quinesis-frontend:latest ./frontend
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend build failed"; exit 1 }

Write-Host "⬆️ Pushing Frontend..."
docker push $DockerUser/quinesis-frontend:latest

Write-Host "✅ All images pushed to Docker Hub!"
