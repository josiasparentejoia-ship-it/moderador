require('dotenv').config();
const { Telegraf } = require('telegraf');
const express = require('express');

// Configurações
const BOT_TOKEN = process.env.BOT_TOKEN;
const GROUP_ID = parseInt(process.env.GROUP_ID);
const WEBAPP_URL = process.env.WEBAPP_URL;
const PORT = process.env.PORT || 3000;

// Inicializa bot e servidor
const bot = new Telegraf(BOT_TOKEN);
const app = express();
const path = require('path');

// Middlewares
app.use(express.json());
app.use(express.static(__dirname)); // Serve arquivos estáticos (index.html, etc)

// Armazena o ID da última mensagem de boas-vindas
let lastWelcomeMessageId = null;

// Função para restringir usuário (apenas leitura)
async function restrictUser(ctx, userId) {
  try {
    await ctx.telegram.restrictChatMember(GROUP_ID, userId, {
      permissions: {
        can_send_messages: false,
        can_send_media_messages: false,
        can_send_polls: false,
        can_send_other_messages: false,
        can_add_web_page_previews: false,
        can_change_info: false,
        can_invite_users: false,
        can_pin_messages: false
      }
    });
    console.log(`✓ Usuário ${userId} restrito`);
  } catch (error) {
    console.error(`✗ Erro ao restringir usuário ${userId}:`, error.message);
  }
}

// Função para liberar usuário (permissões completas)
async function unlockUser(userId) {
  try {
    await bot.telegram.restrictChatMember(GROUP_ID, userId, {
      permissions: {
        can_send_messages: true,
        can_send_media_messages: true,
        can_send_polls: true,
        can_send_other_messages: true,
        can_add_web_page_previews: true,
        can_change_info: false,
        can_invite_users: true,
        can_pin_messages: false
      }
    });
    console.log(`✓ Usuário ${userId} liberado`);
    return true;
  } catch (error) {
    console.error(`✗ Erro ao liberar usuário ${userId}:`, error.message);
    return false;
  }
}

// Monitora novos membros
bot.on('chat_member', async (ctx) => {
  const update = ctx.update.chat_member;
  const oldStatus = update.old_chat_member?.status;
  const newStatus = update.new_chat_member?.status;
  const user = update.new_chat_member.user;
  
  // Verifica se é um novo membro entrando
  if ((oldStatus === 'left' || oldStatus === 'kicked') && 
      (newStatus === 'member' || newStatus === 'administrator')) {
    
    console.log(`\n📥 Novo membro: ${user.first_name} (${user.id})`);
    
    // Apaga a mensagem de boas-vindas anterior (se existir)
    if (lastWelcomeMessageId) {
      try {
        await ctx.telegram.deleteMessage(GROUP_ID, lastWelcomeMessageId);
        console.log('✓ Mensagem anterior apagada');
      } catch (error) {
        console.log('⚠️ Não foi possível apagar mensagem anterior');
      }
    }
    
    // Restringe o novo usuário
    await restrictUser(ctx, user.id);
    
    // Envia nova mensagem de boas-vindas
    const welcomeText = `🎉 Bem-vindo(a), ${user.first_name}!\n\n` +
      `Para liberar o chat e poder enviar mensagens, você precisa ler e concordar com as regras, diretrizes e termos de uso do grupo.\n\n` +
      `👇 Clique no botão abaixo para continuar:`;
    
    try {
      const message = await ctx.telegram.sendMessage(GROUP_ID, welcomeText, {
        reply_markup: {
          inline_keyboard: [[
            {
              text: '📋 ACEITE OS TERMOS DO GRUPO',
              url: WEBAPP_URL
            }
          ]]
        }
      });
      
      lastWelcomeMessageId = message.message_id;
      console.log('✓ Mensagem de boas-vindas enviada');
    } catch (error) {
      console.error('✗ Erro ao enviar boas-vindas:', error.message);
    }
  }
});

// Endpoint API - Libera usuário após concordar
app.post('/api/agree', async (req, res) => {
  try {
    const { initData } = req.body;
    
    if (!initData) {
      return res.status(400).json({ error: 'initData não fornecido' });
    }
    
    // Valida e extrai dados do Telegram
    // Nota: em produção, você deve validar o hash do initData
    const params = new URLSearchParams(initData);
    const userJson = params.get('user');
    
    if (!userJson) {
      return res.status(400).json({ error: 'Dados do usuário não encontrados' });
    }
    
    const user = JSON.parse(userJson);
    const userId = user.id;
    
    console.log(`\n✅ Usuário ${user.first_name} (${userId}) concordou com os termos`);
    
    // Libera o usuário
    const success = await unlockUser(userId);
    
    if (success) {
      // Envia mensagem de confirmação privada (opcional)
      try {
        await bot.telegram.sendMessage(
          userId,
          '✅ Chat liberado! Você já pode enviar mensagens no grupo.'
        );
      } catch (error) {
        console.log('⚠️ Não foi possível enviar mensagem privada');
      }
      
      res.json({ 
        success: true, 
        message: 'Chat liberado com sucesso!' 
      });
    } else {
      res.status(500).json({ 
        error: 'Não foi possível liberar o chat' 
      });
    }
    
  } catch (error) {
    console.error('✗ Erro ao processar concordância:', error);
    res.status(500).json({ 
      error: 'Erro interno do servidor' 
    });
  }
});

// Rota principal - serve o webapp
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Rota de status
app.get('/status', (req, res) => {
  res.json({
    status: 'Bot rodando',
    group_id: GROUP_ID
  });
});

// Inicia servidor Express
app.listen(PORT, () => {
  console.log(`🌐 Servidor rodando na porta ${PORT}`);
});

// Inicia bot
bot.launch({
  allowedUpdates: ['chat_member', 'message']
}).then(() => {
  console.log('🤖 Bot iniciado com sucesso!');
  console.log(`📱 Monitorando grupo: ${GROUP_ID}`);
}).catch((error) => {
  console.error('✗ Erro ao iniciar bot:', error);
});

// Graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
