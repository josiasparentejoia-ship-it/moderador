# 🚀 Guia de Deploy - Bot Moderador Valak Search

## 📦 Deploy com Docker

### Pré-requisitos
- Docker e Docker Compose instalados
- Bot criado no Telegram (@BotFather)
- Bot adicionado como Admin no grupo
- Domínio/URL pública para hospedar o WebApp

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/josiasparentejoia-ship-it/moderador.git
cd moderador
```

### Passo 2: Configurar Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env
```

Configure as seguintes variáveis:
```env
BOT_TOKEN=seu_token_do_botfather
GROUP_ID=-1002603662151
WEBAPP_URL=https://seu-dominio.com
PORT=8000
CRON_SCHEDULE=0 */3 * * *
PERIODIC_MESSAGES=📢 Mensagem 1|||🎯 Mensagem 2|||⭐ Mensagem 3
```

### Passo 3: Obter o ID do Grupo
```bash
# No Telegram, adicione @userinfobot ao seu grupo
# O bot responderá com o ID do grupo (número negativo)
# Cole esse ID no GROUP_ID do arquivo .env
```

### Passo 4: Configurar Permissões do Bot
No Telegram, garanta que o bot tenha as permissões:
- ✅ Apagar mensagens
- ✅ Restringir membros
- ✅ Adicionar novos admins (opcional)

### Passo 5: Build e Deploy
```bash
# Build da imagem
docker-compose build

# Inicia o container em background
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f
```

### Passo 6: Verificar Status
```bash
# Acesse o endpoint de status
curl http://localhost:8000/status

# Ou no navegador
http://seu-ip:8000/status
```

### Comandos Úteis

**Ver logs:**
```bash
docker-compose logs -f
```

**Parar o bot:**
```bash
docker-compose down
```

**Reiniciar após mudanças:**
```bash
docker-compose down
docker-compose up -d --build
```

**Entrar no container:**
```bash
docker exec -it valak-moderador sh
```

**Ver containers rodando:**
```bash
docker ps
```

---

## 🌐 Deploy em Serviços Cloud

### Railway
1. Conecte seu repositório no Railway
2. Configure as variáveis de ambiente no painel
3. Railway detectará automaticamente o Dockerfile
4. Deploy automático a cada push

### Render
1. Crie um novo Web Service
2. Conecte o repositório
3. Configure:
   - Build Command: `docker build -t bot .`
   - Start Command: `docker run bot`
4. Adicione as variáveis de ambiente

### Heroku
```bash
# Login no Heroku
heroku login

# Crie uma nova app
heroku create seu-bot-nome

# Configure as variáveis de ambiente
heroku config:set BOT_TOKEN=seu_token
heroku config:set GROUP_ID=-1002603662151
heroku config:set WEBAPP_URL=https://sua-app.herokuapp.com
heroku config:set CRON_SCHEDULE="0 */3 * * *"
heroku config:set PERIODIC_MESSAGES="Msg1|||Msg2|||Msg3"

# Deploy via container
heroku container:push web
heroku container:release web
```

### VPS/Servidor Próprio
```bash
# Clone o repositório
git clone https://github.com/josiasparentejoia-ship-it/moderador.git
cd moderador

# Configure o .env
nano .env

# Inicie com docker-compose
docker-compose up -d

# Configure para iniciar automaticamente (systemd)
# Crie o arquivo /etc/systemd/system/valak-bot.service
```

Arquivo systemd:
```ini
[Unit]
Description=Valak Moderador Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/caminho/para/moderador
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Ative o serviço:
```bash
sudo systemctl enable valak-bot
sudo systemctl start valak-bot
sudo systemctl status valak-bot
```

---

## 🔧 Troubleshooting

### Bot não recebe eventos de novos membros
- Verifique se o bot é Admin do grupo
- Confirme que `allowedUpdates` inclui `'chat_member'`

### Mensagens periódicas não são enviadas
- Verifique o formato do CRON_SCHEDULE
- Veja os logs: `docker-compose logs -f`
- Teste o cron em: https://crontab.guru/

### Container reinicia constantemente
```bash
# Veja os logs
docker-compose logs -f

# Verifique se todas as variáveis estão no .env
cat .env
```

### Porta já em uso
```bash
# Mude a porta no docker-compose.yml
ports:
  - "8001:8000"  # Usa porta 8001 no host
```

---

## 📊 Monitoramento

**Ver status em tempo real:**
```bash
watch -n 2 'docker-compose ps && echo && docker-compose logs --tail=10'
```

**Métricas do container:**
```bash
docker stats valak-moderador
```

**Endpoint de health check:**
```
GET http://seu-ip:8000/status
```

Resposta esperada:
```json
{
  "status": "Bot rodando",
  "group_id": -1002603662151,
  "periodic_messages": {
    "enabled": true,
    "schedule": "0 */3 * * *",
    "messages_count": 3
  }
}
```

---

## 🔄 Atualização

```bash
# Parar o bot
docker-compose down

# Atualizar código
git pull origin main

# Reconstruir e reiniciar
docker-compose up -d --build

# Verificar logs
docker-compose logs -f
```

---

## 📝 Notas Importantes

1. **Nunca commite o arquivo `.env`** - ele contém informações sensíveis
2. **Use HTTPS** no WEBAPP_URL em produção
3. **Backup regular** das configurações e .env
4. **Monitore os logs** regularmente para detectar problemas
5. **Teste localmente** antes de fazer deploy em produção

---

## 💡 Dicas

- Use `screen` ou `tmux` se rodar sem Docker
- Configure logs rotation para não encher o disco
- Use webhook se possível (mais eficiente que polling)
- Adicione healthchecks no docker-compose para auto-restart
- Configure alerts para quando o bot cair

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs -f`
2. Teste o endpoint: `curl http://localhost:8000/status`
3. Valide o cron: https://crontab.guru/
4. Abra uma issue: https://github.com/josiasparentejoia-ship-it/moderador/issues
