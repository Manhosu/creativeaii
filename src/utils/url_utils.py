#!/usr/bin/env python3
"""URL Utilities - Sistema de Slugify e Validação de URLs"""

import re
import unidecode
import requests
import os
from typing import Optional, Tuple
from loguru import logger

class URLUtils:
    """Utilitários para manipulação e validação de URLs"""
    
    BASE_URL = os.getenv("SITE_BASE_URL", "https://www.creativecopias.com.br")
    
    @staticmethod
    def slugify(text: str) -> str:
        """Converte texto para slug válido para URLs"""
        if not text:
            return ""
        
        text = text.lower()
        text = unidecode.unidecode(text)
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        text = text.strip('-')
        
        return text
    
    @staticmethod
    def generate_product_url(product_name: str, use_produto_path: bool = True) -> str:
        """Gera URL válida para produto"""
        if not product_name:
            return URLUtils.BASE_URL
        
        slug = URLUtils.slugify(product_name)
        
        if use_produto_path:
            path = f"/produto/{slug}"
        else:
            path = f"/{slug}.html"
        
        return f"{URLUtils.BASE_URL}{path}"
    
    @staticmethod
    def generate_category_url(category_name: str) -> str:
        """Gera URL válida para categoria"""
        if not category_name:
            return URLUtils.BASE_URL
        
        slug = URLUtils.slugify(category_name)
        return f"{URLUtils.BASE_URL}/{slug}"
    
    @staticmethod
    def fix_broken_url(url: str) -> str:
        """Corrige URL quebrada"""
        if not url:
            return URLUtils.BASE_URL
        
        url = url.strip()
        url = re.sub(r'\s+', '', url)
        url = url.replace('%20', '-')
        
        url = re.sub(r'creativecopias\.\s*com\.\s*br', 'creativecopias.com.br', url)
        
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        
        if not url.startswith('https://'):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = URLUtils.BASE_URL + url
            elif not url.startswith('http'):
                url = URLUtils.BASE_URL + '/' + url
        
        if 'creativecopias.com.br' in url and 'www.' not in url:
            url = url.replace('creativecopias.com.br', 'www.creativecopias.com.br')
        
        return url
    
    @staticmethod
    def validate_url(url: str, check_availability: bool = False) -> Tuple[bool, str]:
        """Valida se URL está correta"""
        if not url:
            return False, "URL vazia"
        
        if not url.startswith('https://'):
            return False, "URL deve começar com https://"
        
        if 'creativecopias.com.br' not in url:
            return False, "URL deve ser do domínio creativecopias.com.br"
        
        if ' ' in url or '%20' in url:
            return False, "URL contém espaços ou caracteres codificados inválidos"
        
        if check_availability:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code >= 400:
                    return False, f"URL retorna erro {response.status_code}"
            except requests.RequestException as e:
                return False, f"Erro ao acessar URL: {str(e)}"
        
        return True, "URL válida"
    
    @staticmethod
    def generate_buy_link(product_name: str, real_product_url: str = None, validate: bool = True) -> str:
        """
        CORRIGIDO: Gera link de compra usando URL REAL do produto ou categoria válida
        Evita links quebrados direcionando sempre para URLs válidas
        """
        if not product_name or len(product_name.strip()) < 3:
            product_name = "equipamento"
        
        product_url = None
        
        # PRIORIDADE 1: Usar URL real do produto se fornecida e válida
        if real_product_url and real_product_url.strip():
            test_url = real_product_url.strip()
            
            # Corrigir URL se necessário
            test_url = URLUtils.fix_broken_url(test_url)
            
            if validate:
                is_valid, message = URLUtils.validate_url(test_url)
                if is_valid:
                    product_url = test_url
                    logger.info(f"✅ Usando URL real validada: {product_url}")
                else:
                    logger.warning(f"⚠️ URL real inválida: {message} - {test_url}")
            else:
                product_url = test_url
        
        # PRIORIDADE 2: Se URL real não é válida, usar categoria específica
        if not product_url:
            # Determinar categoria baseada no nome do produto
            product_lower = product_name.lower()
            
            if 'impressora' in product_lower or 'multifuncional' in product_lower:
                product_url = "https://www.creativecopias.com.br/impressoras"
            elif 'cartucho' in product_lower and 'tinta' in product_lower:
                product_url = "https://www.creativecopias.com.br/cartuchos-de-tinta"
            elif 'cartucho' in product_lower or 'tinta' in product_lower:
                product_url = "https://www.creativecopias.com.br/cartuchos-de-tinta"
            elif 'toner' in product_lower:
                product_url = "https://www.creativecopias.com.br/cartuchos-de-toner"
            elif 'papel' in product_lower:
                product_url = "https://www.creativecopias.com.br/papel-fotografico"
            elif 'scanner' in product_lower:
                product_url = "https://www.creativecopias.com.br/scanner"
            elif 'refil' in product_lower:
                if 'toner' in product_lower:
                    product_url = "https://www.creativecopias.com.br/refil-de-toner"
                else:
                    product_url = "https://www.creativecopias.com.br/refil-de-tinta"
            else:
                # Fallback para página geral de impressoras
                product_url = "https://www.creativecopias.com.br/impressoras"
            
            logger.info(f"✅ Usando categoria específica: {product_url}")
        
        # VALIDAÇÃO FINAL: Garantir que URL é sempre válida
        if validate:
            is_valid, message = URLUtils.validate_url(product_url)
            if not is_valid:
                logger.error(f"❌ URL final inválida: {message} - {product_url}")
                # Último fallback seguro
                product_url = "https://www.creativecopias.com.br"
        
        return f'<a href="{product_url}" target="_blank" rel="noopener"><strong>Consultar {product_name}</strong></a>'
    
    @staticmethod
    def generate_internal_link(category: str, text: str) -> str:
        """Gera link interno validado"""
        category_url = URLUtils.generate_category_url(category)
        return f'<a href="{category_url}" target="_blank">{text}</a>'

# Funções de conveniência
def slugify(text: str) -> str:
    """Função de conveniência para slugify"""
    return URLUtils.slugify(text)

def fix_url(url: str) -> str:
    """Função de conveniência para corrigir URL"""
    return URLUtils.fix_broken_url(url)

def validate_product_url(url: str) -> bool:
    """Função de conveniência para validar URL de produto"""
    is_valid, _ = URLUtils.validate_url(url)
    return is_valid 