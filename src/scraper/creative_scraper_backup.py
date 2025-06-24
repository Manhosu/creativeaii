"""
Scraper específico para Creative Cópias
Implementa métodos de extração para https://www.creativecopias.com.br
"""

from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import requests
import re
import os
from loguru import logger
from .scraper_base import ScraperBase
from .pagination_handler import PaginationHandler

class CreativeScraper(ScraperBase):
    """Scraper específico para Creative Cópias"""
    
    def __init__(self, delay_range: tuple = (2, 4), timeout: int = 30):
        """
        Inicializa scraper do Creative Cópias
        
        Args:
            delay_range: Delay entre requests (2-4 segundos)
            timeout: Timeout para requests
        """
        super().__init__(delay_range, timeout)
        self.base_url = os.getenv("SITE_BASE_URL", "https://www.creativecopias.com.br")
        
        # Headers específicos para Creative Cópias (sem User-Agent específico)
        # Criar nova sessão limpa para evitar headers herdados
        self.session.close()
        self.session = requests.Session()
            
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Inicializar handler de paginação
        self.pagination_handler = PaginationHandler(delay_range=(1, 2))
        
        logger.info("🚀 Creative Scraper inicializado")
    
    def load_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Carrega página da Creative Cópias
        
        Args:
            url: URL para carregar
            
        Returns:
            BeautifulSoup object ou None se erro
        """
        try:
            logger.info(f"📄 Carregando página: {url}")
            
            # Usar requests simples sem User-Agent específico (funciona melhor com Creative Cópias)
            response = requests.get(url, timeout=self.timeout)
            
            # Verificar se página carregou corretamente
            if "creative" not in response.text.lower():
                logger.warning(f"⚠️ Página pode não ter carregado corretamente: {url}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.debug(f"✅ Página carregada com sucesso: {len(response.content)} bytes")
            
            return soup
            
        except requests.RequestException as e:
            logger.error(f"❌ Erro de rede ao carregar {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao processar página {url}: {e}")
            return None
    
    def parse_product_list(self, html: BeautifulSoup) -> List[Any]:
        """
        Extrai elementos de produtos da página
        
        Args:
            html: BeautifulSoup da página
            
        Returns:
            Lista de elementos de produtos
        """
        try:
            products = []
            
            logger.info("🔍 Iniciando parse_product_list...")
            
            # Primeiro, buscar especificamente por elementos com .product-name (detectado na análise)
            product_names = html.select('.product-name')
            logger.info(f"📦 Busca por .product-name retornou {len(product_names)} elementos")
            
            if product_names:
                logger.info(f"📦 Encontrados {len(product_names)} elementos .product-name")
                for i, name_elem in enumerate(product_names):
                    logger.debug(f"  [{i+1}] Processando: {name_elem.get_text(strip=True)[:50]}...")
                    # Pegar o container pai do produto
                    parent = name_elem.find_parent(['li', 'div', 'article'])
                    if parent and parent not in products:
                        products.append(parent)
                        logger.debug(f"      ✅ Produto {i+1} adicionado")
            
            if products:
                logger.info(f"📦 {len(products)} produtos encontrados via .product-name")
                logger.info(f"🎯 Total de {len(products)} produtos prontos para extração")
                return products
            
            # Se não encontrou, tenta seletores específicos
            selectors = [
                '.item',  # Priorizar .item que funciona para cartuchos/toners
                '.products-grid .item',  # Magento products grid items
                '.category-products .item',  # Magento category products
                '.item .product-name',  # Items com product name dentro
                '.product-item',  # Padrão Magento 2
                '.product',
                '.item-product',
                '[data-product]',
                '.card-product',
                '.product-card',
                '.showcase-item',
                'li[id*="product"]',
                '.vitrine-produto',
                '.produto-item'
            ]
            
            for selector in selectors:
                elements = html.select(selector)
                if elements:
                    logger.info(f"📦 Encontrados {len(elements)} produtos usando seletor: {selector}")
                    # Filtrar elementos que realmente parecem produtos
                    valid_products = []
                    for element in elements:
                        # Verificar se tem características de produto
                        has_name = element.select_one('.product-name, h2, h3, a[title]')
                        has_price = element.select_one('.price-box, .price, .preco')
                        has_link = element.select_one('a[href]')
                        
                        if has_name or has_price or has_link:
                            valid_products.append(element)
                    
                    if valid_products:
                        logger.info(f"✅ {len(valid_products)} produtos válidos encontrados com {selector}")
                        products.extend(valid_products)
                        break
            
            # Se não encontrou com seletores específicos, tenta busca mais genérica
            if not products:
                # Buscar por links que contenham palavras relacionadas a produtos
                links = html.find_all('a', href=True)
                product_links = []
                
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    # Verificar se é link de produto baseado na URL ou texto
                    if any(keyword in href.lower() for keyword in ['produto', 'item', '/p/', '/product']):
                        product_links.append(link.parent or link)
                    elif any(keyword in text for keyword in ['impressora', 'multifuncional', 'toner', 'cartucho']):
                        product_links.append(link.parent or link)
                
                products = list(set(product_links))  # Remove duplicatas
                
                if products:
                    logger.info(f"📦 Encontrados {len(products)} produtos via busca genérica")
            
            # Se ainda não encontrou, buscar por imagens de produtos
            if not products:
                img_elements = html.find_all('img', src=True)
                for img in img_elements:
                    src = img.get('src', '').lower()
                    alt = img.get('alt', '').lower()
                    
                    if any(keyword in src for keyword in ['produto', 'product', 'item']) or \
                       any(keyword in alt for keyword in ['impressora', 'multifuncional', 'toner']):
                        parent = img.find_parent(['div', 'li', 'article', 'section'])
                        if parent:
                            products.append(parent)
                
                products = list(set(products))  # Remove duplicatas
                
                if products:
                    logger.info(f"📦 Encontrados {len(products)} produtos via análise de imagens")
            
            if not products:
                logger.warning("⚠️ Nenhum produto encontrado na página")
                # Debug: salvar HTML para análise
                with open('logs/debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(str(html))
                logger.info("🔍 HTML da página salvo em logs/debug_page.html para análise")
            else:
                logger.info(f"🎯 Total de {len(products)} produtos prontos para extração")
            
            return products
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair lista de produtos: {e}")
            return []
    
    def extract_product_data(self, product_element: Any) -> Dict[str, Any]:
        """
        Extrai dados de um produto específico
        
        Args:
            product_element: Elemento HTML do produto
            
        Returns:
            Dicionário com dados do produto
        """
        try:
            product_data = {}
            
            # Extrair nome do produto
            name = self._extract_product_name(product_element)
            if not name:
                return {}  # Nome é obrigatório
            
            product_data['nome'] = name
            
            # Extrair URL do produto
            url = self._extract_product_url(product_element)
            product_data['url'] = url
            
            # Extrair preço
            price = self._extract_product_price(product_element)
            product_data['preco'] = price
            
            # Extrair código do produto
            codigo = self._extract_product_code(product_element)
            product_data['codigo'] = codigo
            
            # Extrair marca
            marca = self._extract_product_brand(product_element)
            product_data['marca'] = marca
            
            # Extrair descrição
            descricao = self._extract_product_description(product_element)
            product_data['descricao'] = descricao
            
            # Extrair imagem
            imagem = self._extract_product_image(product_element)
            product_data['imagem'] = imagem
            
            # Extrair disponibilidade
            disponivel = self._extract_product_availability(product_element)
            product_data['disponivel'] = disponivel
            
            logger.debug(f"✅ Dados extraídos para: {name}")
            return product_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados do produto: {e}")
            return {}
    
    def _extract_product_name(self, element: Any) -> Optional[str]:
        """Extrai nome do produto"""
        selectors = [
            '.product-name', '.nome-produto', '.title',  # Seletores específicos primeiro
            'a[title]',  # Links com título
            'a',  # Qualquer link (para elementos .item)
            'h3', 'h2', 'h4',  # Headers
            '[data-name]', '.product-title'
        ]
        
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    # Primeiro tentar atributo title
                    if hasattr(found, 'get') and found.get('title'):
                        title = found.get('title').strip()
                        if len(title) > 3:
                            return title
                    
                    # Depois tentar texto do elemento
                    text = found.get_text(strip=True)
                    if len(text) > 3:  # Nome válido deve ter mais de 3 caracteres
                        return text
            except:
                continue
        
        # Última tentativa: pegar primeiro texto significativo
        text = element.get_text(strip=True)
        if text and len(text) > 3:
            # Pegar primeira linha que pareça um nome de produto
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and not line.startswith('R$') and not line.lower().startswith('marca'):
                    return line
        
        return None
    
    def _extract_product_url(self, element: Any) -> Optional[str]:
        """Extrai URL do produto"""
        try:
            # Buscar link dentro do elemento
            link = element.find('a', href=True)
            if link:
                href = link.get('href')
                
                # Se for URL relativa, adicionar domínio
                if href.startswith('/'):
                    return self.base_url + href
                elif href.startswith('http'):
                    return href
                else:
                    return self.base_url + '/' + href
        except:
            pass
        
        return None
    
    def _extract_product_price(self, element: Any) -> Optional[str]:
        """Extrai preço do produto"""
        price_selectors = [
            '.price', '.preco', '.valor',
            '[data-price]', '.product-price',
            '.money', '.currency'
        ]
        
        for selector in price_selectors:
            try:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extrair números e vírgulas/pontos do preço
                    price_match = re.search(r'R\$[\s]*([0-9.,]+)', price_text)
                    if price_match:
                        return f"R$ {price_match.group(1)}"
            except:
                continue
        
        # Busca mais genérica por padrão de preço
        text = element.get_text()
        price_pattern = r'R\$[\s]*([0-9.,]+)'
        match = re.search(price_pattern, text)
        if match:
            return f"R$ {match.group(1)}"
        
        return None
    
    def _extract_product_code(self, element: Any) -> Optional[str]:
        """Extrai código do produto"""
        try:
            text = element.get_text()
            
            # Padrões comuns de código
            patterns = [
                r'Código[:\s]*([A-Z0-9\-]+)',
                r'Ref[:\s]*([A-Z0-9\-]+)',
                r'SKU[:\s]*([A-Z0-9\-]+)',
                r'Item[:\s]*([A-Z0-9\-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        return None
    
    def _extract_product_brand(self, element: Any) -> Optional[str]:
        """Extrai marca do produto"""
        try:
            brand_selectors = [
                '.brand', '.marca', '.fabricante',
                '[data-brand]', '.manufacturer'
            ]
            
            for selector in brand_selectors:
                brand_elem = element.select_one(selector)
                if brand_elem:
                    return brand_elem.get_text(strip=True)
            
            # Buscar marcas conhecidas no texto
            text = element.get_text().lower()
            brands = ['hp', 'canon', 'epson', 'brother', 'samsung', 'lexmark', 'xerox', 'ricoh']
            
            for brand in brands:
                if brand in text:
                    return brand.upper()
        except:
            pass
        
        return None
    
    def _extract_product_description(self, element: Any) -> Optional[str]:
        """Extrai descrição do produto"""
        try:
            desc_selectors = [
                '.description', '.descricao', '.resumo',
                '.product-description', '.summary'
            ]
            
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    desc = desc_elem.get_text(strip=True)
                    if len(desc) > 20:  # Descrição válida deve ser mais longa
                        return desc[:200]  # Limitar tamanho
        except:
            pass
        
        return None
    
    def _extract_product_image(self, element: Any) -> Optional[str]:
        """
        Extrai URL da imagem do produto com priorização da imagem PRINCIPAL
        CORRIGIDO: Evita capturar imagens de produtos relacionados
        """
        try:
            # PRIORIDADE 1: Imagens de ALTA RESOLUÇÃO (foco em qualidade máxima)
            high_res_selectors = [
                'img[src*="/image/1800x/"][src*="media/catalog/product"]',        # Máxima qualidade (1800x)
                'img[src*="/small_image/1800x"][src*="media/catalog/product"]',   # Alta qualidade (1800x small)
                'img[src*="/image/1200x/"][src*="media/catalog/product"]',        # Boa qualidade (1200x)
                'img[src*="/small_image/1200x"][src*="media/catalog/product"]',   # Boa qualidade (1200x small)
                'img[src*="1800x"][src*="media/catalog/product"]',                # Fallback 1800x geral
                'img[src*="1200x"][src*="media/catalog/product"]',                # Fallback 1200x geral
            ]
            
            # Primeiro: Tentar alta resolução
            for selector in high_res_selectors:
                try:
                    images = element.select(selector)
                    for img in images:
                        src = self._get_image_src_with_fallbacks(img)
                        if src and not self._is_invalid_image(src):
                            absolute_url = self._make_absolute_url(src)
                            if absolute_url:
                                logger.info(f"🖼️ ALTA RESOLUÇÃO capturada: {absolute_url}")
                                return absolute_url
                except Exception as e:
                    logger.debug(f"❌ Erro no seletor alta res {selector}: {e}")
                    continue
            
            # PRIORIDADE 2: Imagens principais de produto (média resolução)
            main_selectors = [
                '.product-image-main img[src*="media/catalog/product"]',  # Container principal
                '.main-image img[src*="media/catalog/product"]',          # Imagem principal
                '.product-view .product-image img[src*="media/catalog/product"]',  # View específica
            ]
            
            for selector in main_selectors:
                try:
                    img = element.select_one(selector)
                    if img:
                        src = self._get_image_src_with_fallbacks(img)
                        if src and not self._is_invalid_image(src):
                            # Validação específica para imagem principal
                            if self._is_main_product_image(src, element):
                                absolute_url = self._make_absolute_url(src)
                                if absolute_url:
                                    logger.info(f"🖼️ Imagem PRINCIPAL extraída: {absolute_url}")
                                    return absolute_url
                except Exception as e:
                    logger.debug(f"❌ Erro no seletor principal {selector}: {e}")
                    continue
                    
            # PRIORIDADE 2: Imagens de produto com ALT text correspondente
            product_name = self._extract_product_name_for_image_validation(element)
            
            alt_selectors = [
                'img[src*="media/catalog/product"]',
                '.product-image img',
                'img[class*="product"]'
            ]
            
            for selector in alt_selectors:
                try:
                    imgs = element.select(selector)
                    for img in imgs:
                        src = self._get_image_src_with_fallbacks(img)
                        alt = img.get('alt', '').lower()
                        
                        if src and not self._is_invalid_image(src):
                            # Verificar se ALT text corresponde ao produto
                            if product_name and self._alt_matches_product(alt, product_name):
                                # Priorizar imagens maiores
                                if any(size in src for size in ['1800x', '1200x', '800x']):
                                    absolute_url = self._make_absolute_url(src)
                                    if absolute_url:
                                        logger.info(f"🖼️ Imagem com ALT correspondente: {absolute_url}")
                                        return absolute_url
                except Exception as e:
                    logger.debug(f"❌ Erro no seletor ALT {selector}: {e}")
                    continue
                    
            # PRIORIDADE 3: Fallback para primeira imagem válida de produto (com filtros rigorosos)
            fallback_selectors = [
                'img[src*="/media/catalog/product/"][src*="ampliada"]',  # Imagens ampliadas
                'img[src*="/media/catalog/product/cache/1/image/"]',     # Cache de imagens
                '.product-image img',                                     # Container de produto
            ]
            
            for selector in fallback_selectors:
                try:
                    imgs = element.select(selector)
                    
                    # Filtrar e ordenar por qualidade
                    valid_images = []
                    for img in imgs:
                        src = self._get_image_src_with_fallbacks(img)
                        if src and not self._is_invalid_image(src):
                            # Calcular "score" da imagem
                            score = self._calculate_image_quality_score(src, img)
                            valid_images.append((score, src, img))
                    
                    # Ordenar por score (maior primeiro)
                    valid_images.sort(reverse=True)
                    
                    # Retornar a melhor imagem
                    if valid_images:
                        best_score, best_src, best_img = valid_images[0]
                        absolute_url = self._make_absolute_url(best_src)
                        if absolute_url:
                            logger.info(f"🖼️ Melhor imagem (score: {best_score}): {absolute_url}")
                            return absolute_url
                        
                except Exception as e:
                    logger.debug(f"❌ Erro no seletor fallback {selector}: {e}")
                    continue
            
            logger.warning(f"⚠️ Nenhuma imagem válida encontrada no elemento")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro crítico ao extrair imagem: {e}")
            return None
    
    def _get_image_src_with_fallbacks(self, img) -> Optional[str]:
        """Obtém src da imagem com fallbacks para lazy loading"""
        return (img.get('src') or 
                img.get('data-src') or 
                img.get('data-original') or 
                img.get('data-lazy') or
                img.get('data-image') or
                img.get('data-img'))
    
    def _extract_product_name_for_image_validation(self, element) -> str:
        """Extrai nome do produto para validação de imagem"""
        try:
            # Procurar title da página
            title = element.find('title')
            if title:
                return title.get_text().strip()
            
            # Procurar h1
            h1 = element.find('h1')
            if h1:
                return h1.get_text().strip()
            
            # Procurar meta title
            meta_title = element.find('meta', attrs={'name': 'title'})
            if meta_title:
                return meta_title.get('content', '').strip()
                
            return ""
        except:
            return ""
    
    def _is_main_product_image(self, src: str, element) -> bool:
        """Verifica se é a imagem principal do produto"""
        # Imagens grandes são mais prováveis de serem principais
        if any(size in src for size in ['1800x', '1200x', '800x']):
            return True
        
        # Verificar se não está em seção de produtos relacionados
        src_lower = src.lower()
        if any(related in src_lower for related in ['related', 'similar', 'cross', 'up-sell']):
            return False
        
        return True
    
    def _alt_matches_product(self, alt: str, product_name: str) -> bool:
        """Verifica se ALT text corresponde ao produto"""
        if not alt or not product_name:
            return False
        
        alt = alt.lower()
        product_name = product_name.lower()
        
        # Extrair palavras-chave principais
        keywords = []
        
        # Palavras-chave do produto
        if 'cabo' in product_name:
            keywords.append('cabo')
        if 'painel' in product_name:
            keywords.append('painel')
        if 'pantum' in product_name:
            keywords.append('pantum')
        if 'm6800' in product_name:
            keywords.append('m6800')
        if 'm7100' in product_name:
            keywords.append('m7100')
        if 'm7200' in product_name:
            keywords.append('m7200')
        
        # Verificar se pelo menos 2 palavras-chave coincidem
        matches = sum(1 for keyword in keywords if keyword in alt)
        return matches >= 2
    
    def _calculate_image_quality_score(self, src: str, img) -> int:
        """Calcula score de qualidade da imagem (ATUALIZADO para priorizar 1800x)"""
        score = 0
        
        # Tamanho da imagem (prioridade MÁXIMA para 1800x)
        if '/image/1800x/' in src:
            score += 200  # Prioridade MÁXIMA para cache/1/image/1800x/
        elif '/small_image/1800x' in src:
            score += 180  # Alta prioridade para small_image 1800x
        elif '1800x' in src:
            score += 150  # Prioridade alta para qualquer 1800x
        elif '/image/1200x/' in src:
            score += 120  # Boa qualidade 1200x
        elif '/small_image/1200x' in src:
            score += 100  # Boa qualidade 1200x small
        elif '1200x' in src:
            score += 90   # Qualquer 1200x
        elif '800x' in src:
            score += 60
        elif '455x' in src or '400x' in src:
            score += 40
        elif '220x' in src or '200x' in src:
            score += 20
        elif '70x' in src or '100x' in src:
            score += 5  # Thumbnails têm score baixo
        
        # ALT text presente
        if img.get('alt'):
            score += 20
        
        # Imagem ampliada
        if 'ampliada' in src:
            score += 30
        
        # Evitar imagens de produtos relacionados
        if any(related in src.lower() for related in ['related', 'cross', 'similar']):
            score -= 50
        
        # Preferir imagens do cache principal
        if '/cache/1/image/' in src:
            score += 15
        
        return score
    
    def _is_invalid_image(self, src: str) -> bool:
        """
        Verifica se a URL da imagem deve ser rejeitada
        
        Args:
            src: URL da imagem a verificar
            
        Returns:
            True se a imagem é inválida
        """
        if not src:
            return True
        
        src_lower = src.lower()
        
        # Filtros de tamanho (imagens muito pequenas)
        size_filters = ['1x1', '10x10', '20x20', '0x0', 'px.gif', 'spacer', 'blank']
        if any(size in src_lower for size in size_filters):
            return True
        
        # Filtros de tipo (imagens de controle/sistema)
        type_filters = [
            'placeholder', 'loading', 'spinner', 'ajax-loader',
            'transparent', 'clear', 'empty', 'dummy', 'fake',
            'icon-', 'sprite', 'css', 'background', 'border',
            'arrow', 'button', 'nav', 'menu', 'close', 'search'
        ]
        if any(filter_type in src_lower for filter_type in type_filters):
            return True
        
        # Filtros de extensão inválida
        invalid_extensions = ['.css', '.js', '.txt', '.html', '.php']
        if any(src_lower.endswith(ext) for ext in invalid_extensions):
            return True
        
        # Filtros de URL suspeitas
        suspicious_patterns = [
            'data:image/gif;base64,R0lGOD',  # GIF transparente comum
            'data:image/svg+xml',           # SVG inline muito simples
            'javascript:',                   # URLs JavaScript
            'mailto:',                      # URLs de email
            '#'                            # Links âncora
        ]
        if any(pattern in src for pattern in suspicious_patterns):
            return True
        
        # Se passou por todos os filtros, é válida
        return False
    
    def _make_absolute_url(self, src: str) -> Optional[str]:
        """
        Converte URL relativa para absoluta usando base da Creative Cópias
        
        Args:
            src: URL da imagem (pode ser relativa ou absoluta)
            
        Returns:
            URL absoluta válida ou None
        """
        if not src:
            return None
        
        # Se já é absoluta e válida, retornar
        if src.startswith('http'):
            # Verificar se é do domínio Creative Cópias ou confiável
            trusted_domains = [
                'creativecopias.com.br',
                'via.placeholder.com',
                'images.unsplash.com',
                'picsum.photos'
            ]
            
            if any(domain in src for domain in trusted_domains):
                return src
            else:
                # URL externa - logar mas retornar mesmo assim
                logger.debug(f"📎 URL externa aceita: {src}")
                return src
        
        # URLs data: são válidas mas não ideais
        if src.startswith('data:'):
            logger.debug(f"📊 Data URL encontrada: {src[:50]}...")
            return src
        
        # Converter URL relativa para absoluta
        base_url = getattr(self, 'base_url', 'https://www.creativecopias.com.br')
        
        if src.startswith('/'):
            # URL relativa à raiz
            absolute_url = f"{base_url}{src}"
        elif src.startswith('./'):
            # URL relativa ao diretório atual
            absolute_url = f"{base_url}/{src[2:]}"
        elif src.startswith('../'):
            # URL relativa ao diretório pai (não comum em produtos)
            logger.warning(f"⚠️ URL relativa ao diretório pai: {src}")
            absolute_url = f"{base_url}/{src}"
        else:
            # URL relativa simples
            absolute_url = f"{base_url}/{src}"
        
        # Limpar URL duplicada (evitar ///)
        absolute_url = absolute_url.replace('///', '//')
        if absolute_url.count('//') > 1:
            absolute_url = absolute_url.replace('//', '/', 1).replace('//', '/')
            absolute_url = absolute_url.replace('http:/', 'http://').replace('https:/', 'https://')
        
        logger.debug(f"🔗 URL convertida: {src} → {absolute_url}")
        return absolute_url
    
    def _extract_product_availability(self, element: Any) -> bool:
        """Verifica se produto está disponível"""
        try:
            text = element.get_text().lower()
            
            # Palavras que indicam indisponibilidade
            unavailable_words = ['indisponível', 'esgotado', 'fora de estoque', 'sem estoque']
            
            for word in unavailable_words:
                if word in text:
                    return False
            
            # Se encontrar botão de comprar, provavelmente está disponível
            buy_button = element.find(['button', 'a'], text=re.compile(r'comprar|adicionar', re.I))
            if buy_button:
                return True
                
        except:
            pass
        
        # Assumir disponível por padrão
        return True
    
    def scrape_category_with_pagination(self, category_url: str, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Scraping de categoria com paginação automática
        
        Args:
            category_url: URL da categoria
            max_pages: Máximo de páginas para processar
            
        Returns:
            Lista de produtos de todas as páginas
        """
        logger.info(f"🕷️ Iniciando scraping com paginação: {category_url}")
        
        all_products = []
        
        try:
            # Usar pagination handler para obter todas as páginas
            pages_data = self.pagination_handler.get_all_pages_from_category(
                category_url, 
                category_name=category_url.split('/')[-1]
            )
            
            for page_data in pages_data:
                page_num = page_data['page_number']
                logger.info(f"📄 Processando página {page_num}...")
                
                # Carregar a página para extrair dados completos
                soup = self.load_page(page_data['url'])
                if not soup:
                    logger.warning(f"⚠️ Não foi possível carregar página {page_num}")
                    continue
                
                # Extrair produtos da página atual
                product_elements = self.parse_product_list(soup)
                
                if product_elements:
                    logger.info(f"📦 Encontrados {len(product_elements)} produtos na página {page_num}")
                    
                    # Extrair dados de cada produto
                    for i, element in enumerate(product_elements):
                        try:
                            product_data = self.extract_product_data(element)
                            if product_data and product_data.get('nome'):
                                # Adicionar informações da página
                                product_data['page_number'] = page_num
                                product_data['page_url'] = page_data['url']
                                all_products.append(product_data)
                                logger.debug(f"✅ Produto {i+1} extraído: {product_data['nome'][:50]}...")
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao extrair produto {i+1}: {e}")
                            continue
                else:
                    logger.warning(f"⚠️ Nenhum produto encontrado na página {page_num}")
                
                # Delay entre páginas
                self._apply_delay()
            
            logger.info(f"🎯 Scraping com paginação concluído: {len(all_products)} produtos "
                       f"encontrados em {len(pages_data)} páginas")
            
            return all_products
            
        except Exception as e:
            logger.error(f"❌ Erro no scraping com paginação: {e}")
            return all_products
    
    def analyze_category_structure(self, category_url: str) -> Dict[str, Any]:
        """
        Analisa a estrutura de uma categoria (paginação, produtos, etc.)
        
        Args:
            category_url: URL da categoria para analisar
            
        Returns:
            Análise detalhada da categoria
        """
        logger.info(f"🔍 Analisando estrutura da categoria: {category_url}")
        
        try:
            # Analisar paginação
            pagination_analysis = self.pagination_handler.analyze_pagination_structure(category_url)
            
            # Carregar primeira página para análise de produtos
            soup = self.load_page(category_url)
            if not soup:
                return {'error': 'Não foi possível carregar a página'}
            
            # Analisar produtos na primeira página
            product_elements = self.parse_product_list(soup)
            
            analysis = {
                'category_url': category_url,
                'pagination': pagination_analysis,
                'products_on_first_page': len(product_elements),
                'has_products': len(product_elements) > 0,
                'estimated_total_products': None
            }
            
            # Estimar total de produtos
            if pagination_analysis.get('has_pagination') and pagination_analysis.get('total_pages'):
                estimated_total = len(product_elements) * pagination_analysis['total_pages']
                analysis['estimated_total_products'] = estimated_total
                logger.info(f"📊 Estimativa: ~{estimated_total} produtos em {pagination_analysis['total_pages']} páginas")
            else:
                analysis['estimated_total_products'] = len(product_elements)
                logger.info(f"📊 Categoria sem paginação: {len(product_elements)} produtos")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar categoria: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Fecha conexões"""
        super().close()
        if hasattr(self, 'pagination_handler'):
            self.pagination_handler.close() 
 
 
 
 