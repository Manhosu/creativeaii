#!/usr/bin/env python3
"""URL Utilities - Sistema de Slugify e Validação de URLs"""

import re
import unidecode
import requests
from typing import Optional, Tuple
from loguru import logger

class URLUtils:
    """Utilitários para manipulação e validação de URLs"""
    
    BASE_URL = "https://www.creativecopias.com.br"
    
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
        """Gera link de compra usando URL REAL do produto"""
        if not product_name or len(product_name.strip()) < 3:
            product_name = "equipamento"
        
        if real_product_url and real_product_url.strip():
            product_url = real_product_url.strip()
            
            if validate:
                is_valid, message = URLUtils.validate_url(product_url)
                if not is_valid:
                    logger.warning(f"⚠️ URL real não é válida: {message} - {product_url}")
                    product_url = URLUtils.generate_product_url(product_name)
        else:
            product_url = URLUtils.generate_product_url(product_name)
        
        if validate:
            is_valid, message = URLUtils.validate_url(product_url)
            if not is_valid:
                logger.warning(f"⚠️ URL gerada não é válida: {message} - {product_url}")
                product_url = f"{URLUtils.BASE_URL}/impressoras"
        
        return f'<a href="{product_url}" target="_blank" rel="noopener"><strong>Comprar {product_name}</strong></a>'
    
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