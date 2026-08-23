FROM node:18-alpine

# Diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências
COPY package*.json ./

# Instala dependências
RUN npm ci --only=production

# Copia código da aplicação
COPY . .

# Expõe a porta
EXPOSE 8000

# Comando para iniciar
CMD ["node", "bot.js"]
