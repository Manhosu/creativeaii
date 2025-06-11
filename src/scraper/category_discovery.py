"""
Category Discovery
Descobre automaticamente todas as categorias e subcategorias de produtos no site
"""

import re
import time
from typing import Dict, List, Set, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from loguru import logger

class CategoryDiscovery:
    """Descoberta automática de categorias de produtos"""
    
    def __init__(self, base_url: str = "https://www.creativecopias.com.br", 
                 delay_range: tuple = (1, 2)):
        """
        Inicializa o descobridor de categorias
        
        Args:
            base_url: URL base do site
            delay_range: Delay entre requests
        """
        self.base_url = base_url
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Headers para parecer um navegador real
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Palavras-chave que indicam categorias de produtos
        self.product_keywords = [
            'impressora', 'multifuncional', 'scanner', 'copiadora',
            'toner', 'cartucho', 'cartuchos', 'suprimento', 'suprimentos',
            'papel', 'papéis', 'etiqueta', 'etiquetas', 
            'ribbon', 'fita', 'cabo', 'cabos',
            'peça', 'peças', 'acessório', 'acessórios',
            'manutenção', 'limpeza', 'kit'
        ]
        
        # Padrões de URL que indicam categorias
        self.category_url_patterns = [
            r'/categoria/',
            r'/cat/',
            r'/c/',
            r'/produtos/',
            r'/product/',
            r'/impressoras',
            r'/multifuncionais',
            r'/toners?',
            r'/cartuchos?',
            r'/suprimentos?',
            r'/papel',
            r'/scanner'
        ]
        
        logger.info(f"🔍 Category Discovery inicializado para {base_url}")
    
    def discover_all_categories(self) -> Dict[str, Any]:
        """
        Descobre todas as categorias automaticamente
        
        Returns:
            Dicionário com categorias descobertas
        """
        logger.info("🕵️ Iniciando descoberta automática de categorias...")
        
        start_time = time.time()
        discovered_categories = []
        
        try:
            # Usar categorias conhecidas do Creative Cópias baseadas na análise manual
            logger.info("📋 Usando categorias conhecidas do Creative Cópias...")
            known_categories = self._get_known_creative_categories()
            discovered_categories.extend(known_categories)
            
            # 1. Analisar página principal
            logger.info("📄 Analisando página principal...")
            main_page_categories = self._discover_from_main_page()
            discovered_categories.extend(main_page_categories)
            
            # 2. Analisar menu principal
            logger.info("🍔 Analisando menu de navegação...")
            menu_categories = self._discover_from_navigation_menu()
            discovered_categories.extend(menu_categories)
            
            # 3. Analisar mapa do site (se existir)
            logger.info("🗺️ Procurando por sitemap...")
            sitemap_categories = self._discover_from_sitemap()
            discovered_categories.extend(sitemap_categories)
            
            # 4. Analisar links do rodapé
            logger.info("🦶 Analisando links do rodapé...")
            footer_categories = self._discover_from_footer()
            discovered_categories.extend(footer_categories)
            
            # Remover duplicatas e normalizar
            unique_categories = self._normalize_and_deduplicate(discovered_categories)
            
            # Validar categorias (verificar se realmente têm produtos)
            logger.info(f"✅ Validando {len(unique_categories)} categorias...")
            validated_categories = self._validate_categories(unique_categories)
            
            execution_time = time.time() - start_time
            
            result = {
                'status': 'success',
                'total_discovered': len(discovered_categories),
                'unique_categories': len(unique_categories),
                'validated_categories': len(validated_categories),
                'categories': validated_categories,
                'execution_time': execution_time,
                'methods_used': ['known_categories', 'main_page', 'navigation_menu', 'sitemap', 'footer']
            }
            
            logger.info(f"🎯 Descoberta concluída: {len(validated_categories)} categorias válidas "
                       f"encontradas em {execution_time:.1f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na descoberta de categorias: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'categories': []
            }
    
    def _get_known_creative_categories(self) -> List[Dict[str, Any]]:
        """Retorna categorias conhecidas do Creative Cópias baseadas na análise manual"""
        known_urls = [
            {
                'name': 'Impressoras',
                'url': 'https://www.creativecopias.com.br/impressoras',
                'source': 'known_category',
                'priority': 1
            },
            {
                'name': 'Cartuchos de Toner',
                'url': 'https://www.creativecopias.com.br/cartuchos-de-toner',
                'source': 'known_category',
                'priority': 1
            },
            {
                'name': 'Cartuchos de Tinta',
                'url': 'https://www.creativecopias.com.br/cartuchos-de-tinta',
                'source': 'known_category',
                'priority': 1
            },
            {
                'name': 'Refil de Toner',
                'url': 'https://www.creativecopias.com.br/refil-de-toner',
                'source': 'known_category',
                'priority': 2
            },
            {
                'name': 'Refil de Tinta',
                'url': 'https://www.creativecopias.com.br/refil-de-tinta',
                'source': 'known_category',
                'priority': 2
            },
            {
                'name': 'Papel Fotográfico',
                'url': 'https://www.creativecopias.com.br/papel-fotografico',
                'source': 'known_category',
                'priority': 3
            },
            {
                'name': 'Scanner',
                'url': 'https://www.creativecopias.com.br/scanner',
                'source': 'known_category',
                'priority': 3
            },
            {
                'name': 'Impressora com Defeito',
                'url': 'https://www.creativecopias.com.br/impressora-com-defeito',
                'source': 'known_category',
                'priority': 4
            }
        ]
        
        logger.info(f"📋 Adicionadas {len(known_urls)} categorias conhecidas do Creative Cópias")
        return known_urls
    
    def _discover_from_main_page(self) -> List[Dict[str, Any]]:
        """Descobre categorias na página principal"""
        categories = []
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar por seções de produtos na homepage
            selectors = [
                'nav a[href*="categoria"]',
                'nav a[href*="produtos"]',
                '.menu a[href*="impressora"]',
                '.menu a[href*="multifuncional"]',
                '.menu a[href*="toner"]',
                '.menu a[href*="cartucho"]',
                '.categoria-link',
                '.product-category',
                '.nav-category',
                'a[href*="/c/"]',
                'a[href*="/cat/"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text and self._is_valid_category_link(href, text):
                        full_url = urljoin(self.base_url, href)
                        categories.append({
                            'name': text,
                            'url': full_url,
                            'source': 'main_page',
                            'selector': selector
                        })
            
            logger.info(f"📄 Encontradas {len(categories)} categorias na página principal")
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar página principal: {e}")
        
        return categories
    
    def _discover_from_navigation_menu(self) -> List[Dict[str, Any]]:
        """Descobre categorias no menu de navegação"""
        categories = []
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Selectors específicos para o Creative Cópias baseado na análise
            menu_selectors = [
                'nav a',  # Menu principal
                '.navbar a',  # Navbar
                '.menu a',  # Menu geral
                'nav ul li a',  # Links do menu
                '.navbar-nav a',
                '.main-menu a',
                '.navigation a'
            ]
            
            for selector in menu_selectors:
                links = soup.select(selector)
                logger.info(f"🔍 Selector '{selector}': {len(links)} links encontrados")
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text and self._is_valid_category_link(href, text):
                        full_url = urljoin(self.base_url, href)
                        
                        # Log para debug
                        logger.debug(f"  ✅ Categoria válida: {text} -> {full_url}")
                        
                        categories.append({
                            'name': text,
                            'url': full_url,
                            'source': 'navigation_menu',
                            'selector': selector
                        })
                    else:
                        # Log para debug de links rejeitados
                        if href and text:
                            logger.debug(f"  ❌ Link rejeitado: {text} -> {href}")
            
            # Busca adicional por links específicos do Creative Cópias
            specific_links = soup.find_all('a', href=True)
            for link in specific_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # Verificar se é uma categoria específica do Creative Cópias
                if href and any(keyword in href.lower() for keyword in [
                    'impressoras', 'cartuchos-de-toner', 'cartuchos-de-tinta', 
                    'refil-de-toner', 'refil-de-tinta', 'papel-fotografico',
                    'scanner', 'multifuncional'
                ]):
                    full_url = urljoin(self.base_url, href)
                    
                    # Evitar duplicatas
                    if not any(cat['url'] == full_url for cat in categories):
                        categories.append({
                            'name': text or self._extract_category_name_from_url(href),
                            'url': full_url,
                            'source': 'specific_search',
                            'selector': 'href_pattern_match'
                        })
            
            logger.info(f"🍔 Encontradas {len(categories)} categorias no menu de navegação")
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar menu de navegação: {e}")
        
        return categories
    
    def _discover_from_sitemap(self) -> List[Dict[str, Any]]:
        """Descobre categorias no sitemap"""
        categories = []
        
        try:
            # URLs comuns de sitemap
            sitemap_urls = [
                f"{self.base_url}/sitemap.xml",
                f"{self.base_url}/sitemap",
                f"{self.base_url}/mapa-do-site",
                f"{self.base_url}/site-map"
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    response = self.session.get(sitemap_url, timeout=20)
                    if response.status_code == 200:
                        logger.info(f"📄 Sitemap encontrado em: {sitemap_url}")
                        
                        if 'xml' in response.headers.get('content-type', ''):
                            # Sitemap XML
                            soup = BeautifulSoup(response.content, 'xml')
                            urls = soup.find_all('url')
                            
                            for url_elem in urls:
                                loc = url_elem.find('loc')
                                if loc and loc.text:
                                    url = loc.text
                                    if self._is_category_url(url):
                                        # Extrair nome da categoria da URL
                                        name = self._extract_category_name_from_url(url)
                                        categories.append({
                                            'name': name,
                                            'url': url,
                                            'source': 'sitemap_xml'
                                        })
                        else:
                            # Sitemap HTML
                            soup = BeautifulSoup(response.content, 'html.parser')
                            links = soup.find_all('a', href=True)
                            
                            for link in links:
                                href = link.get('href')
                                text = link.get_text(strip=True)
                                
                                if href and self._is_valid_category_link(href, text):
                                    full_url = urljoin(self.base_url, href)
                                    categories.append({
                                        'name': text,
                                        'url': full_url,
                                        'source': 'sitemap_html'
                                    })
                        
                        break  # Se encontrou um sitemap, não precisa tentar os outros
                        
                except requests.RequestException:
                    continue  # Tentar próximo sitemap
            
            logger.info(f"🗺️ Encontradas {len(categories)} categorias no sitemap")
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar sitemap: {e}")
        
        return categories
    
    def _discover_from_footer(self) -> List[Dict[str, Any]]:
        """Descobre categorias no rodapé"""
        categories = []
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar footer
            footer_selectors = ['footer', '.footer', '#footer', '.rodape']
            
            for footer_selector in footer_selectors:
                footer = soup.select_one(footer_selector)
                if footer:
                    links = footer.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if href and text and self._is_valid_category_link(href, text):
                            full_url = urljoin(self.base_url, href)
                            categories.append({
                                'name': text,
                                'url': full_url,
                                'source': 'footer'
                            })
                    break
            
            logger.info(f"🦶 Encontradas {len(categories)} categorias no rodapé")
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar rodapé: {e}")
        
        return categories
    
    def _is_valid_category_link(self, href: str, text: str) -> bool:
        """Verifica se um link é uma categoria válida"""
        if not href or not text:
            return False
        
        # Ignorar links internos que não são categorias
        ignore_patterns = [
            'javascript:', 'mailto:', 'tel:', '#',
            '/conta', '/login', '/carrinho', '/checkout',
            '/contato', '/sobre', '/politica', '/termos',
            '/blog', '/noticias', '/ajuda', '/suporte',
            '/busca', '/search', '/pesquisa'
        ]
        
        href_lower = href.lower()
        for pattern in ignore_patterns:
            if pattern in href_lower:
                return False
        
        # Verificar se a URL parece uma categoria
        if not self._is_category_url(href):
            return False
        
        # Verificar se o texto contém palavras-chave de produtos do Creative Cópias
        text_lower = text.lower()
        creative_keywords = [
            'impressora', 'multifuncional', 'scanner', 'copiadora',
            'toner', 'cartucho', 'cartuchos', 'suprimento', 'suprimentos',
            'papel', 'papéis', 'etiqueta', 'etiquetas', 
            'ribbon', 'fita', 'cabo', 'cabos',
            'peça', 'peças', 'acessório', 'acessórios',
            'manutenção', 'limpeza', 'kit', 'refil',
            'fotográfico', 'fotografico'
        ]
        
        if any(keyword in text_lower for keyword in creative_keywords):
            return True
        
        # Verificar se o texto parece nome de categoria
        if any(word in text_lower for word in ['categoria', 'produtos', 'equipamentos']):
            return True
        
        # Verificar comprimento mínimo do texto
        if len(text.strip()) < 3:
            return False
        
        # Verificar se não é um link de navegação geral
        navigation_words = [
            'home', 'início', 'voltar', 'anterior', 'próximo',
            'página', 'pagina', 'ver mais', 'todos'
        ]
        
        if any(word in text_lower for word in navigation_words):
            return False
        
        return True
    
    def _is_category_url(self, url: str) -> bool:
        """Verifica se uma URL parece uma categoria de produtos"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Padrões específicos do Creative Cópias
        creative_patterns = [
            r'/impressoras',
            r'/multifuncionais',
            r'/cartuchos-de-toner',
            r'/cartuchos-de-tinta',
            r'/refil-de-toner',
            r'/refil-de-tinta',
            r'/papel-fotografico',
            r'/scanner',
            r'/suprimentos',
            r'/acessorios',
            r'/pecas',
            r'/manutencao'
        ]
        
        # Verificar padrões específicos primeiro
        for pattern in creative_patterns:
            if re.search(pattern, url_lower):
                return True
        
        # Verificar padrões gerais de categoria
        for pattern in self.category_url_patterns:
            if re.search(pattern, url_lower):
                return True
        
        # Verificar palavras-chave na URL
        if any(keyword in url_lower for keyword in self.product_keywords):
            return True
        
        return False
    
    def _extract_category_name_from_url(self, url: str) -> str:
        """Extrai nome da categoria da URL"""
        try:
            # Remover domínio e parâmetros
            path = urlparse(url).path
            
            # Pegar último segmento significativo
            segments = [s for s in path.split('/') if s]
            if segments:
                name = segments[-1]
                # Limpar e formatar
                name = name.replace('-', ' ').replace('_', ' ')
                name = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', name)
                return name.title().strip()
        
        except Exception:
            pass
        
        return "Categoria"
    
    def _normalize_and_deduplicate(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicatas e normaliza categorias"""
        seen_urls = set()
        unique_categories = []
        
        for category in categories:
            url = category['url'].rstrip('/')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_categories.append(category)
        
        return unique_categories
    
    def _validate_categories(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida se as categorias realmente têm produtos"""
        validated = []
        
        for i, category in enumerate(categories):
            try:
                logger.info(f"🔍 Validando categoria {i+1}/{len(categories)}: {category['name']}")
                
                # Fazer request para verificar se a página existe e tem produtos
                # Usar requests simples como no teste que funcionou
                response = requests.get(category['url'], timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Verificar se tem produtos na página (seletores específicos do Creative Cópias)
                    product_indicators = [
                        '.product-name',  # Selector principal encontrado na análise
                        '.item',  # Items de grid encontrados na análise
                        '.products-grid .item',  # Grid de produtos
                        '.category-products .item',  # Produtos de categoria
                        '.product-item',
                        '.product',
                        '.item-product',
                        '.price-box',
                        '.price',
                        '.preco',
                        '[data-product]',
                        'img[alt*="produto"]',
                        'a[href*="produto"]',  # Links de produtos
                        'a[href*="/p/"]',  # Padrão de URL de produto
                        '.showcase-item'  # Itens de vitrine
                    ]
                    
                    has_products = False
                    for indicator in product_indicators:
                        if soup.select(indicator):
                            has_products = True
                            break
                    
                    if has_products:
                        category['status'] = 'validated'
                        category['has_products'] = True
                        validated.append(category)
                        logger.debug(f"✅ Categoria válida: {category['name']}")
                    else:
                        logger.debug(f"⚠️ Categoria sem produtos detectados: {category['name']}")
                        category['status'] = 'no_products'
                        category['has_products'] = False
                else:
                    logger.debug(f"❌ Categoria inacessível (HTTP {response.status_code}): {category['name']}")
                    category['status'] = 'inaccessible'
                    category['has_products'] = False
                
                # Delay entre validações
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao validar categoria {category['name']}: {e}")
                category['status'] = 'error'
                category['has_products'] = False
        
        return validated
    
    def get_category_hierarchy(self, category_urls: List[str]) -> Dict[str, Any]:
        """
        Analisa a hierarquia de categorias
        
        Args:
            category_urls: Lista de URLs de categorias
            
        Returns:
            Hierarquia de categorias
        """
        hierarchy = {}
        
        for url in category_urls:
            try:
                response = self.session.get(url, timeout=20)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Procurar breadcrumbs para entender hierarquia
                breadcrumb_selectors = [
                    '.breadcrumb',
                    '.breadcrumbs', 
                    '.nav-breadcrumb',
                    '.breadcrumb-nav',
                    '[aria-label="breadcrumb"]'
                ]
                
                for selector in breadcrumb_selectors:
                    breadcrumb = soup.select_one(selector)
                    if breadcrumb:
                        links = breadcrumb.find_all('a', href=True)
                        if len(links) > 1:  # Tem hierarquia
                            parent = links[-2].get_text(strip=True)
                            current = links[-1].get_text(strip=True)
                            
                            if parent not in hierarchy:
                                hierarchy[parent] = []
                            if current not in hierarchy[parent]:
                                hierarchy[parent].append(current)
                        break
                
                time.sleep(0.5)  # Delay entre requests
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar hierarquia de {url}: {e}")
        
        return hierarchy
    
    def close(self):
        """Fecha a sessão"""
        self.session.close()