"""
Módulo Scraper - Sistema de Geração Automática de Conteúdo SEO
Extração automatizada de produtos do Creative Cópias
"""

from .scraper_base import ScraperBase
from .creative_scraper import CreativeScraper
from .product_extractor import ProductExtractor
from .url_manager import URLManager

__version__ = "1.0.0"
__author__ = "Sistema SEO"

# Exports principais
__all__ = [
    'ScraperBase',
    'CreativeScraper',
    'ProductExtractor', 
    'URLManager'
]




