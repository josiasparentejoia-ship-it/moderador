# Bot Moderador Valak Search

Bot do Telegram que gerencia novos membros do grupo, requer aceitação de termos antes de liberar o chat.

## 🚀 Funcionalidades

- ✅ Detecta quando um novo membro entra no grupo
- 🔒 Restringe o chat automaticamente para novos membros
- 📨 Envia mensagem de boas-vindas com botão WebApp
- 🗑️ Apaga a mensagem anterior quando um novo membro entra
- ✔️ Libera o chat após o usuário concordar com os termos
- 🌐 API REST para integração com o WebApp
- ⏰ **Mensagens periódicas automáticas** no grupo (agendadas via cron)

## 📋 Pré-requisitos

- Node.js 16+ instalado
- Bot do Telegram criado (via @BotFather)
- Bot com permissões de Admin no grupo
- WebApp hospedado (index.html)

## ⚙️ Configuração

1. **Instale as dependências:**
   ```bash
   npm install
   ```

2. **Configure o arquivo `.env`:**
   ```env
   BOT_TOKEN=seu_token_aqui
   GROUP_ID=-1002603662151
   WEBAPP_URL=https://seu-dominio.com
   PORT=3000

   # Mensagens periódicas (formato cron)
   CRON_SCHEDULE=0 */3 * * *
   PERIODIC_MESSAGES=📢 Mensagem 1|||🎯 Mensagem 2|||⭐ Mensagem 3
   ```

   **Formato CRON_SCHEDULE:**
   - `*/30 * * * *` = a cada 30 minutos
   - `0 */2 * * *` = a cada 2 horas
   - `0 9,15,21 * * *` = às 9h, 15h e 21h
   - `0 */3 * * *` = a cada 3 horas (padrão)

   **PERIODIC_MESSAGES:**
   - Separe múltiplas mensagens com `|||`
   - As mensagens serão enviadas em rodízio
   - Use emojis e HTML para formatação

3. **Importante - Permissões do Bot:**
   - O bot precisa ser Admin do grupo
   - Permissões necessárias:
     - ✅ Restringir membros
     - ✅ Apagar mensagens
     - ✅ Adicionar novos admins (opcional)

## 🏃 Como Executar

**Desenvolvimento:**
```bash
npm run dev
```

**Produção:**
```bash
npm start
```

**Com Docker Compose:**
```bash
# Inicia o container em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar o container
docker-compose down

# Reconstruir após mudanças
docker-compose up -d --build
```

## 🌐 Endpoints da API

### `POST /api/agree`
Libera o chat para o usuário após concordar com os termos.

**Body:**
```json
{
  "initData": "dados_do_telegram_webapp"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Chat liberado com sucesso!"
}
```

### `GET /`
Health check do servidor.

## 📱 Fluxo de Funcionamento

### Boas-vindas a Novos Membros

1. **Novo membro entra** → Bot detecta via `chat_member` update
2. **Bot restringe o usuário** → Apenas leitura no grupo
3. **Bot apaga mensagem anterior** → Mantém apenas uma mensagem de boas-vindas
4. **Bot envia nova mensagem** → Com botão "ACEITE OS TERMOS DO GRUPO"
5. **Usuário clica no botão** → Abre o WebApp
6. **Usuário lê e concorda** → WebApp chama `/api/agree`
7. **Bot libera o chat** → Usuário pode enviar mensagens

### Mensagens Periódicas

1. **Bot inicia** → Agenda mensagens conforme `CRON_SCHEDULE`
2. **No horário agendado** → Envia uma mensagem do rodízio
3. **Rotação automática** → Próxima mensagem será diferente
4. **Ciclo contínuo** → Mensagens se repetem em ordem

## 🔐 Segurança

⚠️ **IMPORTANTE:** 
- Em produção, valide o hash do `initData` do Telegram
- Use HTTPS para o WebApp
- Mantenha o `BOT_TOKEN` seguro (nunca commite no git)
- Considere implementar rate limiting na API

## 📝 Estrutura de Arquivos

```
moderador/
├── bot.js              # Código principal do bot
├── index.html          # WebApp de termos
├── package.json        # Dependências
├── .env               # Configurações (não commitar)
├── .gitignore         # Arquivos ignorados
└── README.md          # Este arquivo
```

## 🐛 Troubleshooting

**Bot não responde a novos membros:**
- Verifique se o bot é Admin do grupo
- Confirme que `allowedUpdates` inclui `'chat_member'`
- Veja os logs do console para erros

**Usuário não é liberado:**
- Verifique se o `GROUP_ID` está correto (número negativo)
- Confirme que o bot tem permissão de "Restringir membros"
- Veja os logs da API

**WebApp não abre:**
- Confirme que `WEBAPP_URL` está correto e acessível
- Verifique se o domínio usa HTTPS
- Teste o WebApp diretamente no navegador

## 📄 Licença

ISC
