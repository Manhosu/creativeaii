"""
WordPress Client
Cliente para integração com WordPress via REST API
"""

import requests
import os
import mimetypes
import base64
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from loguru import logger
from datetime import datetime
import json

class WordPressClient:
    """Cliente para comunicação com WordPress via REST API"""
    
    def __init__(self, site_url: str, username: str = None, password: str = None, 
                 app_password: str = None):
        """
        Inicializa cliente WordPress
        
        Args:
            site_url: URL base do site WordPress
            username: Nome de usuário WordPress
            password: Senha do usuário ou app password
            app_password: App password específico (recomendado)
        """
        self.site_url = site_url.rstrip('/')
        self.username = username or os.getenv('WP_USERNAME')
        self.password = password or app_password or os.getenv('WP_PASSWORD')
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        
        # Configurar sessão
        self.session = requests.Session()
        
        if self.username and self.password:
            # Autenticação básica
            self.session.auth = (self.username, self.password)
        
        # Headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Sistema-SEO-Publisher/1.0'
        })
        
        logger.info(f"🔗 WordPress Client inicializado para {self.site_url}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com o WordPress
        
        Returns:
            Resultado do teste
        """
        try:
            # Testar acesso básico à API
            response = self.session.get(f"{self.api_base}/")
            
            if response.status_code == 200:
                api_info = response.json()
                
                # Testar autenticação tentando acessar posts
                auth_test = self.session.get(f"{self.api_base}/posts", params={'per_page': 1})
                
                result = {
                    'success': True,
                    'site_url': self.site_url,
                    'api_url': self.api_base,
                    'wp_version': api_info.get('description', 'Unknown'),
                    'authenticated': auth_test.status_code == 200,
                    'auth_status_code': auth_test.status_code,
                    'namespaces': api_info.get('namespaces', [])
                }
                
                if not result['authenticated']:
                    result['auth_error'] = f"Falha na autenticação (código {auth_test.status_code})"
                
                logger.info(f"✅ Conexão WordPress testada: {result['authenticated']}")
                return result
            else:
                return {
                    'success': False,
                    'error': f"Falha na conexão: HTTP {response.status_code}",
                    'site_url': self.site_url
                }
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de conexão WordPress: {e}")
            return {
                'success': False,
                'error': str(e),
                'site_url': self.site_url
            }
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Lista todas as categorias do WordPress
        
        Returns:
            Lista de categorias
        """
        try:
            response = self.session.get(f"{self.api_base}/categories", params={'per_page': 100})
            
            if response.status_code == 200:
                categories = response.json()
                logger.debug(f"📁 {len(categories)} categorias encontradas")
                return categories
            else:
                logger.error(f"❌ Erro ao buscar categorias: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar categorias: {e}")
            return []
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """
        Lista todas as tags do WordPress
        
        Returns:
            Lista de tags
        """
        try:
            response = self.session.get(f"{self.api_base}/tags", params={'per_page': 100})
            
            if response.status_code == 200:
                tags = response.json()
                logger.debug(f"🏷️ {len(tags)} tags encontradas")
                return tags
            else:
                logger.error(f"❌ Erro ao buscar tags: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar tags: {e}")
            return []
    
    def create_category(self, name: str, description: str = "", slug: str = None, 
                       parent_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Cria nova categoria no WordPress
        
        Args:
            name: Nome da categoria
            description: Descrição da categoria
            slug: Slug da categoria
            parent_id: ID da categoria pai
            
        Returns:
            Dados da categoria criada ou None se falhou
        """
        try:
            data = {
                'name': name,
                'description': description
            }
            
            if slug:
                data['slug'] = slug
            if parent_id:
                data['parent'] = parent_id
            
            response = self.session.post(f"{self.api_base}/categories", json=data)
            
            if response.status_code == 201:
                category = response.json()
                logger.info(f"✅ Categoria criada: {name} (ID: {category.get('id')})")
                return category
            else:
                error_msg = response.json().get('message', 'Erro desconhecido')
                logger.error(f"❌ Erro ao criar categoria '{name}': {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar categoria '{name}': {e}")
            return None
    
    def create_tag(self, name: str, description: str = "", slug: str = None) -> Optional[Dict[str, Any]]:
        """
        Cria nova tag no WordPress
        
        Args:
            name: Nome da tag
            description: Descrição da tag
            slug: Slug da tag
            
        Returns:
            Dados da tag criada ou None se falhou
        """
        try:
            data = {
                'name': name,
                'description': description
            }
            
            if slug:
                data['slug'] = slug
            
            response = self.session.post(f"{self.api_base}/tags", json=data)
            
            if response.status_code == 201:
                tag = response.json()
                logger.info(f"✅ Tag criada: {name} (ID: {tag.get('id')})")
                return tag
            else:
                error_msg = response.json().get('message', 'Erro desconhecido')
                logger.error(f"❌ Erro ao criar tag '{name}': {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar tag '{name}': {e}")
            return None
    
    def upload_media(self, file_path: str, title: str = None, 
                    alt_text: str = None) -> Optional[Dict[str, Any]]:
        """
        Faz upload de arquivo de mídia para o WordPress
        
        Args:
            file_path: Caminho para o arquivo
            title: Título da mídia
            alt_text: Texto alternativo para imagens
            
        Returns:
            Dados da mídia ou None se falhou
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ Arquivo não encontrado: {file_path}")
                return None
            
            # Determinar tipo MIME
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Preparar arquivo
            filename = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, mime_type)
                }
                
                headers = {
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
                
                if title:
                    headers['Content-Title'] = title
                if alt_text:
                    headers['Content-Alt-Text'] = alt_text
                
                # Fazer upload
                response = self.session.post(
                    f"{self.api_base}/media",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 201:
                media = response.json()
                logger.info(f"✅ Mídia enviada: {filename} (ID: {media.get('id')})")
                return media
            else:
                error_msg = response.json().get('message', 'Erro desconhecido')
                logger.error(f"❌ Erro no upload de '{filename}': {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no upload de mídia: {e}")
            return None
    
    def create_post(self, title: str, content: str, status: str = 'draft',
                   categories: List[int] = None, tags: List[int] = None,
                   featured_media: int = None, excerpt: str = None,
                   slug: str = None, meta: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Cria novo post no WordPress
        
        Args:
            title: Título do post
            content: Conteúdo HTML do post
            status: Status do post (draft, publish, private)
            categories: Lista de IDs de categorias
            tags: Lista de IDs de tags
            featured_media: ID da imagem destacada
            excerpt: Resumo do post
            slug: Slug do post
            meta: Metadados customizados
            
        Returns:
            Dados do post criado ou None se falhou
        """
        try:
            data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            if categories:
                data['categories'] = categories
            if tags:
                data['tags'] = tags
            if featured_media:
                data['featured_media'] = featured_media
            if excerpt:
                data['excerpt'] = excerpt
            if slug:
                data['slug'] = slug
            if meta:
                data['meta'] = meta
            
            response = self.session.post(f"{self.api_base}/posts", json=data)
            
            if response.status_code == 201:
                post = response.json()
                logger.info(f"✅ Post criado: '{title}' (ID: {post.get('id')})")
                return post
            else:
                error_data = response.json()
                error_msg = error_data.get('message', 'Erro desconhecido')
                logger.error(f"❌ Erro ao criar post '{title}': {error_msg}")
                logger.debug(f"Detalhes do erro: {error_data}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar post '{title}': {e}")
            return None
    
    def update_post(self, post_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Atualiza post existente
        
        Args:
            post_id: ID do post
            updates: Campos a atualizar
            
        Returns:
            Dados do post atualizado ou None se falhou
        """
        try:
            response = self.session.post(f"{self.api_base}/posts/{post_id}", json=updates)
            
            if response.status_code == 200:
                post = response.json()
                logger.info(f"✅ Post atualizado: ID {post_id}")
                return post
            else:
                error_msg = response.json().get('message', 'Erro desconhecido')
                logger.error(f"❌ Erro ao atualizar post {post_id}: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar post {post_id}: {e}")
            return None
    
    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca post por ID
        
        Args:
            post_id: ID do post
            
        Returns:
            Dados do post ou None se não encontrado
        """
        try:
            response = self.session.get(f"{self.api_base}/posts/{post_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Post {post_id} não encontrado")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar post {post_id}: {e}")
            return None
    
    def delete_post(self, post_id: int, force: bool = False) -> bool:
        """
        Remove post
        
        Args:
            post_id: ID do post
            force: Se True, remove permanentemente
            
        Returns:
            True se removido com sucesso
        """
        try:
            params = {'force': force} if force else {}
            response = self.session.delete(f"{self.api_base}/posts/{post_id}", params=params)
            
            if response.status_code in [200, 410]:
                logger.info(f"✅ Post {post_id} removido")
                return True
            else:
                logger.error(f"❌ Erro ao remover post {post_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover post {post_id}: {e}")
            return False
    
    def find_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Busca categoria por nome
        
        Args:
            name: Nome da categoria
            
        Returns:
            Dados da categoria ou None se não encontrada
        """
        categories = self.get_categories()
        for category in categories:
            if category.get('name', '').lower() == name.lower():
                return category
        return None
    
    def find_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Busca tag por nome
        
        Args:
            name: Nome da tag
            
        Returns:
            Dados da tag ou None se não encontrada
        """
        tags = self.get_tags()
        for tag in tags:
            if tag.get('name', '').lower() == name.lower():
                return tag
        return None
    
    def get_or_create_category(self, name: str, description: str = "", 
                              slug: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca categoria existente ou cria nova
        
        Args:
            name: Nome da categoria
            description: Descrição da categoria
            slug: Slug da categoria
            
        Returns:
            Dados da categoria
        """
        # Buscar categoria existente
        category = self.find_category_by_name(name)
        if category:
            return category
        
        # Criar nova categoria
        return self.create_category(name, description, slug)
    
    def get_or_create_tag(self, name: str, description: str = "", 
                         slug: str = None) -> Optional[Dict[str, Any]]:
        """
        Busca tag existente ou cria nova
        
        Args:
            name: Nome da tag
            description: Descrição da tag
            slug: Slug da tag
            
        Returns:
            Dados da tag
        """
        # Buscar tag existente
        tag = self.find_tag_by_name(name)
        if tag:
            return tag
        
        # Criar nova tag
        return self.create_tag(name, description, slug) 