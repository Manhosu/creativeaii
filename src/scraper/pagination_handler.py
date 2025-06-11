"""
Pagination Handler
Sistema inteligente de paginação para capturar todos os produtos de cada categoria
"""

import re
import time
from typing import Dict, List, Set, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import requests
from loguru import logger

class PaginationHandler:
    """Manipulador inteligente de paginação"""
    
    def __init__(self, base_url: str = "https://www.creativecopias.com.br", 
                 delay_range: tuple = (1, 2), max_pages: int = 15):
        """
        Inicializa o manipulador de paginação
        
        Args:
            base_url: URL base do site
            delay_range: Delay entre requests
            max_pages: Máximo de páginas para evitar loops infinitos
        """
        self.base_url = base_url
        self.delay_range = delay_range
        self.max_pages = max_pages
        self.session = requests.Session()
        
        # Headers para parecer um navegador real (SEM Brotli para evitar problemas de compressão)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',  # Removido 'br' (Brotli) que estava causando problemas
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Padrões comuns de paginação (Creative Cópias usa 'p')
        self.pagination_patterns = {
            'url_params': [
                'p', 'page', 'pagina', 'pg', 'pagenum',
                'offset', 'start', 'from', 'skip'
            ],
            'css_selectors': [
                '.pagination a',
                '.pager a',
                '.page-numbers a',
                '.pages a',
                '.nav-pages a',
                '.pagination-links a',
                'a[rel="next"]',
                'a.next',
                'a.proximo',
                'a[title*="próxima"]',
                'a[title*="next"]'
            ],
            'text_patterns': [
                r'próxima?\s*página',
                r'next\s*page',
                r'próximo',
                r'next',
                r'>>',
                r'›',
                r'mais\s*produtos',
                r'ver\s*mais'
            ]
        }
        
        logger.info(f"🔄 Pagination Handler inicializado para {base_url}")
    
    def get_all_pages_from_category(self, category_url: str, 
                                   category_name: str = "") -> List[Dict[str, Any]]:
        """
        Obtém todas as páginas de uma categoria
        
        Args:
            category_url: URL da categoria
            category_name: Nome da categoria (para logs)
            
        Returns:
            Lista de páginas com produtos
        """
        logger.info(f"🔄 Iniciando paginação para categoria: {category_name or category_url}")
        
        pages = []
        current_url = category_url
        page_num = 1
        visited_urls = set()
        
        while page_num <= self.max_pages:
            try:
                # Evitar loops infinitos
                if current_url in visited_urls:
                    logger.warning(f"⚠️ URL já visitada, parando paginação: {current_url}")
                    break
                
                visited_urls.add(current_url)
                
                logger.info(f"📄 Processando página {page_num}: {current_url}")
                
                # Fazer request para a página atual
                response = self.session.get(current_url, timeout=30)
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ Página inacessível (HTTP {response.status_code}): {current_url}")
                    break
                
                # Garantir que o conteúdo seja decodificado corretamente
                response.encoding = response.apparent_encoding or 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
# Debug removido para performance
                
                # Verificar se há produtos na página (apenas contagem)
                product_count = self._count_products_on_page(soup)
                
                if product_count == 0:
                    logger.info(f"📄 Página {page_num} sem produtos, finalizando paginação")
                    break
                
                # Adicionar página aos resultados
                page_data = {
                    'page_number': page_num,
                    'url': current_url,
                    'products_count': product_count,
                    'category_name': category_name,
                    'timestamp': time.time()
                }
                
                pages.append(page_data)
                
                logger.info(f"✅ Página {page_num}: {product_count} produtos encontrados")
                
                # Procurar próxima página
                next_url = self._find_next_page_url(soup, current_url)
                
                if not next_url:
                    logger.info(f"📄 Não há próxima página, finalizando paginação")
                    break
                
                current_url = next_url
                page_num += 1
                
                # Delay entre páginas
                time.sleep(self.delay_range[0])
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar página {page_num}: {e}")
                break
        
        total_products = sum(page['products_count'] for page in pages)
        logger.info(f"🎯 Paginação concluída: {len(pages)} páginas, {total_products} produtos totais")
        
        return pages
    
    def _count_products_on_page(self, soup: BeautifulSoup) -> int:
        """Conta produtos em uma página (mais rápido que extrair dados completos)"""
        # Usar os mesmos seletores que o CreativeScraper para consistência
        selectors = [
            '.product-name',  # Seletor específico primeiro
            '.item',  # Priorizar .item que funciona para cartuchos/toners
            '.products-grid .item',  # Grid de produtos
            '.category-products .item',  # Produtos de categoria
            '.product-item',
            '.product'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            
            if elements:
                # Filtrar elementos que realmente parecem produtos
                valid_count = 0
                for element in elements:
                    # Verificar se tem características de produto
                    has_name = element.select_one('.product-name, h2, h3, a[title]')
                    has_price = element.select_one('.price-box, .price, .preco')
                    has_link = element.select_one('a[href]')
                    
                    if has_name or has_price or has_link:
                        valid_count += 1
                
                if valid_count > 0:
                    return valid_count
        return 0
    
    def _extract_products_from_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrai produtos de uma página"""
        products = []
        
        # Seletores para produtos no Creative Cópias (mesmos do CreativeScraper)
        product_selectors = [
            '.product-name',  # Seletor específico primeiro
            '.item',  # Priorizar .item que funciona para cartuchos/toners
            '.products-grid .item',  # Grid de produtos
            '.category-products .item',  # Produtos de categoria
            '.product-item',
            '.product',
            '.showcase-item'
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            
            if elements:
                logger.debug(f"🔍 Encontrados {len(elements)} produtos com selector: {selector}")
                
                for element in elements:
                    product_data = self._extract_product_data(element)
                    if product_data:
                        products.append(product_data)
                
                break  # Usar apenas o primeiro selector que encontrar produtos
        
        # Remover duplicatas baseado no nome ou código
        unique_products = []
        seen_names = set()
        
        for product in products:
            name = product.get('name', '').strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_products.append(product)
        
        return unique_products
    
    def _extract_product_data(self, element) -> Optional[Dict[str, Any]]:
        """Extrai dados de um produto"""
        try:
            # Nome do produto
            name_element = element if element.name == 'a' else element.find('a')
            if not name_element:
                name_element = element.find(class_='product-name')
            
            if not name_element:
                return None
            
            name = name_element.get_text(strip=True)
            if not name:
                return None
            
            # URL do produto
            url = name_element.get('href')
            if url:
                url = urljoin(self.base_url, url)
            
            # Preço (se disponível)
            price = None
            price_selectors = ['.price', '.preco', '.price-box', '.valor']
            for selector in price_selectors:
                price_element = element.find(class_=selector.replace('.', ''))
                if price_element:
                    price = price_element.get_text(strip=True)
                    break
            
            # Imagem (se disponível)
            image = None
            img_element = element.find('img')
            if img_element:
                image = img_element.get('src')
                if image:
                    image = urljoin(self.base_url, image)
            
            return {
                'name': name,
                'url': url,
                'price': price,
                'image': image,
                'source': 'pagination_extract'
            }
            
        except Exception as e:
            logger.debug(f"⚠️ Erro ao extrair dados do produto: {e}")
            return None
    
    def _find_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Encontra a URL da próxima página"""
        
        # Método 1: Procurar por links de "próxima página"
        next_url = self._find_next_by_css_selectors(soup)
        if next_url:
            return urljoin(self.base_url, next_url)
        
        # Método 2: Procurar por padrões de URL com parâmetros
        next_url = self._find_next_by_url_pattern(current_url)
        if next_url:
            return next_url
        
        # Método 3: Procurar por JavaScript patterns
        next_url = self._find_next_by_javascript(soup, current_url)
        if next_url:
            return next_url
        
        return None
    
    def _find_next_by_css_selectors(self, soup: BeautifulSoup) -> Optional[str]:
        """Encontra próxima página usando CSS selectors"""
        
        # Primeiro, procurar especificamente por link "próxima" ou "next"
        next_links = soup.select('a.next, a[rel="next"]')
        if next_links:
            href = next_links[0].get('href')
            if href:
                return href
        
        # Procurar por links de paginação com números
        pagination_links = soup.select('.pagination a, .pager a, .pages a')
        current_page = 1  # Assumir página 1 se não especificado
        
        # Tentar extrair página atual da URL ou elementos
        for link in pagination_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Se o link tem um número e não é a página atual, pode ser próxima
            if text.isdigit():
                page_num = int(text)
                if page_num == current_page + 1:  # Próxima página
                    return href
        
        # Se não encontrou próxima específica, pegar qualquer link com p=2 (assumindo página 1)
        for link in pagination_links:
            href = link.get('href', '')
            if 'p=2' in href:
                return href
        
        return None
    
    def _find_next_by_url_pattern(self, current_url: str) -> Optional[str]:
        """Encontra próxima página incrementando parâmetros da URL"""
        
        parsed = urlparse(current_url)
        query_params = parse_qs(parsed.query)
        
        # Procurar por parâmetros de página
        for param in self.pagination_patterns['url_params']:
            if param in query_params:
                try:
                    current_page = int(query_params[param][0])
                    next_page = current_page + 1
                    
                    # Criar nova URL com próxima página
                    new_params = query_params.copy()
                    new_params[param] = [str(next_page)]
                    
                    new_query = urlencode(new_params, doseq=True)
                    new_parsed = parsed._replace(query=new_query)
                    
                    return urlunparse(new_parsed)
                    
                except (ValueError, IndexError):
                    continue
        
        # Se não há parâmetro de página, tentar adicionar
        if not any(param in query_params for param in self.pagination_patterns['url_params']):
            new_params = query_params.copy()
            new_params['page'] = ['2']  # Assumir que estamos na página 1
            
            new_query = urlencode(new_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            
            return urlunparse(new_parsed)
        
        return None
    
    def _find_next_by_javascript(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Encontra próxima página analisando JavaScript"""
        
        scripts = soup.find_all('script', string=True)
        
        for script in scripts:
            content = script.string
            if not content:
                continue
            
            # Procurar por padrões de paginação em JavaScript
            patterns = [
                r'nextPage\s*:\s*["\']([^"\']+)["\']',
                r'next_page_url\s*:\s*["\']([^"\']+)["\']',
                r'proximaPagina\s*:\s*["\']([^"\']+)["\']',
                r'page\s*\+\s*1',
                r'currentPage\s*\+\s*1'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    return matches[0]
        
        return None
    
    def analyze_pagination_structure(self, category_url: str) -> Dict[str, Any]:
        """
        Analisa a estrutura de paginação de uma categoria
        
        Args:
            category_url: URL da categoria para analisar
            
        Returns:
            Análise da estrutura de paginação
        """
        logger.info(f"🔍 Analisando estrutura de paginação: {category_url}")
        
        try:
            response = self.session.get(category_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': category_url,
                'has_pagination': False,
                'pagination_type': None,
                'total_pages_detected': 0,
                'pagination_elements': [],
                'url_patterns': [],
                'javascript_pagination': False
            }
            
            # Verificar elementos de paginação
            for selector in self.pagination_patterns['css_selectors']:
                elements = soup.select(selector)
                if elements:
                    analysis['has_pagination'] = True
                    analysis['pagination_elements'].append({
                        'selector': selector,
                        'count': len(elements),
                        'links': [elem.get('href') for elem in elements if elem.get('href')]
                    })
            
            # Verificar padrões de URL
            parsed = urlparse(category_url)
            query_params = parse_qs(parsed.query)
            
            for param in self.pagination_patterns['url_params']:
                if param in query_params:
                    analysis['url_patterns'].append({
                        'parameter': param,
                        'current_value': query_params[param][0]
                    })
            
            # Verificar JavaScript
            scripts = soup.find_all('script', string=True)
            for script in scripts:
                if script.string and any(word in script.string.lower() 
                                       for word in ['pagination', 'page', 'next', 'proximo']):
                    analysis['javascript_pagination'] = True
                    break
            
            # Tentar detectar total de páginas
            page_numbers = []
            for element in soup.select('.pagination a, .pager a, .page-numbers a'):
                text = element.get_text(strip=True)
                if text.isdigit():
                    page_numbers.append(int(text))
            
            if page_numbers:
                analysis['total_pages_detected'] = max(page_numbers)
            
            # Determinar tipo de paginação
            if analysis['pagination_elements']:
                analysis['pagination_type'] = 'css_links'
            elif analysis['url_patterns']:
                analysis['pagination_type'] = 'url_parameters'
            elif analysis['javascript_pagination']:
                analysis['pagination_type'] = 'javascript'
            
            logger.info(f"📊 Análise concluída: {analysis['pagination_type']}, "
                       f"{analysis['total_pages_detected']} páginas detectadas")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de paginação: {e}")
            return {
                'url': category_url,
                'error': str(e),
                'has_pagination': False
            }
    
    def close(self):
        """Fecha a sessão"""
        self.session.close()