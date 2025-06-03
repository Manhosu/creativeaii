"""
Classe Base para Scraping
Define interface abstrata para scrapers específicos
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import time
import random
from loguru import logger
import hashlib

class ScraperBase(ABC):
    """Classe abstrata base para todos os scrapers"""
    
    def __init__(self, delay_range: tuple = (1, 3), timeout: int = 30):
        """
        Inicializa o scraper base
        
        Args:
            delay_range: Tupla com min e max delay entre requests
            timeout: Timeout para requests em segundos
        """
        self.delay_range = delay_range
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configurar logger específico para scraper
        logger.add(
            "logs/scraper.log",
            rotation="1 week",
            retention="30 days",
            level="INFO",
            format="{time} | {level} | {message}"
        )
    
    def _apply_delay(self):
        """Aplica delay aleatório entre requests"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _generate_product_id(self, product_data: Dict[str, Any]) -> str:
        """
        Gera ID único para produto baseado nos dados
        
        Args:
            product_data: Dados do produto
            
        Returns:
            ID único do produto
        """
        # Combina nome + URL + código para gerar hash único
        id_string = f"{product_data.get('nome', '')}{product_data.get('url', '')}{product_data.get('codigo', '')}"
        return hashlib.md5(id_string.encode()).hexdigest()
    
    @abstractmethod
    def load_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Carrega página e retorna objeto BeautifulSoup
        
        Args:
            url: URL para carregar
            
        Returns:
            BeautifulSoup object ou None se erro
        """
        pass
    
    @abstractmethod
    def parse_product_list(self, html: BeautifulSoup) -> List[Any]:
        """
        Extrai lista de elementos de produtos da página
        
        Args:
            html: Objeto BeautifulSoup da página
            
        Returns:
            Lista de elementos de produtos
        """
        pass
    
    @abstractmethod
    def extract_product_data(self, product_element: Any) -> Dict[str, Any]:
        """
        Extrai dados de um elemento de produto específico
        
        Args:
            product_element: Elemento HTML do produto
            
        Returns:
            Dicionário com dados do produto
        """
        pass
    
    def scrape_category(self, url: str) -> List[Dict[str, Any]]:
        """
        Scraping completo de uma categoria
        
        Args:
            url: URL da categoria
            
        Returns:
            Lista de produtos extraídos
        """
        logger.info(f"🕷️ Iniciando scraping da categoria: {url}")
        
        try:
            # Carregar página
            html = self.load_page(url)
            if not html:
                logger.error(f"❌ Falha ao carregar página: {url}")
                return []
            
            # Extrair lista de produtos
            product_elements = self.parse_product_list(html)
            logger.info(f"📦 Encontrados {len(product_elements)} produtos na página")
            
            # Extrair dados de cada produto
            products = []
            for i, element in enumerate(product_elements, 1):
                try:
                    product_data = self.extract_product_data(element)
                    
                    if product_data:
                        # Adicionar ID único
                        product_data['id'] = self._generate_product_id(product_data)
                        product_data['categoria_url'] = url
                        product_data['data_scraped'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        products.append(product_data)
                        logger.debug(f"✅ Produto {i} extraído: {product_data.get('nome', 'N/A')}")
                    
                    # Delay entre produtos
                    if i < len(product_elements):
                        self._apply_delay()
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao extrair produto {i}: {e}")
                    continue
            
            logger.info(f"✅ Scraping concluído: {len(products)} produtos extraídos de {url}")
            return products
            
        except Exception as e:
            logger.error(f"❌ Erro no scraping da categoria {url}: {e}")
            return []
    
    def validate_product_data(self, product: Dict[str, Any]) -> bool:
        """
        Valida se os dados do produto são válidos
        
        Args:
            product: Dados do produto
            
        Returns:
            True se válido, False caso contrário
        """
        required_fields = ['nome', 'url']
        return all(product.get(field) for field in required_fields)
    
    def close(self):
        """Fecha sessão e limpa recursos"""
        if hasattr(self, 'session'):
            self.session.close()
        logger.info("🔒 Sessão de scraping fechada") 
 
 
 
 