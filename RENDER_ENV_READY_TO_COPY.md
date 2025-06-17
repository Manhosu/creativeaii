# 🔑 VARIÁVEIS PRONTAS PARA COPIAR - RENDER.COM

## 📋 **COPIE E COLE ESTAS VARIÁVEIS NO RENDER**

### **🚨 SUBSTITUA OS VALORES PELOS SEUS TOKENS REAIS**

---

## ✅ **OBRIGATÓRIAS (Copie uma por vez no Render)**

### **1. OpenAI API Key**
```
Key: OPENAI_API_KEY
Value: COLE_SUA_CHAVE_OPENAI_AQUI
```
**📝 Como obter:** https://platform.openai.com/api-keys → "Create new secret key"

### **2. WordPress Site URL**
```
Key: WP_SITE_URL
Value: https://blog.creativecopias.com.br
```

### **3. WordPress App Password**
```
Key: WP_PASSWORD
Value: COLE_SUA_APP_PASSWORD_WORDPRESS_AQUI
```
**📝 Como obter:** WP Admin → Usuários → Perfil → Senhas de Aplicativo → Adicionar Nova

### **4. Site Base URL**
```
Key: SITE_BASE_URL
Value: https://www.creativecopias.com.br
```

---

## ⚙️ **RECOMENDADAS (Copie e cole direto)**

### **5. Debug Mode**
```
Key: DEBUG
Value: false
```

### **6. WordPress Username**
```
Key: WP_USERNAME
Value: api_seo_bot
```

### **7. WordPress Auto Publish**
```
Key: WP_AUTO_PUBLISH
Value: true
```

### **8. WordPress Default Status**
```
Key: WP_DEFAULT_STATUS
Value: publish
```

### **9. OpenAI Model**
```
Key: OPENAI_MODEL
Value: gpt-4o-mini
```

### **10. OpenAI Temperature**
```
Key: OPENAI_TEMPERATURE
Value: 0.7
```

### **11. OpenAI Max Tokens**
```
Key: OPENAI_MAX_TOKENS
Value: 2000
```

### **12. Content Min Words**
```
Key: CONTENT_MIN_WORDS
Value: 300
```

### **13. Content Max Words**
```
Key: CONTENT_MAX_WORDS
Value: 1000
```

### **14. Scheduler Enabled**
```
Key: SCHEDULER_ENABLED
Value: true
```

---

## 🔑 **TOKENS QUE VOCÊ PRECISA OBTER**

### **🤖 OPENAI API KEY**
1. Acesse: https://platform.openai.com/api-keys
2. Clique "Create new secret key"
3. Nome: "Creative API - Render"
4. Copie a chave que começa com `sk-proj-...`
5. Cole em `OPENAI_API_KEY` no Render

**Formato esperado:**
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### **📝 WORDPRESS APP PASSWORD**
1. Acesse: https://blog.creativecopias.com.br/wp-admin
2. Vá em **Usuários** → **Perfil**
3. Role até **"Senhas de Aplicativo"**
4. Nome: "Creative API Render"
5. Clique **"Adicionar Nova"**
6. Copie a senha gerada (formato: `xxxx xxxx xxxx xxxx`)
7. Cole em `WP_PASSWORD` no Render

**Formato esperado:**
```
abcd efgh ijkl mnop
```

---

## 📋 **PROCESSO NO RENDER**

### **Passo a Passo:**

1. **Render Dashboard** → Seu Service → **Environment**
2. **Add Environment Variable**
3. **Copie cada variável acima** (Key e Value)
4. **Clique Save** após cada uma

### **Ordem recomendada:**
1. ✅ `OPENAI_API_KEY` (obtenha primeiro)
2. ✅ `WP_PASSWORD` (obtenha segundo)  
3. ✅ `WP_SITE_URL`
4. ✅ `SITE_BASE_URL`
5. ✅ Todas as outras (opcionais)

---

## 🔒 **TEMPLATE PARA SUAS CREDENCIAIS**

```bash
# SUAS CREDENCIAIS (complete e guarde em local seguro)
OPENAI_API_KEY=sk-proj-[COLE_AQUI]
WP_PASSWORD=[COLE_APP_PASSWORD_AQUI]

# CONFIGURAÇÕES FIXAS (pode copiar direto)
WP_SITE_URL=https://blog.creativecopias.com.br
SITE_BASE_URL=https://www.creativecopias.com.br
WP_USERNAME=api_seo_bot
DEBUG=false
WP_AUTO_PUBLISH=true
SCHEDULER_ENABLED=true
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
CONTENT_MIN_WORDS=300
CONTENT_MAX_WORDS=1000
```

---

## ✅ **CHECKLIST FINAL**

- [ ] Obtive OPENAI_API_KEY da OpenAI
- [ ] Obtive WP_PASSWORD do WordPress  
- [ ] Configurei todas as 4 obrigatórias no Render
- [ ] Configurei as recomendadas no Render
- [ ] Testei Health Check após deploy
- [ ] Testei WordPress auth

**🎉 Sistema pronto para produção!** 