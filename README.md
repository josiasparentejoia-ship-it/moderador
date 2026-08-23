# Bot Moderador Valak Search

Bot do Telegram que gerencia novos membros do grupo, requer aceitação de termos antes de liberar o chat.

## 🚀 Funcionalidades

- ✅ Detecta quando um novo membro entra no grupo
- 🔒 Restringe o chat automaticamente para novos membros
- 📨 Envia mensagem de boas-vindas com botão WebApp
- 🗑️ Apaga a mensagem anterior quando um novo membro entra
- ✔️ Libera o chat após o usuário concordar com os termos
- 🌐 API REST para integração com o WebApp

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
   ```

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

1. **Novo membro entra** → Bot detecta via `chat_member` update
2. **Bot restringe o usuário** → Apenas leitura no grupo
3. **Bot apaga mensagem anterior** → Mantém apenas uma mensagem de boas-vindas
4. **Bot envia nova mensagem** → Com botão "ACEITE OS TERMOS DO GRUPO"
5. **Usuário clica no botão** → Abre o WebApp
6. **Usuário lê e concorda** → WebApp chama `/api/agree`
7. **Bot libera o chat** → Usuário pode enviar mensagens

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
