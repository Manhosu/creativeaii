# ⚡ Setup Rápido - Railway Deploy - ATUALIZADO

## 🔥 **4 Variáveis OBRIGATÓRIAS**

Configure essas 4 variáveis no Railway Dashboard:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WP_SITE_URL=https://blog.creativecopias.com.br  
WP_PASSWORD=sua_app_password_wordpress
SITE_BASE_URL=https://www.creativecopias.com.br
```

**✅ PRONTO PARA DEPLOY!** Sistema otimizado para Railway.

## 🚀 **Como Configurar**

### **Railway Dashboard**
1. Acesse: https://railway.app/dashboard
2. Selecione seu projeto
3. Clique em **"Variables"**
4. Adicione as 4 variáveis acima

### **Railway CLI** (alternativo)
```bash
# Instalar e fazer login
npm install -g @railway/cli
railway login

# Configurar variáveis
railway variables set OPENAI_API_KEY=sk-proj-xxxxxxxx...
railway variables set WP_SITE_URL=https://blog.creativecopias.com.br
railway variables set WP_PASSWORD=sua_app_password
railway variables set SITE_BASE_URL=https://www.creativecopias.com.br
```

## 🎯 **Como Obter as Credenciais**

### **OPENAI_API_KEY**
1. Acesse: https://platform.openai.com/api-keys
2. Clique **"Create new secret key"**
3. Copie a chave `sk-proj-xxxxxxxx...`

### **WP_PASSWORD**  
1. WordPress Admin → **Usuários** → **Perfil**
2. Role até **"Senhas de Aplicativo"**
3. Nome: `Creative API`
4. Clique **"Adicionar Nova"**
5. Copie a senha gerada

## ✅ **Verificação**

Após deploy, acesse: `https://seu-app.railway.app/health`

Deve retornar:
```json
{"status": "healthy", "timestamp": "2025-01-11T..."}
```

## 🔧 **Melhorias Implementadas**

### **✅ Correções para Railway:**
- **Porta Dinâmica**: Sistema usa `PORT` do Railway automaticamente
- **Python 3.11.9**: Versão estável recomendada
- **Dependências Otimizadas**: Incluindo `uvicorn[standard]` e security packages
- **Logging Melhorado**: Logs estruturados para Railway
- **Tratamento de Erros**: Debug e recovery melhorados
- **Diretórios Automáticos**: Sistema cria `logs/`, `data/`, `static/` automaticamente

### **🛡️ Variáveis de Segurança:**
```bash
DEBUG=false                  # Sempre false em produção
LOG_LEVEL=info              # Nível de log otimizado
```

## 🔧 **Variáveis Opcionais** (configuração avançada)

```bash
# Sistema
DEBUG=false                  # Modo debug (só development)
LOG_LEVEL=info              # Nível de log

# OpenAI
OPENAI_MODEL=gpt-4o-mini    # Modelo da IA
OPENAI_TEMPERATURE=0.7      # Criatividade (0-1)
OPENAI_MAX_TOKENS=2000      # Máximo de tokens

# WordPress
WP_USERNAME=api_seo_bot     # Usuário WP (padrão já configurado)
WP_AUTO_PUBLISH=true        # Publicar automaticamente
WP_DEFAULT_STATUS=publish   # Status padrão dos posts

# Conteúdo
CONTENT_MIN_WORDS=300       # Mínimo de palavras
CONTENT_MAX_WORDS=1000      # Máximo de palavras
```

## 🚨 **Troubleshooting**

### **Erro: OpenAI API Key**
- Verifique se a chave começa com `sk-proj-` ou `sk-`
- Confirme que tem créditos na conta OpenAI

### **Erro: WordPress Auth**
- Use **App Password**, não senha normal
- Verifique se o usuário tem permissões de editor/admin

### **App não carrega**
- Verifique logs no Railway: Dashboard → Deploy → View Logs
- Confirme que todas as 4 variáveis obrigatórias estão configuradas
- Teste conexão WordPress: `/debug/wordpress-auth`

### **Comandos de Debug Railway:**
```bash
# Ver logs em tempo real
railway logs

# Conectar ao terminal do app
railway shell

# Ver variáveis configuradas
railway variables
```

## 🎯 **Deploy Checklist**

- [ ] ✅ OPENAI_API_KEY configurada
- [ ] ✅ WP_SITE_URL configurada  
- [ ] ✅ WP_PASSWORD configurada (App Password!)
- [ ] ✅ SITE_BASE_URL configurada
- [ ] ✅ Python 3.11.9 no runtime.txt
- [ ] ✅ Requirements.txt otimizado
- [ ] ✅ main.py com tratamento de erros
- [ ] ✅ /health endpoint funcionando

**✅ Status**: Sistema TOTALMENTE pronto para produção no Railway! 🚀 