# 🚀 GUIA RÁPIDO - Bot Moderador Python

## ⚡ Início Rápido (5 minutos)

### 1. Obtenha as Informações Necessárias

#### a) Token do Bot
1. Abra o Telegram
2. Procure por `@BotFather`
3. Envie `/newbot`
4. Siga as instruções
5. **Copie o token** (ex: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### b) ID do Grupo
1. Adicione `@userinfobot` ao seu grupo
2. O bot enviará o ID do grupo (ex: `-1002603662151`)
3. **Copie esse número** (sempre negativo)

#### c) Seu ID (Admin)
1. Envie qualquer mensagem para `@userinfobot`
2. O bot responderá com seu ID (ex: `123456789`)
3. **Copie esse número**

### 2. Configure o .env

```bash
# Copie o exemplo
cp .env.example .env

# Edite o arquivo
nano .env  # ou use seu editor favorito
```

Cole seus dados:
```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
GROUP_ID=-1002603662151
WEBAPP_URL=https://seu-dominio.com
ADMIN_ID=123456789
```

### 3. Adicione o Bot ao Grupo

1. No Telegram, procure seu bot
2. Adicione ele ao grupo
3. Promova para **Admin** com permissões:
   - ✅ Apagar mensagens
   - ✅ Restringir membros

### 4. Execute o Bot

#### Opção A: Python Direto
```bash
# Instale dependências
pip install -r requirements.txt

# Execute
python bot_admin.py
```

#### Opção B: Docker
```bash
# Build e run
docker-compose -f docker-compose.python.yml up -d

# Ver logs
docker-compose -f docker-compose.python.yml logs -f
```

### 5. Acesse o Dashboard

1. No Telegram, envie mensagem **privada** para o bot
2. Digite `/admin`
3. Use os botões para gerenciar! 🎉

---

## 📱 Primeiro Uso

### Criar sua primeira mensagem periódica

1. `/admin` → 📨 Mensagens Periódicas → ➕ Nova Mensagem
2. Envie: `📢 Lembre-se de seguir as regras!`
3. Digite intervalo: `60` (1 hora)
4. Clique em "Pular" (sem mídia por enquanto)
5. Pronto! ✅

### Personalizar boas-vindas

1. `/admin` → 👋 Configurar Boas-Vindas
2. ✏️ Editar Texto
3. Envie:
```
🎉 Bem-vindo(a), {name}!

Seja bem-vindo ao nosso grupo!

Para liberar o chat, aceite os termos abaixo:
```
4. Pronto! Teste adicionando alguém ao grupo

### Enviar mensagem no grupo

1. `/admin` → 📤 Enviar no Grupo
2. Envie o texto ou foto/vídeo
3. A mensagem aparecerá no grupo instantaneamente!

---

## 🎯 Casos de Uso

### Mensagem de Regras a cada 3 horas
- Texto: `📜 Regras do grupo: bit.ly/regras`
- Intervalo: `180` minutos

### Lembrete diário
- Texto: `🌅 Bom dia! Seja respeitoso hoje!`
- Intervalo: `1440` minutos (24h)

### Avisos importantes
Use "📤 Enviar no Grupo" para avisos imediatos

---

## ❓ FAQ Rápido

**P: Bot não responde a /admin**
R: Certifique-se de enviar no **privado do bot**, não no grupo

**P: Como adicionar mais admins?**
R: Edite `config.json` e adicione mais IDs na lista `admin_ids`

**P: Posso usar foto na mensagem periódica?**
R: Sim! Ao criar, envie a foto quando pedido

**P: Como pausar uma mensagem periódica?**
R: `/admin` → Mensagens Periódicas → Listar → ⏸️ Pausar

**P: Como testar se está funcionando?**
R: Crie mensagem periódica com intervalo de `1` minuto para teste

---

## 🆘 Problemas Comuns

### Erro: "Bot não é admin"
**Solução:** Promova o bot a Admin no grupo

### Erro: "initData inválido"
**Solução:** Verifique se WEBAPP_URL está correto e acessível

### Bot não detecta novos membros
**Solução:** Confirme que GROUP_ID está correto (número negativo)

### Mensagens periódicas não enviam
**Solução:** 
1. Veja se estão ativadas (▶️)
2. Verifique os logs: `python bot_admin.py`
3. Confirme que o bot está rodando

---

## 📚 Próximos Passos

1. Leia [README_PYTHON.md](README_PYTHON.md) para detalhes completos
2. Veja [DEPLOY.md](DEPLOY.md) para deploy em produção
3. Configure backup do `config.json`
4. Personalize suas mensagens

---

## 💬 Comandos Úteis

```bash
# Ver logs
python bot_admin.py

# Parar bot
Ctrl+C

# Docker logs
docker-compose -f docker-compose.python.yml logs -f

# Reiniciar Docker
docker-compose -f docker-compose.python.yml restart

# Backup config
cp config.json config.backup.json
```

---

**Pronto! Seu bot está funcionando! 🎉**

Use `/admin` no privado do bot para gerenciar tudo via interface amigável!
