"""
Sistema de GeraÃ§Ã£o AutomÃ¡tica de ConteÃºdo SEO
Arquivo principal do FastAPI
"""

# -*- coding: utf-8 -*-
import os
import sys
import asyncio
from pathlib import Path

# Adicionar paths absolutos para importaÃ§Ãµes
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

# Importar loguru logo no inÃ­cio
from loguru import logger

# Carregar variÃ¡veis de ambiente do arquivo .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Definir variÃ¡veis padrÃ£o se nÃ£o existirem
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('OPENAI_MODEL', 'gpt-4o-mini')
os.environ.setdefault('OPENAI_MAX_TOKENS', '2000')
os.environ.setdefault('OPENAI_TEMPERATURE', '0.7')
os.environ.setdefault('CONTENT_MIN_WORDS', '300')
os.environ.setdefault('CONTENT_MAX_WORDS', '1000')

# Configurar outras variÃ¡veis importantes
# Porta serÃ¡ definida pelo Railway via variÃ¡vel de ambiente PORT
os.environ.setdefault('OPENAI_MODEL', 'gpt-4o-mini')

# NÃ£o definir chave de API aqui - deve vir do .env
if not os.getenv('OPENAI_API_KEY'):
    logger.warning("âš ï¸ OPENAI_API_KEY nÃ£o encontrada nas variÃ¡veis de ambiente")
if not os.getenv('WP_PASSWORD'):
    logger.warning("âš ï¸ WP_PASSWORD nÃ£o encontrada nas variÃ¡veis de ambiente")

# Configurar variÃ¡veis de ambiente essenciais - valores devem vir do .env
os.environ.setdefault('WORDPRESS_URL', 'https://blog.creativecopias.com.br/wp-json/wp/v2/')
os.environ.setdefault('WORDPRESS_USERNAME', 'api_seo_bot')
# WP_PASSWORD deve vir do .env - nÃ£o definir aqui
os.environ.setdefault('WP_SITE_URL', 'https://blog.creativecopias.com.br')
os.environ.setdefault('WP_USERNAME', 'api_seo_bot')
# WP_PASSWORD deve vir do .env - nÃ£o definir aqui
os.environ.setdefault('WP_AUTO_PUBLISH', 'true')
os.environ.setdefault('WP_DEFAULT_CATEGORY', 'geral')

# Log das variÃ¡veis carregadas
print(f"ðŸ”§ ConfiguraÃ§Ãµes carregadas:")
print(f"   PORT: {os.getenv('PORT')}")
print(f"   WP_SITE_URL: {os.getenv('WP_SITE_URL')}")
print(f"   WP_USERNAME: {os.getenv('WP_USERNAME')}")
print(f"   OPENAI_API_KEY: {'âœ… Configurada' if os.getenv('OPENAI_API_KEY') else 'âŒ NÃ£o encontrada'}")
print(f"   OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")

# ConfiguraÃ§Ãµes WordPress vÃªm das variÃ¡veis de ambiente
# NÃ£o forÃ§ar valores hardcoded aqui

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import logging
from typing import List
from datetime import datetime
from fastapi.openapi.utils import get_openapi

# Importar mÃ³dulo scraper
try:
    from src.scraper.scraper_manager import ScraperManager
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    logger.warning("âš ï¸ MÃ³dulo scraper nÃ£o disponÃ­vel")

# Importar mÃ³dulo generator
try:
    from src.generator.generator_manager import GeneratorManager
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    logger.warning("âš ï¸ MÃ³dulo generator nÃ£o disponÃ­vel")

# Importar mÃ³dulo review
try:
    from src.review.review_manager import ReviewManager
    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False
    logger.warning("âš ï¸ MÃ³dulo review nÃ£o disponÃ­vel")

# Importar mÃ³dulo publisher
try:
    from src.publisher.publication_manager import PublicationManager
    PUBLISHER_AVAILABLE = True
except ImportError:
    PUBLISHER_AVAILABLE = False
    logger.warning("âš ï¸ MÃ³dulo publisher nÃ£o disponÃ­vel")

# Importar mÃ³dulo config
try:
    from src.config.config_manager import ConfigManager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("âš ï¸ MÃ³dulo config nÃ£o disponÃ­vel")

# Importar mÃ³dulo scheduler
try:
    from src.scheduler.scheduler_manager import SchedulerManager
    SCHEDULER_AVAILABLE = True
    logger.info("âœ… MÃ³dulo scheduler carregado com sucesso")
except ImportError as e:
    SCHEDULER_AVAILABLE = False
    logger.warning(f"âš ï¸ MÃ³dulo scheduler nÃ£o disponÃ­vel: {e}")

# Importar mÃ³dulos de inteligÃªncia
try:
    from src.intelligence.priority_manager import PriorityManager
    from src.intelligence.publication_monitor import PublicationMonitor
    from src.intelligence.ai_learning import AILearning
    INTELLIGENCE_AVAILABLE = True
    logger.info("âœ… MÃ³dulos de inteligÃªncia carregados com sucesso")
except ImportError as e:
    INTELLIGENCE_AVAILABLE = False
    logger.warning(f"âš ï¸ MÃ³dulos de inteligÃªncia nÃ£o disponÃ­veis: {e}")

# Importar mÃ³dulo de categorias ativas
try:
    from src.config.active_categories_manager import ActiveCategoriesManager
    CATEGORIES_AVAILABLE = True
    logger.info("âœ… MÃ³dulo de categorias ativas carregado com sucesso")
except ImportError as e:
    CATEGORIES_AVAILABLE = False
    logger.warning(f"âš ï¸ MÃ³dulo de categorias ativas nÃ£o disponÃ­vel: {e}")

# ConfiguraÃ§Ãµes
APP_NAME = "Sistema de GeraÃ§Ã£o AutomÃ¡tica de ConteÃºdo SEO"
APP_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", 3025))

# ConfiguraÃ§Ã£o de logs
logger.add("logs/main.log", rotation="1 week", retention="30 days", level="INFO")

# Models para requests
class ScrapingRequest(BaseModel):
    url: str = None
    full_scraping: bool = False

class GenerationRequest(BaseModel):
    product_id: str = None
    product_data: dict = None
    custom_keywords: List[str] = None
    custom_instructions: str = None
    tone: str = "profissional"
    wp_category: str = None
    produto_original: str = None

class ReviewRequest(BaseModel):
    titulo: str = None
    slug: str = None
    meta_descricao: str = None
    conteudo: str = None
    tags: List[str] = None
    comentario_revisor: str = None
    wp_category: str = None
    produto_original: str = None

class ReviewActionRequest(BaseModel):
    comment: str = ""
    reviewer: str = "Sistema"
    wp_category: str = None
    produto_original: str = None
    skip_availability_check: bool = False

class PublicationRequest(BaseModel):
    article_id: int
    publish_immediately: bool = True
    scheduled_date: str = None  # ISO format string

class WordPressConfigRequest(BaseModel):
    site_url: str
    username: str
    password: str

class ConfigUpdateRequest(BaseModel):
    configurations: dict = None

class URLAddRequest(BaseModel):
    category: str
    name: str
    url: str
    priority: int = 5

class TemplateAddRequest(BaseModel):
    template_name: str
    product_type: str
    title_template: str
    content_template: str
    meta_description_template: str = None
    keywords_template: str = None

class JobExecutionRequest(BaseModel):
    job_id: str = None

class CategoryUpdateRequest(BaseModel):
    is_active: bool

class CategoryPriorityRequest(BaseModel):
    priority: int

class CategoriesBatchUpdateRequest(BaseModel):
    categories: dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicaÃ§Ã£o"""
    logger.info("ðŸš€ Iniciando Sistema de GeraÃ§Ã£o de ConteÃºdo SEO")
    
    # InicializaÃ§Ã£o
    try:
        # Criar diretÃ³rios necessÃ¡rios
        os.makedirs("logs", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        os.makedirs("templates", exist_ok=True)
        
        logger.info("ðŸ“ DiretÃ³rios criados com sucesso")
        
        # Inicializar banco de dados
        # await init_database()
        
        # Inicializar scheduler automÃ¡tico
        if SCHEDULER_AVAILABLE:
            try:
                global scheduler_manager
                # Determinar URL base para o scheduler
                scheduler_base_url = (
                    os.getenv('SCHEDULER_BASE_URL') or 
                    os.getenv('SYSTEM_BASE_URL') or 
                    f"http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '3025')}"
                )
                logger.info(f"â° Inicializando scheduler com URL base: {scheduler_base_url}")
                
                scheduler_manager = SchedulerManager(base_url=scheduler_base_url)
                scheduler_manager.start()
                logger.info("â° Scheduler iniciado com sucesso")
            except Exception as e:
                logger.error(f"âŒ Erro ao iniciar scheduler: {e}")
        
        logger.info("âœ… AplicaÃ§Ã£o iniciada com sucesso")
        
    except Exception as e:
        logger.error(f"âŒ Erro na inicializaÃ§Ã£o: {e}")
        raise
    
    yield
    
    # FinalizaÃ§Ã£o
    logger.info("ðŸ›‘ Finalizando aplicaÃ§Ã£o")
    
    # Parar scheduler se estiver rodando
    if SCHEDULER_AVAILABLE and 'scheduler_manager' in globals():
        try:
            scheduler_manager.stop()
            logger.info("â° Scheduler parado com sucesso")
        except Exception as e:
            logger.error(f"âŒ Erro ao parar scheduler: {e}")


# CriaÃ§Ã£o da aplicaÃ§Ã£o FastAPI
app = FastAPI(
    title=APP_NAME,
    description="Sistema automatizado para geraÃ§Ã£o de conteÃºdo SEO baseado em produtos de e-commerce",
    version=APP_VERSION,
    docs_url=None,
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar arquivos estÃ¡ticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# CustomizaÃ§Ã£o do Swagger UI com CSS e JavaScript
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Swagger UI customizado com busca e tema dark"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
        <link rel="shortcut icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>âš™ï¸</text></svg>">
        <title>Sistema de GeraÃ§Ã£o de ConteÃºdo SEO - DocumentaÃ§Ã£o API</title>
        <style>
            /* CSS Customizado para Dark Mode e Melhorias */
            :root {
                --bg-primary: #0a0a0a;
                --bg-secondary: #1a1a1a;
                --bg-tertiary: #2a2a2a;
                --text-primary: #ffffff;
                --text-secondary: #a1a1aa;
                --accent-blue: #007aff;
                --accent-green: #34c759;
                --accent-orange: #ff9500;
                --accent-red: #ff3b30;
                --glass-bg: rgba(255, 255, 255, 0.05);
                --glass-border: rgba(255, 255, 255, 0.1);
            }
            
            /* Dark Mode Base */
            body {
                background: var(--bg-primary) !important;
                color: var(--text-primary) !important;
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif !important;
                margin: 0;
                padding: 0;
            }
            
            .swagger-ui {
                background: var(--bg-primary) !important;
            }
            
            .swagger-ui .topbar {
                background: var(--bg-secondary) !important;
                border-bottom: 1px solid var(--glass-border) !important;
                padding: 10px 0;
            }
            
            .swagger-ui .info {
                margin: 30px 0 !important;
                background: var(--bg-secondary) !important;
                padding: 20px !important;
                border-radius: 8px !important;
            }
            
            .swagger-ui .info .title {
                color: var(--accent-blue) !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
            }
            
            /* Barra de busca customizada */
            .custom-search-bar {
                position: sticky;
                top: 0;
                background: var(--glass-bg);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 20px;
                margin: 20px;
                z-index: 1000;
            }
            
            .search-container {
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }
            
            .search-input {
                flex: 1;
                min-width: 300px;
                padding: 12px 16px;
                background: var(--bg-tertiary);
                border: 1px solid var(--glass-border);
                border-radius: 8px;
                color: var(--text-primary);
                font-size: 14px;
            }
            
            .search-input::placeholder {
                color: var(--text-secondary);
            }
            
            .search-input:focus {
                outline: none;
                border-color: var(--accent-blue);
                box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2);
            }
            
            .filter-buttons {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .filter-btn {
                padding: 6px 12px;
                background: var(--bg-tertiary);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                color: var(--text-secondary);
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
            }
            
            .filter-btn:hover, .filter-btn.active {
                background: var(--accent-blue);
                color: white;
                border-color: var(--accent-blue);
            }
            
            .search-stats {
                color: var(--text-secondary);
                font-size: 12px;
                margin-left: 10px;
            }
            
            /* EstilizaÃ§Ã£o das operaÃ§Ãµes */
            .swagger-ui .opblock {
                margin: 10px 0;
                border-radius: 8px !important;
                border: 1px solid var(--glass-border) !important;
                background: var(--bg-secondary) !important;
            }
            
            .swagger-ui .opblock.opblock-get {
                border-left: 4px solid var(--accent-blue) !important;
            }
            
            .swagger-ui .opblock.opblock-post {
                border-left: 4px solid var(--accent-green) !important;
            }
            
            .swagger-ui .opblock.opblock-delete {
                border-left: 4px solid var(--accent-red) !important;
            }
            
            .swagger-ui .opblock.opblock-put {
                border-left: 4px solid var(--accent-orange) !important;
            }
            
            /* Dark theme para swagger */
            .swagger-ui .scheme-container,
            .swagger-ui .wrapper,
            .swagger-ui .opblock-tag,
            .swagger-ui .opblock .opblock-summary {
                background: var(--bg-secondary) !important;
                color: var(--text-primary) !important;
            }
            
            .swagger-ui .opblock .opblock-summary-description {
                color: var(--text-primary) !important;
            }
            
            .swagger-ui .opblock .opblock-summary-path {
                color: var(--accent-blue) !important;
            }
            
            /* Ocultar operaÃ§Ãµes filtradas */
            .swagger-ui .opblock.hidden-by-search {
                display: none !important;
            }
            
            .swagger-ui .opblock-tag.hidden-by-search {
                display: none !important;
            }
            
            /* BotÃ£o de voltar ao dashboard */
            .back-to-dashboard {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: var(--accent-blue);
                color: white !important;
                padding: 12px 16px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 500;
                box-shadow: 0 8px 25px rgba(0, 122, 255, 0.4);
                transition: all 0.3s ease;
                z-index: 1001;
            }
            
            .back-to-dashboard:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 35px rgba(0, 122, 255, 0.6);
                color: white !important;
                text-decoration: none;
            }
            
            /* Responsividade */
            @media (max-width: 768px) {
                .search-container {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .search-input {
                    min-width: auto;
                }
                
                .filter-buttons {
                    justify-content: center;
                }
                
                .custom-search-bar {
                    margin: 10px;
                    padding: 15px;
                }
            }
        </style>
    </head>
    <body>
        <div class="custom-search-bar">
            <div class="search-container">
                <input type="text" id="apiSearch" class="search-input" placeholder="ðŸ” Buscar endpoints, operaÃ§Ãµes ou descriÃ§Ãµes...">
                <div class="filter-buttons">
                    <button class="filter-btn active" data-method="all">Todos</button>
                    <button class="filter-btn" data-method="get">GET</button>
                    <button class="filter-btn" data-method="post">POST</button>
                    <button class="filter-btn" data-method="delete">DELETE</button>
                    <button class="filter-btn" data-method="put">PUT</button>
                </div>
                <span class="search-stats" id="searchStats">Carregando endpoints...</span>
            </div>
        </div>
        <a href="/" class="back-to-dashboard">â† Dashboard</a>
        <div id="swagger-ui"></div>
        
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
        <script>
            const ui = SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                syntaxHighlight: {
                    activated: true,
                    theme: "agate"
                },
                tryItOutEnabled: true,
                displayRequestDuration: true,
                showExtensions: true,
                showCommonExtensions: true,
                docExpansion: "list",
                operationsSorter: "alpha",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1
            });
            
            // JavaScript para funcionalidade de busca avanÃ§ada
            document.addEventListener('DOMContentLoaded', function() {
                let currentFilter = 'all';
                let searchTerm = '';
                
                const searchInput = document.getElementById('apiSearch');
                const filterButtons = document.querySelectorAll('.filter-btn');
                const searchStats = document.getElementById('searchStats');
                
                // Aguardar o Swagger UI carregar completamente
                const waitForSwaggerUI = () => {
                    if (document.querySelectorAll('.opblock').length > 0) {
                        initializeSearch();
                    } else {
                        setTimeout(waitForSwaggerUI, 500);
                    }
                };
                
                const initializeSearch = () => {
                    updateStats();
                    setupEventListeners();
                };
                
                const setupEventListeners = () => {
                    // Busca em tempo real
                    searchInput.addEventListener('input', (e) => {
                        searchTerm = e.target.value.toLowerCase();
                        performSearch();
                    });
                    
                    // Filtros por mÃ©todo
                    filterButtons.forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            filterButtons.forEach(b => b.classList.remove('active'));
                            e.target.classList.add('active');
                            currentFilter = e.target.dataset.method;
                            performSearch();
                        });
                    });
                    
                    // Atalhos de teclado
                    document.addEventListener('keydown', (e) => {
                        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                            e.preventDefault();
                            searchInput.focus();
                        }
                        
                        if (e.key === 'Escape' && document.activeElement === searchInput) {
                            searchInput.value = '';
                            searchTerm = '';
                            performSearch();
                        }
                    });
                };
                
                const performSearch = () => {
                    const operations = document.querySelectorAll('.opblock');
                    const sections = document.querySelectorAll('.opblock-tag');
                    let visibleCount = 0;
                    
                    operations.forEach(op => {
                        const method = getOperationMethod(op);
                        const summary = op.querySelector('.opblock-summary-description')?.textContent?.toLowerCase() || '';
                        const path = op.querySelector('.opblock-summary-path')?.textContent?.toLowerCase() || '';
                        const tag = op.closest('.opblock-tag')?.querySelector('.opblock-tag-section h3')?.textContent?.toLowerCase() || '';
                        
                        const matchesMethod = currentFilter === 'all' || method === currentFilter;
                        const matchesSearch = searchTerm === '' || 
                                           summary.includes(searchTerm) || 
                                           path.includes(searchTerm) || 
                                           tag.includes(searchTerm);
                        
                        if (matchesMethod && matchesSearch) {
                            op.classList.remove('hidden-by-search');
                            visibleCount++;
                        } else {
                            op.classList.add('hidden-by-search');
                        }
                    });
                    
                    // Ocultar seÃ§Ãµes vazias
                    sections.forEach(section => {
                        const visibleOps = section.querySelectorAll('.opblock:not(.hidden-by-search)');
                        if (visibleOps.length === 0) {
                            section.classList.add('hidden-by-search');
                        } else {
                            section.classList.remove('hidden-by-search');
                        }
                    });
                    
                    updateStats(visibleCount);
                };
                
                const getOperationMethod = (operation) => {
                    if (operation.classList.contains('opblock-get')) return 'get';
                    if (operation.classList.contains('opblock-post')) return 'post';
                    if (operation.classList.contains('opblock-delete')) return 'delete';
                    if (operation.classList.contains('opblock-put')) return 'put';
                    if (operation.classList.contains('opblock-patch')) return 'patch';
                    return 'unknown';
                };
                
                const updateStats = (visible = null) => {
                    const total = document.querySelectorAll('.opblock').length;
                    const count = visible !== null ? visible : total;
                };
                
                // Inicializar quando o Swagger UI estiver pronto
                setTimeout(waitForSwaggerUI, 3000);
                
                // Recriar listeners se o Swagger UI recarregar
                const observer = new MutationObserver(() => {
                    if (document.querySelectorAll('.opblock').length > 0) {
                        setTimeout(initializeSearch, 1000);
                    }
                });
                
                observer.observe(document.getElementById('swagger-ui'), {
                    childList: true,
                    subtree: true
                });
            });
        </script>
    </body>
    </html>
    """)

# ConfiguraÃ§Ã£o de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produÃ§Ã£o, especificar domÃ­nios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ConfiguraÃ§Ã£o de arquivos estÃ¡ticos e templates
templates = None
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    if os.path.exists("templates"):
        templates = Jinja2Templates(directory="templates")
    logger.info("âœ… Arquivos estÃ¡ticos e templates configurados")
except Exception as e:
    logger.warning(f"âš ï¸ NÃ£o foi possÃ­vel configurar arquivos estÃ¡ticos: {e}")
    templates = None


# =====================================================
# CUSTOMIZAÃ‡ÃƒO DO OPENAPI
# =====================================================

def custom_openapi():
    """GeraÃ§Ã£o customizada do OpenAPI para compatibilidade com Swagger UI"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        description="Sistema automatizado para geraÃ§Ã£o de conteÃºdo SEO baseado em produtos de e-commerce",
        routes=app.routes,
    )
    
    # ForÃ§ar versÃ£o 3.0.0 para compatibilidade com Swagger UI
    openapi_schema["openapi"] = "3.0.0"
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# =====================================================
# ROTAS PRINCIPAIS
# =====================================================

@app.get("/")
async def dashboard():
    """Dashboard principal do sistema"""
    try:
        
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sistema de GeraÃ§Ã£o AutomÃ¡tica de ConteÃºdo</title>
                <link rel="stylesheet" href="/static/css/_design_system.css">
                <style>
                    .page-wrapper {
                        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .page-wrapper::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: radial-gradient(circle at 30% 40%, rgba(0, 122, 255, 0.1) 0%, transparent 50%),
                                    radial-gradient(circle at 70% 60%, rgba(48, 209, 88, 0.1) 0%, transparent 50%);
                        pointer-events: none;
                        z-index: 0;
                    }
                    
                    .content {
                        position: relative;
                        z-index: 1;
                        width: 100%;
                        max-width: 900px;
                        padding: var(--space-6);
                    }
                    
                    .header {
                        text-align: center;
                        margin-bottom: var(--space-16);
                    }
                    
                    .header h1 { 
                        font-size: var(--text-5xl);
                        font-weight: var(--font-bold);
                        margin-bottom: 0;
                        background: linear-gradient(135deg, var(--primary), var(--success));
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                        animation: fadeInUp 0.8s ease-out;
                    }
                    

                    
                    .main-actions {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                        gap: var(--space-8);
                        margin-bottom: var(--space-16);
                    }
                    
                    .action-card {
                        background: var(--bg-card);
                        border: 1px solid var(--border-primary);
                        border-radius: var(--radius-3xl);
                        padding: var(--space-12);
                        text-align: center;
                        transition: all var(--transition-spring);
                        position: relative;
                        overflow: hidden;
                        backdrop-filter: blur(20px);
                        animation: fadeInUp 0.8s ease-out var(--delay, 0.6s) both;
                    }
                    

                    
                    .action-card:nth-child(1) { --delay: 0.2s; }
                    .action-card:nth-child(2) { --delay: 0.4s; }
                    .action-card:nth-child(3) { --delay: 0.6s; }
                    
                    .action-card::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(135deg, transparent, rgba(0, 122, 255, 0.05));
                        opacity: 0;
                        transition: var(--transition-normal);
                    }
                    
                    .action-card:hover::before {
                        opacity: 1;
                    }
                    
                    .action-card:hover {
                        transform: translateY(-8px) scale(1.02);
                        border-color: var(--border-accent);
                        box-shadow: var(--shadow-2xl), var(--shadow-glow);
                    }
                    
                    .action-icon {
                        font-size: 4rem;
                        margin-bottom: var(--space-6);
                        display: block;
                        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
                    }
                    
                    .action-title {
                        font-size: var(--text-2xl);
                        font-weight: var(--font-bold);
                        margin-bottom: var(--space-4);
                        color: var(--text-primary);
                    }
                    
                    .action-desc {
                        color: var(--text-secondary);
                        margin-bottom: var(--space-8);
                        font-size: var(--text-base);
                        line-height: var(--leading-relaxed);
                    }
                    
                    .action-btn {
                        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                        color: white;
                        border: none;
                        padding: var(--space-4) var(--space-8);
                        border-radius: var(--radius-2xl);
                        font-size: var(--text-lg);
                        font-weight: var(--font-semibold);
                        cursor: pointer;
                        transition: all var(--transition-spring);
                        text-decoration: none; 
                        display: inline-flex;
                        align-items: center;
                        gap: var(--space-2);
                        box-shadow: var(--shadow-lg), var(--shadow-glow);
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .action-btn:hover {
                        transform: translateY(-3px);
                        box-shadow: var(--shadow-xl), var(--shadow-glow);
                        background: linear-gradient(135deg, var(--primary-light), var(--primary));
                    }
                    
                    .action-btn.success-btn {
                        background: linear-gradient(135deg, var(--success), var(--success-dark));
                        box-shadow: var(--shadow-lg), var(--shadow-glow-success);
                    }
                    
                    .action-btn.success-btn:hover {
                        box-shadow: var(--shadow-xl), var(--shadow-glow-success);
                        background: linear-gradient(135deg, var(--success-light), var(--success));
                    }
                    
                    .action-btn.warning-btn {
                        background: linear-gradient(135deg, var(--warning), var(--warning-dark));
                        box-shadow: var(--shadow-lg), var(--shadow-glow-warning);
                    }
                    
                    .action-btn.warning-btn:hover {
                        box-shadow: var(--shadow-xl), var(--shadow-glow-warning);
                        background: linear-gradient(135deg, var(--warning-light), var(--warning));
                    }
                    

                    
                    @media (max-width: 768px) {
                        .header h1 { 
                            font-size: var(--text-3xl); 
                        }
                        .main-actions {
                            grid-template-columns: 1fr;
                        }
                        .action-card { 
                            padding: var(--space-8); 
                        }
                        .action-icon {
                            font-size: 3rem;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="page-wrapper">
                    <div class="content">
                        <div class="container">
                            <div class="header">
                                <h1>Sistema de GeraÃ§Ã£o AutomÃ¡tica de ConteÃºdo</h1>
                            </div>
                            

                            
                            <div class="main-actions">
                                <div class="action-card">
                                    <span class="action-icon">ðŸ”</span>
                                    <h3 class="action-title">Scraper</h3>
                                    <p class="action-desc">Busca de produtos e gera artigos automaticamente</p>
                                    <a href="/interface/scraper" class="action-btn">
                                        <span>Acessar</span>
                                        <span>â†’</span>
                                    </a>
                                </div>
                                
                                <div class="action-card">
                                    <span class="action-icon">âš™ï¸</span>
                                    <h3 class="action-title">ConfiguraÃ§Ãµes</h3>
                                    <p class="action-desc">Painel de configuraÃ§Ã£o geral do sistema</p>
                                    <a href="/config" class="action-btn warning-btn">
                                        <span>Acessar</span>
                                        <span>â†’</span>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return JSONResponse({"error": "Erro interno do servidor"}, status_code=500)


@app.get("/health")
async def health_check():
    """VerificaÃ§Ã£o de saÃºde do sistema"""
    modules_status = {
        "scraper": "ready" if SCRAPER_AVAILABLE else "not_available",
        "generator": "ready" if GENERATOR_AVAILABLE else "not_available", 
        "review": "ready" if REVIEW_AVAILABLE else "not_available",
        "publisher": "ready" if PUBLISHER_AVAILABLE else "not_available",
        "config": "ready" if CONFIG_AVAILABLE else "not_available",
        "scheduler": "ready" if SCHEDULER_AVAILABLE else "not_available"
    }
    
    # Verificar status do scraper se disponÃ­vel
    if SCRAPER_AVAILABLE:
        try:
            manager = ScraperManager()
            scraper_data = manager.get_scraping_status()
            modules_status["scraper"] = "operational"
            modules_status["scraper_details"] = {
                "urls_configuradas": scraper_data.get("urls_configuradas", 0),
                "produtos_processados": scraper_data.get("produtos_processados", 0)
            }
        except Exception as e:
            modules_status["scraper"] = "error"
            modules_status["scraper_error"] = str(e)
    
    # Verificar status do generator se disponÃ­vel
    if GENERATOR_AVAILABLE:
        try:
            gen_manager = GeneratorManager()
            gen_stats = gen_manager.get_stats()
            modules_status["generator"] = "operational"
            modules_status["generator_details"] = {
                "simulation_mode": gen_stats.get("simulation_mode", True),
                "articles_generated": gen_stats.get("total_articles_in_memory", 0),
                "total_generated": gen_stats["manager_stats"].get("total_generated", 0)
            }
        except Exception as e:
            modules_status["generator"] = "error"
            modules_status["generator_error"] = str(e)
    
    # Verificar status do review se disponÃ­vel
    if REVIEW_AVAILABLE:
        try:
            review_manager = ReviewManager()
            review_stats = review_manager.get_statistics()
            modules_status["review"] = "operational"
            modules_status["review_details"] = {
                "total_articles": review_stats.get("total_artigos", 0),
                "pending_review": review_stats.get("pendentes", 0),
                "approved": review_stats.get("aprovados", 0),
                "rejected": review_stats.get("rejeitados", 0)
            }
        except Exception as e:
            modules_status["review"] = "error"
            modules_status["review_error"] = str(e)
    
    # Verificar status do publisher se disponÃ­vel
    if PUBLISHER_AVAILABLE:
        try:
            pub_manager = PublicationManager()
            pub_stats = pub_manager.get_publication_statistics()
            modules_status["publisher"] = "operational"
            modules_status["publisher_details"] = {
                "total_publications": pub_stats.get("total_publications", 0),
                "published": pub_stats.get("published", 0),
                "failed": pub_stats.get("failed", 0),
                "pending": pub_stats.get("pending", 0),
                "wordpress_configured": pub_stats.get("wordpress_configured", False)
            }
        except Exception as e:
            modules_status["publisher"] = "error"
            modules_status["publisher_error"] = str(e)
    
    # Adicionar status do config
    if CONFIG_AVAILABLE:
        try:
            config_manager = ConfigManager()
            modules_status["config"] = {
                "status": "operational",
                "statistics": config_manager.get_statistics()
            }
        except Exception as e:
            modules_status["config"] = {'status': 'error', 'error': str(e)}
    else:
        modules_status["config"] = {'status': 'not_available'}
    
    # Verificar status do scheduler se disponÃ­vel
    if SCHEDULER_AVAILABLE and 'scheduler_manager' in globals():
        try:
            scheduler_status = scheduler_manager.get_status()
            modules_status["scheduler"] = {
                "status": "operational",
                "is_running": scheduler_status.get("is_running", False),
                "jobs_count": scheduler_status.get("jobs_count", 0),
                "recent_executions": len(scheduler_status.get("recent_executions", [])),
                "details": scheduler_status
            }
        except Exception as e:
            modules_status["scheduler"] = {'status': 'error', 'error': str(e)}
    else:
        modules_status["scheduler"] = {'status': 'not_available' if not SCHEDULER_AVAILABLE else 'not_initialized'}
    
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "port": PORT,
        "modules": modules_status
    }


@app.get("/api-docs", response_class=HTMLResponse)
async def api_documentation():
    """DocumentaÃ§Ã£o interativa da API com campo de busca"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DocumentaÃ§Ã£o da API - Sistema SEO</title>
        <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            :root {
                --bg-primary: #0a0a0a;
                --bg-secondary: #1a1a1a;
                --bg-tertiary: #2a2a2a;
                --text-primary: #ffffff;
                --text-secondary: #a1a1aa;
                --accent-blue: #007aff;
                --accent-green: #34c759;
                --accent-orange: #ff9500;
                --accent-red: #ff3b30;
                --accent-purple: #af52de;
                --glass-bg: rgba(255, 255, 255, 0.05);
                --glass-border: rgba(255, 255, 255, 0.1);
            }
            
            body {
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                background: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
            }
            
            .header {
                background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
                padding: 30px 0;
                text-align: center;
                border-bottom: 1px solid var(--glass-border);
            }
            
            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--accent-blue), var(--accent-green));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .header p {
                color: var(--text-secondary);
                font-size: 1.1rem;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .search-section {
                background: var(--glass-bg);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 30px;
                margin-bottom: 40px;
                position: sticky;
                top: 20px;
                z-index: 100;
            }
            
            .search-box {
                position: relative;
                margin-bottom: 20px;
            }
            
            .search-input {
                width: 100%;
                padding: 15px 50px 15px 20px;
                background: var(--bg-tertiary);
                border: 1px solid var(--glass-border);
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            
            .search-input:focus {
                outline: none;
                border-color: var(--accent-blue);
                box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
            }
            
            .search-icon {
                position: absolute;
                right: 15px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--text-secondary);
                font-size: 1.2rem;
            }
            
            .filters {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .filter-btn {
                padding: 8px 16px;
                background: var(--bg-tertiary);
                border: 1px solid var(--glass-border);
                border-radius: 20px;
                color: var(--text-secondary);
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .filter-btn:hover, .filter-btn.active {
                background: var(--accent-blue);
                color: white;
                border-color: var(--accent-blue);
            }
            
            .stats {
                margin-top: 15px;
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .modules {
                display: grid;
                gap: 30px;
            }
            
            .module {
                background: var(--glass-bg);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 30px;
                transition: all 0.3s ease;
            }
            
            .module:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .module-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid var(--glass-border);
            }
            
            .module-icon {
                font-size: 2rem;
            }
            
            .module-title {
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .module-desc {
                color: var(--text-secondary);
                margin-bottom: 20px;
            }
            
            .endpoints {
                display: grid;
                gap: 15px;
            }
            
            .endpoint {
                background: var(--bg-tertiary);
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
                border-left: 4px solid transparent;
            }
            
            .endpoint:hover {
                background: rgba(255, 255, 255, 0.05);
            }
            
            .endpoint.get { border-left-color: var(--accent-blue); }
            .endpoint.post { border-left-color: var(--accent-green); }
            .endpoint.put { border-left-color: var(--accent-orange); }
            .endpoint.delete { border-left-color: var(--accent-red); }
            
            .endpoint-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 10px;
            }
            
            .method {
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.8rem;
                font-weight: 600;
                min-width: 60px;
                text-align: center;
            }
            
            .method.get { background: var(--accent-blue); }
            .method.post { background: var(--accent-green); }
            .method.put { background: var(--accent-orange); }
            .method.delete { background: var(--accent-red); }
            
            .endpoint-path {
                font-family: 'Courier New', monospace;
                font-size: 1rem;
                color: var(--text-primary);
                flex: 1;
            }
            
            .endpoint-desc {
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .hidden {
                display: none !important;
            }
            
            .no-results {
                text-align: center;
                padding: 60px 20px;
                color: var(--text-secondary);
            }
            
            .no-results h3 {
                font-size: 1.5rem;
                margin-bottom: 10px;
            }
            
            @media (max-width: 768px) {
                .filters {
                    justify-content: center;
                }
                
                .endpoint-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ðŸ“š DocumentaÃ§Ã£o da API</h1>
            <p>Sistema de GeraÃ§Ã£o AutomÃ¡tica de ConteÃºdo SEO</p>
        </div>
        
        <div class="container">
            <div class="search-section">
                <div class="search-box">
                    <input type="text" class="search-input" placeholder="ðŸ” Buscar endpoints, mÃ³dulos ou funcionalidades..." id="searchInput">
                    <span class="search-icon">ðŸ”</span>
                </div>
                
                <div class="filters">
                    <button class="filter-btn active" data-filter="all">Todos</button>
                    <button class="filter-btn" data-filter="get">GET</button>
                    <button class="filter-btn" data-filter="post">POST</button>
                    <button class="filter-btn" data-filter="delete">DELETE</button>
                    <button class="filter-btn" data-filter="scraper">Scraper</button>
                    <button class="filter-btn" data-filter="generator">Generator</button>
                    <button class="filter-btn" data-filter="review">Review</button>
                    <button class="filter-btn" data-filter="publisher">Publisher</button>
                    <button class="filter-btn" data-filter="config">Config</button>
                    <button class="filter-btn" data-filter="scheduler">Scheduler</button>
                </div>
                
                <div class="stats">
                    <span id="resultsCount">53 endpoints encontrados</span> | 
                    <a href="/docs" style="color: var(--accent-blue);">Swagger UI</a> | 
                    <a href="/redoc" style="color: var(--accent-blue);">ReDoc</a> |
                    <a href="/" style="color: var(--accent-blue);">â† Dashboard</a>
                </div>
            </div>
            
            <div class="modules" id="modulesContainer">
                <!-- Sistema -->
                <div class="module" data-module="sistema">
                    <div class="module-header">
                        <span class="module-icon">ðŸ </span>
                        <div>
                            <div class="module-title">Sistema</div>
                            <div class="module-desc">Endpoints principais do sistema</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/" data-description="Dashboard principal dark mode responsivo">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/</span>
                            </div>
                            <div class="endpoint-desc">Dashboard principal do sistema com design dark mode Apple style</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/health" data-description="VerificaÃ§Ã£o de saÃºde completa do sistema">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/health</span>
                            </div>
                            <div class="endpoint-desc">Health check completo com status de todos os mÃ³dulos</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/api-docs" data-description="DocumentaÃ§Ã£o interativa com busca">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/api-docs</span>
                            </div>
                            <div class="endpoint-desc">DocumentaÃ§Ã£o interativa da API com campo de busca avanÃ§ado</div>
                        </div>
                    </div>
                </div>
                
                <!-- Scraper -->
                <div class="module" data-module="scraper">
                    <div class="module-header">
                        <span class="module-icon">ðŸ•·ï¸</span>
                        <div>
                            <div class="module-title">MÃ³dulo Scraper</div>
                            <div class="module-desc">ExtraÃ§Ã£o automatizada de produtos Creative CÃ³pias</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/scraper" data-description="Status detalhado scraper com estatÃ­sticas">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scraper</span>
                            </div>
                            <div class="endpoint-desc">Status e estatÃ­sticas completas do mÃ³dulo scraper</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scraper/test" data-description="Testar conexÃ£o Creative CÃ³pias">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scraper/test</span>
                            </div>
                            <div class="endpoint-desc">Teste de conectividade com o site alvo</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scraper/run" data-description="Executar scraping completo background">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scraper/run</span>
                            </div>
                            <div class="endpoint-desc">Scraping completo de todas as categorias em background</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scraper/run-single" data-description="Scraping categoria especÃ­fica">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scraper/run-single</span>
                            </div>
                            <div class="endpoint-desc">Executar scraping de uma categoria especÃ­fica</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scraper/stats" data-description="EstatÃ­sticas produtos processados">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scraper/stats</span>
                            </div>
                            <div class="endpoint-desc">MÃ©tricas e estatÃ­sticas de produtos processados</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scraper/cleanup" data-description="Limpeza dados antigos cache">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scraper/cleanup</span>
                            </div>
                            <div class="endpoint-desc">Limpeza de dados antigos e cache SQLite</div>
                        </div>
                    </div>
                </div>
                
                <!-- Generator -->
                <div class="module" data-module="generator">
                    <div class="module-header">
                        <span class="module-icon">âš™ï¸</span>
                        <div>
                            <div class="module-title">MÃ³dulo Generator</div>
                            <div class="module-desc">GeraÃ§Ã£o IA de conteÃºdo SEO otimizado</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/generator" data-description="Status generator OpenAI simulaÃ§Ã£o">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/generator</span>
                            </div>
                            <div class="endpoint-desc">Status do gerador com modo OpenAI/simulaÃ§Ã£o</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/generator/test" data-description="Teste geraÃ§Ã£o produto fictÃ­cio">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/generator/test</span>
                            </div>
                            <div class="endpoint-desc">Teste de geraÃ§Ã£o com produto fictÃ­cio para validaÃ§Ã£o</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/generator/generate" data-description="Gerar artigo SEO produto">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/generator/generate</span>
                            </div>
                            <div class="endpoint-desc">Gerar artigo SEO otimizado a partir de dados do produto</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/generator/stats" data-description="EstatÃ­sticas artigos gerados templates">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/generator/stats</span>
                            </div>
                            <div class="endpoint-desc">EstatÃ­sticas de artigos gerados e templates usados</div>
                        </div>
                    </div>
                </div>
                
                <!-- Review -->
                <div class="module" data-module="review">
                    <div class="module-header">
                        <span class="module-icon">ðŸ“</span>
                        <div>
                            <div class="module-title">Sistema Review</div>
                            <div class="module-desc">RevisÃ£o e aprovaÃ§Ã£o de artigos gerados</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/review" data-description="Status review artigos pendentes">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review</span>
                            </div>
                            <div class="endpoint-desc">Status do sistema com artigos pendentes/aprovados</div>
                        </div>
                        
                        <!-- Endpoint removido - usar /interface/review -->
                        
                        <div class="endpoint get" data-path="/review/stats" data-description="EstatÃ­sticas sistema revisÃ£o">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/stats</span>
                            </div>
                            <div class="endpoint-desc">EstatÃ­sticas completas do sistema de revisÃ£o</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/review/approved" data-description="Artigos aprovados prontos publicaÃ§Ã£o">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/approved</span>
                            </div>
                            <div class="endpoint-desc">Lista de artigos aprovados prontos para publicaÃ§Ã£o</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/review/{id}" data-description="Visualizar artigo especÃ­fico">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/{id}</span>
                            </div>
                            <div class="endpoint-desc">VisualizaÃ§Ã£o detalhada de artigo especÃ­fico</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/review/{id}/edit" data-description="Editor artigo inline">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/{id}/edit</span>
                            </div>
                            <div class="endpoint-desc">Interface de ediÃ§Ã£o inline com validaÃ§Ã£o SEO</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/{id}/update" data-description="Atualizar dados artigo">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/{id}/update</span>
                            </div>
                            <div class="endpoint-desc">Atualizar conteÃºdo e metadados do artigo</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/{id}/approve" data-description="Aprovar artigo publicaÃ§Ã£o">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/{id}/approve</span>
                            </div>
                            <div class="endpoint-desc">Aprovar artigo para publicaÃ§Ã£o no WordPress</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/{id}/reject" data-description="Rejeitar artigo motivo">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/{id}/reject</span>
                            </div>
                            <div class="endpoint-desc">Rejeitar artigo com motivo da rejeiÃ§Ã£o</div>
                        </div>
                        
                        <div class="endpoint delete" data-path="/review/{id}" data-description="Remover artigo sistema">
                            <div class="endpoint-header">
                                <span class="method delete">DELETE</span>
                                <span class="endpoint-path">/review/{id}</span>
                            </div>
                            <div class="endpoint-desc">Remover artigo permanentemente do sistema</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/save-from-generator" data-description="Salvar artigo gerado revisÃ£o">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/save-from-generator</span>
                            </div>
                            <div class="endpoint-desc">Endpoint interno para salvar artigos do Generator</div>
                        </div>
                    </div>
                </div>
                
                <!-- Publisher -->
                <div class="module" data-module="publisher">
                    <div class="module-header">
                        <span class="module-icon">ðŸ“¤</span>
                        <div>
                            <div class="module-title">MÃ³dulo Publisher</div>
                            <div class="module-desc">PublicaÃ§Ã£o automÃ¡tica WordPress REST API</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/publisher" data-description="Status publisher WordPress conexÃ£o">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher</span>
                            </div>
                            <div class="endpoint-desc">Status e teste de conexÃ£o com WordPress</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/test" data-description="Testar conexÃ£o WordPress API">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/test</span>
                            </div>
                            <div class="endpoint-desc">Teste de conectividade e autenticaÃ§Ã£o WordPress</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/publish" data-description="Publicar artigo aprovado WordPress">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/publish</span>
                            </div>
                            <div class="endpoint-desc">Publicar artigo aprovado no WordPress</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/list" data-description="Listar publicaÃ§Ãµes status">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/list</span>
                            </div>
                            <div class="endpoint-desc">Lista de publicaÃ§Ãµes com filtro por status</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/stats" data-description="EstatÃ­sticas publicaÃ§Ãµes WordPress">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/stats</span>
                            </div>
                            <div class="endpoint-desc">EstatÃ­sticas de publicaÃ§Ãµes e falhas</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/retry/{id}" data-description="Tentar republicar falha">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/retry/{id}</span>
                            </div>
                            <div class="endpoint-desc">Retry de publicaÃ§Ã£o que falhou</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/cleanup" data-description="Limpeza registros antigos">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/cleanup</span>
                            </div>
                            <div class="endpoint-desc">Limpeza de registros antigos de publicaÃ§Ã£o</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/categories" data-description="Categorias WordPress disponÃ­veis">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/categories</span>
                            </div>
                            <div class="endpoint-desc">Lista todas as categorias do WordPress</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/tags" data-description="Tags WordPress disponÃ­veis">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/tags</span>
                            </div>
                            <div class="endpoint-desc">Lista todas as tags do WordPress</div>
                        </div>
                    </div>
                </div>
                
                <!-- Config -->
                <div class="module" data-module="config">
                    <div class="module-header">
                        <span class="module-icon">âš™ï¸</span>
                        <div>
                            <div class="module-title">MÃ³dulo Config</div>
                            <div class="module-desc">ConfiguraÃ§Ãµes centralizadas com backup</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/config" data-description="Painel configuraÃ§Ãµes dark mode">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config</span>
                            </div>
                            <div class="endpoint-desc">Interface web de configuraÃ§Ãµes com design dark mode</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/config/data" data-description="Obter todas configuraÃ§Ãµes">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config/data</span>
                            </div>
                            <div class="endpoint-desc">Retorna todas as configuraÃ§Ãµes do sistema</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/update" data-description="Atualizar configuraÃ§Ãµes sistema">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/update</span>
                            </div>
                            <div class="endpoint-desc">Atualizar configuraÃ§Ãµes do sistema</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/config/export" data-description="Exportar configuraÃ§Ãµes JSON">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config/export</span>
                            </div>
                            <div class="endpoint-desc">Exportar todas as configuraÃ§Ãµes em JSON</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/import" data-description="Importar configuraÃ§Ãµes backup">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/import</span>
                            </div>
                            <div class="endpoint-desc">Importar configuraÃ§Ãµes de backup</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/backup" data-description="Criar backup configuraÃ§Ãµes">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/backup</span>
                            </div>
                            <div class="endpoint-desc">Criar backup automÃ¡tico das configuraÃ§Ãµes</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/config/stats" data-description="EstatÃ­sticas configuraÃ§Ãµes URLs">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config/stats</span>
                            </div>
                            <div class="endpoint-desc">EstatÃ­sticas de configuraÃ§Ãµes e URLs monitoradas</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/urls/add" data-description="Adicionar URL monitorada">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/urls/add</span>
                            </div>
                            <div class="endpoint-desc">Adicionar nova URL para monitoramento</div>
                        </div>
                        
                        <div class="endpoint delete" data-path="/config/urls/{id}" data-description="Remover URL monitorada">
                            <div class="endpoint-header">
                                <span class="method delete">DELETE</span>
                                <span class="endpoint-path">/config/urls/{id}</span>
                            </div>
                            <div class="endpoint-desc">Remover URL do monitoramento</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/templates/add" data-description="Adicionar template conteÃºdo">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/templates/add</span>
                            </div>
                            <div class="endpoint-desc">Adicionar novo template de conteÃºdo personalizado</div>
                        </div>
                    </div>
                </div>
                
                <!-- Scheduler -->
                <div class="module" data-module="scheduler">
                    <div class="module-header">
                        <span class="module-icon">â°</span>
                        <div>
                            <div class="module-title">Scheduler</div>
                            <div class="module-desc">AutomaÃ§Ã£o semanal domingos 10h</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/scheduler" data-description="Status agendamento prÃ³ximas execuÃ§Ãµes">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler</span>
                            </div>
                            <div class="endpoint-desc">Status e prÃ³ximas execuÃ§Ãµes do agendador semanal</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scheduler/status" data-description="Status detalhado jobs ativos">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler/status</span>
                            </div>
                            <div class="endpoint-desc">Status detalhado de todos os jobs configurados</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scheduler/run" data-description="Executar fluxo completo manual">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scheduler/run</span>
                            </div>
                            <div class="endpoint-desc">ExecuÃ§Ã£o manual do fluxo completo (scraping + geraÃ§Ã£o)</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scheduler/pause" data-description="Pausar todos jobs">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scheduler/pause</span>
                            </div>
                            <div class="endpoint-desc">Pausar temporariamente todos os jobs agendados</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scheduler/resume" data-description="Reativar todos jobs">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scheduler/resume</span>
                            </div>
                            <div class="endpoint-desc">Reativar execuÃ§Ã£o de todos os jobs pausados</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scheduler/next" data-description="PrÃ³ximas execuÃ§Ãµes 24h">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler/next</span>
                            </div>
                            <div class="endpoint-desc">Lista prÃ³ximas execuÃ§Ãµes nas prÃ³ximas 24 horas</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scheduler/history" data-description="HistÃ³rico execuÃ§Ãµes recentes">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler/history</span>
                            </div>
                            <div class="endpoint-desc">HistÃ³rico das execuÃ§Ãµes mais recentes</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="no-results hidden" id="noResults">
                <h3>ðŸ” Nenhum resultado encontrado</h3>
                <p>Tente ajustar sua busca ou filtros</p>
            </div>
        </div>
        
        <script>
            const searchInput = document.getElementById('searchInput');
            const filterBtns = document.querySelectorAll('.filter-btn');
            const modules = document.querySelectorAll('.module');
            const endpoints = document.querySelectorAll('.endpoint');
            const resultsCount = document.getElementById('resultsCount');
            const noResults = document.getElementById('noResults');
            const modulesContainer = document.getElementById('modulesContainer');
            
            let currentFilter = 'all';
            let currentSearch = '';
            
            // FunÃ§Ã£o de busca
            function performSearch() {
                const searchTerm = searchInput.value.toLowerCase();
                currentSearch = searchTerm;
                filterContent();
            }
            
            // FunÃ§Ã£o de filtro
            function filterContent() {
                let visibleCount = 0;
                
                modules.forEach(module => {
                    const moduleData = module.dataset.module.toLowerCase();
                    const moduleText = module.textContent.toLowerCase();
                    const moduleEndpoints = module.querySelectorAll('.endpoint');
                    
                    let hasVisibleEndpoints = false;
                    
                    moduleEndpoints.forEach(endpoint => {
                        const method = endpoint.querySelector('.method').textContent.toLowerCase();
                        const path = endpoint.dataset.path.toLowerCase();
                        const description = endpoint.dataset.description.toLowerCase();
                        const endpointText = endpoint.textContent.toLowerCase();
                        
                        // Verificar filtro de mÃ©todo
                        const matchesMethodFilter = currentFilter === 'all' || 
                                                  method === currentFilter || 
                                                  moduleData === currentFilter;
                        
                        // Verificar busca
                        const matchesSearch = currentSearch === '' ||
                                            path.includes(currentSearch) ||
                                            description.includes(currentSearch) ||
                                            endpointText.includes(currentSearch) ||
                                            moduleData.includes(currentSearch);
                        
                        if (matchesMethodFilter && matchesSearch) {
                            endpoint.style.display = 'block';
                            hasVisibleEndpoints = true;
                            visibleCount++;
                        } else {
                            endpoint.style.display = 'none';
                        }
                    });
                    
                    // Mostrar/ocultar mÃ³dulo baseado nos endpoints visÃ­veis
                    if (hasVisibleEndpoints) {
                        module.style.display = 'block';
                    } else {
                        module.style.display = 'none';
                    }
                });
                
                // Atualizar contador e mostrar/ocultar "sem resultados"
                
                if (visibleCount === 0) {
                    noResults.classList.remove('hidden');
                    modulesContainer.style.display = 'none';
                } else {
                    noResults.classList.add('hidden');
                    modulesContainer.style.display = 'grid';
                }
            }
            
            // Event listeners
            searchInput.addEventListener('input', performSearch);
            
            filterBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    // Remover classe active de todos os botÃµes
                    filterBtns.forEach(b => b.classList.remove('active'));
                    // Adicionar classe active ao botÃ£o clicado
                    btn.classList.add('active');
                    // Atualizar filtro atual
                    currentFilter = btn.dataset.filter;
                    // Aplicar filtro
                    filterContent();
                });
            });
            
            // Busca em tempo real com debounce
            let searchTimeout;
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(performSearch, 300);
            });
            
            // Atalhos de teclado
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + K para focar na busca
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    searchInput.focus();
                }
                
                // Escape para limpar busca
                if (e.key === 'Escape' && document.activeElement === searchInput) {
                    searchInput.value = '';
                    performSearch();
                }
            });
            
            // Inicializar contadores
            filterContent();
        </script>
    </body>
    </html>
    """)


# =====================================================
# FUNÃ‡Ã•ES AUXILIARES
# =====================================================

def _detect_product_type_from_name(product_name: str) -> str:
    """
    Detecta o tipo correto do produto baseado no nome para categorizaÃ§Ã£o WordPress correta
    ORDEM DE PRIORIDADE FIXA para evitar classificaÃ§Ãµes incorretas
    """
    try:
        if not product_name:
            return "generico"
        
        nome_lower = product_name.lower()
        
        # PRIORIDADE 1: Multifuncionais (ANTES de impressora)
        if ('multifuncional' in nome_lower or 'mfc' in nome_lower or 
            'dcp' in nome_lower or 'all-in-one' in nome_lower):
            return "multifuncional"
        
        # PRIORIDADE 2: CabeÃ§as de impressÃ£o (especÃ­fico)
        elif 'cabeÃ§a' in nome_lower and 'impressÃ£o' in nome_lower:
            return "cabeca_impressao"
        
        # PRIORIDADE 3: Cartuchos e tintas (SEM impressora)
        elif ('cartucho' in nome_lower or 'tinta' in nome_lower or 
              'refil' in nome_lower) and 'impressora' not in nome_lower:
            if 'toner' in nome_lower:
                return "toner"
            return "cartucho"
        
        # PRIORIDADE 4: Toners especÃ­ficos
        elif 'toner' in nome_lower:
            return "toner"
        
        # PRIORIDADE 5: PapÃ©is
        elif ('papel' in nome_lower or 'photo' in nome_lower or 
              'glossy' in nome_lower or 'matte' in nome_lower):
            return "papel"
        
        # PRIORIDADE 6: Scanners
        elif 'scanner' in nome_lower:
            return "scanner"
        
        # PRIORIDADE 7: Impressoras (por Ãºltimo)
        elif ('impressora' in nome_lower or 'printer' in nome_lower or
              'laserjet' in nome_lower or 'deskjet' in nome_lower):
            return "impressora"
        
        # DEFAULT: genÃ©rico
        else:
            return "generico"
            
    except Exception as e:
        logger.error(f"âŒ Erro ao detectar tipo do produto: {e}")
        return "generico"

# =====================================================
# ROTAS DO MÃ“DULO SCRAPER
# =====================================================

@app.get("/scraper")
async def scraper_status():
    """Status detalhado do mÃ³dulo de scraping"""
    if not SCRAPER_AVAILABLE:
        return {
            "module": "scraper",
            "status": "not_available",
            "message": "MÃ³dulo scraper nÃ£o foi importado corretamente",
            "dependencies": ["beautifulsoup4", "requests", "lxml"]
        }
    
    try:
        manager = ScraperManager()
        status_data = manager.get_scraping_status()
        
        return {
            "module": "scraper",
            "status": "ready",
            "description": "MÃ³dulo para extrair produtos do Creative CÃ³pias",
            "data": status_data,
            "actions": {
                "test_connection": "/scraper/test",
                "run_full_scraping": "/scraper/run",
                "run_single_category": "/scraper/run-single",
                "get_stats": "/scraper/stats",
                "cleanup": "/scraper/cleanup"
            }
        }
        
    except Exception as e:
        logger.error(f"âŒ Erro ao obter status do scraper: {e}")
        return {
            "module": "scraper",
            "status": "error",
            "message": str(e)
        }

@app.post("/scraper/test")
async def test_scraper_connection(request: ScrapingRequest = None):
    """Testa conexÃ£o com o site Creative CÃ³pias"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="MÃ³dulo scraper nÃ£o disponÃ­vel")
    
    try:
        manager = ScraperManager()
        test_url = request.url if request and request.url else None
        result = manager.test_connection(test_url)
        
        return result
        
    except Exception as e:
        logger.error(f"âŒ Erro no teste de conexÃ£o: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/run")
async def run_full_scraping(background_tasks: BackgroundTasks):
    """Executa scraping completo de todas as categorias"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="MÃ³dulo scraper nÃ£o disponÃ­vel")
    
    try:
        # Executar scraping em background para nÃ£o bloquear a API
        def run_scraping():
            manager = ScraperManager()
            # Para compatibilidade, manter limitaÃ§Ã£o de 100 produtos no endpoint padrÃ£o
            result = manager.run_full_scraping(max_products_per_category=100)
            
            # Atualizar contagens automaticamente apÃ³s o scraping
            try:
                from src.config.active_categories_manager import ActiveCategoriesManager
                cat_manager = ActiveCategoriesManager()
                cat_manager.update_products_count_from_scraper()
                logger.info("âœ… Contagens de produtos atualizadas automaticamente")
            except Exception as e:
                logger.warning(f"âš ï¸ Erro ao atualizar contagens automaticamente: {e}")
            
            return result
        
        background_tasks.add_task(run_scraping)
        
        return {
            "status": "started",
            "message": "Scraping completo iniciado em background",
            "check_status": "/scraper/stats"
        }
        
    except Exception as e:
        logger.error(f"âŒ Erro ao iniciar scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/run-single")
async def run_single_category_scraping(request: ScrapingRequest):
    """Executa scraping de uma categoria especÃ­fica"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="MÃ³dulo scraper nÃ£o disponÃ­vel")
    
    if not request.url:
        raise HTTPException(status_code=400, detail="URL Ã© obrigatÃ³ria")
    
    try:
        manager = ScraperManager()
        result = manager.run_single_category_scraping(request.url)
        
        return result
        
    except Exception as e:
        logger.error(f"âŒ Erro no scraping da categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/stats")
async def get_scraper_stats():
    """Retorna estatÃ­sticas do mÃ³dulo scraper"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="MÃ³dulo scraper nÃ£o disponÃ­vel")
    
    try:
        manager = ScraperManager()
        stats = manager.get_scraping_status()
        
        return stats
        
    except Exception as e:
        logger.error(f"âŒ Erro ao obter estatÃ­sticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/products")
async def get_scraped_products(limit: int = 100, offset: int = 0, categoria: str = None, search: str = None):
    """Retorna lista de produtos encontrados pelo scraper com pesquisa e filtros"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="MÃ³dulo scraper nÃ£o disponÃ­vel")
    
    try:
        import json
        import os
        import glob
        from datetime import datetime
        
        # TESTE: Usar lÃ³gica simplificada igual ao teste direto
        json_files = glob.glob("logs/products_*.json")
        
        if not json_files:
            return {
                "success": True,
                "products": [],
                "total": 0,
                "message": "Nenhum produto encontrado ainda. Execute uma busca primeiro."
            }
        
        # ðŸš¨ CORREÃ‡ÃƒO URGENTE: USAR MESMA LÃ“GICA CORRIGIDA DO URL_MANAGER
        logger.info(f"ðŸ” Encontrados {len(json_files)} arquivos para processar")
        
        # CORREÃ‡ÃƒO: Identificar arquivos Ãºnicos (preferir _CORRIGIDO)
        categoria_files = {}
        for json_file in json_files:
            filename = os.path.basename(json_file)
            categoria_key = filename.replace('products_', '').split('_')[0]
            
            if 'CORRIGIDO' in filename:
                # Arquivo corrigido tem prioridade
                categoria_files[categoria_key] = json_file
            elif categoria_key not in categoria_files:
                # Primeiro arquivo desta categoria
                categoria_files[categoria_key] = json_file
            # Ignorar arquivos duplicados
        
        logger.info(f"ðŸ“Š CORREÃ‡ÃƒO APLICADA: {len(categoria_files)} categorias Ãºnicas (eliminando duplicatas)")
        
        # Mapeamento de categorias
        categorias_mapeamento = {
            'cartuchos-de-tinta': 'Cartuchos de Tinta',
            'cartuchos-de-toner': 'Cartuchos de Toner', 
            'refil-de-toner': 'Refil de Toner',
            'impressoras': 'Impressoras',
            'multifuncional': 'Multifuncionais',
            'plotters': 'Plotters',
            'suprimentos': 'Suprimentos'
        }
        
        all_products = []
        unique_products = set()  # Para contar produtos Ãºnicos
        
        for categoria_key in sorted(categoria_files.keys()):
            json_file = categoria_files[categoria_key]
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            filename = os.path.basename(json_file)
            categoria_nome = categorias_mapeamento.get(categoria_key, categoria_key.title())
            
            if isinstance(data, list):
                for product in data:
                    product['categoria_key'] = categoria_key
                    product['categoria_nome'] = categoria_nome
                    product['source_file'] = filename
                    all_products.append(product)
                    # Contar produtos Ãºnicos
                    if product.get('nome'):
                        unique_products.add(product['nome'])
            elif isinstance(data, dict) and 'produtos' in data:
                for product in data['produtos']:
                    product['categoria_key'] = categoria_key
                    product['categoria_nome'] = categoria_nome
                    product['source_file'] = filename
                    all_products.append(product)
                    # Contar produtos Ãºnicos
                    if product.get('nome'):
                        unique_products.add(product['nome'])
            
            logger.info(f"âœ… {categoria_key}: carregado de {filename}")
            
        logger.info(f"ðŸ“Š CORREÃ‡ÃƒO CRÃTICA: {len(unique_products)} produtos Ãºnicos de {len(categoria_files)} categorias (era {len(all_products)} incluindo duplicatas)")
        
        # Aplicar filtro de categoria com COMPARAÃ‡ÃƒO EXATA
        if categoria and categoria.lower() != 'todas':
            filtered = []
            filtered_unique = set()
            for product in all_products:
                if categoria.lower() == product.get('categoria_key', '').lower():
                    filtered.append(product)
                    if product.get('nome'):
                        filtered_unique.add(product['nome'])
            all_products = filtered
            unique_products = filtered_unique  # Atualizar produtos Ãºnicos para filtro
            logger.info(f"ðŸ” Filtro '{categoria}': {len(filtered_unique)} produtos Ãºnicos (de {len(all_products)} total)")
        
        # ðŸš¨ CORREÃ‡ÃƒO CRÃTICA: IMPLEMENTAR PESQUISA QUE ESTAVA FALTANDO!
        if search and search.strip():
            search_term = search.strip().lower()
            filtered_by_search = []
            filtered_unique_search = set()
            
            for product in all_products:
                # Garantir que os campos nÃ£o sejam None antes de chamar .lower()
                nome = (product.get('nome') or '').lower()
                marca = (product.get('marca') or '').lower()
                codigo = (product.get('codigo') or '').lower()
                descricao = (product.get('descricao') or '').lower()
                
                # Buscar em nome, marca, cÃ³digo e descriÃ§Ã£o
                if (search_term in nome or 
                    search_term in marca or 
                    search_term in codigo or 
                    search_term in descricao):
                    filtered_by_search.append(product)
                    if product.get('nome'):
                        filtered_unique_search.add(product['nome'])
            
            all_products = filtered_by_search
            unique_products = filtered_unique_search
            logger.info(f"ðŸ” Pesquisa '{search}': {len(filtered_unique_search)} produtos Ãºnicos encontrados")
        
        # ðŸš¨ CORREÃ‡ÃƒO: Usar contagem de produtos Ãºnicos, nÃ£o lista bruta com duplicatas
        total_products_unique = len(unique_products)  # REAL: produtos Ãºnicos
        start_idx = offset
        end_idx = offset + limit
        paginated_products = all_products[start_idx:end_idx]
        
        # Formatar produtos - CORREÃ‡ÃƒO CRÃTICA: INCLUIR IMAGEM!
        products = []
        for product in paginated_products:
            products.append({
                'id': product.get('id', product.get('nome', '')),
                'nome': product.get('nome', ''),
                'url': product.get('url', ''),
                'imagem': product.get('imagem', ''),  # ðŸš¨ CORREÃ‡ÃƒO: Campo imagem estava faltando!
                'categoria_key': product.get('categoria_key', ''),
                'categoria_nome': product.get('categoria_nome', ''),
                'categoria_url': product.get('categoria_url', ''),
                'preco': product.get('preco', ''),
                'marca': product.get('marca', ''),  # ðŸš¨ CORREÃ‡ÃƒO: Campo marca tambÃ©m estava faltando!
                'codigo': product.get('codigo', ''),  # ðŸš¨ CORREÃ‡ÃƒO: Campo codigo tambÃ©m estava faltando!
                'descricao': product.get('descricao', ''),  # ðŸš¨ CORREÃ‡ÃƒO: Campo descricao tambÃ©m estava faltando!
                'disponivel': product.get('disponivel', True),
                'source_file': product.get('source_file', ''),
                'data_processed': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return {
            "success": True,
            "products": products,
            "total": total_products_unique,  # ðŸš¨ CORREÃ‡ÃƒO: usar contagem Ãºnica
            "limit": limit,
            "offset": offset,
            "categoria_filtro": categoria,
            "search_filtro": search,
            "produtos_brutos": len(all_products),  # Para debug: total com duplicatas
            "produtos_unicos": total_products_unique,  # Para debug: total real
            "message": f"âœ… CORRIGIDO: {len(products)} produtos (de {total_products_unique} Ãºnicos) - {'com pesquisa' if search else 'sem duplicatas'}!"
        }

        
    except Exception as e:
        logger.error(f"âŒ Erro ao obter produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/categories")
async def get_scraper_categories():
    """Retorna lista de categorias disponÃ­veis nos produtos"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="MÃ³dulo scraper nÃ£o disponÃ­vel")
    
    try:
        from src.config.active_categories_manager import ActiveCategoriesManager
        
        # Usar o manager para obter categorias ativas com contagens atualizadas
        manager = ActiveCategoriesManager()
        categories_data = manager.get_all_categories()
        
        # Transformar para o formato esperado pelo frontend
        categorias_lista = []
        for cat in categories_data:
            if cat.get('is_active', True):  # Apenas categorias ativas
                categorias_lista.append({
                    'key': cat['category_key'],
                    'name': cat['category_name'],
                    'count': cat.get('products_count', 0),
                    'url': cat['category_url']
                })
        
        # Ordenar por nome
        categorias_lista.sort(key=lambda x: x['name'])
        
        return {
            "success": True,
            "categories": categorias_lista,
            "total": len(categorias_lista),
            "message": f"Encontradas {len(categorias_lista)} categorias ativas"
        }
        
    except Exception as e:
        logger.error(f"âŒ Erro ao obter categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/generate-article-advanced")
async def generate_advanced_article_from_product(product_data: dict, allow_duplicates: bool = False):
    """Gera artigo super completo usando templates avanÃ§ados"""
    
    # ðŸ”§ NORMALIZAR FORMATO DOS DADOS - aceitar tanto 'nome' quanto 'productName'
    if 'productName' in product_data and 'nome' not in product_data:
        product_data['nome'] = product_data['productName']
    
    # Garantir campos mÃ­nimos sempre (REMOVIDO busca desnecessÃ¡ria que causava erro 500)
    produto_nome = product_data.get('nome', 'Produto')
    
    # Garantir que temos todos os campos necessÃ¡rios
    default_values = {
        'categoria_nome': 'produtos',
        'preco': 'Consulte',
        'codigo': 'N/A',
        'marca': 'N/A',
        'descricao': f'Produto {produto_nome} de qualidade disponÃ­vel em nossa loja.',
        'url': '#',
        'imagem': ''
    }
    
    # Aplicar defaults apenas para campos ausentes ou vazios
    for key, default_value in default_values.items():
        if not product_data.get(key):
            product_data[key] = default_value
    
    logger.info(f"ðŸŽ¨ Gerando artigo avanÃ§ado para: {product_data.get('nome', 'Produto')}")
    
    try:
        if not REVIEW_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de revisÃ£o nÃ£o disponÃ­vel")
        
        # Detectar tipo do produto (sem exibir sugestÃµes da IA para o usuÃ¡rio)
        produto_nome = product_data.get('nome', '')
        tipo_produto_detectado = _detect_product_type_from_name(produto_nome)
        categoria = tipo_produto_detectado
        
        # Usar o ReviewManager adequado
        from src.review.review_manager import ReviewManager
        review_manager = ReviewManager()
        
        # ðŸŽ¨ USAR SISTEMA AVANÃ‡ADO DE TEMPLATES (com fallback)
        try:
            from src.generator.article_templates import AdvancedArticleTemplates
            template_generator = AdvancedArticleTemplates()
            
            # Gerar artigo super completo
            logger.info(f"ðŸ”§ Dados para geraÃ§Ã£o: nome={product_data.get('nome', 'N/A')}, categoria={categoria}")
            advanced_article = template_generator.generate_advanced_article(product_data, categoria)
            
        except ImportError as template_error:
            logger.warning(f"âš ï¸ Template avanÃ§ado nÃ£o disponÃ­vel: {template_error}")
            # Fallback para template simples
            advanced_article = {
                'titulo': f"Review: {product_data.get('nome', 'Produto')}",
                'slug': product_data.get('nome', 'produto').lower().replace(' ', '-'),
                'meta_descricao': f"Review completo do {product_data.get('nome', 'produto')}",
                            'conteudo': f"""<h2>InformaÃ§Ãµes do Produto</h2>
<p>Este Ã© um produto de qualidade disponÃ­vel em nossa loja.</p>

<h3>CaracterÃ­sticas</h3>
<ul>
<li>Categoria: {categoria}</li>
<li>PreÃ§o: {product_data.get('preco', 'Consulte')}</li>
<li>CÃ³digo: {product_data.get('codigo', 'N/A')}</li>
<li>Marca: {product_data.get('marca', 'N/A')}</li>
</ul>

<p><a href="{product_data.get('url', '#')}" target="_blank">Ver produto no site</a></p>""",
                'tags': [categoria, 'produtos']
            }
        except Exception as template_gen_error:
            logger.error(f"âŒ Erro na geraÃ§Ã£o do template: {template_gen_error}")
            raise Exception(f"Falha na geraÃ§Ã£o do artigo: {template_gen_error}")
        
        if not advanced_article:
            raise Exception("Falha na geraÃ§Ã£o do artigo pelo template")
        
        # Sem sugestÃµes da IA para o usuÃ¡rio
        conteudo_extra = ""
        
        # Preparar dados do artigo para o ReviewManager
        article_data = {
            'titulo': advanced_article['titulo'],
            'slug': advanced_article['slug'],
            'meta_descricao': advanced_article['meta_descricao'],
            'conteudo': conteudo_extra + advanced_article['conteudo'],
            'tags': advanced_article['tags'],
            'wp_category': categoria,
            'produto_original': product_data.get('nome', ''),
            'produto_nome': product_data.get('nome', ''),
            'tipo_produto': tipo_produto_detectado,
            'tom_usado': 'profissional',
            'status': 'pendente'
        }
        
        # ðŸ” VERIFICAÃ‡ÃƒO INTELIGENTE DE DUPLICATAS (ignora artigos rejeitados)
        if not allow_duplicates:
            existing_article = review_manager.check_product_has_non_rejected_article(produto_nome)
            
            if existing_article:
                logger.warning(f"ðŸ”„ Artigo nÃ£o rejeitado jÃ¡ existe para {produto_nome}")
                raise HTTPException(
                    status_code=409,  # Conflict
                    detail={
                        "success": False,
                        "error": "duplicate_detected",
                        "message": f"Artigo para '{produto_nome}' jÃ¡ existe (Status: {existing_article['status']})",
                        "suggestion": "ðŸ’¡ Use o botÃ£o 'ForÃ§ar Novo' para criar mesmo assim",
                        "existing_article_id": existing_article['id'],
                        "action": "redirect_to_existing"
                    }
                )
        
        # Log interno sobre histÃ³rico (sem exibir para o usuÃ¡rio)
        rejection_history = review_manager.get_rejection_history_for_product(produto_nome)
        if rejection_history:
            logger.warning(f"âš ï¸ ATENÃ‡ÃƒO: {produto_nome} tem {len(rejection_history)} rejeiÃ§Ãµes anteriores - melhorando internamente")
        
        # Salvar usando o ReviewManager (sempre permite agora, jÃ¡ foi verificado acima)
        try:
            article_id = review_manager.save_article_for_review(article_data, allow_duplicates=True)
        except Exception as save_error:
            logger.error(f"âŒ Erro ao salvar artigo: {save_error}")
            raise Exception(f"Falha ao salvar artigo: {save_error}")
        
        if article_id:
            logger.info(f"âœ… Artigo avanÃ§ado salvo com ID: {article_id}")
            
            response_data = {
                "success": True,
                "article_id": article_id,
                "article": advanced_article,  # CORREÃ‡ÃƒO: Incluir o artigo na resposta
                "message": f"Artigo avanÃ§ado criado e enviado para revisÃ£o com sucesso!",
                "produto": product_data.get('nome', ''),
                "categoria": product_data.get('categoria_nome', ''),
                "allow_duplicates": allow_duplicates,
                "template_type": "advanced"
            }
            
            # Adicionar informaÃ§Ãµes de aprendizado se houver
            # Log interno (sem expor para usuÃ¡rio)
            if has_rejections:
                logger.info(f"âœ… Sistema aplicado silenciosamente para {produto_nome}")



            
            return response_data
        else:
            raise Exception("Falha ao salvar artigo no sistema de revisÃ£o")
        
    except HTTPException:
        # Re-raise HTTPException para manter o status code correto
        raise
    except Exception as e:
        logger.error(f"âŒ Erro ao gerar artigo avanÃ§ado: {e}")
        import traceback
        logger.error(f"âŒ Traceback: {traceback.format_exc()}")
        
        # Retornar erro estruturado para o JavaScript
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "Erro ao criar artigo avanÃ§ado",
                "suggestion": "ðŸ’¡ Tente adicionar ?allow_duplicates=true na URL se quiser forÃ§ar a criaÃ§Ã£o",
                "error_type": "generation_error"
            }
        )

@app.post("/scraper/generate-article")
async def generate_article_from_product(product_data: dict, allow_duplicates: bool = False):
    """Gera artigo a partir de dados do produto com sistema inteligente integrado"""
    
    logger.info(f"ðŸ¤– Gerando artigo inteligente para produto: {product_data.get('nome', 'Produto')}")
    
    try:
        if not REVIEW_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de revisÃ£o nÃ£o disponÃ­vel")
        
        # ðŸ§  SISTEMA INTELIGENTE - VERIFICAR STATUS DO PRODUTO (com fallback)
        product_status = {'status': 'clean'}  # Fallback padrÃ£o
        
        learning_manager = None  # Inicializar como None
        
        try:
            from src.intelligence.learning_manager import LearningManager
            learning_manager = LearningManager()
            product_status = learning_manager.check_product_status(product_data)
        except ImportError:
            logger.debug("ðŸ’¡ Sistema de aprendizado nÃ£o disponÃ­vel, continuando sem inteligÃªncia")
        except Exception as learning_error:
            logger.warning(f"âš ï¸ Erro no sistema de aprendizado: {learning_error}")
        
        # 1. REDIRECIONAR SE JÃ EXISTE ARTIGO PENDENTE
        if product_status['status'] == 'has_pending':
            logger.info(f"ðŸ“‹ Redirecionando para artigo pendente: {product_status['article_id']}")
            return {
                "success": True,
                "action": "redirect",
                "redirect_to": product_status['redirect_url'],
                "article_id": product_status['article_id'],
                "message": product_status['message'],
                "article_title": product_status['article_title'],
                "recommendation": "ðŸ‘† Revise o artigo existente ao invÃ©s de criar um novo"
            }
        
        # 2. GERAR CONTEÃšDO COM MELHORIAS DA IA
        produto_nome = product_data.get('nome', '')
        tipo_produto_detectado = _detect_product_type_from_name(produto_nome)
        categoria = tipo_produto_detectado
        
        # Criar conteÃºdo base
        titulo = f"Review: {produto_nome}"
        slug = produto_nome.lower().replace(' ', '-').replace(':', '').replace(',', '')
        
        conteudo_base = f"""<h2>InformaÃ§Ãµes do Produto</h2>
<ul>
<li><strong>Categoria:</strong> {categoria}</li>
<li><strong>PreÃ§o:</strong> {product_data.get('preco', 'Consulte')}</li>
<li><strong>CÃ³digo:</strong> {product_data.get('codigo', 'N/A')}</li>
<li><strong>Marca:</strong> {product_data.get('marca', 'N/A')}</li>
</ul>

<h2>DescriÃ§Ã£o</h2>
<p>{product_data.get('descricao', 'Produto de qualidade disponÃ­vel em nossa loja.')}</p>

<h2>CaracterÃ­sticas</h2>
<p>Este produto oferece excelente qualidade e desempenho para suas necessidades.</p>

<h3>Vantagens</h3>
<ul>
<li>Qualidade superior</li>
<li>Ã“timo custo-benefÃ­cio</li>
<li>Entrega rÃ¡pida</li>
