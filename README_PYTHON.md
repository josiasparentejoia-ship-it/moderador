# 🤖 Bot Moderador Valak Search - Python Edition

Bot administrativo completo para Telegram com dashboard inline para gerenciar grupo.

## ✨ Funcionalidades

### Dashboard Admin (via botões inline no privado do bot)
- 📨 **Mensagens Periódicas**
  - Criar mensagens com texto/foto/vídeo
  - Configurar intervalo de envio (minutos)
  - Ativar/pausar mensagens
  - Deletar mensagens
  - Listar todas as mensagens

- 👋 **Boas-Vindas Personalizadas**
  - Editar texto de boas-vindas
  - Adicionar foto ou vídeo
  - Visualizar preview
  - Usar `{name}` para nome do usuário

- 📤 **Envio Direto no Grupo**
  - Enviar texto
  - Enviar foto com legenda
  - Enviar vídeo com legenda

- 📊 **Status do Bot**
  - Visualizar estatísticas
  - Ver mensagens ativas
  - Informações do grupo

### Sistema Automático
- ✅ Detecta novos membros
- 🔒 Restringe automaticamente
- 📨 Envia mensagem de boas-vindas
- 🗑️ Apaga mensagem anterior
- ⏰ Envia mensagens periódicas

## 📋 Pré-requisitos

- Python 3.11+
- Bot do Telegram (@BotFather)
- Bot como Admin no grupo
- Seu USER_ID (use @userinfobot)

## ⚙️ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/josiasparentejoia-ship-it/moderador.git
cd moderador
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o .env
```bash
cp .env.example .env
nano .env
```

Configure:
```env
BOT_TOKEN=seu_token_do_botfather
GROUP_ID=-1002603662151
WEBAPP_URL=https://seu-dominio.com
ADMIN_ID=seu_user_id
```

**Como obter seu ADMIN_ID:**
1. No Telegram, envie mensagem para @userinfobot
2. O bot responderá com seu ID
3. Cole esse número no ADMIN_ID

### 4. Execute o bot
```bash
python bot_admin.py
```

## 🐳 Docker

### Build e Run
```bash
# Build da imagem
docker build -f Dockerfile.python -t valak-bot-python .

# Run
docker run -d --name valak-bot \
  --env-file .env \
  -v $(pwd)/config.json:/app/config.json \
  valak-bot-python
```

### Docker Compose
```bash
# Inicia
docker-compose -f docker-compose.python.yml up -d

# Ver logs
docker-compose -f docker-compose.python.yml logs -f

# Parar
docker-compose -f docker-compose.python.yml down
```

## 📱 Como Usar o Dashboard

### 1. Acesse o painel
No Telegram, envie `/admin` **no privado do bot** (não no grupo).

### 2. Menu Principal
Você verá o menu com as opções:
- 📨 Mensagens Periódicas
- 👋 Configurar Boas-Vindas
- 📤 Enviar no Grupo
- 📊 Ver Status
- ❌ Fechar

### 3. Criar Mensagem Periódica

1. Clique em "📨 Mensagens Periódicas"
2. Clique em "➕ Nova Mensagem"
3. Envie o texto da mensagem
4. Informe o intervalo em minutos (ex: 180 para 3 horas)
5. (Opcional) Envie foto ou vídeo, ou clique em "Pular"
6. Pronto! Mensagem criada e ativa

**Exemplos de intervalo:**
- `60` = envia a cada 1 hora
- `180` = envia a cada 3 horas
- `1440` = envia a cada 1 dia (24h)

### 4. Configurar Boas-Vindas

1. Clique em "👋 Configurar Boas-Vindas"
2. Escolha a opção:
   - **Editar Texto**: Envie o novo texto
   - **Adicionar Mídia**: Envie foto ou vídeo
   - **Remover Mídia**: Remove foto/vídeo atual
   - **Visualizar**: Vê como ficará a mensagem

**Use `{name}` no texto** para inserir o nome do usuário:
```
🎉 Bem-vindo(a), {name}!

Seja bem-vindo ao nosso grupo!
```

### 5. Enviar Mensagem no Grupo

1. Clique em "📤 Enviar no Grupo"
2. Envie:
   - **Texto simples**, ou
   - **Foto** (com legenda opcional), ou
   - **Vídeo** (com legenda opcional)
3. A mensagem será enviada imediatamente no grupo

### 6. Gerenciar Mensagens Periódicas

1. Clique em "📨 Mensagens Periódicas"
2. Clique em "📋 Listar Mensagens"
3. Para cada mensagem você pode:
   - **⏸️ Pausar** / **▶️ Ativar**: Liga/desliga o envio
   - **🗑️ Deletar**: Remove permanentemente

### 7. Cancelar Operação

Se você iniciou alguma operação e quer cancelar, envie:
```
/cancelar
```

## 📂 Estrutura de Arquivos

```
moderador/
├── bot_admin.py           # Bot principal (Python)
├── config.json            # Configurações (criado automaticamente)
├── .env                   # Variáveis de ambiente
├── requirements.txt       # Dependências Python
├── Dockerfile.python      # Docker para Python
├── docker-compose.python.yml
└── README_PYTHON.md       # Este arquivo
```

## 🔧 Configuração Avançada

### config.json

O arquivo `config.json` é criado automaticamente e armazena:
- IDs dos admins
- Configuração de boas-vindas
- Lista de mensagens periódicas

**Exemplo:**
```json
{
  "admin_ids": [123456789],
  "welcome_message": {
    "text": "🎉 Bem-vindo(a), {name}!...",
    "media": null,
    "media_type": null,
    "button": {
      "text": "📋 ACEITE OS TERMOS",
      "url": "https://seu-dominio.com"
    }
  },
  "periodic_messages": [
    {
      "id": 1692810923000,
      "text": "📢 Mensagem periódica!",
      "media": null,
      "media_type": null,
      "interval": 180,
      "enabled": true
    }
  ]
}
```

### Adicionar Múltiplos Admins

Edite `config.json` e adicione mais IDs:
```json
{
  "admin_ids": [123456789, 987654321, 555555555]
}
```

## 🛡️ Permissões Necessárias

O bot precisa ser **Admin do grupo** com:
- ✅ Apagar mensagens
- ✅ Restringir membros
- ✅ Adicionar novos admins (opcional)

## 🐛 Troubleshooting

### Bot não responde a /admin
- Verifique se você é admin (ADMIN_ID no .env)
- Envie /admin **no privado do bot**, não no grupo

### Mensagens periódicas não são enviadas
- Verifique se a mensagem está ativada (▶️)
- Veja os logs: `python bot_admin.py` ou `docker logs valak-bot`
- Confirme que o bot está rodando

### Bot não detecta novos membros
- Bot precisa ser Admin do grupo
- Confirme que GROUP_ID está correto (número negativo)

### Erro ao salvar config.json
- Verifique permissões do diretório
- Certifique-se que o arquivo não está aberto

## 🚀 Deploy em Produção

### Railway

1. Conecte seu repositório
2. Configure variáveis de ambiente:
   - `BOT_TOKEN`
   - `GROUP_ID`
   - `WEBAPP_URL`
   - `ADMIN_ID`
3. Defina Start Command: `python bot_admin.py`
4. Deploy!

### Heroku

```bash
heroku create valak-bot
heroku config:set BOT_TOKEN=seu_token
heroku config:set GROUP_ID=-1002603662151
heroku config:set WEBAPP_URL=https://sua-app.herokuapp.com
heroku config:set ADMIN_ID=seu_id
git push heroku main
```

### VPS

```bash
# Clone e configure
git clone https://github.com/josiasparentejoia-ship-it/moderador.git
cd moderador
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano .env

# Rode com screen/tmux
screen -S valak-bot
python bot_admin.py

# Ou use systemd (veja DEPLOY.md)
```

## 📊 Logs e Monitoramento

### Ver logs em tempo real
```bash
# Rodando direto
python bot_admin.py

# Docker
docker logs -f valak-bot

# Docker Compose
docker-compose -f docker-compose.python.yml logs -f
```

### Logs importantes
- `✓ Mensagem periódica enviada` - mensagem automática enviada
- `✓ Usuário X restrito` - novo membro detectado
- `✓ Mensagem de boas-vindas enviada` - boas-vindas ok
- `✗ Erro` - indica problema

## 💡 Dicas

1. **Teste localmente primeiro**: Execute `python bot_admin.py` antes de fazer deploy
2. **Backup do config.json**: Faça backup regular das configurações
3. **Teste mensagens periódicas**: Use intervalos curtos (1-2 min) para testar
4. **Use /cancelar**: Se errar alguma operação
5. **Visualize antes**: Sempre use "👁️ Visualizar" para ver como ficará

## 🔐 Segurança

- **Nunca commite o .env** (já está no .gitignore)
- **Mantenha o BOT_TOKEN seguro**
- **Não compartilhe config.json** com tokens/IDs sensíveis
- **Use HTTPS** para WEBAPP_URL em produção

## 📝 Comandos do Bot

### Comandos Admin (privado do bot)
- `/admin` - Abre o painel administrativo
- `/cancelar` - Cancela operação atual

### Comandos do Usuário
- `/start` - Inicia interação com o bot (se implementado)

## 🆘 Suporte

Problemas ou dúvidas:
1. Veja os logs do bot
2. Confira este README
3. Abra uma issue: https://github.com/josiasparentejoia-ship-it/moderador/issues

## 📄 Licença

ISC

---

**Desenvolvido com ❤️ usando Python e aiogram**

🐍 Python 3.11+ | 🤖 aiogram 3.x | 🐳 Docker | ⚡ FastAPI
