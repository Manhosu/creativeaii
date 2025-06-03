"""
Scraper específico para Creative Cópias
Implementa métodos de extração para https://www.creativecopias.com.br
"""

from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import requests
import re
from loguru import logger
from .scraper_base import ScraperBase

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
        self.base_url = "https://www.creativecopias.com.br"
        
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
                '.products-grid .item',  # Magento products grid items
                '.category-products .item',  # Magento category products
                '.product-item',  # Padrão Magento 2
                '.item .product-name',  # Items com product name dentro
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
            'h3', 'h2', 'h4',
            '.product-name', '.nome-produto', '.title',
            '[data-name]', '.product-title',
            'a[title]'
        ]
        
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    text = found.get_text(strip=True)
                    if len(text) > 3:  # Nome válido deve ter mais de 3 caracteres
                        return text
                    
                # Tentar atributo title
                if hasattr(found, 'get') and found.get('title'):
                    return found.get('title').strip()
            except:
                continue
        
        # Última tentativa: pegar primeiro texto significativo
        text = element.get_text(strip=True)
        if text and len(text) > 3:
            # Pegar primeira linha que pareça um nome de produto
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and not line.startswith('R$'):
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
        """Extrai URL da imagem do produto"""
        try:
            img = element.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    # Se for URL relativa, adicionar domínio
                    if src.startswith('/'):
                        return self.base_url + src
                    elif src.startswith('http'):
                        return src
        except:
            pass
        
        return None
    
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
 
 
 
 