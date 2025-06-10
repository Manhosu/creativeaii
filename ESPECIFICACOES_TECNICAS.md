# 🔧 Sistema Creative API - Especificações Técnicas

## 📋 **Arquitetura do Sistema**

### **Stack Tecnológico**
- **Backend:** Python 3.11+ com FastAPI
- **Banco de Dados:** SQLite (local) com backup automático
- **IA/ML:** OpenAI GPT-4o-mini
- **Web Framework:** FastAPI + Uvicorn
- **Interface:** HTML5/CSS3/JavaScript responsivo
- **CMS Integration:** WordPress REST API
- **Automação:** APScheduler com jobs agendados

### **Módulos Principais**

#### 🔍 **Scraper Module**
```
src/scraper/
├── creative_scraper.py      # Scraper principal
├── product_extractor.py     # Extração de dados de produtos
├── url_manager.py          # Gerenciamento de URLs monitoradas
└── scraper_manager.py      # Orquestração do scraping
```

#### 🤖 **Generator Module**
```
src/generator/
├── content_generator.py    # Geração de conteúdo com IA
├── prompt_builder.py      # Construção de prompts otimizados
├── seo_optimizer.py       # Otimização automática para SEO
├── template_manager.py    # Templates de artigos
└── product_database.py    # Base de dados de produtos
```

#### 📝 **Review Module**
```
src/review/
└── review_manager.py      # Sistema de revisão e aprovação
```

#### 🚀 **Publisher Module**
```
src/publisher/
├── publication_manager.py  # Gerenciamento de publicações
└── wordpress_client.py     # Cliente WordPress REST API
```

#### ⏰ **Scheduler Module**
```
src/scheduler/
└── scheduler_manager.py    # Agendamento automático de tarefas
```

---

## 🗃️ **Estrutura de Dados**

### **Produtos (SQLite)**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT,
    model TEXT,
    specifications TEXT,
    url TEXT,
    price REAL,
    date_found DATETIME,
    category TEXT
);
```

### **Artigos de Revisão (SQLite)**
```sql
CREATE TABLE review_articles (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    slug TEXT UNIQUE,
    meta_descricao TEXT,
    conteudo TEXT,
    tags TEXT,
    status TEXT DEFAULT 'pendente',
    data_criacao DATETIME,
    data_atualizacao DATETIME,
    revisor TEXT,
    comentario_revisor TEXT
);
```

### **Publicações (SQLite)**
```sql
CREATE TABLE publications (
    id INTEGER PRIMARY KEY,
    article_id INTEGER,
    wp_post_id INTEGER,
    wp_url TEXT,
    status TEXT,
    publication_date DATETIME,
    type TEXT
);
```

---

## ⚙️ **Configurações e Variáveis de Ambiente**

### **Arquivo .env**
```env
# Servidor
PORT=3025

# WordPress
WP_SITE_URL=https://blog.creativecopias.com.br
WP_USERNAME=api_seo_bot
WP_PASSWORD=S9OnT0E1DlCRqp3XdLF0Tcco

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Sistema
DEBUG=False
LOG_LEVEL=INFO
```

### **Configurações de SEO**
```python
SEO_CONFIG = {
    "title_max_length": 60,
    "meta_description_max_length": 155,
    "focus_keyphrase_density": 1.5,  # 1.5%
    "min_content_length": 300,
    "max_content_length": 800,
    "yoast_green_score": True
}
```

---

## 🕐 **Agendamentos Automáticos**

### **Jobs Configurados**
```python
# Scraping semanal - Domingos às 10h00
scheduler.add_job(
    func=run_weekly_scraping,
    trigger='cron',
    day_of_week='sun',
    hour=10,
    minute=0,
    id='weekly_scraping'
)

# Geração de artigos - Domingos às 10h15
scheduler.add_job(
    func=run_weekly_generation,
    trigger='cron',
    day_of_week='sun',
    hour=10,
    minute=15,
    id='weekly_generation'
)

# Limpeza mensal - 1º domingo às 02h00
scheduler.add_job(
    func=run_monthly_cleanup,
    trigger='cron',
    day_of_week='sun',
    hour=2,
    minute=0,
    id='monthly_cleanup'
)
```

---

## 🔗 **APIs e Integrações**

### **Endpoints Principais**
```
GET  /                          # Dashboard principal
GET  /health                    # Status do sistema
GET  /interface/review          # Interface de revisão
GET  /interface/publisher       # Interface de publicação

POST /scraper/run              # Executar scraping manual
POST /generator/generate       # Gerar artigo manual
POST /publisher/publish        # Publicar artigo
POST /scheduler/run           # Executar processo completo
```

### **WordPress REST API**
```python
# Endpoints utilizados
wp_api = {
    "posts": f"{WP_SITE_URL}/wp-json/wp/v2/posts",
    "categories": f"{WP_SITE_URL}/wp-json/wp/v2/categories",
    "tags": f"{WP_SITE_URL}/wp-json/wp/v2/tags",
    "users": f"{WP_SITE_URL}/wp-json/wp/v2/users/me"
}
```

### **OpenAI API**
```python
# Configuração do cliente
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=2000
)
```

---

## 📊 **Monitoramento e Logs**

### **Sistema de Logs**
```python
# Configuração Loguru
logger.add(
    "logs/system_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}"
)
```

### **Métricas Coletadas**
- ✅ **Performance:** Tempo de execução de cada módulo
- ✅ **Qualidade:** Score SEO dos artigos gerados
- ✅ **Produtividade:** Número de artigos gerados/publicados
- ✅ **Erros:** Logs detalhados de falhas e recuperações
- ✅ **WordPress:** Status de conexão e publicações

---

## 🔒 **Segurança e Backup**

### **Medidas de Segurança**
```python
# Autenticação WordPress
auth_headers = {
    'Authorization': f'Basic {base64_credentials}',
    'Content-Type': 'application/json'
}

# Validação de dados
def validate_article_data(data):
    # Sanitização de entrada
    # Validação de campos obrigatórios
    # Escape de caracteres especiais
```

### **Backup Automático**
```python
# Backup diário dos bancos de dados
backup_schedule = {
    "frequency": "daily",
    "time": "02:00",
    "retention": "30 days",
    "location": "backups/"
}
```

---

## 🚀 **Performance e Otimização**

### **Otimizações Implementadas**
- ✅ **Cache em memória** para produtos processados
- ✅ **Rate limiting** para APIs externas
- ✅ **Processamento assíncrono** quando possível
- ✅ **Compressão de responses** HTTP
- ✅ **Pool de conexões** para banco de dados

### **Benchmarks**
```
Scraping de produtos: ~2-5 segundos por página
Geração de artigo: ~15-30 segundos por artigo
Publicação WordPress: ~3-5 segundos por post
Processo completo: ~5-10 minutos para 4-6 artigos
```

---

## 🔧 **Instalação e Deploy**

### **Requisitos do Sistema**
```
Python 3.11+
Dependências: requirements.txt
Espaço em disco: 1GB mínimo
RAM: 512MB mínimo
Conexão com internet: Obrigatória
```

### **Comandos de Execução**
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Executar servidor
python -m uvicorn src.main:app --host 0.0.0.0 --port 3025 --reload
```

---

## 📈 **Escalabilidade**

### **Preparado para Crescimento**
- ✅ **Múltiplos sites** WordPress (configuração simples)
- ✅ **Mais fornecedores** monitorados (adicionar URLs)
- ✅ **Maior volume** de artigos (ajustar agendamentos)
- ✅ **Banco de dados** SQLite → PostgreSQL (se necessário)
- ✅ **Deploy em cloud** (AWS, Azure, Google Cloud)

### **Limites Atuais**
- **Artigos por execução:** 10-15 (configurável)
- **Sites monitorados:** 20+ (expandível)
- **Artigos no banco:** 10.000+ (SQLite suporta)
- **Concurrent requests:** 50+ (FastAPI assíncrono)

---

## 🛠️ **Manutenção**

### **Tarefas Automáticas**
- ✅ **Limpeza de logs** antigos (30 dias)
- ✅ **Backup** de bancos de dados (diário)
- ✅ **Verificação** de saúde do sistema (contínua)
- ✅ **Atualizações** de dependências (manual)

### **Troubleshooting**
```python
# Verificação de saúde
GET /health

# Logs detalhados
tail -f logs/system_*.log

# Reset do sistema
POST /debug/reset (se necessário)
```

---

*Especificações técnicas atualizadas em: Junho 2025*
*Versão do Sistema: 1.0.0* 