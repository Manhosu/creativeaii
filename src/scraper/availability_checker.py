"""
Availability Checker
Módulo para verificação robusta de disponibilidade de produtos
"""

import requests
import time
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from loguru import logger
import re
from urllib.parse import urlparse
import concurrent.futures
import threading

class AvailabilityChecker:
    """Verificador de disponibilidade de produtos"""
    
    def __init__(self, timeout: int = 8, max_retries: int = 1):
        """
        Inicializa o verificador de disponibilidade
        
        Args:
            timeout: Timeout para requests em segundos (reduzido para 8s)
            max_retries: Número máximo de tentativas (reduzido para 1)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.cache = {}  # Cache simples para URLs já verificadas
        
        # Headers simples (como no teste que funcionou)
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info("🔍 Availability Checker inicializado")
    
    def check_product_availability(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica disponibilidade detalhada de um produto
        
        Args:
            product: Dados do produto (deve conter 'url')
            
        Returns:
            Resultado da verificação com detalhes
        """
        url = product.get('url')
        nome = product.get('nome', 'Produto sem nome')
        
        if not url:
            return {
                'disponivel': False,
                'motivo': 'URL não fornecida',
                'status_code': None,
                'detalhes': 'Produto sem URL para verificação'
            }
        
        # Verificar cache primeiro
        if url in self.cache:
            logger.debug(f"💾 Cache hit para: {nome}")
            return self.cache[url]
        
        logger.debug(f"🔍 Verificando disponibilidade: {nome}")
        
        try:
            # Verificar se URL é acessível
            response = self._make_request(url)
            
            if response is None:
                return {
                    'disponivel': False,
                    'motivo': 'Erro de conexão',
                    'status_code': None,
                    'detalhes': 'Não foi possível acessar a página do produto'
                }
            
            if response.status_code == 404:
                return {
                    'disponivel': False,
                    'motivo': 'Produto não encontrado (404)',
                    'status_code': 404,
                    'detalhes': 'A página do produto não existe mais'
                }
            
            if response.status_code >= 400:
                return {
                    'disponivel': False,
                    'motivo': f'Erro HTTP {response.status_code}',
                    'status_code': response.status_code,
                    'detalhes': 'Erro ao acessar página do produto'
                }
            
            # Analisar conteúdo da página
            soup = BeautifulSoup(response.content, 'html.parser')
            availability_result = self._analyze_page_content(soup, url)
            availability_result['status_code'] = response.status_code
            
            # Adicionar ao cache
            self.cache[url] = availability_result
            
            return availability_result
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar produto {nome}: {e}")
            return {
                'disponivel': False,
                'motivo': 'Erro de processamento',
                'status_code': None,
                'detalhes': str(e)
            }
    
    def check_products_batch(self, products: List[Dict[str, Any]], delay: float = 0.1, max_workers: int = 10, use_parallel: bool = True) -> List[Dict[str, Any]]:
        """
        Verifica disponibilidade de lista de produtos (com opção de paralelismo)
        
        Args:
            products: Lista de produtos para verificar
            delay: Delay entre verificações em segundos (apenas para modo sequencial)
            max_workers: Número máximo de threads para processamento paralelo
            use_parallel: Se True, usa processamento paralelo
            
        Returns:
            Lista de produtos com status de disponibilidade atualizado
        """
        logger.info(f"🔍 Verificando disponibilidade de {len(products)} produtos {'(PARALELO)' if use_parallel else '(SEQUENCIAL)'}")
        
        if use_parallel and len(products) > 5:
            return self._check_products_parallel(products, max_workers)
        else:
            return self._check_products_sequential(products, delay)
    
    def _check_products_parallel(self, products: List[Dict[str, Any]], max_workers: int = 10) -> List[Dict[str, Any]]:
        """
        Verifica produtos em paralelo usando ThreadPoolExecutor
        """
        verified_products = []
        available_count = 0
        completed_count = 0
        lock = threading.Lock()
        
        def verify_single_product(product_with_index):
            nonlocal available_count, completed_count
            i, product = product_with_index
            
            try:
                # Verificar disponibilidade
                availability = self.check_product_availability(product)
                
                # Atualizar produto com resultado
                updated_product = product.copy()
                updated_product['disponivel'] = availability['disponivel']
                updated_product['verificacao_disponibilidade'] = availability
                
                with lock:
                    completed_count += 1
                    if availability['disponivel']:
                        available_count += 1
                        verified_products.append(updated_product)
                        logger.debug(f"✅ [{completed_count}/{len(products)}] {product.get('nome', 'N/A')} - DISPONÍVEL")
                    else:
                        logger.info(f"❌ [{completed_count}/{len(products)}] {product.get('nome', 'N/A')} - INDISPONÍVEL: {availability['motivo']}")
                
                return updated_product if availability['disponivel'] else None
                
            except Exception as e:
                with lock:
                    completed_count += 1
                logger.error(f"❌ Erro ao verificar produto {i}: {e}")
                return None
        
        # Executar em paralelo
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            futures = {executor.submit(verify_single_product, (i, product)): product 
                      for i, product in enumerate(products, 1)}
            
            # Aguardar conclusão
            concurrent.futures.as_completed(futures)
        
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (available_count / len(products) * 100) if products else 0
        
        logger.info(f"✅ Verificação PARALELA concluída em {duration:.1f}s: {available_count}/{len(products)} produtos disponíveis ({success_rate:.1f}%)")
        
        return verified_products
    
    def _check_products_sequential(self, products: List[Dict[str, Any]], delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Verifica produtos sequencialmente (método original)
        """
        verified_products = []
        available_count = 0
        
        for i, product in enumerate(products, 1):
            try:
                # Verificar disponibilidade
                availability = self.check_product_availability(product)
                
                # Atualizar produto com resultado
                updated_product = product.copy()
                updated_product['disponivel'] = availability['disponivel']
                updated_product['verificacao_disponibilidade'] = availability
                
                if availability['disponivel']:
                    available_count += 1
                    verified_products.append(updated_product)
                    logger.debug(f"✅ [{i}/{len(products)}] {product.get('nome', 'N/A')} - DISPONÍVEL")
                else:
                    logger.info(f"❌ [{i}/{len(products)}] {product.get('nome', 'N/A')} - INDISPONÍVEL: {availability['motivo']}")
                
                # Delay entre verificações
                if i < len(products):
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"❌ Erro ao verificar produto {i}: {e}")
                continue
        
        success_rate = (available_count / len(products) * 100) if products else 0
        logger.info(f"✅ Verificação SEQUENCIAL concluída: {available_count}/{len(products)} produtos disponíveis ({success_rate:.1f}%)")
        
        return verified_products
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Faz request com retry automático
        
        Args:
            url: URL para acessar
            
        Returns:
            Response object ou None se falhar
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Usar requests simples como no teste que funcionou
                response = requests.get(url, timeout=self.timeout)
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout na tentativa {attempt}/{self.max_retries} para {url}")
                if attempt < self.max_retries:
                    time.sleep(2 * attempt)  # Backoff exponencial
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Erro de conexão na tentativa {attempt}/{self.max_retries} para {url}")
                if attempt < self.max_retries:
                    time.sleep(2 * attempt)
                    
            except Exception as e:
                logger.error(f"❌ Erro inesperado na tentativa {attempt}/{self.max_retries}: {e}")
                break
        
        return None
    
    def _analyze_page_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Analisa conteúdo da página para determinar disponibilidade
        
        Args:
            soup: BeautifulSoup da página
            url: URL da página
            
        Returns:
            Resultado da análise
        """
        try:
            page_text = soup.get_text().lower()
            
            # Verificar indicadores de indisponibilidade
            unavailable_indicators = [
                'produto indisponível',
                'fora de estoque',
                'esgotado',
                'sem estoque',
                'produto esgotado',
                'temporariamente indisponível',
                'produto não disponível',
                'out of stock',
                'not available',
                'unavailable'
            ]
            
            for indicator in unavailable_indicators:
                if indicator in page_text:
                    return {
                        'disponivel': False,
                        'motivo': f'Indicador encontrado: "{indicator}"',
                        'detalhes': 'Página indica que produto está indisponível'
                    }
            
            # Verificar se a página é do Creative Cópias
            if 'creativecopias' not in page_text and 'creative' not in page_text:
                return {
                    'disponivel': False,
                    'motivo': 'Página não pertence ao site Creative Cópias',
                    'detalhes': 'URL pode ter sido redirecionada ou alterada'
                }
            
            # Verificar presença de elementos que indicam produto ativo
            positive_indicators = [
                # Botões de compra
                soup.find(['button', 'a'], text=re.compile(r'comprar|adicionar.*carrinho|buy now', re.I)),
                # Preços
                soup.find(['span', 'div'], class_=re.compile(r'price|preco|valor', re.I)),
                # Campos de quantidade
                soup.find('input', {'type': 'number', 'name': re.compile(r'qty|quantity|quantidade', re.I)}),
                # Formulários de compra
                soup.find('form', action=re.compile(r'cart|carrinho|checkout', re.I))
            ]
            
            active_indicators = sum(1 for indicator in positive_indicators if indicator)
            
            if active_indicators >= 2:
                return {
                    'disponivel': True,
                    'motivo': f'{active_indicators} indicadores positivos encontrados',
                    'detalhes': 'Página contém elementos que indicam produto ativo'
                }
            elif active_indicators == 1:
                return {
                    'disponivel': True,
                    'motivo': 'Indicador positivo encontrado',
                    'detalhes': 'Produto parece estar disponível mas verificação limitada'
                }
            else:
                # Verificar se pelo menos tem estrutura básica de produto
                has_product_structure = any([
                    soup.find(['h1', 'h2', 'h3'], text=re.compile(r'.{10,}', re.I)),  # Título do produto
                    soup.find('img', src=re.compile(r'product|produto', re.I)),  # Imagem do produto
                    'código' in page_text or 'sku' in page_text  # Código do produto
                ])
                
                if has_product_structure:
                    return {
                        'disponivel': True,
                        'motivo': 'Estrutura de produto detectada',
                        'detalhes': 'Não há indicadores claros de indisponibilidade'
                    }
                else:
                    return {
                        'disponivel': False,
                        'motivo': 'Página não parece ser de produto',
                        'detalhes': 'Não foram encontrados elementos típicos de página de produto'
                    }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar conteúdo da página: {e}")
            return {
                'disponivel': False,
                'motivo': 'Erro na análise da página',
                'detalhes': str(e)
            }
    
    def get_statistics(self, verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera estatísticas das verificações realizadas
        
        Args:
            verification_results: Lista de resultados de verificação
            
        Returns:
            Estatísticas detalhadas
        """
        if not verification_results:
            return {'total': 0}
        
        total = len(verification_results)
        available = sum(1 for r in verification_results if r.get('verificacao_disponibilidade', {}).get('disponivel', False))
        
        # Contar motivos de indisponibilidade
        motivos = {}
        for result in verification_results:
            verif = result.get('verificacao_disponibilidade', {})
            if not verif.get('disponivel', True):
                motivo = verif.get('motivo', 'Motivo não especificado')
                motivos[motivo] = motivos.get(motivo, 0) + 1
        
        return {
            'total_verificados': total,
            'disponiveis': available,
            'indisponiveis': total - available,
            'taxa_disponibilidade': (available / total * 100) if total > 0 else 0,
            'motivos_indisponibilidade': motivos
        }
    
    def close(self):
        """Fecha sessão HTTP"""
        try:
            self.session.close()
            logger.debug("🔒 Sessão HTTP fechada")
        except:
            pass