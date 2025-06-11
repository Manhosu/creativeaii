"""
Sistema de Geração Automática de Conteúdo SEO
Arquivo principal do FastAPI
"""

# -*- coding: utf-8 -*-
import os
import sys
import asyncio
from pathlib import Path

# Adicionar paths absolutos para importações
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

# Importar loguru logo no início
from loguru import logger

# Carregar variáveis de ambiente do arquivo .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Definir variáveis padrão se não existirem
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('OPENAI_MODEL', 'gpt-4o-mini')
os.environ.setdefault('OPENAI_MAX_TOKENS', '2000')
os.environ.setdefault('OPENAI_TEMPERATURE', '0.7')
os.environ.setdefault('CONTENT_MIN_WORDS', '300')
os.environ.setdefault('CONTENT_MAX_WORDS', '1000')

# Configurar outras variáveis importantes
os.environ['PORT'] = '3025'  # FORÇAR porta 3025
os.environ.setdefault('OPENAI_MODEL', 'gpt-4o-mini')

# Não definir chave de API aqui - deve vir do .env
if not os.getenv('OPENAI_API_KEY'):
    logger.warning("⚠️ OPENAI_API_KEY não encontrada nas variáveis de ambiente")
if not os.getenv('WP_PASSWORD'):
    logger.warning("⚠️ WP_PASSWORD não encontrada nas variáveis de ambiente")

# Configurar variáveis de ambiente essenciais - valores devem vir do .env
os.environ.setdefault('WORDPRESS_URL', 'https://blog.creativecopias.com.br/wp-json/wp/v2/')
os.environ.setdefault('WORDPRESS_USERNAME', 'api_seo_bot')
# WP_PASSWORD deve vir do .env - não definir aqui
os.environ.setdefault('WP_SITE_URL', 'https://blog.creativecopias.com.br')
os.environ.setdefault('WP_USERNAME', 'api_seo_bot')
# WP_PASSWORD deve vir do .env - não definir aqui
os.environ.setdefault('WP_AUTO_PUBLISH', 'true')
os.environ.setdefault('WP_DEFAULT_CATEGORY', 'geral')

# Log das variáveis carregadas
print(f"🔧 Configurações carregadas:")
print(f"   PORT: {os.getenv('PORT')}")
print(f"   WP_SITE_URL: {os.getenv('WP_SITE_URL')}")
print(f"   WP_USERNAME: {os.getenv('WP_USERNAME')}")
print(f"   OPENAI_API_KEY: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') else '❌ Não encontrada'}")
print(f"   OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")

# Configurações WordPress vêm das variáveis de ambiente
# Não forçar valores hardcoded aqui

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

# Importar módulo scraper
try:
    from src.scraper.scraper_manager import ScraperManager
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    logger.warning("⚠️ Módulo scraper não disponível")

# Importar módulo generator
try:
    from src.generator.generator_manager import GeneratorManager
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    logger.warning("⚠️ Módulo generator não disponível")

# Importar módulo review
try:
    from src.review.review_manager import ReviewManager
    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False
    logger.warning("⚠️ Módulo review não disponível")

# Importar módulo publisher
try:
    from src.publisher.publication_manager import PublicationManager
    PUBLISHER_AVAILABLE = True
except ImportError:
    PUBLISHER_AVAILABLE = False
    logger.warning("⚠️ Módulo publisher não disponível")

# Importar módulo config
try:
    from src.config.config_manager import ConfigManager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("⚠️ Módulo config não disponível")

# Importar módulo scheduler
try:
    from src.scheduler.scheduler_manager import SchedulerManager
    SCHEDULER_AVAILABLE = True
    logger.info("✅ Módulo scheduler carregado com sucesso")
except ImportError as e:
    SCHEDULER_AVAILABLE = False
    logger.warning(f"⚠️ Módulo scheduler não disponível: {e}")

# Importar módulos de inteligência
try:
    from src.intelligence.priority_manager import PriorityManager
    from src.intelligence.publication_monitor import PublicationMonitor
    INTELLIGENCE_AVAILABLE = True
    logger.info("✅ Módulos de inteligência carregados com sucesso")
except ImportError as e:
    INTELLIGENCE_AVAILABLE = False
    logger.warning(f"⚠️ Módulos de inteligência não disponíveis: {e}")

# Importar módulo de categorias ativas
try:
    from src.config.active_categories_manager import ActiveCategoriesManager
    CATEGORIES_AVAILABLE = True
    logger.info("✅ Módulo de categorias ativas carregado com sucesso")
except ImportError as e:
    CATEGORIES_AVAILABLE = False
    logger.warning(f"⚠️ Módulo de categorias ativas não disponível: {e}")

# Configurações
APP_NAME = "Sistema de Geração Automática de Conteúdo SEO"
APP_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", 3025))

# Configuração de logs
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
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando Sistema de Geração de Conteúdo SEO")
    
    # Inicialização
    try:
        # Criar diretórios necessários
        os.makedirs("logs", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        os.makedirs("templates", exist_ok=True)
        
        logger.info("📁 Diretórios criados com sucesso")
        
        # Inicializar banco de dados
        # await init_database()
        
        # Inicializar scheduler automático
        if SCHEDULER_AVAILABLE:
            try:
                global scheduler_manager
                # Determinar URL base para o scheduler
                scheduler_base_url = (
                    os.getenv('SCHEDULER_BASE_URL') or 
                    os.getenv('SYSTEM_BASE_URL') or 
                    f"http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '3025')}"
                )
                logger.info(f"⏰ Inicializando scheduler com URL base: {scheduler_base_url}")
                
                scheduler_manager = SchedulerManager(base_url=scheduler_base_url)
                scheduler_manager.start()
                logger.info("⏰ Scheduler iniciado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar scheduler: {e}")
        
        logger.info("✅ Aplicação iniciada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    yield
    
    # Finalização
    logger.info("🛑 Finalizando aplicação")
    
    # Parar scheduler se estiver rodando
    if SCHEDULER_AVAILABLE and 'scheduler_manager' in globals():
        try:
            scheduler_manager.stop()
            logger.info("⏰ Scheduler parado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao parar scheduler: {e}")


# Criação da aplicação FastAPI
app = FastAPI(
    title=APP_NAME,
    description="Sistema automatizado para geração de conteúdo SEO baseado em produtos de e-commerce",
    version=APP_VERSION,
    docs_url=None,
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Customização do Swagger UI com CSS e JavaScript
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Swagger UI customizado com busca e tema dark"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
        <link rel="shortcut icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚙️</text></svg>">
        <title>Sistema de Geração de Conteúdo SEO - Documentação API</title>
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
            
            /* Estilização das operações */
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
            
            /* Ocultar operações filtradas */
            .swagger-ui .opblock.hidden-by-search {
                display: none !important;
            }
            
            .swagger-ui .opblock-tag.hidden-by-search {
                display: none !important;
            }
            
            /* Botão de voltar ao dashboard */
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
                <input type="text" id="apiSearch" class="search-input" placeholder="🔍 Buscar endpoints, operações ou descrições...">
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
        <a href="/" class="back-to-dashboard">← Dashboard</a>
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
            
            // JavaScript para funcionalidade de busca avançada
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
                    
                    // Filtros por método
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
                    
                    // Ocultar seções vazias
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
                    searchStats.textContent = `${count} de ${total} endpoints encontrados`;
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

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de arquivos estáticos e templates
templates = None
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    if os.path.exists("templates"):
        templates = Jinja2Templates(directory="templates")
    logger.info("✅ Arquivos estáticos e templates configurados")
except Exception as e:
    logger.warning(f"⚠️ Não foi possível configurar arquivos estáticos: {e}")
    templates = None


# =====================================================
# CUSTOMIZAÇÃO DO OPENAPI
# =====================================================

def custom_openapi():
    """Geração customizada do OpenAPI para compatibilidade com Swagger UI"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        description="Sistema automatizado para geração de conteúdo SEO baseado em produtos de e-commerce",
        routes=app.routes,
    )
    
    # Forçar versão 3.0.0 para compatibilidade com Swagger UI
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
                <title>Sistema de Geração Automática de Conteúdo</title>
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
                                <h1>Sistema de Geração Automática de Conteúdo</h1>
                            </div>
                            

                            
                            <div class="main-actions">
                                <div class="action-card">
                                    <span class="action-icon">🔍</span>
                                    <h3 class="action-title">Scraper</h3>
                                    <p class="action-desc">Busca de produtos e categorias de sites e-commerce</p>
                                    <a href="/interface/scraper" class="action-btn">
                                        <span>Acessar</span>
                                        <span>→</span>
                                    </a>
                                </div>
                                
                                <div class="action-card">
                                    <span class="action-icon">📝</span>
                                    <h3 class="action-title">Revisão</h3>
                                    <p class="action-desc">Revise e gerencie artigos antes da publicação</p>
                                    <a href="/interface/review" class="action-btn success-btn">
                                        <span>Acessar</span>
                                        <span>→</span>
                                    </a>
                                </div>
                                
                                <div class="action-card">
                                    <span class="action-icon">⚙️</span>
                                    <h3 class="action-title">Configurações</h3>
                                    <p class="action-desc">Painel de configuração geral do sistema</p>
                                    <a href="/config" class="action-btn warning-btn">
                                        <span>Acessar</span>
                                        <span>→</span>
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
    """Verificação de saúde do sistema"""
    modules_status = {
        "scraper": "ready" if SCRAPER_AVAILABLE else "not_available",
        "generator": "ready" if GENERATOR_AVAILABLE else "not_available", 
        "review": "ready" if REVIEW_AVAILABLE else "not_available",
        "publisher": "ready" if PUBLISHER_AVAILABLE else "not_available",
        "config": "ready" if CONFIG_AVAILABLE else "not_available",
        "scheduler": "ready" if SCHEDULER_AVAILABLE else "not_available"
    }
    
    # Verificar status do scraper se disponível
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
    
    # Verificar status do generator se disponível
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
    
    # Verificar status do review se disponível
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
    
    # Verificar status do publisher se disponível
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
    
    # Verificar status do scheduler se disponível
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
    """Documentação interativa da API com campo de busca"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Documentação da API - Sistema SEO</title>
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
            <h1>📚 Documentação da API</h1>
            <p>Sistema de Geração Automática de Conteúdo SEO</p>
        </div>
        
        <div class="container">
            <div class="search-section">
                <div class="search-box">
                    <input type="text" class="search-input" placeholder="🔍 Buscar endpoints, módulos ou funcionalidades..." id="searchInput">
                    <span class="search-icon">🔍</span>
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
                    <a href="/" style="color: var(--accent-blue);">← Dashboard</a>
                </div>
            </div>
            
            <div class="modules" id="modulesContainer">
                <!-- Sistema -->
                <div class="module" data-module="sistema">
                    <div class="module-header">
                        <span class="module-icon">🏠</span>
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
                        
                        <div class="endpoint get" data-path="/health" data-description="Verificação de saúde completa do sistema">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/health</span>
                            </div>
                            <div class="endpoint-desc">Health check completo com status de todos os módulos</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/api-docs" data-description="Documentação interativa com busca">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/api-docs</span>
                            </div>
                            <div class="endpoint-desc">Documentação interativa da API com campo de busca avançado</div>
                        </div>
                    </div>
                </div>
                
                <!-- Scraper -->
                <div class="module" data-module="scraper">
                    <div class="module-header">
                        <span class="module-icon">🕷️</span>
                        <div>
                            <div class="module-title">Módulo Scraper</div>
                            <div class="module-desc">Extração automatizada de produtos Creative Cópias</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/scraper" data-description="Status detalhado scraper com estatísticas">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scraper</span>
                            </div>
                            <div class="endpoint-desc">Status e estatísticas completas do módulo scraper</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/scraper/test" data-description="Testar conexão Creative Cópias">
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
                        
                        <div class="endpoint post" data-path="/scraper/run-single" data-description="Scraping categoria específica">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/scraper/run-single</span>
                            </div>
                            <div class="endpoint-desc">Executar scraping de uma categoria específica</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scraper/stats" data-description="Estatísticas produtos processados">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scraper/stats</span>
                            </div>
                            <div class="endpoint-desc">Métricas e estatísticas de produtos processados</div>
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
                        <span class="module-icon">⚙️</span>
                        <div>
                            <div class="module-title">Módulo Generator</div>
                            <div class="module-desc">Geração IA de conteúdo SEO otimizado</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/generator" data-description="Status generator OpenAI simulação">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/generator</span>
                            </div>
                            <div class="endpoint-desc">Status do gerador com modo OpenAI/simulação</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/generator/test" data-description="Teste geração produto fictício">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/generator/test</span>
                            </div>
                            <div class="endpoint-desc">Teste de geração com produto fictício para validação</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/generator/generate" data-description="Gerar artigo SEO produto">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/generator/generate</span>
                            </div>
                            <div class="endpoint-desc">Gerar artigo SEO otimizado a partir de dados do produto</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/generator/stats" data-description="Estatísticas artigos gerados templates">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/generator/stats</span>
                            </div>
                            <div class="endpoint-desc">Estatísticas de artigos gerados e templates usados</div>
                        </div>
                    </div>
                </div>
                
                <!-- Review -->
                <div class="module" data-module="review">
                    <div class="module-header">
                        <span class="module-icon">📝</span>
                        <div>
                            <div class="module-title">Sistema Review</div>
                            <div class="module-desc">Revisão e aprovação de artigos gerados</div>
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
                        
                        <div class="endpoint get" data-path="/review/stats" data-description="Estatísticas sistema revisão">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/stats</span>
                            </div>
                            <div class="endpoint-desc">Estatísticas completas do sistema de revisão</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/review/approved" data-description="Artigos aprovados prontos publicação">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/approved</span>
                            </div>
                            <div class="endpoint-desc">Lista de artigos aprovados prontos para publicação</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/review/{id}" data-description="Visualizar artigo específico">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/{id}</span>
                            </div>
                            <div class="endpoint-desc">Visualização detalhada de artigo específico</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/review/{id}/edit" data-description="Editor artigo inline">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/review/{id}/edit</span>
                            </div>
                            <div class="endpoint-desc">Interface de edição inline com validação SEO</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/{id}/update" data-description="Atualizar dados artigo">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/{id}/update</span>
                            </div>
                            <div class="endpoint-desc">Atualizar conteúdo e metadados do artigo</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/{id}/approve" data-description="Aprovar artigo publicação">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/{id}/approve</span>
                            </div>
                            <div class="endpoint-desc">Aprovar artigo para publicação no WordPress</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/{id}/reject" data-description="Rejeitar artigo motivo">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/review/{id}/reject</span>
                            </div>
                            <div class="endpoint-desc">Rejeitar artigo com motivo da rejeição</div>
                        </div>
                        
                        <div class="endpoint delete" data-path="/review/{id}" data-description="Remover artigo sistema">
                            <div class="endpoint-header">
                                <span class="method delete">DELETE</span>
                                <span class="endpoint-path">/review/{id}</span>
                            </div>
                            <div class="endpoint-desc">Remover artigo permanentemente do sistema</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/review/save-from-generator" data-description="Salvar artigo gerado revisão">
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
                        <span class="module-icon">📤</span>
                        <div>
                            <div class="module-title">Módulo Publisher</div>
                            <div class="module-desc">Publicação automática WordPress REST API</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/publisher" data-description="Status publisher WordPress conexão">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher</span>
                            </div>
                            <div class="endpoint-desc">Status e teste de conexão com WordPress</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/test" data-description="Testar conexão WordPress API">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/test</span>
                            </div>
                            <div class="endpoint-desc">Teste de conectividade e autenticação WordPress</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/publish" data-description="Publicar artigo aprovado WordPress">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/publish</span>
                            </div>
                            <div class="endpoint-desc">Publicar artigo aprovado no WordPress</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/list" data-description="Listar publicações status">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/list</span>
                            </div>
                            <div class="endpoint-desc">Lista de publicações com filtro por status</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/stats" data-description="Estatísticas publicações WordPress">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/stats</span>
                            </div>
                            <div class="endpoint-desc">Estatísticas de publicações e falhas</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/retry/{id}" data-description="Tentar republicar falha">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/retry/{id}</span>
                            </div>
                            <div class="endpoint-desc">Retry de publicação que falhou</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/publisher/cleanup" data-description="Limpeza registros antigos">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/publisher/cleanup</span>
                            </div>
                            <div class="endpoint-desc">Limpeza de registros antigos de publicação</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/categories" data-description="Categorias WordPress disponíveis">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/publisher/categories</span>
                            </div>
                            <div class="endpoint-desc">Lista todas as categorias do WordPress</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/publisher/tags" data-description="Tags WordPress disponíveis">
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
                        <span class="module-icon">⚙️</span>
                        <div>
                            <div class="module-title">Módulo Config</div>
                            <div class="module-desc">Configurações centralizadas com backup</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/config" data-description="Painel configurações dark mode">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config</span>
                            </div>
                            <div class="endpoint-desc">Interface web de configurações com design dark mode</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/config/data" data-description="Obter todas configurações">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config/data</span>
                            </div>
                            <div class="endpoint-desc">Retorna todas as configurações do sistema</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/update" data-description="Atualizar configurações sistema">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/update</span>
                            </div>
                            <div class="endpoint-desc">Atualizar configurações do sistema</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/config/export" data-description="Exportar configurações JSON">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config/export</span>
                            </div>
                            <div class="endpoint-desc">Exportar todas as configurações em JSON</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/import" data-description="Importar configurações backup">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/import</span>
                            </div>
                            <div class="endpoint-desc">Importar configurações de backup</div>
                        </div>
                        
                        <div class="endpoint post" data-path="/config/backup" data-description="Criar backup configurações">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/backup</span>
                            </div>
                            <div class="endpoint-desc">Criar backup automático das configurações</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/config/stats" data-description="Estatísticas configurações URLs">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/config/stats</span>
                            </div>
                            <div class="endpoint-desc">Estatísticas de configurações e URLs monitoradas</div>
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
                        
                        <div class="endpoint post" data-path="/config/templates/add" data-description="Adicionar template conteúdo">
                            <div class="endpoint-header">
                                <span class="method post">POST</span>
                                <span class="endpoint-path">/config/templates/add</span>
                            </div>
                            <div class="endpoint-desc">Adicionar novo template de conteúdo personalizado</div>
                        </div>
                    </div>
                </div>
                
                <!-- Scheduler -->
                <div class="module" data-module="scheduler">
                    <div class="module-header">
                        <span class="module-icon">⏰</span>
                        <div>
                            <div class="module-title">Scheduler</div>
                            <div class="module-desc">Automação semanal domingos 10h</div>
                        </div>
                    </div>
                    
                    <div class="endpoints">
                        <div class="endpoint get" data-path="/scheduler" data-description="Status agendamento próximas execuções">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler</span>
                            </div>
                            <div class="endpoint-desc">Status e próximas execuções do agendador semanal</div>
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
                            <div class="endpoint-desc">Execução manual do fluxo completo (scraping + geração)</div>
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
                            <div class="endpoint-desc">Reativar execução de todos os jobs pausados</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scheduler/next" data-description="Próximas execuções 24h">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler/next</span>
                            </div>
                            <div class="endpoint-desc">Lista próximas execuções nas próximas 24 horas</div>
                        </div>
                        
                        <div class="endpoint get" data-path="/scheduler/history" data-description="Histórico execuções recentes">
                            <div class="endpoint-header">
                                <span class="method get">GET</span>
                                <span class="endpoint-path">/scheduler/history</span>
                            </div>
                            <div class="endpoint-desc">Histórico das execuções mais recentes</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="no-results hidden" id="noResults">
                <h3>🔍 Nenhum resultado encontrado</h3>
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
            
            // Função de busca
            function performSearch() {
                const searchTerm = searchInput.value.toLowerCase();
                currentSearch = searchTerm;
                filterContent();
            }
            
            // Função de filtro
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
                        
                        // Verificar filtro de método
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
                    
                    // Mostrar/ocultar módulo baseado nos endpoints visíveis
                    if (hasVisibleEndpoints) {
                        module.style.display = 'block';
                    } else {
                        module.style.display = 'none';
                    }
                });
                
                // Atualizar contador e mostrar/ocultar "sem resultados"
                resultsCount.textContent = `${visibleCount} endpoints encontrados`;
                
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
                    // Remover classe active de todos os botões
                    filterBtns.forEach(b => b.classList.remove('active'));
                    // Adicionar classe active ao botão clicado
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
# ROTAS DO MÓDULO SCRAPER
# =====================================================

@app.get("/scraper")
async def scraper_status():
    """Status detalhado do módulo de scraping"""
    if not SCRAPER_AVAILABLE:
        return {
            "module": "scraper",
            "status": "not_available",
            "message": "Módulo scraper não foi importado corretamente",
            "dependencies": ["beautifulsoup4", "requests", "lxml"]
        }
    
    try:
        manager = ScraperManager()
        status_data = manager.get_scraping_status()
        
        return {
            "module": "scraper",
            "status": "ready",
            "description": "Módulo para extrair produtos do Creative Cópias",
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
        logger.error(f"❌ Erro ao obter status do scraper: {e}")
        return {
            "module": "scraper",
            "status": "error",
            "message": str(e)
        }

@app.post("/scraper/test")
async def test_scraper_connection(request: ScrapingRequest = None):
    """Testa conexão com o site Creative Cópias"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        test_url = request.url if request and request.url else None
        result = manager.test_connection(test_url)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de conexão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/run")
async def run_full_scraping(background_tasks: BackgroundTasks):
    """Executa scraping completo de todas as categorias"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        # Executar scraping em background para não bloquear a API
        def run_scraping():
            manager = ScraperManager()
            # Para compatibilidade, manter limitação de 100 produtos no endpoint padrão
            result = manager.run_full_scraping(max_products_per_category=100)
            
            # Atualizar contagens automaticamente após o scraping
            try:
                from .config.active_categories_manager import ActiveCategoriesManager
                cat_manager = ActiveCategoriesManager()
                cat_manager.update_products_count_from_scraper()
                logger.info("✅ Contagens de produtos atualizadas automaticamente")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao atualizar contagens automaticamente: {e}")
            
            return result
        
        background_tasks.add_task(run_scraping)
        
        return {
            "status": "started",
            "message": "Scraping completo iniciado em background",
            "check_status": "/scraper/stats"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/run-single")
async def run_single_category_scraping(request: ScrapingRequest):
    """Executa scraping de uma categoria específica"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    if not request.url:
        raise HTTPException(status_code=400, detail="URL é obrigatória")
    
    try:
        manager = ScraperManager()
        result = manager.run_single_category_scraping(request.url)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no scraping da categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/stats")
async def get_scraper_stats():
    """Retorna estatísticas do módulo scraper"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        stats = manager.get_scraping_status()
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/products")
async def get_scraped_products(limit: int = 100, offset: int = 0, categoria: str = None, search: str = None):
    """Retorna lista de produtos encontrados pelo scraper com pesquisa e filtros"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        import json
        import os
        import glob
        from datetime import datetime
        
        # Buscar arquivos JSON de produtos
        json_files = glob.glob("logs/products_*.json")
        
        if not json_files:
            return {
                "success": True,
                "products": [],
                "total": 0,
                "message": "Nenhum produto encontrado ainda. Execute uma busca primeiro."
            }
        
        all_products = []
        
        # Mapeamento de categorias conhecidas
        categorias_mapeamento = {
            'cartuchos-de-tinta': 'Cartuchos de Tinta',
            'cartuchos-de-toner': 'Cartuchos de Toner', 
            'refil-de-toner': 'Refil de Toner',
            'impressoras': 'Impressoras',
            'multifuncional': 'Multifuncionais',
            'plotters': 'Plotters',
            'suprimentos': 'Suprimentos'
        }
        
        # Agrupar arquivos por categoria e pegar apenas o mais recente de cada uma
        categoria_files = {}
        for json_file in json_files:
            filename = os.path.basename(json_file)
            categoria_from_file = filename.replace('products_', '').split('_')[0]
            
            # Se não existe ou é mais recente, atualizar
            if categoria_from_file not in categoria_files:
                categoria_files[categoria_from_file] = json_file
            else:
                # Comparar timestamps nos nomes dos arquivos
                current_timestamp = filename.split('_')[-1].replace('.json', '')
                existing_filename = os.path.basename(categoria_files[categoria_from_file])
                existing_timestamp = existing_filename.split('_')[-1].replace('.json', '')
                
                if current_timestamp > existing_timestamp:
                    categoria_files[categoria_from_file] = json_file
        
        logger.info(f"🔍 Usando apenas arquivos mais recentes: {len(categoria_files)} categorias de {len(json_files)} arquivos totais")
        
        # Carregar produtos apenas dos arquivos mais recentes
        for categoria_key, json_file in categoria_files.items():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Usar categoria_key já extraída
                    filename = os.path.basename(json_file)
                    categoria_nome = categorias_mapeamento.get(categoria_key, categoria_key.title())
                    
                    # Adicionar produtos
                    if isinstance(data, list):
                        for product in data:
                            product['categoria_key'] = categoria_key
                            product['categoria_nome'] = categoria_nome
                            product['source_file'] = filename
                            all_products.append(product)
                    elif isinstance(data, dict) and 'produtos' in data:
                        for product in data['produtos']:
                            product['categoria_key'] = categoria_key
                            product['categoria_nome'] = categoria_nome
                            product['source_file'] = filename
                            all_products.append(product)
            except Exception as e:
                logger.warning(f"Erro ao carregar arquivo {json_file}: {e}")
                continue
        
                # DEDUPLIFICAÇÃO COMPLETA - Remove produtos duplicados por nome/URL
        unique_products = {}
        for product in all_products:
            # Usar nome + URL como chave única (nome pode ter variações pequenas)
            nome = product.get('nome', '').strip()
            url = product.get('url', '').strip()
            
            # Criar chave única baseada no nome (removendo espaços extras e normalizando)
            key = nome.lower().replace('  ', ' ').strip()
            
            # Se não existe ou se tem URL (preferir produtos com URL)
            if key not in unique_products or (url and not unique_products[key].get('url')):
                unique_products[key] = product
        
        # Converter de volta para lista
        all_products = list(unique_products.values())
        logger.info(f"🔍 Deduplificação: {len(all_products)} produtos únicos de {len(unique_products)} processados")

        # Aplicar filtro de pesquisa se especificado
        if search:
            search_lower = search.lower()
            filtered_products = []
            for product in all_products:
                nome = product.get('nome', '').lower()
                if search_lower in nome:
                    filtered_products.append(product)
            all_products = filtered_products

        # Filtrar por categoria se especificado
        if categoria and categoria.lower() != 'todas':
            filtered_products = []
            for product in all_products:
                if (categoria.lower() in product.get('categoria_key', '').lower() or
                    categoria.lower() in product.get('categoria_nome', '').lower()):
                    filtered_products.append(product)
            all_products = filtered_products

        # Ordenar por nome
        all_products.sort(key=lambda x: x.get('nome', ''))
        
        # Aplicar paginação
        total_products = len(all_products)
        start_idx = offset
        end_idx = offset + limit
        paginated_products = all_products[start_idx:end_idx]
        
        # Formatar produtos para resposta
        products = []
        for product in paginated_products:
            products.append({
                'id': product.get('id', product.get('nome', '')),
                'nome': product.get('nome', ''),
                'url': product.get('url', ''),
                'categoria_key': product.get('categoria_key', ''),
                'categoria_nome': product.get('categoria_nome', ''),
                'categoria_url': product.get('categoria_url', ''),
                'preco': product.get('preco', ''),
                'disponivel': product.get('disponivel', True),
                'source_file': product.get('source_file', ''),
                'data_processed': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return {
            "success": True,
            "products": products,
            "total": total_products,
            "limit": limit,
            "offset": offset,
            "categoria_filtro": categoria,
            "search_filtro": search,
            "message": f"Encontrados {len(products)} produtos (de {total_products} total)"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/categories")
async def get_scraper_categories():
    """Retorna lista de categorias disponíveis nos produtos"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        
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
        logger.error(f"❌ Erro ao obter categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/generate-article")
async def generate_article_from_product(product_data: dict):
    """Gera artigo a partir de dados do produto e envia para revisão"""
    if not GENERATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo gerador não disponível")
    
    try:
        from src.generator.generator_manager import GeneratorManager
        from src.review.review_manager import ReviewManager
        
        # Criar instâncias dos managers
        generator_manager = GeneratorManager()
        review_manager = ReviewManager()
        
        logger.info(f"🤖 Gerando artigo para produto: {product_data.get('nome', 'N/A')}")
        
        # Preparar dados para geração
        generation_request = {
            'product_data': product_data,
            'tone': 'profissional',
            'wp_category': product_data.get('categoria_nome', ''),
            'produto_original': product_data.get('nome', '')
        }
        
        # Gerar o artigo
        article_data = generator_manager.generate_article_from_product(product_data, 
                                                                      tone=generation_request.get('tone', 'profissional'),
                                                                      wp_category=generation_request.get('wp_category', ''),
                                                                      produto_original=generation_request.get('produto_original', ''),
                                                                      skip_availability_check=product_data.get('skip_availability_check', False))
        
        # Verificar se a geração foi bem-sucedida
        if not article_data or article_data.get('status') == 'skipped':
            error_msg = article_data.get('motivo', 'Erro na geração do artigo')
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Verificar se é um artigo válido
        if not article_data.get('titulo') or not article_data.get('conteudo'):
            raise HTTPException(status_code=500, detail="Artigo gerado está incompleto")
        
        review_data = {
            'titulo': article_data.get('titulo', ''),
            'slug': article_data.get('slug', ''),
            'meta_descricao': article_data.get('meta_descricao', ''),
            'conteudo': article_data.get('conteudo', ''),
            'tags': article_data.get('tags', []),
            'wp_category': product_data.get('categoria_nome', ''),
            'produto_original': product_data.get('nome', ''),
            'status': 'pending'
        }
        
        # Salvar na revisão
        article_id = review_manager.save_article_for_review(review_data)
        review_result = {'success': True, 'article_id': article_id}
        
        if review_result.get('success'):
            return {
                "success": True,
                "article_id": review_result.get('article_id'),
                "message": f"Artigo gerado e enviado para revisão com sucesso!",
                "produto": product_data.get('nome', ''),
                "categoria": product_data.get('categoria_nome', '')
            }
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar artigo para revisão")
        
    except HTTPException:
        # Re-raise HTTPExceptions para que o FastAPI as trate corretamente
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar artigo: {e}")
        logger.error(f"❌ Tipo do erro: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        error_detail = str(e) if str(e) else f"Erro interno: {type(e).__name__}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/scraper/products/export")
async def export_scraped_products():
    """Exporta todos os produtos encontrados pelo scraper"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        filename = manager.url_manager.export_processed_products()
        
        if filename:
            return {
                "success": True,
                "message": "Produtos exportados com sucesso",
                "filename": filename
            }
        else:
            return {
                "success": False,
                "message": "Erro ao exportar produtos"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro ao exportar produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/cleanup")
async def cleanup_scraper_data():
    """Limpa dados antigos do scraper"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        result = manager.cleanup_old_data()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/discover-categories")
async def discover_categories(force_refresh: bool = False):
    """Descobre automaticamente todas as categorias de produtos"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        result = manager.url_manager.auto_discover_categories(force_refresh=force_refresh)
        return result
    except Exception as e:
        logger.error(f"❌ Erro na descoberta de categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/update-urls-from-discovery")
async def update_urls_from_discovery():
    """Atualiza URLs de categorias com base na descoberta automática"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        result = manager.url_manager.update_category_urls_from_discovery()
        return result
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar URLs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraper/analyze-category/{category_url:path}")
async def analyze_category(category_url: str):
    """Analisa estrutura de uma categoria específica"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        analysis = manager.scraper.analyze_category_structure(category_url)
        return analysis
    except Exception as e:
        logger.error(f"❌ Erro ao analisar categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/validate-urls")
async def validate_category_urls():
    """Valida todas as URLs de categorias configuradas"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        result = manager.url_manager.validate_all_category_urls()
        return result
    except Exception as e:
        logger.error(f"❌ Erro ao validar URLs: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/scraper/run-enhanced")
async def run_enhanced_scraping(use_pagination: bool = True, discover_categories: bool = False, max_products_per_category: int = 0):
    """Executa scraping com funcionalidades avançadas e controle de limitação"""
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    try:
        manager = ScraperManager()
        result = manager.run_full_scraping(
            use_pagination=use_pagination,
            discover_categories=discover_categories,
            max_products_per_category=max_products_per_category
        )
        return result
    except Exception as e:
        logger.error(f"❌ Erro no scraping avançado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/run-manual-complete")
async def run_manual_complete_scraping(background_tasks: BackgroundTasks):
    """
    BUSCA MANUAL INICIAL - Coleta TODOS os produtos do site sem limitação
    Esta é a busca completa que deve ser executada uma vez para mapear todo o catálogo
    """
    if not SCRAPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo scraper não disponível")
    
    def run_complete_scraping():
        """Executa busca completa sem limitações"""
        try:
            logger.info("🚀 INICIANDO BUSCA MANUAL COMPLETA - TODOS OS PRODUTOS")
            logger.info("📋 Esta é a busca inicial que coletará todo o catálogo do site")
            
            manager = ScraperManager()
            
            # Executar com parâmetros para busca completa
            result = manager.run_full_scraping(
                use_pagination=True,  # Usar paginação para não perder produtos
                discover_categories=True,  # Descobrir novas categorias
                max_products_per_category=0  # SEM LIMITAÇÃO - pegar todos os produtos
            )
            
            logger.info("✅ BUSCA MANUAL COMPLETA FINALIZADA")
            logger.info(f"📊 Resultado: {result.get('total_products_found', 0)} produtos encontrados")
            logger.info(f"🆕 Novos produtos: {result.get('total_new_products', 0)}")
            logger.info(f"⏱️ Tempo total: {result.get('execution_time', 0):.1f}s")
            
            # Atualizar contagens automaticamente
            try:
                from src.config.active_categories_manager import ActiveCategoriesManager
                cat_manager = ActiveCategoriesManager()
                cat_manager.update_products_count_from_scraper()
                logger.info("✅ Contagens de categorias atualizadas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao atualizar contagens: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na busca manual completa: {e}")
            raise
    
    try:
        # Executar em background para não bloquear
        background_tasks.add_task(run_complete_scraping)
        
        return {
            "status": "started",
            "message": "🚀 BUSCA MANUAL COMPLETA iniciada - coletando TODOS os produtos",
            "note": "Esta é a busca inicial que mapeia todo o catálogo do site",
            "warning": "⚠️ Este processo pode demorar bastante (10-30 minutos dependendo do site)",
            "check_status": "/scraper/stats",
            "type": "manual_complete"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar busca completa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraper/process-active-categories")
async def process_active_categories(background_tasks: BackgroundTasks, max_articles: int = 10):
    """Processa automaticamente: scraping + geração de artigos das categorias ativas"""
    if not SCRAPER_AVAILABLE or not GENERATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulos scraper/generator não disponíveis")
    
    def run_complete_process():
        """Executa o processo completo em background"""
        try:
            logger.info("🚀 Iniciando processamento automático das categorias ativas")
            
            # Etapa 1: Verificar categorias ativas
            if CATEGORIES_AVAILABLE:
                from src.config.active_categories_manager import ActiveCategoriesManager
                categories_manager = ActiveCategoriesManager()
                active_categories = categories_manager.get_active_categories()
                
                if not active_categories:
                    logger.warning("❌ Nenhuma categoria ativa encontrada")
                    return
                
                logger.info(f"📋 {len(active_categories)} categorias ativas encontradas")
            
            # Etapa 2: Executar scraping
            logger.info("📡 Executando scraping das categorias ativas...")
            scraper_manager = ScraperManager()
            scraping_result = scraper_manager.run_full_scraping(
                use_pagination=True,
                discover_categories=False,
                max_products_per_category=50  # Limitação para busca automática semanal
            )
            
            logger.info(f"✅ Scraping concluído: {scraping_result.get('status', 'unknown')}")
            
            # Etapa 3: Buscar produtos recém-coletados
            products_data = scraper_manager.get_scraped_products(limit=max_articles * 2)
            
            if not products_data.get('produtos'):
                logger.warning("⚠️ Nenhum produto encontrado para gerar artigos")
                return
            
            products = products_data['produtos'][:max_articles]  # Limitar quantidade
            logger.info(f"📦 {len(products)} produtos selecionados para geração de artigos")
            
            # Etapa 4: Gerar artigos
            logger.info("✍️ Iniciando geração de artigos...")
            generator_manager = GeneratorManager()
            generated_count = 0
            
            for i, product in enumerate(products):
                try:
                    logger.info(f"📝 Gerando artigo {i+1}/{len(products)}: {product.get('nome', 'Produto')[:50]}...")
                    
                    article = generator_manager.generate_article_from_product(
                        product=product,
                        tone='profissional',
                        wp_category='geral'
                    )
                    
                    if article:
                        generated_count += 1
                        logger.info(f"✅ Artigo gerado com sucesso: {article.get('titulo', 'Sem título')[:50]}...")
                    else:
                        logger.warning(f"⚠️ Falha ao gerar artigo para: {product.get('nome', 'Produto')[:30]}...")
                        
                except Exception as gen_error:
                    logger.error(f"❌ Erro ao gerar artigo para {product.get('nome', 'Produto')[:30]}: {gen_error}")
                    continue
            
            logger.info(f"🎉 Processamento automático concluído!")
            logger.info(f"📊 Resumo: {generated_count} artigos gerados de {len(products)} produtos processados")
            logger.info(f"📋 Verifique a página de Revisão para ver os artigos gerados")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento automático: {e}")
    
    # Executar em background
    background_tasks.add_task(run_complete_process)
    
    return {
        "status": "success",
        "message": "Processamento automático iniciado em segundo plano",
        "max_articles": max_articles,
        "note": "Acompanhe o progresso nos logs do sistema"
    }


# =====================================================
# ROTAS DO MÓDULO GENERATOR
# =====================================================

@app.get("/generator")
async def generator_status():
    """Status detalhado do módulo de geração de conteúdo"""
    if not GENERATOR_AVAILABLE:
        return {
            "module": "generator",
            "status": "not_available",
            "message": "Módulo generator não foi importado corretamente",
            "dependencies": ["openai", "loguru"]
        }
    
    try:
        manager = GeneratorManager()
        status_data = manager.get_stats()
        
        return {
            "module": "generator",
            "status": "ready",
            "description": "Módulo para gerar artigos SEO com IA",
            "data": status_data,
            "actions": {
                "test_generation": "/generator/test",
                "generate_from_product": "/generator/generate",
                "get_stats": "/generator/stats"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do generator: {e}")
        return {
            "module": "generator",
            "status": "error",
            "message": str(e)
        }

@app.post("/generator/test")
async def test_generator():
    """Testa geração de conteúdo com produto fictício"""
    if not GENERATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo generator não disponível")
    
    try:
        manager = GeneratorManager()
        result = manager.test_generation()
        
        if result:
            return {
                "status": "success",
                "message": "Teste de geração bem-sucedido",
                "article": result
            }
        else:
            return {
                "status": "failed",
                "message": "Falha no teste de geração"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de geração: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generator/generate")
async def generate_article(request: GenerationRequest):
    """Gera artigo a partir de dados de produto"""
    if not GENERATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo generator não disponível")
    
    if not request.product_data and not request.product_id:
        raise HTTPException(status_code=400, detail="product_data ou product_id é obrigatório")
    
    try:
        manager = GeneratorManager()
        
        # Se foi fornecido product_id, buscar dados do scraper
        if request.product_id and not request.product_data:
            # TODO: Integrar com scraper para buscar produto por ID
            raise HTTPException(status_code=400, detail="Integração com scraper ainda não implementada. Use product_data.")
        
        # Gerar artigo
        article = manager.generate_article_from_product(
            product=request.product_data,
            custom_keywords=request.custom_keywords,
            custom_instructions=request.custom_instructions,
            tone=request.tone,
            wp_category=request.wp_category,
            produto_original=request.produto_original
        )
        
        if article:
            # Salvar automaticamente no sistema de revisão
            try:
                if REVIEW_AVAILABLE:
                    from src.review.review_manager import ReviewManager
                    review_manager = ReviewManager()
                    
                    # Salvar artigo para revisão
                    article_id = review_manager.save_article(
                        title=article.get('titulo', 'Artigo sem título'),
                        content=article.get('conteudo', ''),
                        meta_description=article.get('meta_descricao', ''),
                        slug=article.get('slug', ''),
                        tags=article.get('tags', []),
                        wp_category=request.wp_category,
                        produto_original=request.produto_original,
                        status='pendente'
                    )
                    
                    return {
                        "success": True,
                        "status": "success",
                        "article": article,
                        "article_id": article_id,
                        "message": "Artigo gerado e salvo para revisão com sucesso"
                    }
                else:
                    return {
                        "success": True,
                        "status": "success",
                        "article": article,
                        "message": "Artigo gerado com sucesso (sistema de revisão não disponível)"
                    }
                    
            except Exception as review_error:
                logger.warning(f"Erro ao salvar no sistema de revisão: {review_error}")
                return {
                    "success": True,
                    "status": "success",
                    "article": article,
                    "message": "Artigo gerado com sucesso, mas não foi possível salvar automaticamente para revisão"
                }
        else:
            return {
                "success": False,
                "status": "failed",
                "message": "Falha na geração do artigo"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro na geração do artigo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generator/generate-random")
async def generate_random_article():
    """Gera artigo com produto aleatório respeitando filtros de preferências"""
    if not GENERATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo generator não disponível")
    
    try:
        manager = GeneratorManager()
        
        # Gerar artigo com produto aleatório (aplica filtros automaticamente)
        article = manager.content_generator.generate_article_from_random_product()
        
        if article:
            return {
                "status": "success",
                "article": article,
                "message": "Artigo gerado com produto aleatório respeitando filtros de preferências"
            }
        else:
            return {
                "status": "failed",
                "message": "Falha na geração do artigo com produto aleatório"
            }
        
    except ValueError as e:
        # Erro específico de filtros (nenhum produto disponível)
        return {
            "status": "error",
            "message": f"Erro de filtros: {str(e)}",
            "suggestion": "Verifique as preferências de geração ou sincronize mais produtos"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na geração com produto aleatório: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generator/stats")
async def get_generator_stats():
    """Retorna estatísticas do módulo generator"""
    if not GENERATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo generator não disponível")
    
    try:
        manager = GeneratorManager()
        stats = manager.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ROTAS DO MÓDULO REVIEW
# =====================================================

@app.get("/review")
async def review_status():
    """Status detalhado do módulo de revisão"""
    if not REVIEW_AVAILABLE:
        return {
            "module": "review",
            "status": "not_available",
            "message": "Módulo review não foi importado corretamente",
            "dependencies": ["sqlite3", "loguru"]
        }
    
    try:
        manager = ReviewManager()
        status_data = manager.get_statistics()
        
        return {
            "module": "review",
            "status": "ready",
            "description": "Sistema de revisão de artigos com interface web",
            "data": status_data,
            "actions": {
                "list_articles": "/interface/review",
                "view_article": "/review/{id}",
                "edit_article": "/review/{id}/edit",
                "approve_article": "/review/{id}/approve",
                "reject_article": "/review/{id}/reject",
                "get_stats": "/review/stats",
                "approved_articles": "/review/approved"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do review: {e}")
        return {
            "module": "review",
            "status": "error",
            "message": str(e)
        }

# Endpoint removido - usar /interface/review

@app.get("/review/stats")
async def review_statistics():
    """Estatísticas do sistema de revisão"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        stats = review_manager.get_statistics()
        
        return JSONResponse({
            "success": True,
            "statistics": stats,
            "module": "review"
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas de revisão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/review/approved")
async def review_approved_articles():
    """Listar artigos aprovados para publicação"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        approved_articles = review_manager.get_approved_articles_for_publishing()
        
        return JSONResponse({
            "success": True,
            "approved_articles": approved_articles,
            "count": len(approved_articles)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar artigos aprovados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/review/articles")
async def get_review_articles(status: str = None, limit: int = 50):
    """Retornar artigos para a interface em formato JSON"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        articles = review_manager.list_articles(status=status, limit=limit)
        
        # Garantir formatação correta das datas para JSON
        for article in articles:
            # Corrigir encoding e garantir que campos existam
            article_dict = dict(article)
            
            # Corrigir encoding e garantir que campos existam
            article_dict['titulo'] = article_dict.get('titulo') or 'Título não disponível'
            article_dict['conteudo'] = article_dict.get('conteudo') or 'Conteúdo não foi gerado ou está vazio'
            article_dict['status'] = article_dict.get('status') or 'pendente'
            article_dict['meta_descricao'] = article_dict.get('meta_descricao') or ''
            article_dict['slug'] = article_dict.get('slug') or ''
            article_dict['tags'] = article_dict.get('tags') or []
            
            # Garantir que datas sejam strings
            if 'data_criacao' in article_dict and article_dict['data_criacao']:
                article_dict['data_criacao'] = str(article_dict['data_criacao'])
            
            if 'data_revisao' in article_dict and article_dict['data_revisao']:
                article_dict['data_revisao'] = str(article_dict['data_revisao'])
        
        return JSONResponse({
            "success": True,
            "articles": articles,
            "count": len(articles),
            "status_filter": status
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter artigos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/review/{article_id}")
async def review_article_view(article_id: int):
    """Visualizar artigo específico"""
    
    # Forçar Content-Type para JSON
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if not REVIEW_AVAILABLE:
        return JSONResponse({
            "success": False,
            "error": "Módulo Review não disponível",
            "status_code": 503
        }, status_code=503, headers=headers)
    
    try:
        review_manager = ReviewManager()
        article = review_manager.get_article(article_id)
        
        if not article:
            return JSONResponse({
                "success": False,
                "error": "Artigo não encontrado",
                "status_code": 404,
                "article_id": article_id
            }, status_code=404, headers=headers)
        
        # Converter para dict simples
        article_dict = dict(article)
        
        # Garantir campos básicos
        article_dict['titulo'] = article_dict.get('titulo') or 'Título não disponível'
        article_dict['conteudo'] = article_dict.get('conteudo') or 'Conteúdo não foi gerado ou está vazio'
        article_dict['status'] = article_dict.get('status') or 'pendente'
        article_dict['meta_descricao'] = article_dict.get('meta_descricao') or ''
        article_dict['slug'] = article_dict.get('slug') or ''
        article_dict['tags'] = article_dict.get('tags') or []
        
        # Garantir que datas sejam strings
        if 'data_criacao' in article_dict and article_dict['data_criacao']:
            article_dict['data_criacao'] = str(article_dict['data_criacao'])
        
        if 'data_revisao' in article_dict and article_dict['data_revisao']:
            article_dict['data_revisao'] = str(article_dict['data_revisao'])
        
        return JSONResponse({
            "success": True,
            "article": article_dict,
            "article_id": article_id
        }, headers=headers)
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar artigo {article_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Erro interno: {str(e)}",
            "status_code": 500,
            "article_id": article_id
        }, status_code=500, headers=headers)

@app.get("/review/{article_id}/view", response_class=HTMLResponse)
async def review_article_view_html(article_id: int):
    """Interface de visualização de artigo (HTML)"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        article = review_manager.get_article(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Artigo não encontrado")
        
        if not templates:
            return JSONResponse({
                "article": article,
                "edit_mode": False,
                "message": "Templates não disponíveis"
            })
        
        return templates.TemplateResponse("review_article.html", {
            "request": {},
            "article": article,
            "is_edit_mode": False
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao carregar visualização para artigo {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/review/{article_id}/edit", response_class=HTMLResponse)
async def review_article_edit(article_id: int):
    """Interface de edição de artigo"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        article = review_manager.get_article(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Artigo não encontrado")
        
        if not templates:
            return JSONResponse({
                "article": article,
                "edit_mode": True,
                "message": "Use a API /review/{id}/update para editar via JSON"
            })
        
        return templates.TemplateResponse("review_article.html", {
            "request": {},
            "article": article,
            "is_edit_mode": True
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao carregar editor para artigo {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/review/{article_id}/update")
async def review_article_update(article_id: int, request: ReviewRequest):
    """Atualizar dados do artigo"""
    
    # Forçar Content-Type para JSON
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if not REVIEW_AVAILABLE:
        return JSONResponse({
            "success": False,
            "error": "Módulo Review não disponível",
            "status_code": 503
        }, status_code=503, headers=headers)
    
    try:
        review_manager = ReviewManager()
        
        # Converter request para dict, removendo valores None
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            return JSONResponse({
                "success": False,
                "error": "Nenhum campo válido para atualizar",
                "status_code": 400,
                "article_id": article_id
            }, status_code=400, headers=headers)
        
        success = review_manager.update_article(article_id, updates, "API User")
        
        if not success:
            return JSONResponse({
                "success": False,
                "error": "Artigo não encontrado",
                "status_code": 404,
                "article_id": article_id
            }, status_code=404, headers=headers)
        
        # Retornar artigo atualizado
        updated_article = review_manager.get_article(article_id)
        
        return JSONResponse({
            "success": True,
            "message": "Artigo atualizado com sucesso",
            "article": dict(updated_article) if updated_article else None,
            "article_id": article_id
        }, headers=headers)
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar artigo {article_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Erro interno: {str(e)}",
            "status_code": 500,
            "article_id": article_id
        }, status_code=500, headers=headers)

@app.post("/review/{article_id}/approve")
async def review_article_approve(article_id: int, request: ReviewActionRequest = None):
    """Aprovar artigo para publicação"""
    
    # Forçar Content-Type para JSON
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if not REVIEW_AVAILABLE:
        return JSONResponse({
            "success": False,
            "error": "Módulo Review não disponível",
            "status_code": 503
        }, status_code=503, headers=headers)
    
    try:
        # Se request é None, criar um vazio
        if not request:
            request = ReviewActionRequest()
        
        review_manager = ReviewManager()
        
        success = review_manager.approve_article(
            article_id, 
            request.reviewer, 
            request.comment,
            wp_category=request.wp_category,
            produto_original=request.produto_original,
            skip_availability_check=request.skip_availability_check
        )
        
        if not success:
            return JSONResponse({
                "success": False,
                "error": "Artigo não encontrado",
                "status_code": 404,
                "article_id": article_id
            }, status_code=404, headers=headers)
        
        return JSONResponse({
            "success": True,
            "message": f"Artigo {article_id} aprovado com sucesso",
            "action": "approved",
            "reviewer": request.reviewer,
            "article_id": article_id
        }, headers=headers)
        
    except Exception as e:
        logger.error(f"❌ Erro ao aprovar artigo {article_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Erro interno: {str(e)}",
            "status_code": 500,
            "article_id": article_id
        }, status_code=500, headers=headers)

@app.post("/review/{article_id}/reject")
async def review_article_reject(article_id: int, request: ReviewActionRequest = None):
    """Rejeitar artigo"""
    
    # Forçar Content-Type para JSON
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if not REVIEW_AVAILABLE:
        return JSONResponse({
            "success": False,
            "error": "Módulo Review não disponível",
            "status_code": 503
        }, status_code=503, headers=headers)
    
    try:
        # Se request é None, criar um vazio
        if not request:
            request = ReviewActionRequest()
        
        if not request.comment:
            return JSONResponse({
                "success": False,
                "error": "Motivo da rejeição é obrigatório",
                "status_code": 400,
                "article_id": article_id
            }, status_code=400, headers=headers)
        
        review_manager = ReviewManager()
        
        success = review_manager.reject_article(
            article_id, 
            request.comment,  # Motivo da rejeição
            request.reviewer
        )
        
        if not success:
            return JSONResponse({
                "success": False,
                "error": "Artigo não encontrado",
                "status_code": 404,
                "article_id": article_id
            }, status_code=404, headers=headers)
        
        return JSONResponse({
            "success": True,
            "message": f"Artigo {article_id} rejeitado",
            "action": "rejected",
            "reason": request.comment,
            "reviewer": request.reviewer,
            "article_id": article_id
        }, headers=headers)
        
    except Exception as e:
        logger.error(f"❌ Erro ao rejeitar artigo {article_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Erro interno: {str(e)}",
            "status_code": 500,
            "article_id": article_id
        }, status_code=500, headers=headers)

@app.delete("/review/{article_id}")
async def review_delete_article(article_id: int):
    """Remover artigo do sistema"""
    
    # Forçar Content-Type para JSON
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if not REVIEW_AVAILABLE:
        return JSONResponse({
            "success": False,
            "error": "Módulo Review não disponível",
            "status_code": 503
        }, status_code=503, headers=headers)
    
    try:
        review_manager = ReviewManager()
        success = review_manager.delete_article(article_id, "API User")
        
        if not success:
            return JSONResponse({
                "success": False,
                "error": "Artigo não encontrado",
                "status_code": 404,
                "article_id": article_id
            }, status_code=404, headers=headers)
        
        return JSONResponse({
            "success": True,
            "message": f"Artigo {article_id} removido com sucesso",
            "article_id": article_id
        }, headers=headers)
        
    except Exception as e:
        logger.error(f"❌ Erro ao remover artigo {article_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Erro interno: {str(e)}",
            "status_code": 500,
            "article_id": article_id
        }, status_code=500, headers=headers)

@app.post("/review/save-from-generator")
async def review_save_from_generator(article_data: dict):
    """Salvar artigo gerado para revisão (usado pelo Generator)"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        article_id = review_manager.save_article_for_review(article_data)
        
        return JSONResponse({
            "success": True,
            "message": "Artigo salvo para revisão",
            "article_id": article_id,
            "review_url": f"/review/{article_id}"
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar artigo para revisão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/review/api/list")
async def get_review_articles_api(status: str = None, limit: int = 50):
    """Endpoint API para listar artigos - interface amigável"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        articles = review_manager.list_articles(status=status, limit=limit)
        
        # Garantir formatação correta das datas para JSON
        formatted_articles = []
        for article in articles:
            formatted_article = dict(article)
            
            # Corrigir encoding e garantir que campos existam
            formatted_article['titulo'] = formatted_article.get('titulo') or 'Título não disponível'
            formatted_article['conteudo'] = formatted_article.get('conteudo') or 'Conteúdo não foi gerado ou está vazio'
            formatted_article['status'] = formatted_article.get('status') or 'pendente'
            formatted_article['meta_descricao'] = formatted_article.get('meta_descricao') or ''
            formatted_article['slug'] = formatted_article.get('slug') or ''
            formatted_article['tags'] = formatted_article.get('tags') or []
            
            # Garantir que datas sejam strings
            if 'data_criacao' in formatted_article and formatted_article['data_criacao']:
                formatted_article['data_criacao'] = str(formatted_article['data_criacao'])
            
            if 'data_revisao' in formatted_article and formatted_article['data_revisao']:
                formatted_article['data_revisao'] = str(formatted_article['data_revisao'])
            
            # Garantir que ID existe
            if 'id' not in formatted_article or not formatted_article['id']:
                logger.warning(f"Artigo sem ID encontrado: {formatted_article}")
                continue
            
            formatted_articles.append(formatted_article)
        
        return JSONResponse({
            "success": True,
            "articles": formatted_articles,
            "count": len(formatted_articles),
            "status_filter": status
        }, media_type="application/json; charset=utf-8")
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter artigos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/review/{article_id}/test")
async def test_review_article(article_id: int):
    """Endpoint de teste para debug"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        article = review_manager.get_article(article_id)
        
        if not article:
            return {"error": "Artigo não encontrado"}
        
        # Retornar dados básicos
        return {
            "success": True,
            "id": article.get('id'),
            "titulo": article.get('titulo'),
            "has_content": bool(article.get('conteudo')),
            "content_length": len(str(article.get('conteudo', ''))),
            "data_criacao": str(article.get('data_criacao')),
            "data_criacao_type": str(type(article.get('data_criacao')))
        }
        
    except Exception as e:
        return {"error": str(e), "type": str(type(e))}


# =====================================================
# ROTAS DO MÓDULO PUBLISHER
# =====================================================

@app.get("/publisher")
async def publisher_status():
    """Status detalhado do módulo de publicação"""
    if not PUBLISHER_AVAILABLE:
        return {
            "module": "publisher",
            "status": "not_available",
            "message": "Módulo publisher não foi importado corretamente",
            "dependencies": ["requests", "python-dotenv"]
        }
    
    try:
        manager = PublicationManager()
        status_data = manager.get_publication_statistics()
        
        # Testar conexão WordPress
        wp_test = manager.test_wordpress_connection()
        
        return {
            "module": "publisher",
            "status": "ready",
            "description": "Módulo para publicação automática no WordPress",
            "data": status_data,
            "wordpress": wp_test,
            "actions": {
                "test_wordpress": "/publisher/test",
                "publish_article": "/publisher/publish",
                "list_publications": "/publisher/list",
                "get_stats": "/publisher/stats"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do publisher: {e}")
        return {
            "module": "publisher",
            "status": "error",
            "message": str(e)
        }

@app.post("/publisher/test")
async def test_wordpress_connection():
    """Testa conexão com WordPress"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        result = manager.test_wordpress_connection()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no teste WordPress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publisher/publish")
async def publish_article(publication_data: dict):
    """Publica artigo aprovado no WordPress"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo review necessário para buscar artigo")
    
    try:
        # CORREÇÃO URGENTE: Validação robusta dos dados de entrada
        logger.info(f"🚀 Recebendo requisição de publicação: {publication_data}")
        
        # Validar e extrair article_id
        article_id = publication_data.get('article_id')
        if not article_id:
            logger.error("❌ ERRO 400: article_id não fornecido")
            raise HTTPException(status_code=400, detail="Campo 'article_id' é obrigatório")
        
        # Converter para int se necessário
        try:
            article_id = int(article_id)
        except (ValueError, TypeError):
            logger.error(f"❌ ERRO 400: article_id inválido: {article_id}")
            raise HTTPException(status_code=400, detail=f"Campo 'article_id' deve ser um número válido. Recebido: {article_id}")
        
        # Extrair outros parâmetros com valores padrão
        publish_immediately = publication_data.get('publish_immediately', True)
        scheduled_date_str = publication_data.get('scheduled_date')
        
        logger.info(f"📝 Processando publicação: article_id={article_id}, publish_immediately={publish_immediately}")
        
        # Buscar artigo no sistema de revisão
        review_manager = ReviewManager()
        article = review_manager.get_article(article_id)  # Usar método correto
        
        if not article:
            logger.error(f"❌ ERRO 404: Artigo {article_id} não encontrado")
            raise HTTPException(status_code=404, detail=f"Artigo com ID {article_id} não encontrado")
        
        # Verificar status do artigo
        article_status = article.get('status', '').lower()
        if article_status != 'aprovado':
            logger.warning(f"⚠️ Artigo {article_id} não está aprovado (status: {article_status})")
            raise HTTPException(status_code=400, detail=f"Apenas artigos aprovados podem ser publicados. Status atual: {article_status}")
        
        # Processar data agendada se fornecida
        scheduled_date = None
        if scheduled_date_str:
            try:
                scheduled_date = datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"❌ Erro no formato da data: {e}")
                raise HTTPException(status_code=400, detail="Formato de data inválido. Use formato ISO.")
        
        # Publicar artigo
        logger.info(f"📤 Iniciando publicação do artigo {article_id}")
        pub_manager = PublicationManager()
        
        result = pub_manager.publish_article(
            article_data=article,
            publish_immediately=publish_immediately,
            scheduled_date=scheduled_date
        )
        
        logger.info(f"📊 Resultado da publicação: {result}")
        
        # Se publicação foi bem-sucedida, marcar artigo como publicado
        if result.get('success') and publish_immediately:
            try:
                review_manager.mark_as_published(
                    article_id, 
                    result.get('wp_url', '')
                )
                logger.info(f"✅ Artigo {article_id} marcado como publicado no sistema de revisão")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao marcar como publicado: {e}")
        
        # Retornar resultado com informações adicionais
        if result.get('success'):
            response = {
                'success': True,
                'message': 'Artigo publicado com sucesso!',
                'wp_post_id': result.get('wp_post_id'),
                'wp_url': result.get('wp_url'),
                'status': result.get('status'),
                'note': result.get('note'),
                'publication_id': result.get('publication_id'),
                'article_id': article_id
            }
        else:
            response = {
                'success': False,
                'error': result.get('error', 'Erro desconhecido na publicação'),
                'error_code': 'PUBLICATION_FAILED',
                'article_id': article_id
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO ao publicar artigo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/publisher/list")
async def list_publications(status: str = None, limit: int = 50):
    """Lista publicações"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        publications = manager.list_publications(status=status, limit=limit)
        
        return {
            "success": True,
            "publications": publications,
            "count": len(publications),
            "status_filter": status
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar publicações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/publisher/stats")
async def get_publisher_stats():
    """Retorna estatísticas do módulo publisher"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        stats = manager.get_publication_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "module": "publisher"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publisher/retry/{publication_id}")
async def retry_publication(publication_id: int):
    """Tenta republicar artigo que falhou"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        result = manager.retry_failed_publication(publication_id)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro ao tentar retry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publisher/cleanup")
async def cleanup_publications():
    """Limpa registros antigos de publicação"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        removed_count = manager.cleanup_old_publications()
        
        return {
            "success": True,
            "message": f"{removed_count} registros antigos removidos",
            "removed_count": removed_count
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/publisher/categories")
async def get_wordpress_categories():
    """Lista categorias do WordPress"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        
        if not manager.wp_client:
            raise HTTPException(status_code=400, detail="WordPress não configurado")
        
        categories = manager.wp_client.get_categories()
        
        return {
            "success": True,
            "categories": categories,
            "count": len(categories)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/publisher/tags")
async def get_wordpress_tags():
    """Lista tags do WordPress"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        
        if not manager.wp_client:
            raise HTTPException(status_code=400, detail="WordPress não configurado")
        
        tags = manager.wp_client.get_tags()
        
        return {
            "success": True,
            "tags": tags,
            "count": len(tags)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS DE INTELIGÊNCIA ====================

@app.get("/intelligence")
async def intelligence_status():
    """Status dos sistemas de inteligência"""
    if not INTELLIGENCE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulos de inteligência não disponíveis")
    
    try:
        priority_manager = PriorityManager()
        publication_monitor = PublicationMonitor()
        
        # Estatísticas de aprendizado
        learning_stats = priority_manager.get_learning_stats()
        
        # Status de monitoramento
        monitor_stats = publication_monitor.get_monitor_stats()
        
        # Verificação de configuração WordPress
        wp_config = publication_monitor.check_wordpress_config()
        
        return {
            "success": True,
            "systems": {
                "priority_learning": {
                    "active": True,
                    "stats": learning_stats
                },
                "publication_monitor": {
                    "active": True,
                    "stats": monitor_stats,
                    "wp_config": wp_config
                }
            },
            "message": "Sistemas de inteligência operacionais"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no status de inteligência: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intelligence/priority")
async def get_priority_stats():
    """Estatísticas do sistema de priorização"""
    if not INTELLIGENCE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulos de inteligência não disponíveis")
    
    try:
        priority_manager = PriorityManager()
        
        # Estatísticas completas
        stats = priority_manager.get_learning_stats()
        
        # Produtos priorizados
        prioritized = priority_manager.get_prioritized_products(limit=20)
        
        # Performance por categoria
        category_performance = priority_manager.get_category_performance()
        
        return {
            "success": True,
            "learning_stats": stats,
            "prioritized_products": prioritized,
            "category_performance": category_performance
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas de prioridade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intelligence/monitor")
async def get_publication_monitor():
    """Dashboard de monitoramento de publicações"""
    if not INTELLIGENCE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulos de inteligência não disponíveis")
    
    try:
        publication_monitor = PublicationMonitor()
        
        # Dashboard completo
        dashboard = publication_monitor.get_pending_articles_dashboard()
        
        # Verificação de publicações pendentes
        pending_check = publication_monitor.check_pending_publications()
        
        return {
            "success": True,
            "dashboard": dashboard,
            "pending_check": pending_check
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no monitor de publicações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intelligence/monitor/config")
async def check_wordpress_publication_config():
    """Verificar configuração de publicação WordPress"""
    if not INTELLIGENCE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulos de inteligência não disponíveis")
    
    try:
        publication_monitor = PublicationMonitor()
        
        config_check = publication_monitor.check_wordpress_config()
        
        return {
            "success": True,
            "config_check": config_check
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar configuração: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config", response_class=HTMLResponse)
async def config_page():
    """Página principal de configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        if templates:
            return templates.TemplateResponse("config.html", {"request": {}})
        else:
            # HTML básico caso templates não estejam disponíveis
            with open("templates/config.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            return HTMLResponse(html_content)
    except Exception as e:
        logger.error(f"❌ Erro ao carregar página de config: {e}")
        raise HTTPException(status_code=500, detail="Erro ao carregar página")

@app.get("/config/data")
async def get_config_data():
    """Obter todas as configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        
        return {
            "success": True,
            "configurations": manager.get_all_configs(),
            "monitored_urls": manager.get_monitored_urls(active_only=False),
            "content_templates": manager.get_content_templates(active_only=False)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados de config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/update")
async def update_config(request: ConfigUpdateRequest):
    """Atualizar configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        # Validar se há configurações para atualizar
        if not request.configurations:
            raise HTTPException(status_code=400, detail="Nenhuma configuração fornecida para atualização")
        
        manager = ConfigManager()
        manager.update_configs(request.configurations)
        
        return {
            "success": True,
            "message": "Configurações atualizadas com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar configurações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/export")
async def export_config():
    """Exportar configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        export_data = manager.export_config()
        
        return export_data
        
    except Exception as e:
        logger.error(f"❌ Erro ao exportar configurações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/import")
async def import_config(config_data: dict, overwrite: bool = False):
    """Importar configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        manager.import_config(config_data, overwrite=overwrite)
        
        return {
            "success": True,
            "message": "Configurações importadas com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao importar configurações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/backup")
async def create_config_backup():
    """Criar backup das configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        backup_name = manager.create_backup()
        
        return {
            "success": True,
            "backup_name": backup_name,
            "message": f"Backup '{backup_name}' criado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/stats")
async def get_config_stats():
    """Obter estatísticas das configurações"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        stats = manager.get_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/urls/add")
async def add_monitored_url(request: URLAddRequest):
    """Adicionar URL monitorada"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        manager.add_monitored_url(
            category=request.category,
            name=request.name,
            url=request.url,
            priority=request.priority
        )
        
        return {
            "success": True,
            "message": "URL adicionada com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/config/urls/{url_id}")
async def remove_monitored_url(url_id: int):
    """Remover URL monitorada"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        manager.remove_monitored_url(url_id)
        
        return {
            "success": True,
            "message": "URL removida com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao remover URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/templates/add")
async def add_content_template(request: TemplateAddRequest):
    """Adicionar template de conteúdo"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        manager.add_content_template(
            template_name=request.template_name,
            product_type=request.product_type,
            title_template=request.title_template,
            content_template=request.content_template,
            meta_description_template=request.meta_description_template,
            keywords_template=request.keywords_template
        )
        
        return {
            "success": True,
            "message": "Template adicionado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# ROTAS PARA PREFERÊNCIAS DE GERAÇÃO
# =====================================================

@app.get("/config/products")
async def get_products(tipo: str = None, categoria: str = None):
    """Lista produtos disponíveis"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        products = manager.get_products(tipo=tipo, categoria=categoria)
        
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/products/sync")
async def sync_products():
    """Sincroniza produtos do ProductDatabase"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        manager.sync_products_from_database()
        
        # Contar produtos sincronizados
        products = manager.get_products()
        
        return {
            "success": True,
            "message": "Produtos sincronizados com sucesso",
            "products_count": len(products)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/generation-preferences")
async def get_generation_preferences():
    """Retorna preferências de geração atuais"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        
        preferences = {
            "allowed_categories": manager.get_allowed_categories(),
            "allowed_products": manager.get_allowed_products(),
            "filter_mode": manager.get_filter_mode()
        }
        
        return {
            "success": True,
            "preferences": preferences
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter preferências: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/generation-preferences/categories")
async def set_allowed_categories(request: dict):
    """Define categorias permitidas"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        categories = request.get('categories', [])
        
        manager = ConfigManager()
        manager.set_allowed_categories(categories)
        
        return {
            "success": True,
            "message": f"Categorias permitidas atualizadas: {len(categories)} categorias",
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao definir categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/generation-preferences/products")
async def set_allowed_products(request: dict):
    """Define produtos específicos permitidos"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        product_ids = request.get('product_ids', [])
        
        manager = ConfigManager()
        manager.set_allowed_products(product_ids)
        
        return {
            "success": True,
            "message": f"Produtos permitidos atualizados: {len(product_ids)} produtos",
            "product_count": len(product_ids)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao definir produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/generation-preferences/clear")
async def clear_generation_filters():
    """Remove todos os filtros de geração"""
    if not CONFIG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo config não disponível")
    
    try:
        manager = ConfigManager()
        manager.clear_generation_filters()
        
        return {
            "success": True,
            "message": "Filtros de geração removidos com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar filtros: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/env")
async def debug_env():
    """Debug das variáveis de ambiente (remover em produção)"""
    api_key = os.getenv('OPENAI_API_KEY')
    return {
        "openai_key_exists": bool(api_key),
        "openai_key_length": len(api_key) if api_key else 0,
        "openai_key_preview": f"{api_key[:10]}..." if api_key else "None",
        "working_directory": os.getcwd(),
        "env_files_exist": {
            ".env": os.path.exists(".env"),
            "../.env": os.path.exists("../.env")
        }
    }

@app.get("/debug/wordpress-auth")
async def debug_wordpress_auth():
    """Debug específico para autenticação WordPress"""
    try:
        from src.publisher.wordpress_client import WordPressClient
        
        # Obter credenciais das variáveis de ambiente
        wp_site_url = os.getenv('WP_SITE_URL')
        wp_username = os.getenv('WP_USERNAME') 
        wp_password = os.getenv('WP_PASSWORD')
        
        if not all([wp_site_url, wp_username, wp_password]):
            return {
                "error": "Credenciais WordPress não configuradas",
                "missing": {
                    "WP_SITE_URL": not wp_site_url,
                    "WP_USERNAME": not wp_username, 
                    "WP_PASSWORD": not wp_password
                }
            }
        
        # Testar conexão
        client = WordPressClient(wp_site_url, wp_username, wp_password)
        test_result = client.test_connection()
        
        # Informações adicionais
        debug_info = {
            "credentials": {
                "site_url": wp_site_url,
                "username": wp_username,
                "password_length": len(wp_password) if wp_password else 0,
                "password_preview": f"{wp_password[:4]}..." if wp_password else None
            },
            "test_result": test_result
        }
        
        # Testar criação de post de teste (se autenticado)
        if test_result.get('authenticated'):
            try:
                test_post = {
                    'title': 'Teste de Autenticação - Sistema SEO',
                    'content': '<p>Este é um post de teste para verificar autenticação. Pode ser removido.</p>',
                    'status': 'draft'  # Criar como rascunho
                }
                
                create_result = client.create_post(test_post)
                debug_info["create_test"] = {
                    "success": create_result is not None,
                    "post_id": create_result.get('id') if create_result else None
                }
                
                # Remover o post de teste se foi criado
                if create_result:
                    client.delete_post(create_result['id'], force=True)
                    debug_info["create_test"]["cleaned_up"] = True
                    
            except Exception as e:
                debug_info["create_test"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return debug_info
        
    except Exception as e:
        return {
            "error": f"Erro no diagnóstico: {str(e)}"
        }


# =====================================================
# ROTAS DO MÓDULO SCHEDULER
# =====================================================

@app.get("/scheduler")
async def scheduler_status():
    """Status do sistema de agendamento"""
    try:
        if not SCHEDULER_AVAILABLE:
            return {
                "success": False,
                "status": "disabled",
                "message": "Scheduler não está disponível - APScheduler não instalado",
                "available_jobs": [],
                "next_executions": []
            }
        
        if 'scheduler_manager' not in globals():
            return {
                "success": True,
                "status": "not_initialized",
                "message": "Scheduler ainda não foi inicializado",
                "available_jobs": [],
                "next_executions": []
            }
        
        status_data = scheduler_manager.get_status()
        
        # Adicionar informações de configuração
        status_data["configuration"] = {
            "base_url": scheduler_manager.base_url,
            "system_url": os.getenv('SYSTEM_BASE_URL', 'Não configurada'),
            "scheduler_url": os.getenv('SCHEDULER_BASE_URL', 'Não configurada'),
            "host": os.getenv('HOST', '0.0.0.0'),
            "port": os.getenv('PORT', '3025')
        }
        
        return {
            "success": True,
            "status": "operational" if status_data["is_running"] else "stopped",
            "scheduler": status_data,
            "message": f"Scheduler {'ativo' if status_data['is_running'] else 'parado'} com {len(status_data.get('jobs', []))} jobs configurados"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do scheduler: {e}")
        return {
            "success": False,
            "status": "error",
            "message": f"Erro ao obter status: {str(e)}",
            "error": str(e)
        }

@app.get("/scheduler/status")
async def get_scheduler_status():
    """Retorna status detalhado do scheduler"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        return scheduler_manager.get_status()
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/run")
async def run_scheduler_job_get(request: JobExecutionRequest = None):
    """Executa job do scheduler (GET)"""
    return await run_scheduler_job(request)

@app.post("/scheduler/run")
async def run_scheduler_job(request: JobExecutionRequest = None):
    """Executa job específico ou fluxo completo se não especificado"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        # Se nenhum job_id for especificado, executar fluxo completo
        if not request or not hasattr(request, 'job_id') or not request.job_id:
            logger.info("🚀 Executando fluxo completo automaticamente")
            result = scheduler_manager.run_complete_workflow()
            return {
                "success": True,
                "action": "complete_workflow", 
                "result": result,
                "message": "Fluxo completo executado com sucesso! Verifique a área de revisão para os novos artigos.",
                "redirect_to": "/review"
            }
        
        # Caso contrário, executar job específico
        result = scheduler_manager.run_job_manually(request.job_id)
        return {
            "success": True,
            "action": "specific_job",
            "result": result,
            "message": f"Job {request.job_id} executado com sucesso!"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scheduler/pause")
async def pause_scheduler():
    """Pausa todos os jobs do scheduler"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        result = scheduler_manager.pause()
        return result
    except Exception as e:
        logger.error(f"❌ Erro ao pausar scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scheduler/resume")
async def resume_scheduler():
    """Resume todos os jobs do scheduler"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        result = scheduler_manager.resume()
        return result
    except Exception as e:
        logger.error(f"❌ Erro ao resumir scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/next")
async def get_next_executions(hours: int = 24):
    """Retorna próximas execuções nas próximas X horas"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        executions = scheduler_manager.get_next_executions(hours)
        return {
            "next_executions": executions,
            "period_hours": hours,
            "count": len(executions)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter próximas execuções: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/stats")
async def get_scheduler_stats():
    """Retorna estatísticas do scheduler"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        status = scheduler_manager.get_status()
        jobs = status.get('jobs', [])
        recent_executions = status.get('recent_executions', [])
        
        # Calcular estatísticas
        active_jobs = len([j for j in jobs if j.get('id')])
        executions_today = len([e for e in recent_executions 
                              if e.get('execution_time', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
        success_rate = 0
        if recent_executions:
            successes = len([e for e in recent_executions if e.get('status') == 'success'])
            success_rate = round((successes / len(recent_executions)) * 100, 1)
        
        # Próxima execução
        next_execution = None
        if jobs:
            next_runs = [j.get('next_run') for j in jobs if j.get('next_run')]
            if next_runs:
                next_execution = min(next_runs)
        
        return {
            "success": True,
            "statistics": {
                "active_jobs": active_jobs,
                "executions_today": executions_today,
                "success_rate": success_rate,
                "next_execution": next_execution,
                "total_jobs_configured": len(jobs),
                "scheduler_running": status.get('is_running', False)
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/jobs")
async def get_scheduler_jobs():
    """Retorna lista de jobs do scheduler"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        status = scheduler_manager.get_status()
        jobs = status.get('jobs', [])
        
        # Formatar jobs para o frontend
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                'id': job.get('id'),
                'name': job.get('name'),
                'status': 'active' if status.get('is_running') else 'paused',
                'schedule': job.get('trigger', 'N/A'),
                'next_run': job.get('next_run'),
                'last_run': None,  # Podemos melhorar isso depois
                'task_type': job.get('func_name', 'Unknown'),
                'description': f"Job automático: {job.get('name', 'Sem nome')}"
            })
        
        return {
            "success": True,
            "jobs": formatted_jobs,
            "count": len(formatted_jobs)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/history")
async def get_scheduler_history():
    """Retorna histórico de execuções"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        status = scheduler_manager.get_status()
        return {
            "recent_executions": status.get("recent_executions", []),
            "count": len(status.get("recent_executions", []))
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/debug")
async def scheduler_debug():
    """Debug completo do scheduler"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        return {"error": "Scheduler não disponível"}
    
    try:
        status = scheduler_manager.get_status()
        return {
            "timestamp": datetime.now().isoformat(),
            "scheduler_available": SCHEDULER_AVAILABLE,
            "scheduler_manager_exists": 'scheduler_manager' in globals(),
            "status": status,
            "raw_response": status
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/scheduler/progress")
async def get_workflow_progress():
    """Retorna o progresso atual do fluxo de trabalho"""
    if not SCHEDULER_AVAILABLE or 'scheduler_manager' not in globals():
        raise HTTPException(status_code=503, detail="Módulo scheduler não disponível")
    
    try:
        # Verificar o status atual do sistema
        status = {}
        
        # Verificar scraper
        if SCRAPER_AVAILABLE:
            try:
                scraper_manager = ScraperManager()
                scraper_data = scraper_manager.get_scraping_status()
                status['scraper'] = {
                    'running': scraper_data.get('is_running', False),
                    'progress': scraper_data.get('progress_percentage', 0),
                    'message': scraper_data.get('status_message', 'Aguardando...')
                }
            except:
                status['scraper'] = {'running': False, 'progress': 0, 'message': 'Inativo'}
        
        # Verificar generator
        if GENERATOR_AVAILABLE:
            try:
                gen_manager = GeneratorManager()
                gen_stats = gen_manager.get_stats()
                status['generator'] = {
                    'running': gen_stats.get('is_processing', False),
                    'progress': gen_stats.get('progress_percentage', 0),
                    'message': gen_stats.get('status_message', 'Aguardando...')
                }
            except:
                status['generator'] = {'running': False, 'progress': 0, 'message': 'Inativo'}
        
        # Verificar histórico recente do scheduler
        scheduler_status = scheduler_manager.get_status()
        recent_executions = scheduler_status.get('recent_executions', [])
        
        # Determinar status geral
        overall_status = 'idle'
        if any(s.get('running', False) for s in status.values()):
            overall_status = 'running'
        
        return {
            'status': overall_status,
            'modules': status,
            'recent_executions': recent_executions[:3],  # Últimas 3 execuções
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter progresso: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ROTAS DE INTERFACE VISUAL
# =====================================================

@app.get("/interface/scraper", response_class=HTMLResponse)
async def scraper_interface():
    """Interface visual para o módulo Scraper"""
    if not SCRAPER_AVAILABLE:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Módulo Scraper Indisponível</h1>
        <p>O módulo de scraping não está disponível.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    
    try:
        with open("templates/scraper_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
        
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Template não encontrado</h1>
        <p>O arquivo de template não foi encontrado.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    except Exception as e:
        logger.error(f"Erro na interface do scraper: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/interface/generator", response_class=HTMLResponse)
async def generator_interface():
    """Interface visual para o módulo Generator"""
    if not GENERATOR_AVAILABLE:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Módulo Generator Indisponível</h1>
        <p>O módulo de geração não está disponível.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    
    try:
        with open("templates/generator_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
        
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Template não encontrado</h1>
        <p>O arquivo de template não foi encontrado.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    except Exception as e:
        logger.error(f"Erro na interface do generator: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/interface/publisher", response_class=HTMLResponse)
async def publisher_interface():
    """Interface visual para o módulo Publisher"""
    if not PUBLISHER_AVAILABLE:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Módulo Publisher Indisponível</h1>
        <p>O módulo de publicação não está disponível.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    
    try:
        with open("templates/publisher_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
        
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Template não encontrado</h1>
        <p>O arquivo de template não foi encontrado.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    except Exception as e:
        logger.error(f"Erro na interface do publisher: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/interface/scheduler", response_class=HTMLResponse)
async def scheduler_interface():
    """Interface visual para o módulo Scheduler"""
    if not SCHEDULER_AVAILABLE:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Módulo Scheduler Indisponível</h1>
        <p>O módulo de agendamento não está disponível.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    
    try:
        with open("templates/scheduler_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Adicionar timestamp para evitar cache
        from datetime import datetime
        timestamp = int(datetime.now().timestamp())
        html_content = html_content.replace("{{ timestamp }}", str(timestamp))
        
        return HTMLResponse(html_content)
        
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Template não encontrado</h1>
        <p>O arquivo de template não foi encontrado.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    except Exception as e:
        logger.error(f"Erro na interface do scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/interface/review", response_class=HTMLResponse)
async def review_interface():
    """Interface visual para o módulo Review"""
    if not REVIEW_AVAILABLE:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Módulo Review Indisponível</h1>
        <p>O módulo de revisão não está disponível.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    
    try:
        with open("templates/review_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
        
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Template não encontrado</h1>
        <p>O arquivo de template não foi encontrado.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    except Exception as e:
        logger.error(f"Erro na interface do review: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/interface/config", response_class=HTMLResponse)
async def config_interface():
    """Interface de configuração do sistema"""
    try:
        return templates.TemplateResponse("config.html", {"request": {}})
    except Exception as e:
        logger.error(f"❌ Erro ao carregar interface de config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interface/categorias", response_class=HTMLResponse)
async def categorias_config():
    """Interface de configuração de categorias"""
    try:
        return templates.TemplateResponse("categoria_config.html", {"request": {}})
    except Exception as e:
        logger.error(f"❌ Erro ao carregar interface de categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ROTAS DE API PARA GERENCIAMENTO DE CATEGORIAS ===

@app.get("/config/categories")
async def get_categories():
    """Listar todas as categorias configuradas"""
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        manager = ActiveCategoriesManager()
        categories = manager.get_all_categories()
        
        return {
            "success": True,
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter categorias: {e}")
        return {"success": False, "error": str(e)}

@app.post("/config/categories")
async def add_category(category_data: dict):
    """Adicionar nova categoria"""
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        manager = ActiveCategoriesManager()
        
        # Validar dados
        required_fields = ['category_name', 'category_key', 'category_url']
        for field in required_fields:
            if field not in category_data:
                raise ValueError(f"Campo obrigatório: {field}")
        
        # Adicionar categoria
        success = manager.add_category(
            category_key=category_data['category_key'],
            category_name=category_data['category_name'],
            category_url=category_data['category_url']
        )
        
        if success:
            return {"success": True, "message": "Categoria adicionada com sucesso"}
        else:
            return {"success": False, "error": "Erro ao adicionar categoria"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar categoria: {e}")
        return {"success": False, "error": str(e)}

@app.patch("/config/categories/{category_key}")
async def update_category(category_key: str, update_data: dict):
    """Atualizar categoria existente"""
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        manager = ActiveCategoriesManager()
        
        success = manager.update_category(category_key, update_data)
        
        if success:
            return {"success": True, "message": "Categoria atualizada com sucesso"}
        else:
            return {"success": False, "error": "Categoria não encontrada"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar categoria: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/config/categories/{category_key}")
async def remove_category(category_key: str):
    """Remover categoria"""
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        manager = ActiveCategoriesManager()
        
        success = manager.remove_category(category_key)
        
        if success:
            return {"success": True, "message": "Categoria removida com sucesso"}
        else:
            return {"success": False, "error": "Categoria não encontrada"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao remover categoria: {e}")
        return {"success": False, "error": str(e)}

@app.get("/config/categories/{category_key}/test")
async def test_category(category_key: str):
    """Testar categoria (verificar quantos produtos existem)"""
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        manager = ActiveCategoriesManager()
        
        # Buscar categoria
        category = manager.get_category(category_key)
        if not category:
            return {"success": False, "error": "Categoria não encontrada"}
        
        # Obter contagem real de produtos
        products_found = manager.get_category_product_count(category_key)
        
        return {
            "success": True,
            "products_found": products_found,
            "message": f"Categoria {category['category_name']} possui {products_found} produtos"
        }
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar categoria: {e}")
        return {"success": False, "error": str(e)}

@app.post("/config/categories/update-counts")
async def update_categories_counts():
    """Atualizar contagem de produtos em todas as categorias"""
    try:
        from .config.active_categories_manager import ActiveCategoriesManager
        manager = ActiveCategoriesManager()
        
        success = manager.update_products_count_from_scraper()
        
        if success:
            # Retornar categorias atualizadas
            categories = manager.get_all_categories()
            total_products = sum(cat.get('products_count', 0) for cat in categories)
            
            return {
                "success": True,
                "message": "Contagens atualizadas com sucesso",
                "total_products": total_products,
                "categories": categories
            }
        else:
            return {"success": False, "error": "Erro ao atualizar contagens"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar contagens: {e}")
        return {"success": False, "error": str(e)}

@app.get("/test-template", response_class=HTMLResponse)
async def test_template():
    """Endpoint de teste para verificar se os templates estão funcionando"""
    try:
        with open("templates/test_simple.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
        
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Template de teste não encontrado</h1>
        <p>O arquivo de template de teste não foi encontrado.</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)
    except Exception as e:
        logger.error(f"Erro no template de teste: {e}")
        return HTMLResponse(f"""
        <html><body style="text-align:center; font-family: Arial; padding: 50px; background: #0a0a0a; color: white;">
        <h1>❌ Erro no Template</h1>
        <p>Erro: {str(e)}</p>
        <a href="/" style="color: #007aff;">← Voltar ao Dashboard</a>
        </body></html>
        """)


@app.get("/debug-scraper-template")
async def debug_scraper_template():
    """Debug do template do scraper"""
    try:
        import os
        template_path = "templates/scraper_interface.html"
        
        # Verificar se arquivo existe
        if not os.path.exists(template_path):
            return JSONResponse({
                "error": "Template não encontrado",
                "path": template_path,
                "exists": False
            })
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(template_path)
        
        # Tentar ler o arquivo
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return JSONResponse({
            "success": True,
            "path": template_path,
            "exists": True,
            "file_size": file_size,
            "content_length": len(content),
            "first_100_chars": content[:100],
            "last_100_chars": content[-100:],
            "scraper_available": SCRAPER_AVAILABLE
        })
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "type": type(e).__name__
        })


# =====================================================
# TRATAMENTO DE ERROS
# =====================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Tratamento de páginas não encontradas"""
    
    # Verificar se a requisição espera JSON
    accept_header = request.headers.get("accept", "")
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in accept_header or "application/json" in content_type or request.url.path.startswith("/review/") or request.url.path.startswith("/api/"):
        return JSONResponse({
            "success": False,
            "error": "Endpoint não encontrado",
            "status_code": 404,
            "path": str(request.url.path)
        }, status_code=404, headers={"Content-Type": "application/json; charset=utf-8"})
    
    # Retornar HTML para requisições de browser
    return HTMLResponse(
        content="""
        <html>
            <body style="font-family: Arial; text-align: center; margin-top: 50px; background: #0a0a0a; color: white;">
                <h1>404 - Página não encontrada</h1>
                <p>A página que você procura não existe.</p>
                <a href="/" style="color: #007aff;">Voltar ao Dashboard</a>
            </body>
        </html>
        """,
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Tratamento de erros internos"""
    logger.error(f"Erro interno: {exc}")
    
    # Verificar se a requisição espera JSON
    accept_header = request.headers.get("accept", "")
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in accept_header or "application/json" in content_type or request.url.path.startswith("/review/") or request.url.path.startswith("/api/"):
        return JSONResponse({
            "success": False,
            "error": "Erro interno do servidor",
            "status_code": 500,
            "path": str(request.url.path)
        }, status_code=500, headers={"Content-Type": "application/json; charset=utf-8"})
    
    # Retornar HTML para requisições de browser
    return HTMLResponse(
        content="""
        <html>
            <body style="font-family: Arial; text-align: center; margin-top: 50px; background: #0a0a0a; color: white;">
                <h1>500 - Erro interno do servidor</h1>
                <p>Ocorreu um erro interno. Verifique os logs.</p>
                <a href="/" style="color: #007aff;">Voltar ao Dashboard</a>
            </body>
        </html>
        """,
        status_code=500
    )

@app.get("/test_status.html", response_class=HTMLResponse)
async def test_status_page():
    """Página de teste para verificar status do sistema"""
    try:
        with open("test_status.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo de teste não encontrado")

@app.get("/test_generator_stats.html", response_class=HTMLResponse)
async def test_generator_stats_page():
    """Página de teste para verificar estatísticas do generator"""
    try:
        with open("test_generator_stats.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo de teste não encontrado")


# =====================================================
# WEEKLY ARCHIVE ENDPOINTS - Sistema de Arquivos Semanais
# =====================================================

# ===== NOVAS ROTAS DE CONFIGURAÇÃO =====

# Configurações da API
@app.get("/config/api")
async def get_api_config():
    """Obter configurações da API OpenAI"""
    try:
        config = {}
        if CONFIG_AVAILABLE:
            try:
                config_manager = ConfigManager()
                # Obter cada configuração individualmente
                api_key = config_manager.get_config("api_settings", "api_key", "")
                model = config_manager.get_config("api_settings", "model", "")
                temperature = config_manager.get_config("api_settings", "temperature", "0.7")
                config = {
                    "api_key": api_key,
                    "model": model,
                    "temperature": temperature
                }
            except:
                config = {}
        
        return {
            "api_key": config.get("api_key", os.getenv("OPENAI_API_KEY", "")),
            "model": config.get("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
            "temperature": float(config.get("temperature", os.getenv("OPENAI_TEMPERATURE", "0.7")))
        }
    except Exception as e:
        logger.error(f"Erro ao obter configurações da API: {e}")
        return {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        }

@app.post("/config/api")
async def save_api_config(config_data: dict):
    """Salvar configurações da API OpenAI"""
    try:
        if CONFIG_AVAILABLE:
            config_manager = ConfigManager()
            
            # Atualizar variáveis de ambiente
            if config_data.get("api_key"):
                os.environ["OPENAI_API_KEY"] = config_data["api_key"]
            if config_data.get("model"):
                os.environ["OPENAI_MODEL"] = config_data["model"]
            if config_data.get("temperature") is not None:
                os.environ["OPENAI_TEMPERATURE"] = str(config_data["temperature"])
            
            # Salvar no config manager
            config_manager.set_config("api_settings", "api_config", config_data)
            
            logger.info("✅ Configurações da API salvas com sucesso")
            return {"success": True, "message": "Configurações da API salvas com sucesso"}
        else:
            # Fallback: apenas atualizar variáveis de ambiente
            if config_data.get("api_key"):
                os.environ["OPENAI_API_KEY"] = config_data["api_key"]
            if config_data.get("model"):
                os.environ["OPENAI_MODEL"] = config_data["model"]
            if config_data.get("temperature") is not None:
                os.environ["OPENAI_TEMPERATURE"] = str(config_data["temperature"])
            
            return {"success": True, "message": "Configurações da API salvas nas variáveis de ambiente"}
            
    except Exception as e:
        logger.error(f"Erro ao salvar configurações da API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configurações do WordPress
@app.get("/config/wordpress")
async def get_wordpress_config():
    """Obter configurações do WordPress"""
    try:
        config = {}
        if CONFIG_AVAILABLE:
            try:
                config_manager = ConfigManager()
                # Obter cada configuração individualmente
                site_url = config_manager.get_config("wordpress_settings", "site_url", "")
                username = config_manager.get_config("wordpress_settings", "username", "")
                password = config_manager.get_config("wordpress_settings", "password", "")
                config = {
                    "site_url": site_url,
                    "username": username,
                    "password": password
                }
            except:
                config = {}
        
        return {
            "site_url": config.get("site_url", os.getenv("WP_SITE_URL", "")),
            "username": config.get("username", os.getenv("WP_USERNAME", "")),
            "password": config.get("password", os.getenv("WP_PASSWORD", ""))
        }
    except Exception as e:
        logger.error(f"Erro ao obter configurações do WordPress: {e}")
        return {
            "site_url": os.getenv("WP_SITE_URL", ""),
            "username": os.getenv("WP_USERNAME", ""),
            "password": os.getenv("WP_PASSWORD", "")
        }

@app.post("/config/wordpress")
async def save_wordpress_config(config_data: dict):
    """Salvar configurações do WordPress"""
    try:
        if CONFIG_AVAILABLE:
            config_manager = ConfigManager()
            
            # Atualizar variáveis de ambiente
            if config_data.get("site_url"):
                os.environ["WP_SITE_URL"] = config_data["site_url"]
                os.environ["WORDPRESS_URL"] = config_data["site_url"] + "/wp-json/wp/v2/"
            if config_data.get("username"):
                os.environ["WP_USERNAME"] = config_data["username"]
                os.environ["WORDPRESS_USERNAME"] = config_data["username"]
            if config_data.get("password"):
                os.environ["WP_PASSWORD"] = config_data["password"]
            
            # Salvar no config manager
            config_manager.set_config("wordpress_settings", "wp_config", config_data)
            
            logger.info("✅ Configurações do WordPress salvas com sucesso")
            return {"success": True, "message": "Configurações do WordPress salvas com sucesso"}
        else:
            # Fallback: apenas atualizar variáveis de ambiente
            if config_data.get("site_url"):
                os.environ["WP_SITE_URL"] = config_data["site_url"]
                os.environ["WORDPRESS_URL"] = config_data["site_url"] + "/wp-json/wp/v2/"
            if config_data.get("username"):
                os.environ["WP_USERNAME"] = config_data["username"]
                os.environ["WORDPRESS_USERNAME"] = config_data["username"]
            if config_data.get("password"):
                os.environ["WP_PASSWORD"] = config_data["password"]
                
            return {"success": True, "message": "Configurações do WordPress salvas nas variáveis de ambiente"}
            
    except Exception as e:
        logger.error(f"Erro ao salvar configurações do WordPress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/wordpress/test")
async def test_wordpress_connection_config(config_data: dict):
    """Testar conexão com WordPress"""
    try:
        if PUBLISHER_AVAILABLE:
            # Criar publisher temporário com as configurações fornecidas
            temp_wp_url = config_data.get("site_url", "").rstrip('/') + "/wp-json/wp/v2/"
            temp_username = config_data.get("username", "")
            temp_password = config_data.get("password", "")
            
            # Testar conexão básica
            import requests
            from requests.auth import HTTPBasicAuth
            
            response = requests.get(
                temp_wp_url + "users/me",
                auth=HTTPBasicAuth(temp_username, temp_password),
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True, 
                    "message": f"Conexão bem-sucedida! Usuário: {user_data.get('name', 'N/A')}"
                }
            else:
                return {
                    "success": False, 
                    "message": f"Falha na autenticação (HTTP {response.status_code})"
                }
        else:
            return {"success": False, "message": "Módulo publisher não disponível"}
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão WordPress: {e}")
        return {"success": False, "message": f"Erro na conexão: {str(e)}"}

# Configurações gerais
@app.get("/config/geral")
async def get_geral_config():
    """Obter configurações gerais"""
    try:
        config = {}
        if CONFIG_AVAILABLE:
            try:
                config_manager = ConfigManager()
                # Obter cada configuração individualmente
                linguagem = config_manager.get_config("geral_settings", "linguagem", "pt-BR")
                tom_conteudo = config_manager.get_config("geral_settings", "tom_conteudo", "profissional")
                palavras_min = config_manager.get_config("geral_settings", "palavras_min", "500")
                palavras_max = config_manager.get_config("geral_settings", "palavras_max", "1500")
                config = {
                    "linguagem": linguagem,
                    "tom_conteudo": tom_conteudo,
                    "palavras_min": palavras_min,
                    "palavras_max": palavras_max
                }
            except:
                config = {}
        
        return {
            "linguagem": config.get("linguagem", "pt-BR"),
            "tom_conteudo": config.get("tom_conteudo", "profissional"),
            "palavras_min": int(config.get("palavras_min", os.getenv("CONTENT_MIN_WORDS", "500"))),
            "palavras_max": int(config.get("palavras_max", os.getenv("CONTENT_MAX_WORDS", "1500")))
        }
    except Exception as e:
        logger.error(f"Erro ao obter configurações gerais: {e}")
        return {
            "linguagem": "pt-BR",
            "tom_conteudo": "profissional",
            "palavras_min": int(os.getenv("CONTENT_MIN_WORDS", "500")),
            "palavras_max": int(os.getenv("CONTENT_MAX_WORDS", "1500"))
        }

@app.post("/config/geral")
async def save_geral_config(config_data: dict):
    """Salvar configurações gerais"""
    try:
        if CONFIG_AVAILABLE:
            config_manager = ConfigManager()
            
            # Atualizar variáveis de ambiente
            if config_data.get("palavras_min"):
                os.environ["CONTENT_MIN_WORDS"] = str(config_data["palavras_min"])
            if config_data.get("palavras_max"):
                os.environ["CONTENT_MAX_WORDS"] = str(config_data["palavras_max"])
            
            # Salvar no config manager
            config_manager.set_config("geral_settings", "general_config", config_data)
            
            logger.info("✅ Configurações gerais salvas com sucesso")
            return {"success": True, "message": "Configurações gerais salvas com sucesso"}
        else:
            # Fallback: apenas atualizar variáveis de ambiente
            if config_data.get("palavras_min"):
                os.environ["CONTENT_MIN_WORDS"] = str(config_data["palavras_min"])
            if config_data.get("palavras_max"):
                os.environ["CONTENT_MAX_WORDS"] = str(config_data["palavras_max"])
                
            return {"success": True, "message": "Configurações gerais salvas nas variáveis de ambiente"}
            
    except Exception as e:
        logger.error(f"Erro ao salvar configurações gerais: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configurações da agenda
@app.get("/config/agenda")
async def get_agenda_config():
    """Obter configurações da agenda"""
    try:
        config = {}
        next_execution = "Scheduler não disponível"
        last_execution = "Scheduler não disponível"
        
        if CONFIG_AVAILABLE:
            try:
                config_manager = ConfigManager()
                # Obter cada configuração individualmente
                dia_execucao = config_manager.get_config("agenda_settings", "dia_execucao", "0")
                horario_execucao = config_manager.get_config("agenda_settings", "horario_execucao", "10:00")
                config = {
                    "dia_execucao": dia_execucao,
                    "horario_execucao": horario_execucao
                }
            except:
                config = {}
                
        if SCHEDULER_AVAILABLE:
            try:
                scheduler_manager = SchedulerManager()
                scheduler_status = scheduler_manager.get_status()
                
                # Verificar se há jobs programados
                if scheduler_status.get("is_running") and scheduler_status.get("jobs"):
                    jobs = scheduler_status.get("jobs", [])
                    if jobs:
                        # Pegar o próximo job programado
                        next_job = min(jobs, key=lambda x: x.get("next_run", "9999-12-31T23:59:59"))
                        next_execution = f"Domingo às 10:00 (Programada)"
                    else:
                        next_execution = "Domingo às 10:00 (Programada)"
                    
                    # Verificar execuções recentes
                    recent_executions = scheduler_status.get("recent_executions", [])
                    if recent_executions:
                        last_execution = f"Última execução: {recent_executions[0].get('execution_time', 'N/A')}"
                    else:
                        last_execution = "Sistema ativo - aguardando primeira execução"
                else:
                    next_execution = "Domingo às 10:00 (Programada)"
                    last_execution = "Sistema ativo - aguardando primeira execução"
            except Exception as e:
                logger.warning(f"Erro ao obter status do scheduler: {e}")
                next_execution = "Domingo às 10:00 (Programada)"
                last_execution = "Sistema ativo"
        
        return {
            "dia_execucao": int(config.get("dia_execucao", "0")),  # 0 = Domingo
            "horario_execucao": config.get("horario_execucao", "10:00"),
            "next_execution": next_execution,
            "last_execution": last_execution
        }
    except Exception as e:
        logger.error(f"Erro ao obter configurações da agenda: {e}")
        return {
            "dia_execucao": 0,
            "horario_execucao": "10:00",
            "next_execution": "Erro no scheduler",
            "last_execution": "Erro no scheduler"
        }

@app.post("/config/agenda")
async def save_agenda_config(config_data: dict):
    """Salvar configurações da agenda"""
    try:
        if CONFIG_AVAILABLE:
            config_manager = ConfigManager()
            
            # Salvar no config manager
            config_manager.set_config("agenda_settings", "schedule_config", config_data)
            
            # Se o scheduler estiver disponível, reconfigurar
            if SCHEDULER_AVAILABLE:
                try:
                    scheduler_manager = SchedulerManager()
                    
                    # Apenas logar a tentativa de reconfiguração (o scheduler já está configurado no startup)
                    dia_semana = int(config_data.get("dia_execucao", 0))
                    horario = config_data.get("horario_execucao", "10:00")
                    
                    logger.info(f"✅ Configuração da agenda atualizada: {['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'][dia_semana]} às {horario}")
                except Exception as scheduler_error:
                    logger.warning(f"Erro ao reconfigurar scheduler: {scheduler_error}")
            
            logger.info("✅ Configurações da agenda salvas com sucesso")
            return {"success": True, "message": "Configurações da agenda salvas com sucesso"}
        else:
            return {"success": False, "message": "Config manager não disponível"}
            
    except Exception as e:
        logger.error(f"Erro ao salvar configurações da agenda: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Gerenciamento de categorias (rotas para a seção de categorias)
@app.get("/api/categories")
async def get_categories_list():
    """Obter lista completa de categorias para gerenciamento"""
    try:
        formatted_categories = []
        
        # TEMPORÁRIO: Pular ActiveCategoriesManager e ir direto para Scraper para obter nomes reais
        logger.info("🔄 Pulando ActiveCategoriesManager para obter nomes reais das categorias do scraper")
        
        # Ir direto para o scraper para obter categorias com nomes reais
        if SCRAPER_AVAILABLE:
            try:
                scraper_manager = ScraperManager()
                # Obter URLs das categorias configuradas
                category_urls = scraper_manager.url_manager.get_category_urls()
                
                for i, url in enumerate(category_urls):
                    # Extrair nome da categoria da URL de forma mais inteligente
                    url_parts = [part for part in url.split('/') if part and part != 'https:' and part != 'www.creativecopias.com.br']
                    
                    if url_parts:
                        # Pegar a parte que representa a categoria
                        category_slug = url_parts[-1] if url_parts[-1] else (url_parts[-2] if len(url_parts) > 1 else f"categoria-{i+1}")
                        
                        # Converter slug para nome legível
                        category_name = category_slug.replace('-', ' ').replace('_', ' ')
                        # Capitalizar cada palavra corretamente
                        category_name = ' '.join(word.capitalize() for word in category_name.split())
                        
                        # Melhorar nomes específicos conhecidos
                        improvements = {
                            'Hp': 'HP',
                            'Impressoras Hp': 'Impressoras HP',
                            'Canon': 'Canon',
                            'Epson': 'Epson',
                            'Brother': 'Brother',
                            'Toners': 'Toners',
                            'Cartuchos': 'Cartuchos',
                            'Plotters': 'Plotters'
                        }
                        
                        for key, value in improvements.items():
                            if key.lower() in category_name.lower():
                                category_name = category_name.replace(key, value)
                    else:
                        category_name = f"Categoria {i+1}"
                    
                    # Obter contagem básica de produtos (simplificado)
                    products_count = 0  # Será atualizado dinamicamente pelo sistema
                    
                    formatted_categories.append({
                        "id": f"cat_{i}",
                        "name": category_name,
                        "url": url,
                        "active": True,
                        "products_count": products_count,
                        "created_at": datetime.now().isoformat()
                    })
                    
            except Exception as scraper_error:
                logger.warning(f"Erro ao acessar categorias do scraper: {scraper_error}")
        
        return formatted_categories
                
    except Exception as e:
        logger.error(f"Erro ao obter categorias: {e}")
        return []

@app.post("/api/categories")
async def add_new_category(category_data: dict):
    """Adicionar nova categoria"""
    try:
        url = category_data.get("url", "")
        if not url:
            raise HTTPException(status_code=400, detail="URL é obrigatória")
        
        if CATEGORIES_AVAILABLE:
            categories_manager = ActiveCategoriesManager()
            
            # Extrair nome da categoria da URL de forma mais inteligente
            url_parts = [part for part in url.split('/') if part and part != 'https:' and part != 'www.creativecopias.com.br']
            
            if url_parts:
                # Pegar a parte que representa a categoria
                category_slug = url_parts[-1] if url_parts[-1] else (url_parts[-2] if len(url_parts) > 1 else "nova-categoria")
                
                # Converter slug para nome legível
                category_name = category_slug.replace('-', ' ').replace('_', ' ')
                # Capitalizar cada palavra corretamente
                category_name = ' '.join(word.capitalize() for word in category_name.split())
                
                # Melhorar nomes específicos conhecidos
                improvements = {
                    'Hp': 'HP',
                    'Impressoras Hp': 'Impressoras HP',
                    'Canon': 'Canon',
                    'Epson': 'Epson',
                    'Brother': 'Brother',
                    'Toners': 'Toners',
                    'Cartuchos': 'Cartuchos',
                    'Plotters': 'Plotters'
                }
                
                for key, value in improvements.items():
                    if key.lower() in category_name.lower():
                        category_name = category_name.replace(key, value)
            else:
                category_name = "Nova Categoria"
            
            # Adicionar categoria
            category_key = categories_manager.add_category(
                name=category_name,
                url=url,
                is_active=True
            )
            
            # Se o scraper estiver disponível, tentar fazer scraping da categoria
            if SCRAPER_AVAILABLE:
                try:
                    scraper_manager = ScraperManager()
                    scraper_manager.add_category_url(url, category_name)
                    logger.info(f"Categoria {category_name} adicionada ao scraper")
                except Exception as scraper_error:
                    logger.warning(f"Erro ao adicionar categoria ao scraper: {scraper_error}")
            
            logger.info(f"✅ Nova categoria adicionada: {category_name}")
            return {"success": True, "message": f"Categoria '{category_name}' adicionada com sucesso", "category_id": category_key}
        else:
            # Fallback: adicionar apenas ao scraper se disponível
            if SCRAPER_AVAILABLE:
                scraper_manager = ScraperManager()
                
                # Usar a mesma lógica de extração de nome
                url_parts = [part for part in url.split('/') if part and part != 'https:' and part != 'www.creativecopias.com.br']
                
                if url_parts:
                    category_slug = url_parts[-1] if url_parts[-1] else (url_parts[-2] if len(url_parts) > 1 else "nova-categoria")
                    category_name = category_slug.replace('-', ' ').replace('_', ' ')
                    category_name = ' '.join(word.capitalize() for word in category_name.split())
                    
                    # Melhorar nomes específicos
                    improvements = {
                        'Hp': 'HP', 'Impressoras Hp': 'Impressoras HP',
                        'Canon': 'Canon', 'Epson': 'Epson', 'Brother': 'Brother',
                        'Toners': 'Toners', 'Cartuchos': 'Cartuchos', 'Plotters': 'Plotters'
                    }
                    
                    for key, value in improvements.items():
                        if key.lower() in category_name.lower():
                            category_name = category_name.replace(key, value)
                else:
                    category_name = "Nova Categoria"
                
                scraper_manager.add_category_url(url, category_name)
                return {"success": True, "message": f"Categoria '{category_name}' adicionada ao scraper"}
            else:
                raise HTTPException(status_code=500, detail="Nenhum sistema de categorias disponível")
                
    except Exception as e:
        logger.error(f"Erro ao adicionar categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/categories/{category_id}/toggle")
async def toggle_category_status(category_id: str, status_data: dict):
    """Ativar/desativar categoria"""
    try:
        new_status = status_data.get("active", True)
        
        if CATEGORIES_AVAILABLE:
            categories_manager = ActiveCategoriesManager()
            categories_manager.set_category_status(category_id, new_status)
            
            action = "ativada" if new_status else "desativada"
            logger.info(f"✅ Categoria {category_id} {action}")
            return {"success": True, "message": f"Categoria {action} com sucesso"}
        else:
            return {"success": False, "message": "Sistema de categorias não disponível"}
            
    except Exception as e:
        logger.error(f"Erro ao alterar status da categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/categories/{category_id}")
async def remove_category(category_id: str):
    """Remover categoria"""
    try:
        if CATEGORIES_AVAILABLE:
            categories_manager = ActiveCategoriesManager()
            categories_manager.remove_category(category_id)
            
            logger.info(f"✅ Categoria {category_id} removida")
            return {"success": True, "message": "Categoria removida com sucesso"}
        else:
            return {"success": False, "message": "Sistema de categorias não disponível"}
            
    except Exception as e:
        logger.error(f"Erro ao remover categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categories/sync")
async def sync_all_categories():
    """Sincronizar todas as categorias"""
    try:
        synced_count = 0
        
        if SCRAPER_AVAILABLE:
            scraper_manager = ScraperManager()
            # Executar descoberta de categorias
            discovery_result = scraper_manager.discover_categories()
            synced_count = len(discovery_result.get("discovered_categories", []))
        
        if CATEGORIES_AVAILABLE:
            categories_manager = ActiveCategoriesManager()
            categories_manager.sync_with_scraper()
        
        logger.info(f"✅ Sincronização concluída: {synced_count} categorias")
        return {"success": True, "message": f"Sincronização concluída: {synced_count} categorias processadas"}
        
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/categories/enable-all")
async def enable_all_categories():
    """Ativar todas as categorias"""
    try:
        if CATEGORIES_AVAILABLE:
            categories_manager = ActiveCategoriesManager()
            categories = categories_manager.get_all_categories()
            
            count = 0
            for category_id in categories.keys():
                categories_manager.set_category_status(category_id, True)
                count += 1
            
            logger.info(f"✅ {count} categorias ativadas")
            return {"success": True, "message": f"{count} categorias ativadas com sucesso"}
        else:
            return {"success": False, "message": "Sistema de categorias não disponível"}
            
    except Exception as e:
        logger.error(f"Erro ao ativar categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/categories/disable-all")
async def disable_all_categories():
    """Desativar todas as categorias"""
    try:
        if CATEGORIES_AVAILABLE:
            categories_manager = ActiveCategoriesManager()
            categories = categories_manager.get_all_categories()
            
            count = 0
            for category_id in categories.keys():
                categories_manager.set_category_status(category_id, False)
                count += 1
            
            logger.info(f"✅ {count} categorias desativadas")
            return {"success": True, "message": f"{count} categorias desativadas com sucesso"}
        else:
            return {"success": False, "message": "Sistema de categorias não disponível"}
            
    except Exception as e:
        logger.error(f"Erro ao desativar categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== FIM DAS NOVAS ROTAS DE CONFIGURAÇÃO =====

@app.get("/archive")
async def archive_status():
    """Status do sistema de arquivos semanais"""
    try:
        from src.review.weekly_archive import WeeklyArchiveManager
        archive_manager = WeeklyArchiveManager()
        
        stats = archive_manager.get_statistics()
        current_week = archive_manager.get_current_week_info()
        
        return {
            "module": "weekly_archive",
            "status": "ready",
            "description": "Sistema de arquivamento semanal de artigos",
            "data": {
                "current_week": f"{current_week['year']}-W{current_week['week_number']:02d}",
                "current_week_range": f"{current_week['start_date']} a {current_week['end_date']}",
                **stats
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro no status do archive: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/archive/sessions")
async def get_weekly_sessions(limit: int = 10):
    """Lista de sessões semanais arquivadas"""
    try:
        from src.review.weekly_archive import WeeklyArchiveManager
        archive_manager = WeeklyArchiveManager()
        
        sessions = archive_manager.get_weekly_sessions(limit=limit)
        
        return {
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter sessões: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/archive/sessions/{session_id}/articles")
async def get_session_articles(session_id: int):
    """Artigos de uma sessão semanal específica"""
    try:
        from src.review.weekly_archive import WeeklyArchiveManager
        archive_manager = WeeklyArchiveManager()
        
        articles = archive_manager.get_articles_from_week(session_id)
        
        return {
            "success": True,
            "articles": articles,
            "total": len(articles),
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter artigos da sessão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/archive/articles/{article_id}/restore")
async def restore_archived_article(article_id: int):
    """Restaura um artigo arquivado para o sistema de revisão"""
    try:
        from src.review.weekly_archive import WeeklyArchiveManager
        archive_manager = WeeklyArchiveManager()
        
        result = archive_manager.restore_article_to_review(article_id)
        
        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        logger.error(f"❌ Erro ao restaurar artigo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/archive/run")
async def run_weekly_archive():
    """Executa arquivamento manual da semana anterior"""
    try:
        from src.review.weekly_archive import WeeklyArchiveManager
        archive_manager = WeeklyArchiveManager()
        
        result = archive_manager.archive_previous_week_articles()
        
        return {
            "success": result['status'] == 'success',
            "result": result
        }
    except Exception as e:
        logger.error(f"❌ Erro no arquivamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/archive/interface", response_class=HTMLResponse)
async def archive_interface():
    """Interface web para gerenciar arquivos semanais"""
    try:
        with open("templates/archive_interface.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Interface não encontrada")

@app.get("/publisher/test")
async def test_wordpress_connection_get():
    """Testa conexão com WordPress (GET)"""
    return await test_wordpress_connection()

@app.post("/publisher/test")
async def test_wordpress_connection():
    """Testa conexão com WordPress"""
    if not PUBLISHER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo publisher não disponível")
    
    try:
        manager = PublicationManager()
        result = manager.test_wordpress_connection()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no teste WordPress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/review-api")
async def test_review_api():
    """Endpoint de teste para verificar se a API de review está funcionando corretamente"""
    try:
        # Testar se módulo review está disponível
        if not REVIEW_AVAILABLE:
            return JSONResponse({
                "success": False,
                "error": "Módulo Review não disponível",
                "tests": {
                    "module_available": False
                }
            }, headers={"Content-Type": "application/json; charset=utf-8"})
        
        # Testar listagem de artigos
        review_manager = ReviewManager()
        articles = review_manager.list_articles(limit=1)
        
        tests = {
            "module_available": True,
            "can_list_articles": True,
            "articles_count": len(articles),
            "first_article": articles[0] if articles else None
        }
        
        # Se há artigos, testar visualização
        if articles:
            article_id = articles[0].get('id')
            if article_id:
                try:
                    article = review_manager.get_article(article_id)
                    tests["can_get_article"] = article is not None
                    tests["test_article_id"] = article_id
                except Exception as e:
                    tests["can_get_article"] = False
                    tests["get_article_error"] = str(e)
        
        return JSONResponse({
            "success": True,
            "message": "API de review testada com sucesso",
            "tests": tests,
            "timestamp": datetime.now().isoformat()
        }, headers={"Content-Type": "application/json; charset=utf-8"})
        
    except Exception as e:
        logger.error(f"❌ Erro no teste da API: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Erro no teste: {str(e)}",
            "tests": {
                "module_available": REVIEW_AVAILABLE
            }
        }, status_code=500, headers={"Content-Type": "application/json; charset=utf-8"})


# ================================
# CATEGORIAS ATIVAS - Endpoints
# ================================

@app.get("/categories/")
async def get_all_categories():
    """Retorna todas as categorias (ativas e inativas)"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        categories = categories_manager.get_all_categories()
        summary = categories_manager.get_categories_summary()
        
        return {
            "status": "success",
            "categories": categories,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/active")
async def get_active_categories():
    """Retorna apenas categorias ativas ordenadas por prioridade"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        categories = categories_manager.get_active_categories()
        
        return {
            "status": "success",
            "active_categories": categories,
            "count": len(categories)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categorias ativas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/summary")
async def get_categories_summary():
    """Retorna resumo estatístico das categorias"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        summary = categories_manager.get_categories_summary()
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/categories/{category_key}/status")
async def update_category_status(category_key: str, request: CategoryUpdateRequest):
    """Ativa ou desativa uma categoria específica"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        success = categories_manager.update_category_status(category_key, request.is_active)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Categoria '{category_key}' não encontrada")
        
        status_text = "ativada" if request.is_active else "desativada"
        
        return {
            "status": "success",
            "message": f"Categoria '{category_key}' {status_text} com sucesso",
            "category_key": category_key,
            "is_active": request.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/categories/{category_key}/priority")
async def update_category_priority(category_key: str, request: CategoryPriorityRequest):
    """Atualiza a prioridade de processamento de uma categoria"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        success = categories_manager.update_category_priority(category_key, request.priority)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Categoria '{category_key}' não encontrada")
        
        return {
            "status": "success",
            "message": f"Prioridade da categoria '{category_key}' atualizada para {request.priority}",
            "category_key": category_key,
            "priority": request.priority
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar prioridade da categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/categories/batch")
async def update_categories_batch(request: CategoriesBatchUpdateRequest):
    """Atualiza status de múltiplas categorias em uma operação"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        success = categories_manager.update_categories_batch(request.categories)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erro na atualização em lote")
        
        active_count = sum(1 for active in request.categories.values() if active)
        total_count = len(request.categories)
        
        return {
            "status": "success",
            "message": f"Atualização em lote concluída: {active_count}/{total_count} categorias ativas",
            "updated_categories": request.categories,
            "active_count": active_count,
            "total_count": total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na atualização em lote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories/discover")
async def discover_categories_endpoint(background_tasks: BackgroundTasks):
    """Descobre automaticamente novas categorias do site"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        new_categories = await categories_manager.discover_and_update_categories()
        
        return {
            "status": "success",
            "message": f"Descoberta concluída: {new_categories} novas categorias encontradas",
            "new_categories_count": new_categories
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na descoberta de categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/{category_key}")
async def get_category_details(category_key: str):
    """Retorna detalhes de uma categoria específica"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        categories = categories_manager.get_all_categories()
        category = next((cat for cat in categories if cat['category_key'] == category_key), None)
        
        if not category:
            raise HTTPException(status_code=404, detail=f"Categoria '{category_key}' não encontrada")
        
        return {
            "status": "success",
            "category": category
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/{category_key}/is-active")
async def check_category_active(category_key: str):
    """Verifica rapidamente se uma categoria está ativa"""
    try:
        if not CATEGORIES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de categorias não disponível")
        
        categories_manager = ActiveCategoriesManager()
        is_active = categories_manager.is_category_active(category_key)
        
        return {
            "status": "success",
            "category_key": category_key,
            "is_active": is_active
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review/clean-template-variables")
async def clean_template_variables():
    """Corrigir artigos existentes que ainda têm variáveis de template não substituídas"""
    if not REVIEW_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulo Review não disponível")
    
    try:
        review_manager = ReviewManager()
        
        # Buscar todos os artigos
        articles = review_manager.list_articles(limit=100)
        
        cleaned_count = 0
        template_manager = TemplateManager()
        
        for article in articles:
            article_dict = dict(article)
            content = article_dict.get('conteudo', '')
            
            # Verificar se contém variáveis não substituídas
            if '{{ FEATURED_IMAGE_URL }}' in content or '{{{{ FEATURED_IMAGE_URL }}}}' in content:
                # Aplicar limpeza
                cleaned_content = template_manager._clean_template_variables(content)
                
                # Atualizar o artigo
                success = review_manager.update_article(
                    article_dict['id'], 
                    {'conteudo': cleaned_content},
                    "Sistema - Limpeza Automática"
                )
                
                if success:
                    cleaned_count += 1
                    logger.info(f"✅ Artigo {article_dict['id']} corrigido - removidas variáveis de template")
        
        return JSONResponse({
            "success": True,
            "message": f"Limpeza concluída: {cleaned_count} artigos corrigidos",
            "cleaned_count": cleaned_count,
            "total_articles": len(articles)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza de variáveis: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


# =====================================================
# PONTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Iniciando servidor FastAPI na porta {PORT}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    ) 
 
 