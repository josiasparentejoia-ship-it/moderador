#!/bin/bash

# Script de deploy rápido para o bot moderador
# Uso: ./deploy.sh [local|vps|railway]

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🐳 BOT MODERADOR - DEPLOY COM DOCKER                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar modo de deploy
MODE="${1:-local}"

case $MODE in
  local)
    echo "📍 Modo: Deploy Local"
    echo ""

    # Verificar .env
    if [ ! -f .env ]; then
      echo "❌ Arquivo .env não encontrado!"
      echo "Copie .env.example e configure:"
      echo "  cp .env.example .env"
      echo "  nano .env"
      exit 1
    fi

    echo "✓ Arquivo .env encontrado"

    # Verificar config.json
    if [ ! -f config.json ]; then
      echo "⚠️ config.json não encontrado. Criando..."
      cat > config.json << 'EOF'
{
  "admin_ids": [],
  "welcome_message": {
    "text": "🎉 Bem-vindo(a), {name}!\n\nPara liberar o chat, aceite os termos do grupo.\n\n👇 Clique abaixo:",
    "media": null,
    "media_type": null,
    "button": {
      "text": "📋 ACEITE OS TERMOS",
      "url": "https://josiasparentejoia-ship-it.github.io/moderador/"
    }
  },
  "periodic_messages": []
}
EOF
      echo "✓ config.json criado"
    else
      echo "✓ config.json encontrado"
    fi

    echo ""
    echo "🔨 Fazendo build da imagem..."
    docker-compose -f docker-compose.python.yml build

    echo ""
    echo "🚀 Iniciando container..."
    docker-compose -f docker-compose.python.yml up -d

    echo ""
    echo "✅ Deploy concluído!"
    echo ""
    echo "📊 Ver logs:"
    echo "  docker-compose -f docker-compose.python.yml logs -f"
    echo ""
    echo "🛑 Parar bot:"
    echo "  docker-compose -f docker-compose.python.yml down"
    ;;

  vps)
    echo "📍 Modo: Deploy em VPS"
    echo ""
    echo "Este script instalará Docker e fará deploy do bot."
    echo "Certifique-se de estar conectado ao servidor via SSH."
    echo ""
    read -p "Continuar? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi

    # Instalar Docker
    if ! command -v docker &> /dev/null; then
      echo "🔨 Instalando Docker..."
      curl -fsSL https://get.docker.com -o get-docker.sh
      sudo sh get-docker.sh
      sudo usermod -aG docker $USER
      rm get-docker.sh
      echo "✓ Docker instalado"
    else
      echo "✓ Docker já instalado"
    fi

    # Instalar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
      echo "🔨 Instalando Docker Compose..."
      sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
      echo "✓ Docker Compose instalado"
    else
      echo "✓ Docker Compose já instalado"
    fi

    # Criar .env se não existir
    if [ ! -f .env ]; then
      echo ""
      echo "Configure o arquivo .env:"
      cp .env.example .env
      nano .env
    fi

    # Build e deploy
    echo ""
    echo "🔨 Fazendo build..."
    docker-compose -f docker-compose.python.yml build

    echo "🚀 Iniciando bot..."
    docker-compose -f docker-compose.python.yml up -d

    # Configurar systemd
    echo ""
    read -p "Configurar auto-start com systemd? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      CURRENT_DIR=$(pwd)
      CURRENT_USER=$(whoami)

      sudo tee /etc/systemd/system/valak-bot.service > /dev/null <<EOF
[Unit]
Description=Valak Moderador Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.python.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.python.yml down
User=$CURRENT_USER

[Install]
WantedBy=multi-user.target
EOF

      sudo systemctl daemon-reload
      sudo systemctl enable valak-bot
      echo "✓ Systemd configurado"
    fi

    echo ""
    echo "✅ Deploy concluído!"
    ;;

  railway)
    echo "📍 Modo: Deploy no Railway"
    echo ""

    # Verificar Railway CLI
    if ! command -v railway &> /dev/null; then
      echo "❌ Railway CLI não encontrado!"
      echo "Instale com: npm i -g @railway/cli"
      exit 1
    fi

    echo "🔐 Fazendo login no Railway..."
    railway login

    echo "🆕 Inicializando projeto..."
    railway init

    echo "🔧 Configurando variáveis de ambiente..."
    echo ""
    echo "Digite as variáveis:"
    read -p "BOT_TOKEN: " BOT_TOKEN
    read -p "GROUP_ID: " GROUP_ID
    read -p "WEBAPP_URL: " WEBAPP_URL
    read -p "ADMIN_ID: " ADMIN_ID

    railway variables set BOT_TOKEN="$BOT_TOKEN"
    railway variables set GROUP_ID="$GROUP_ID"
    railway variables set WEBAPP_URL="$WEBAPP_URL"
    railway variables set ADMIN_ID="$ADMIN_ID"

    echo ""
    echo "🚀 Fazendo deploy..."
    railway up

    echo ""
    echo "✅ Deploy concluído!"
    ;;

  *)
    echo "❌ Modo inválido: $MODE"
    echo ""
    echo "Uso: ./deploy.sh [local|vps|railway]"
    echo ""
    echo "Modos disponíveis:"
    echo "  local    - Deploy local (teste)"
    echo "  vps      - Deploy em VPS/servidor"
    echo "  railway  - Deploy no Railway"
    exit 1
    ;;
esac
