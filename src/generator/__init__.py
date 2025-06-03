"""
Módulo Generator - Sistema de Geração Automática de Conteúdo SEO
Geração de artigos otimizados com IA a partir de produtos extraídos
"""

from .content_generator import ContentGenerator
from .seo_optimizer import SEOOptimizer
from .prompt_builder import PromptBuilder
from .template_manager import TemplateManager
from .generator_manager import GeneratorManager

__version__ = "1.0.0"
__author__ = "Sistema SEO"

# Exports principais
__all__ = [
    'ContentGenerator',
    'SEOOptimizer', 
    'PromptBuilder',
    'TemplateManager',
    'GeneratorManager'
]








