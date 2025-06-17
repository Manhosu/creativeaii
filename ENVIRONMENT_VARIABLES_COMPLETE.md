# 🔧 VARIÁVEIS DE AMBIENTE COMPLETAS - CREATIVE API

## 📋 **TODAS AS ENVIRONMENT VARIABLES SUPORTADAS**

### 🔑 **OBRIGATÓRIAS (4 variáveis)**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br
```

---

### ⚙️ **CONFIGURAÇÕES GERAIS**
```bash
# Sistema
DEBUG=false
LOG_LEVEL=info
PORT=3000
ENVIRONMENT=production

# Aplicação
APP_NAME=Sistema de Geração Automática de Conteúdo SEO
APP_VERSION=1.0.0
```

---

### 🤖 **OPENAI / IA**
```bash
# API e Modelo
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
OPENAI_TIMEOUT=60

# Configurações Avançadas
OPENAI_ORGANIZATION=org-xxxxxxxxxxxxxxxx
OPENAI_PROJECT=proj_xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
```

---

### 📝 **WORDPRESS**
```bash
# Conexão Principal
WP_SITE_URL=https://blog.creativecopias.com.br
WP_USERNAME=api_seo_bot
WP_PASSWORD=xxxx xxxx xxxx xxxx

# Configurações de Publicação
WP_AUTO_PUBLISH=true
WP_DEFAULT_STATUS=publish
WP_DEFAULT_AUTHOR=1
WP_DEFAULT_COMMENT_STATUS=open
WP_DEFAULT_PING_STATUS=open

# Categorias e Tags
WP_DEFAULT_CATEGORY=1
WP_AUTO_TAGS=true
WP_MAX_TAGS=10

# Timeouts e Retry
WP_TIMEOUT=30
WP_MAX_RETRIES=3
WP_RETRY_DELAY=5
```

---

### 🕷️ **SCRAPER**
```bash
# Site Principal
SITE_BASE_URL=https://www.creativecopias.com.br

# Configurações de Scraping
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
SCRAPER_TIMEOUT=30
SCRAPER_MAX_RETRIES=3
SCRAPER_DELAY=1
SCRAPER_MAX_PAGES=10

# Headers e Proxies
SCRAPER_HEADERS={"User-Agent": "...", "Accept": "..."}
SCRAPER_PROXIES=http://proxy:port
SCRAPER_VERIFY_SSL=true

# Rate Limiting
SCRAPER_RATE_LIMIT=10
SCRAPER_RATE_WINDOW=60
```

---

### 📖 **GERAÇÃO DE CONTEÚDO**
```bash
# Tamanhos de Conteúdo
CONTENT_MIN_WORDS=300
CONTENT_MAX_WORDS=1000
CONTENT_TARGET_WORDS=600

# SEO
SEO_TITLE_MAX_LENGTH=60
SEO_DESCRIPTION_MAX_LENGTH=160
SEO_KEYWORDS_MAX=10

# Templates
TEMPLATE_VARIATION_COUNT=3
TEMPLATE_USE_ADVANCED=true

# Qualidade
CONTENT_MIN_READABILITY_SCORE=60
CONTENT_REQUIRE_IMAGES=true
CONTENT_AUTO_OPTIMIZE=true
```

---

### 📊 **SCHEDULER**
```bash
# Jobs Principais
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=America/Sao_Paulo

# Cronogramas (Cron Format)
SCRAPING_SCHEDULE=0 10 * * 0
GENERATION_SCHEDULE=15 10 * * 0
CLEANUP_SCHEDULE=0 2 1 * *
HEALTH_CHECK_SCHEDULE=*/15 * * * *

# Job Limits
MAX_CONCURRENT_JOBS=3
JOB_TIMEOUT=3600
JOB_MAX_RETRIES=2
```

---

### 📂 **BANCO DE DADOS**
```bash
# Arquivos SQLite
DB_PRODUCTS_PATH=src/database/products.db
DB_REVIEWS_PATH=data/review_articles.db
DB_PUBLICATIONS_PATH=src/data/publications.db
DB_CONFIG_PATH=src/data/config.db
DB_PRIORITY_PATH=src/data/priority_intelligence.db

# Configurações
DB_TIMEOUT=30
DB_BACKUP_ENABLED=true
DB_BACKUP_INTERVAL=24
DB_BACKUP_RETENTION=7
```

---

### 🔍 **INTELIGÊNCIA E PRIORIDADE**
```bash
# Sistema de Aprendizado
INTELLIGENCE_ENABLED=true
PRIORITY_LEARNING=true
ANALYTICS_ENABLED=true

# Configurações de Análise
ANALYTICS_TRACK_VIEWS=true
ANALYTICS_TRACK_ENGAGEMENT=true
ANALYTICS_RETENTION_DAYS=90

# Machine Learning
ML_MODEL_UPDATE_INTERVAL=168
ML_CONFIDENCE_THRESHOLD=0.7
ML_FEATURE_EXTRACTION=true
```

---

### 📤 **REVIEW E PUBLICAÇÃO**
```bash
# Sistema de Review
REVIEW_ENABLED=true
REVIEW_AUTO_APPROVE=false
REVIEW_REQUIRE_MANUAL=true

# Workflow
PUBLICATION_QUEUE_SIZE=50
PUBLICATION_BATCH_SIZE=5
PUBLICATION_DELAY=300

# Notificações
NOTIFICATION_ENABLED=false
NOTIFICATION_EMAIL=admin@creativecopias.com.br
NOTIFICATION_WEBHOOK=https://webhook.site/xxxxx
```

---

### 🖼️ **IMAGENS E MÍDIA**
```bash
# Configurações de Imagem
IMAGE_PROCESSING_ENABLED=true
IMAGE_PLACEHOLDER_URL=https://placeholder.com/300x200
IMAGE_DEFAULT_ALT=Produto Creative Cópias
IMAGE_MAX_SIZE=1024
IMAGE_QUALITY=85

# CDN e Storage
MEDIA_CDN_URL=https://cdn.creativecopias.com.br
MEDIA_UPLOAD_PATH=/uploads
MEDIA_ALLOWED_FORMATS=jpg,jpeg,png,webp
```

---

### 🔐 **SEGURANÇA**
```bash
# API Security
API_RATE_LIMIT=1000
API_RATE_WINDOW=3600
API_MAX_REQUESTS_PER_IP=100

# CORS
CORS_ORIGINS=https://creativecopias.com.br,https://blog.creativecopias.com.br
CORS_METHODS=GET,POST,PUT,DELETE
CORS_HEADERS=Content-Type,Authorization

# Tokens e Chaves
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here
```

---

### 📡 **MONITORAMENTO**
```bash
# Health Checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=60
HEALTH_CHECK_ENDPOINTS=/health,/status

# Métricas
METRICS_ENABLED=true
METRICS_ENDPOINT=/metrics
METRICS_RETENTION=7

# Logging
LOG_FORMAT=json
LOG_FILE_ENABLED=true
LOG_FILE_PATH=logs/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5
```

---

### 🌐 **REDE E PROXY**
```bash
# Proxy Settings
HTTP_PROXY=http://proxy:port
HTTPS_PROXY=https://proxy:port
NO_PROXY=localhost,127.0.0.1

# Timeouts
HTTP_TIMEOUT=30
CONNECTION_TIMEOUT=10
READ_TIMEOUT=30
```

---

### 🎛️ **FEATURES FLAGS**
```bash
# Funcionalidades
FEATURE_AUTO_GENERATION=true
FEATURE_AUTO_PUBLISHING=true
FEATURE_INTELLIGENT_PRIORITY=true
FEATURE_ADVANCED_SEO=true
FEATURE_IMAGE_PROCESSING=true
FEATURE_ANALYTICS=true
FEATURE_NOTIFICATIONS=false
FEATURE_API_DOCS=true
```

---

## 🎯 **CONFIGURAÇÕES POR AMBIENTE**

### 🔥 **PRODUÇÃO (Render/Railway)**
```bash
# Mínimas Obrigatórias
OPENAI_API_KEY=sk-proj-xxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br

# Recomendadas
DEBUG=false
LOG_LEVEL=info
WP_AUTO_PUBLISH=true
SCHEDULER_ENABLED=true
REVIEW_REQUIRE_MANUAL=true
```

### 🧪 **DESENVOLVIMENTO**
```bash
# Básicas
OPENAI_API_KEY=sk-proj-xxxxx
WP_SITE_URL=https://staging.blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://staging.creativecopias.com.br

# Debug
DEBUG=true
LOG_LEVEL=debug
WP_AUTO_PUBLISH=false
SCHEDULER_ENABLED=false
REVIEW_AUTO_APPROVE=true
```

### 🔬 **TESTE**
```bash
# Simulação
OPENAI_API_KEY=test-key
WP_SITE_URL=http://localhost:8080
WP_PASSWORD=test-password
SITE_BASE_URL=http://localhost:3000

# Configurações de Teste
DEBUG=true
LOG_LEVEL=debug
FEATURE_AUTO_GENERATION=false
FEATURE_AUTO_PUBLISHING=false
SCHEDULER_ENABLED=false
```

---

## 📝 **EXEMPLOS DE USO**

### **Render.com**
```bash
OPENAI_API_KEY=sk-proj-xxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br
DEBUG=false
LOG_LEVEL=info
WP_AUTO_PUBLISH=true
SCHEDULER_ENABLED=true
```

### **Railway.app**
```bash
OPENAI_API_KEY=sk-proj-xxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br
RAILWAY_ENVIRONMENT=production
```

### **Heroku**
```bash
OPENAI_API_KEY=sk-proj-xxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br
DYNO=web
```

### **Vercel**
```bash
OPENAI_API_KEY=sk-proj-xxxxx
WP_SITE_URL=https://blog.creativecopias.com.br
WP_PASSWORD=xxxx xxxx xxxx xxxx
SITE_BASE_URL=https://www.creativecopias.com.br
VERCEL=1
```

---

## ⚠️ **IMPORTANTE**

### **🔒 Variáveis Secretas (NUNCA committar)**
- `OPENAI_API_KEY`
- `WP_PASSWORD`
- `SECRET_KEY`
- `JWT_SECRET`
- `ENCRYPTION_KEY`

### **📋 Prioridade de Configuração**
1. **Environment Variables** (mais alta)
2. **Arquivo .env**
3. **Configurações padrão do código**

### **🔧 Validação Automática**
O sistema valida automaticamente:
- ✅ Variáveis obrigatórias presentes
- ✅ Formato de URLs correto
- ✅ Chaves de API válidas
- ✅ Tipos de dados corretos

---

## 🎉 **TOTAL: 80+ VARIÁVEIS**

**Sistema completamente configurável para qualquer ambiente!** 🚀 