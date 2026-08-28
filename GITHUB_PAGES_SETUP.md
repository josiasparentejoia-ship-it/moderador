# 📄 Configurar GitHub Pages

## 1️⃣ Ativar GitHub Pages no Repositório

1. Vá para o seu repositório no GitHub:
   ```
   https://github.com/josiasparentejoia-ship-it/moderador
   ```

2. Clique em **Settings** (Configurações)

3. No menu lateral, clique em **Pages**

4. Em **Source**, selecione:
   - **Source:** GitHub Actions

5. Clique em **Save**

## 2️⃣ Fazer Push do Workflow

```bash
git add .github/workflows/deploy-pages.yml
git commit -m "Add GitHub Pages deployment workflow"
git push origin main
```

## 3️⃣ Aguardar Deploy

- Vá em **Actions** no GitHub
- Aguarde o workflow "Deploy to GitHub Pages" completar
- Quando terminar, seu site estará em:
  ```
  https://josiasparentejoia-ship-it.github.io/moderador/
  ```

## 4️⃣ Atualizar URLs no Projeto

### Opção A: Apenas index.html (Recomendado)

Se você quer hospedar apenas o WebApp (index.html) no GitHub Pages e manter o bot rodando localmente:

1. **Atualize o .env:**
   ```env
   WEBAPP_URL=https://josiasparentejoia-ship-it.github.io/moderador/
   ```

2. **Atualize o config.json:**
   ```json
   {
     "welcome_message": {
       "button": {
         "url": "https://josiasparentejoia-ship-it.github.io/moderador/"
       }
     }
   }
   ```

3. **Reinicie o bot:**
   ```bash
   # Parar bot atual
   Get-Process python | Where-Object {$_.Path -like "*python*"} | Stop-Process -Force
   
   # Iniciar bot
   python bot_admin.py
   ```

### Opção B: Domínio Personalizado (Opcional)

Se você tiver um domínio próprio (ex: `bot.seudominio.com`):

1. Nas configurações do GitHub Pages, adicione seu domínio customizado
2. Configure DNS CNAME apontando para `josiasparentejoia-ship-it.github.io`
3. Aguarde propagação DNS (até 24h)
4. Use seu domínio no WEBAPP_URL

## 5️⃣ Testar

1. Acesse: `https://josiasparentejoia-ship-it.github.io/moderador/`
2. Verifique se o site carrega
3. Adicione novo membro ao grupo
4. Clique no botão de boas-vindas
5. Deve abrir o WebApp!

## 📝 Arquivos que Serão Publicados

GitHub Pages publicará automaticamente:
- `index.html` (WebApp principal)
- Todos os arquivos estáticos (imagens, vídeos, etc.)

**NÃO serão publicados** (devido ao .gitignore):
- `node_modules/`
- `.env`
- Arquivos Python (bot_admin.py, etc.)
- config.json

## 🔒 Segurança

✅ **Seguro para publicar:**
- index.html
- Imagens (PNG, JPG)
- Vídeos (MP4)

❌ **NUNCA publique:**
- .env (com BOT_TOKEN)
- config.json (com ADMIN_ID)
- Códigos do bot (*.py, *.js)

---

## ⚠️ Importante

Após ativar GitHub Pages, **sempre que você fizer mudanças no index.html**:

1. Commit e push para o GitHub
2. O workflow rodará automaticamente
3. Site será atualizado em ~1-2 minutos

---

**URL Final:** `https://josiasparentejoia-ship-it.github.io/moderador/`
