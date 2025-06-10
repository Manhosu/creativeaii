#!/usr/bin/env python3
"""
Sistema de Validação e Correção de URLs/Slugs
Garante que todos os links e slugs sejam válidos antes da publicação
"""

import re
import urllib.parse
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import logging

# Importação robusta do slugify
try:
    from slugify import slugify
except ImportError:
    # Fallback se slugify não estiver disponível
    import re
    def slugify(text, **kwargs):
        """Fallback simples para slugify"""
        if not text:
            return "slug"
        # Converter para minúsculas e substituir espaços por hífens
        slug = re.sub(r'[^\w\s-]', '', str(text).lower())
        slug = re.sub(r'\s+', '-', slug)
        return slug.strip('-')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLValidator:
    """
    Valida e corrige URLs e slugs para evitar links quebrados
    """
    
    def __init__(self):
        """Inicializa o validador de URLs"""
        # Padrões de caracteres problemáticos
        self.invalid_chars = [
            ' ', '\t', '\n', '\r',  # Espaços em branco
            '"', "'", '<', '>',      # Aspas e símbolos HTML
            '{', '}', '[', ']',      # Chaves e colchetes
            '|', '\\', '^', '`',     # Símbolos especiais
            '…', '–', '—',           # Caracteres especiais Unicode
        ]
        
        # Palavras proibidas em slugs
        self.forbidden_words = [
            'admin', 'api', 'www', 'ftp', 'mail', 'email',
            'test', 'demo', 'temp', 'backup', 'old',
            'wp-admin', 'wp-content', 'wp-includes'
        ]
        
        # Configurações de slugify
        self.slugify_config = {
            'max_length': 100,
            'word_boundary': True,
            'separator': '-',
            'lowercase': True
        }
        
        logger.info("🔗 URL Validator inicializado")
    
    def validate_and_fix_slug(self, text: str, fallback: str = "artigo") -> str:
        """
        Valida e corrige slug para ser URL-safe
        
        Args:
            text: Texto para criar slug
            fallback: Texto de fallback se necessário
            
        Returns:
            Slug válido e limpo
        """
        try:
            if not text or not text.strip():
                text = fallback
            
            # Remover caracteres problemáticos antes do slugify
            cleaned_text = self._remove_invalid_chars(text)
            
            # Aplicar slugify
            base_slug = slugify(
                cleaned_text,
                max_length=self.slugify_config['max_length'],
                word_boundary=self.slugify_config['word_boundary'],
                separator=self.slugify_config['separator'],
                lowercase=self.slugify_config['lowercase']
            )
            
            # Verificar se slug é válido
            if not base_slug or len(base_slug) < 3:
                base_slug = slugify(fallback)
            
            # Verificar palavras proibidas
            base_slug = self._avoid_forbidden_words(base_slug)
            
            # Garantir que não comece/termine com separador
            base_slug = base_slug.strip('-')
            
            # Verificar comprimento mínimo novamente
            if len(base_slug) < 3:
                base_slug = f"{fallback}-{len(base_slug)}"
            
            logger.debug(f"✅ Slug validado: '{text}' → '{base_slug}'")
            return base_slug
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar slug: {e}")
            return slugify(fallback)
    
    def _remove_invalid_chars(self, text: str) -> str:
        """Remove caracteres problemáticos"""
        cleaned = text
        
        # Remover caracteres inválidos
        for char in self.invalid_chars:
            cleaned = cleaned.replace(char, ' ')
        
        # Remover múltiplos espaços
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remover símbolos problemáticos específicos
        cleaned = re.sub(r'[^\w\s\-áàâãéèêíìîóòôõúùûç]', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _avoid_forbidden_words(self, slug: str) -> str:
        """Evita palavras proibidas em slugs"""
        
        slug_words = slug.split('-')
        
        # Verificar se alguma palavra é proibida
        for i, word in enumerate(slug_words):
            if word.lower() in self.forbidden_words:
                slug_words[i] = f"{word}-post"
        
        return '-'.join(slug_words)
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Valida se uma URL é bem formada
        
        Args:
            url: URL para validar
            
        Returns:
            Dicionário com resultado da validação
        """
        try:
            if not url or not url.strip():
                return {
                    'valid': False,
                    'error': 'URL vazia',
                    'corrected_url': None
                }
            
            # Limpar URL
            cleaned_url = url.strip()
            
            # Verificar se tem protocolo
            if not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = f"https://{cleaned_url}"
            
            # Parse da URL
            parsed = urllib.parse.urlparse(cleaned_url)
            
            # Verificações básicas
            if not parsed.netloc:
                return {
                    'valid': False,
                    'error': 'Domínio inválido',
                    'corrected_url': None
                }
            
            # Verificar caracteres problemáticos
            if any(char in cleaned_url for char in [' ', '\t', '\n']):
                # Tentar corrigir
                corrected_url = self._fix_url_spaces(cleaned_url)
                return {
                    'valid': False,
                    'error': 'URL contém espaços',
                    'corrected_url': corrected_url,
                    'auto_fixable': True
                }
            
            # URL parece válida
            return {
                'valid': True,
                'error': None,
                'corrected_url': cleaned_url
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Erro na validação: {str(e)}',
                'corrected_url': None
            }
    
    def _fix_url_spaces(self, url: str) -> str:
        """Corrige espaços em URLs"""
        # Substituir espaços por %20
        fixed = url.replace(' ', '%20')
        fixed = fixed.replace('\t', '%09')
        fixed = fixed.replace('\n', '')
        fixed = fixed.replace('\r', '')
        
        return fixed
    
    def validate_article_links(self, content: str) -> Dict[str, Any]:
        """
        Valida todos os links em um artigo
        
        Args:
            content: Conteúdo HTML do artigo
            
        Returns:
            Relatório de validação de links
        """
        try:
            # Encontrar todos os links
            link_pattern = r'href=["\']([^"\']+)["\']'
            links = re.findall(link_pattern, content, re.IGNORECASE)
            
            validation_results = {
                'total_links': len(links),
                'valid_links': 0,
                'invalid_links': 0,
                'fixed_links': 0,
                'issues': [],
                'corrected_content': content
            }
            
            corrected_content = content
            
            for link in links:
                validation = self.validate_url(link)
                
                if validation['valid']:
                    validation_results['valid_links'] += 1
                else:
                    validation_results['invalid_links'] += 1
                    
                    issue = {
                        'original_url': link,
                        'error': validation['error'],
                        'corrected_url': validation.get('corrected_url'),
                        'auto_fixable': validation.get('auto_fixable', False)
                    }
                    
                    validation_results['issues'].append(issue)
                    
                    # Tentar correção automática se possível
                    if validation.get('auto_fixable') and validation.get('corrected_url'):
                        corrected_content = corrected_content.replace(
                            f'href="{link}"', 
                            f'href="{validation["corrected_url"]}"'
                        )
                        corrected_content = corrected_content.replace(
                            f"href='{link}'", 
                            f"href='{validation['corrected_url']}'"
                        )
                        validation_results['fixed_links'] += 1
            
            validation_results['corrected_content'] = corrected_content
            
            logger.info(f"🔗 Links validados: {validation_results['valid_links']}/{validation_results['total_links']} válidos")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de links: {e}")
            return {
                'total_links': 0,
                'valid_links': 0,
                'invalid_links': 0,
                'fixed_links': 0,
                'issues': [{'error': f'Erro na validação: {str(e)}'}],
                'corrected_content': content
            }
    
    def generate_unique_slug(self, title: str, existing_slugs: List[str] = None) -> str:
        """
        Gera slug único evitando duplicatas
        
        Args:
            title: Título para gerar slug
            existing_slugs: Lista de slugs existentes para evitar
            
        Returns:
            Slug único
        """
        if existing_slugs is None:
            existing_slugs = []
        
        # Gerar slug base
        base_slug = self.validate_and_fix_slug(title)
        
        # Verificar se é único
        if base_slug not in existing_slugs:
            return base_slug
        
        # Adicionar numeração se necessário
        counter = 1
        while True:
            numbered_slug = f"{base_slug}-{counter}"
            if numbered_slug not in existing_slugs:
                logger.info(f"🔄 Slug numerado gerado: {numbered_slug}")
                return numbered_slug
            counter += 1
            
            # Evitar loop infinito
            if counter > 1000:
                import time
                timestamp_slug = f"{base_slug}-{int(time.time())}"
                logger.warning(f"⚠️ Fallback para timestamp: {timestamp_slug}")
                return timestamp_slug
    
    def validate_before_publish(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validação completa antes de publicar artigo
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            Resultado da validação com correções
        """
        try:
            results = {
                'valid': True,
                'warnings': [],
                'errors': [],
                'corrections': {},
                'corrected_data': article_data.copy()
            }
            
            # 1. Validar e corrigir slug
            if 'slug' in article_data:
                original_slug = article_data['slug']
                corrected_slug = self.validate_and_fix_slug(original_slug)
                
                if original_slug != corrected_slug:
                    results['corrections']['slug'] = {
                        'original': original_slug,
                        'corrected': corrected_slug
                    }
                    results['corrected_data']['slug'] = corrected_slug
                    results['warnings'].append(f"Slug corrigido: '{original_slug}' → '{corrected_slug}'")
            
            # 2. Validar título para slug se necessário
            if 'titulo' in article_data and ('slug' not in article_data or not article_data['slug']):
                generated_slug = self.validate_and_fix_slug(article_data['titulo'])
                results['corrected_data']['slug'] = generated_slug
                results['corrections']['slug_generated'] = generated_slug
                results['warnings'].append(f"Slug gerado automaticamente: '{generated_slug}'")
            
            # 3. Validar links no conteúdo
            if 'conteudo' in article_data:
                link_validation = self.validate_article_links(article_data['conteudo'])
                
                if link_validation['invalid_links'] > 0:
                    results['warnings'].append(f"{link_validation['invalid_links']} links inválidos encontrados")
                    
                    # Aplicar correções automáticas
                    if link_validation['fixed_links'] > 0:
                        results['corrected_data']['conteudo'] = link_validation['corrected_content']
                        results['corrections']['links_fixed'] = link_validation['fixed_links']
                        results['warnings'].append(f"{link_validation['fixed_links']} links corrigidos automaticamente")
                    
                    # Adicionar problemas não corrigidos
                    unfixed_issues = [issue for issue in link_validation['issues'] if not issue.get('auto_fixable')]
                    if unfixed_issues:
                        for issue in unfixed_issues:
                            results['errors'].append(f"Link problemático: {issue['original_url']} - {issue['error']}")
                        results['valid'] = False
            
            # 4. Validar meta description para caracteres problemáticos
            if 'meta_descricao' in article_data:
                meta = article_data['meta_descricao']
                cleaned_meta = self._remove_invalid_chars(meta)
                
                if meta != cleaned_meta:
                    results['corrected_data']['meta_descricao'] = cleaned_meta
                    results['corrections']['meta_description'] = {
                        'original': meta,
                        'corrected': cleaned_meta
                    }
                    results['warnings'].append("Meta description corrigida")
            
            logger.info(f"✅ Validação pré-publicação: {'APROVADO' if results['valid'] else 'REPROVADO'}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na validação pré-publicação: {e}")
            return {
                'valid': False,
                'warnings': [],
                'errors': [f'Erro na validação: {str(e)}'],
                'corrections': {},
                'corrected_data': article_data
            }
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        return {
            'config': self.slugify_config,
            'forbidden_words_count': len(self.forbidden_words),
            'invalid_chars_count': len(self.invalid_chars),
            'validation_features': [
                'Slug validation and correction',
                'URL format validation', 
                'Link validation in content',
                'Meta description cleaning',
                'Automatic fixing when possible'
            ]
        } 