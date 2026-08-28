# 🐳 Deploy com Docker - Guia Completo

## 📋 Visão Geral

Este guia mostra como fazer deploy do bot usando Docker em diferentes plataformas.

---

## 🚀 Deploy Local (Teste)

### 1. Build da Imagem

```bash
docker-compose -f docker-compose.python.yml build
```

### 2. Configurar Variáveis (.env)

Certifique-se que o `.env` está configurado:

```env
BOT_TOKEN=seu_token_aqui
GROUP_ID=-1002603662151
WEBAPP_URL=https://josiasparentejoia-ship-it.github.io/moderador/
ADMIN_ID=5657795813
```

### 3. Iniciar Container

```bash
# Inicia em background
docker-compose -f docker-compose.python.yml up -d

# Ver logs em tempo real
docker-compose -f docker-compose.python.yml logs -f

# Ver status
docker-compose -f docker-compose.python.yml ps
```

### 4. Parar Container

```bash
docker-compose -f docker-compose.python.yml down
```

### 5. Reiniciar (após mudanças)

```bash
docker-compose -f docker-compose.python.yml down
docker-compose -f docker-compose.python.yml up -d --build
```

---

## ☁️ Deploy em VPS/Servidor Cloud

### Pré-requisitos

- Servidor Linux (Ubuntu/Debian)
- Docker e Docker Compose instalados
- Acesso SSH ao servidor

### Passo a Passo

#### 1. Conectar ao Servidor

```bash
ssh user@seu-servidor.com
```

#### 2. Instalar Docker (se necessário)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

#### 3. Clonar Repositório

```bash
git clone https://github.com/josiasparentejoia-ship-it/moderador.git
cd moderador
```

#### 4. Configurar Variáveis

```bash
# Criar .env
nano .env
```

Cole suas configurações:
```env
BOT_TOKEN=seu_token
GROUP_ID=-1002603662151
WEBAPP_URL=https://josiasparentejoia-ship-it.github.io/moderador/
ADMIN_ID=5657795813
```

Salve: `Ctrl+O` → `Enter` → `Ctrl+X`

#### 5. Criar config.json Inicial

```bash
cat > config.json << 'EOF'
{
  "admin_ids": [5657795813],
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
```

#### 6. Build e Deploy

```bash
# Build da imagem
docker-compose -f docker-compose.python.yml build

# Iniciar em background
docker-compose -f docker-compose.python.yml up -d

# Ver logs
docker-compose -f docker-compose.python.yml logs -f
```

#### 7. Configurar Auto-Start (systemd)

```bash
# Criar service
sudo nano /etc/systemd/system/valak-bot.service
```

Cole:
```ini
[Unit]
Description=Valak Moderador Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/moderador
ExecStart=/usr/local/bin/docker-compose -f docker-compose.python.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.python.yml down
User=user

[Install]
WantedBy=multi-user.target
```

**Importante:** Substitua `/home/user/moderador` pelo caminho correto!

Ativar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable valak-bot
sudo systemctl start valak-bot
sudo systemctl status valak-bot
```

---

## 🌐 Deploy no Railway

### Método 1: Usando Railway CLI

#### 1. Instalar Railway CLI

```bash
npm i -g @railway/cli
```

#### 2. Login

```bash
railway login
```

#### 3. Criar Projeto

```bash
cd moderador
railway init
```

#### 4. Adicionar Variáveis

```bash
railway variables set BOT_TOKEN=seu_token
railway variables set GROUP_ID=-1002603662151
railway variables set WEBAPP_URL=https://josiasparentejoia-ship-it.github.io/moderador/
railway variables set ADMIN_ID=5657795813
```

#### 5. Deploy

```bash
railway up
```

### Método 2: GitHub Integration

1. Vá em https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Selecione: `josiasparentejoia-ship-it/moderador`
4. Railway detectará o Dockerfile automaticamente
5. Adicione as variáveis de ambiente no painel
6. Deploy automático!

---

## 🔵 Deploy no Render

1. Vá em https://render.com
2. **New** → **Web Service**
3. Conecte seu repositório GitHub
4. Configurações:
   - **Name:** valak-moderador-bot
   - **Environment:** Docker
   - **Docker Build Context:** .
   - **Dockerfile Path:** Dockerfile.python

5. Adicione variáveis de ambiente:
   ```
   BOT_TOKEN=seu_token
   GROUP_ID=-1002603662151
   WEBAPP_URL=https://josiasparentejoia-ship-it.github.io/moderador/
   ADMIN_ID=5657795813
   ```

6. **Create Web Service**

---

## 🟣 Deploy no Heroku

### Usando Container Registry

```bash
# Login
heroku login
heroku container:login

# Criar app
heroku create valak-moderador-bot

# Configurar variáveis
heroku config:set BOT_TOKEN=seu_token
heroku config:set GROUP_ID=-1002603662151
heroku config:set WEBAPP_URL=https://josiasparentejoia-ship-it.github.io/moderador/
heroku config:set ADMIN_ID=5657795813

# Build e push
heroku container:push web -a valak-moderador-bot

# Release
heroku container:release web -a valak-moderador-bot

# Ver logs
heroku logs --tail -a valak-moderador-bot
```

---

## 🔧 Comandos Úteis

### Ver Logs

```bash
# Tempo real
docker-compose -f docker-compose.python.yml logs -f

# Últimas 100 linhas
docker-compose -f docker-compose.python.yml logs --tail=100

# Logs específicos
docker logs valak-moderador-bot -f
```

### Entrar no Container

```bash
docker exec -it valak-moderador-bot bash
```

### Reiniciar Bot

```bash
docker-compose -f docker-compose.python.yml restart
```

### Atualizar Bot

```bash
# Parar
docker-compose -f docker-compose.python.yml down

# Pull código novo
git pull origin main

# Build e iniciar
docker-compose -f docker-compose.python.yml up -d --build
```

### Ver Status

```bash
docker-compose -f docker-compose.python.yml ps
```

### Limpar Tudo

```bash
# Para e remove containers
docker-compose -f docker-compose.python.yml down

# Remove imagens também
docker-compose -f docker-compose.python.yml down --rmi all

# Remove volumes também
docker-compose -f docker-compose.python.yml down -v
```

---

## 📊 Monitoramento

### Ver Uso de Recursos

```bash
docker stats valak-moderador-bot
```

### Healthcheck

```bash
docker inspect --format='{{json .State.Health}}' valak-moderador-bot | python -m json.tool
```

### Ver Configurações

```bash
docker-compose -f docker-compose.python.yml config
```

---

## 🔐 Segurança

### ✅ Boas Práticas Implementadas

- Container roda como usuário não-root
- Logs com rotação automática (max 10MB, 3 arquivos)
- Healthcheck configurado
- Restart automático
- Variáveis sensíveis via .env (não no código)

### ⚠️ Importante

- **NUNCA** commite o arquivo `.env`
- **NUNCA** exponha o `BOT_TOKEN`
- Use volumes para `config.json` (persiste dados)
- Configure backup regular do `config.json`

---

## 📝 Arquivo .dockerignore

Já configurado para excluir:
```
node_modules
*.log
.env
.env.local
.git
.gitignore
*.md
.DS_Store
*.py
railway.toml
*.PNG
*.png
*.mp4
```

---

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs de erro
docker-compose -f docker-compose.python.yml logs

# Verificar se variáveis estão corretas
docker-compose -f docker-compose.python.yml config
```

### Bot não responde

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.python.yml logs -f

# Entrar no container e testar
docker exec -it valak-moderador-bot python -c "import aiogram; print('OK')"
```

### Erro de permissão

```bash
# Dar permissão ao config.json
chmod 666 config.json
```

### Container reinicia constantemente

```bash
# Ver status e última saída
docker ps -a
docker logs valak-moderador-bot --tail=50
```

---

## 🎯 Checklist de Deploy

- [ ] Dockerfile.python atualizado
- [ ] docker-compose.python.yml configurado
- [ ] .env criado com todas as variáveis
- [ ] config.json criado
- [ ] Build da imagem OK
- [ ] Container iniciou sem erros
- [ ] Bot respondendo no Telegram (/admin)
- [ ] Logs sem erros
- [ ] Healthcheck passando
- [ ] Auto-restart configurado

---

## 📚 Recursos

- Docker Docs: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose/
- Railway: https://railway.app
- Render: https://render.com
- Heroku: https://heroku.com

---

**Bot online com Docker! 🐳🚀**
