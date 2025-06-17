# ⚡ DEPLOY RÁPIDO - RENDER.COM

## 🎯 **EM 5 PASSOS - 15 MINUTOS**

### **📋 PASSO 1: CONTA E REPOSITÓRIO**
1. **Criar conta**: https://render.com → "Get Started for Free"
2. **Conectar GitHub**: Autorize acesso ao repositório
3. **Selecionar repo**: `creative-api`

---

### **🚀 PASSO 2: CRIAR WEB SERVICE**
1. **Render Dashboard** → "New +" → "Web Service"
2. **Configurações**:
   ```
   Name: creative-api-seo
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   Health Check Path: /health
   ```

---

### **🔑 PASSO 3: VARIÁVEIS OBRIGATÓRIAS**
No Render → **Environment** → **Add Environment Variable**:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br
```

**⚠️ IMPORTANTE**: 
- `WP_PASSWORD` = **App Password** do WordPress (não senha normal)
- `OPENAI_API_KEY` = Chave da OpenAI com créditos

---

### **🚀 PASSO 4: DEPLOY**
1. **Clique**: "Create Web Service"
2. **Aguarde**: 3-5 minutos para build
3. **URL gerada**: `https://creative-api-seo.onrender.com`

---

### **✅ PASSO 5: TESTAR**
1. **Health Check**: `https://seu-app.onrender.com/health`
   ```json
   {"status": "healthy"}
   ```

2. **Dashboard**: `https://seu-app.onrender.com`
   - Deve mostrar interface completa

3. **WordPress**: `https://seu-app.onrender.com/debug/wordpress-auth`
   ```json
   {"success": true}
   ```

---

## 🆘 **PROBLEMAS COMUNS**

| Erro | Solução |
|------|---------|
| ❌ Build failed | Confirme `requirements.txt` e `runtime.txt` |
| ❌ Health check failed | Aguarde 2-3 minutos para inicialização |
| ❌ WordPress auth failed | Use **App Password**, não senha normal |
| ❌ OpenAI failed | Verifique chave e créditos disponíveis |

---

## 📞 **OBTER CREDENCIAIS**

### **OpenAI API Key**
1. https://platform.openai.com/api-keys
2. "Create new secret key" → Nome: "Creative API"
3. Copie `sk-proj-xxxxxxxx...`

### **WordPress App Password**
1. https://blog.creativecopias.com.br/wp-admin
2. **Usuários** → **Perfil** → **Senhas de Aplicativo**
3. Nome: "Creative API" → **Adicionar Nova**
4. Copie senha no formato: `xxxx xxxx xxxx xxxx`

---

## 🎉 **PRONTO!**

Seu sistema estará rodando em:
- **🌐 URL**: `https://seu-app.onrender.com`
- **🩺 Health**: `https://seu-app.onrender.com/health`
- **📊 Dashboard**: `https://seu-app.onrender.com`

**Sistema gerando conteúdo SEO automaticamente! 🚀** 