"""
Módulo Publisher - Sistema de Publicação no WordPress
Publicação automática de artigos aprovados
"""

from .wordpress_client import WordPressClient
from .publication_manager import PublicationManager

__version__ = "1.0.0"
__author__ = "Sistema SEO"

# Exports principais
__all__ = [
    'WordPressClient',
    'PublicationManager'
]
