require('dotenv').config();
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.WEBAPP_PORT || 8080;

// Servir arquivos estáticos
app.use(express.static(__dirname));

// Rota principal - serve o index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Inicia servidor
app.listen(PORT, () => {
  console.log(`🌐 WebApp rodando em http://localhost:${PORT}`);
  console.log(`📄 Acesse: http://localhost:${PORT}`);
});
