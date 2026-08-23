require('dotenv').config();
const { Telegraf } = require('telegraf');

const BOT_TOKEN = process.env.BOT_TOKEN;
const GROUP_ID = parseInt(process.env.GROUP_ID);
const WEBAPP_URL = process.env.WEBAPP_URL;

const bot = new Telegraf(BOT_TOKEN);

async function sendTestWelcome() {
  console.log('📤 Enviando mensagem de boas-vindas de teste...\n');
  
  const welcomeText = `🎉 Bem-vindo(a), Usuário Teste!\n\n` +
    `Para liberar o chat e poder enviar mensagens, você precisa ler e concordar com as regras, diretrizes e termos de uso do grupo.\n\n` +
    `👇 Clique no botão abaixo para continuar:`;
  
  try {
    const message = await bot.telegram.sendMessage(GROUP_ID, welcomeText, {
      reply_markup: {
        inline_keyboard: [[
          {
            text: '📋 ACEITE OS TERMOS DO GRUPO',
            url: WEBAPP_URL
          }
        ]]
      }
    });
    
    console.log('✅ Mensagem enviada com sucesso!');
    console.log(`📌 ID da mensagem: ${message.message_id}`);
    console.log(`💬 Texto: "${welcomeText.substring(0, 50)}..."`);
    console.log(`🔗 WebApp URL: ${WEBAPP_URL}\n`);
    
    process.exit(0);
  } catch (error) {
    console.error('❌ Erro ao enviar mensagem:', error.message);
    process.exit(1);
  }
}

sendTestWelcome();
