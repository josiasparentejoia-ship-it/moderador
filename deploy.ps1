# Script de deploy rápido para Windows
# Uso: .\deploy.ps1 [local|test]

param([string]$Mode = "local")

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  BOT MODERADOR - DEPLOY COM DOCKER (Windows)  " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($Mode -eq "local") {
    Write-Host "[*] Modo: Deploy Local" -ForegroundColor Yellow
    Write-Host ""

    # Verificar Docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "[X] Docker nao encontrado!" -ForegroundColor Red
        Write-Host "Instale Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    }
    Write-Host "[OK] Docker encontrado" -ForegroundColor Green

    # Verificar .env
    if (-not (Test-Path .env)) {
        Write-Host "[X] Arquivo .env nao encontrado!" -ForegroundColor Red
        Write-Host "Configure: Copy-Item .env.example .env; notepad .env"
        exit 1
    }
    Write-Host "[OK] Arquivo .env encontrado" -ForegroundColor Green

    # Criar config.json se não existir
    if (-not (Test-Path config.json)) {
        Write-Host "[!] Criando config.json..." -ForegroundColor Yellow
        @"
{
  "admin_ids": [],
  "welcome_message": {
    "text": "Bem-vindo(a), {name}!",
    "media": null,
    "media_type": null,
    "button": {
      "text": "ACEITE OS TERMOS",
      "url": "https://josiasparentejoia-ship-it.github.io/moderador/"
    }
  },
  "periodic_messages": []
}
"@ | Out-File -FilePath config.json -Encoding UTF8
        Write-Host "[OK] config.json criado" -ForegroundColor Green
    } else {
        Write-Host "[OK] config.json encontrado" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "[*] Fazendo build da imagem..." -ForegroundColor Yellow
    docker-compose -f docker-compose.python.yml build

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] Erro no build!" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "[*] Iniciando container..." -ForegroundColor Yellow
    docker-compose -f docker-compose.python.yml up -d

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] Erro ao iniciar!" -ForegroundColor Red
        exit 1
    }

    Start-Sleep -Seconds 3

    Write-Host ""
    Write-Host "[OK] Deploy concluido!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Comandos uteis:" -ForegroundColor Cyan
    Write-Host "  Ver logs: docker-compose -f docker-compose.python.yml logs -f"
    Write-Host "  Status:   docker-compose -f docker-compose.python.yml ps"
    Write-Host "  Parar:    docker-compose -f docker-compose.python.yml down"

} elseif ($Mode -eq "test") {
    Write-Host "[*] Modo: Teste Rapido" -ForegroundColor Yellow
    Write-Host ""

    # Testar Python
    Write-Host "Testando Python..." -ForegroundColor White
    try { python --version; Write-Host "  [OK] Python" -ForegroundColor Green }
    catch { Write-Host "  [X] Python nao encontrado" -ForegroundColor Red }

    # Testar Docker
    Write-Host "Testando Docker..." -ForegroundColor White
    try { docker --version; Write-Host "  [OK] Docker" -ForegroundColor Green }
    catch { Write-Host "  [X] Docker nao encontrado" -ForegroundColor Red }

    # Testar Docker Compose
    Write-Host "Testando Docker Compose..." -ForegroundColor White
    try { docker-compose --version; Write-Host "  [OK] Docker Compose" -ForegroundColor Green }
    catch { Write-Host "  [X] Docker Compose nao encontrado" -ForegroundColor Red }

    # Verificar arquivos
    Write-Host ""
    Write-Host "Verificando arquivos..." -ForegroundColor Yellow
    $files = @("bot_admin.py", "Dockerfile.python", "docker-compose.python.yml", "requirements.txt", ".env", "config.json")
    foreach ($file in $files) {
        if (Test-Path $file) {
            Write-Host "  [OK] $file" -ForegroundColor Green
        } else {
            Write-Host "  [X] $file (nao encontrado)" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "[OK] Teste concluido!" -ForegroundColor Green

} else {
    Write-Host "[X] Modo invalido: $Mode" -ForegroundColor Red
    Write-Host ""
    Write-Host "Uso: .\deploy.ps1 [local|test]"
    Write-Host "  local - Deploy local com Docker"
    Write-Host "  test  - Testar configuracao"
    exit 1
}
