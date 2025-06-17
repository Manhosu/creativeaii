# 🔧 VARIÁVEIS DE AMBIENTE - RENDER.COM

## 🔑 **OBRIGATÓRIAS (4 variáveis)**

### **No Render Dashboard → Environment**

```bash
# 1. OpenAI API Key (OBRIGATÓRIA)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 2. WordPress Site URL (OBRIGATÓRIA)
WP_SITE_URL=https://blog.creativecopias.com.br

# 3. WordPress App Password (OBRIGATÓRIA)
WP_PASSWORD=xxxx xxxx xxxx xxxx

# 4. Site Base URL (OBRIGATÓRIA)
SITE_BASE_URL=https://www.creativecopias.com.br
```

---

## ⚙️ **RECOMENDADAS (Configurações de Produção)**

```bash
# Sistema
DEBUG=false
LOG_LEVEL=info
ENVIRONMENT=production

# WordPress
WP_USERNAME=api_seo_bot
WP_AUTO_PUBLISH=true
WP_DEFAULT_STATUS=publish

# OpenAI
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Conteúdo
CONTENT_MIN_WORDS=300
CONTENT_MAX_WORDS=1000

# Sistema de Agendamento
SCHEDULER_ENABLED=true
```

---

## 🚫 **NÃO CONFIGURAR NO RENDER**

```bash
# ❌ NÃO definir - Render configura automaticamente
PORT
HOST

# ❌ NÃO definir - Configuração específica Railway/Heroku
RAILWAY_ENVIRONMENT
DYNO
VERCEL
```

---

## 📋 **COMO CONFIGURAR NO RENDER**

### **Passo a Passo:**

1. **Render Dashboard** → Seu Service → **Environment**
2. **Add Environment Variable**
3. **Copie e cole** cada variável:

```
Key: OPENAI_API_KEY
Value: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

```
Key: WP_SITE_URL  
Value: https://blog.creativecopias.com.br
```

```
Key: WP_PASSWORD
Value: xxxx xxxx xxxx xxxx
```

```
Key: SITE_BASE_URL
Value: https://www.creativecopias.com.br
```

**⚠️ IMPORTANTE:** 
- `WP_PASSWORD` = **App Password** do WordPress
- Não inclua espaços extras ou quebras de linha

---

## 🔍 **VALIDAÇÃO**

### **Testar após deploy:**

1. **Health Check**: `https://seu-app.onrender.com/health`
   ```json
   {"status": "healthy"}
   ```

2. **Config Status**: `https://seu-app.onrender.com/debug/config`
   ```json
   {
     "openai_configured": true,
     "wordpress_configured": true
   }
   ```

3. **WordPress Auth**: `https://seu-app.onrender.com/debug/wordpress-auth`
   ```json
   {"success": true}
   ```

---

## 🆘 **TROUBLESHOOTING**

| Erro | Variável | Solução |
|------|----------|---------|
| ❌ OpenAI failed | `OPENAI_API_KEY` | Verifique chave válida com créditos |
| ❌ WordPress auth failed | `WP_PASSWORD` | Use App Password (não senha normal) |
| ❌ Site not found | `WP_SITE_URL` | URL sem / no final |
| ❌ Scraper failed | `SITE_BASE_URL` | URL do e-commerce correto |

---

## 🔒 **SEGURANÇA**

### **Variáveis Secretas:**
- ✅ Configurar no Render Dashboard
- ❌ NUNCA committar no código
- ❌ NUNCA colocar em arquivos públicos

### **Verificação:**
```bash
# ✅ Correto
OPENAI_API_KEY=sk-proj-xxxxx (no Render)

# ❌ Errado  
OPENAI_API_KEY=sk-proj-xxxxx (no código)
```

---

## 🎯 **CONFIGURAÇÃO MÍNIMA PARA PRODUÇÃO**

```bash
# OBRIGATÓRIAS (sistema não funciona sem estas)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br

# RECOMENDADAS (para produção estável)
DEBUG=false
WP_AUTO_PUBLISH=true
SCHEDULER_ENABLED=true
```

**Total: 7 variáveis para sistema completo em produção!** 🚀 