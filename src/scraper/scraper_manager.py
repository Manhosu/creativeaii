"""
Scraper Manager
Orquestrador principal que coordena todo o processo de scraping
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from .creative_scraper import CreativeScraper
from .product_extractor import ProductExtractor  
from .url_manager import URLManager

class ScraperManager:
    """Gerenciador principal do módulo de scraping"""
    
    def __init__(self):
        """Inicializa o gerenciador de scraping"""
        self.scraper = CreativeScraper()
        self.extractor = ProductExtractor()
        self.url_manager = URLManager()
        
        logger.info("🚀 Scraper Manager inicializado com sucesso")
    
    def run_full_scraping(self) -> Dict[str, Any]:
        """
        Executa scraping completo de todas as categorias configuradas
        
        Returns:
            Relatório completo do processo
        """
        logger.info("🔄 Iniciando scraping completo...")
        
        start_time = time.time()
        total_products_found = 0
        total_new_products = 0
        processed_categories = []
        errors = []
        
        try:
            # Obter URLs de categorias
            category_urls = self.url_manager.get_category_urls()
            
            if not category_urls:
                logger.warning("⚠️ Nenhuma URL de categoria configurada")
                return {
                    'status': 'warning',
                    'message': 'Nenhuma URL configurada',
                    'total_categories': 0,
                    'total_products': 0,
                    'new_products': 0
                }
            
            logger.info(f"📋 Processando {len(category_urls)} categorias")
            
            # Processar cada categoria
            for i, url in enumerate(category_urls, 1):
                try:
                    logger.info(f"🕷️ Processando categoria {i}/{len(category_urls)}: {url}")
                    
                    category_start = time.time()
                    
                    # Fazer scraping da categoria
                    raw_products = self.scraper.scrape_category(url)
                    
                    if not raw_products:
                        logger.warning(f"⚠️ Nenhum produto encontrado em: {url}")
                        processed_categories.append({
                            'url': url,
                            'total_products': 0,
                            'new_products': 0,
                            'status': 'empty'
                        })
                        continue
                    
                    # Normalizar produtos
                    normalized_products = self.extractor.normalize_products_batch(raw_products)
                    
                    # Filtrar apenas produtos novos
                    new_products = self.url_manager.filter_new_products(normalized_products)
                    
                    # Marcar produtos como processados
                    if new_products:
                        self.url_manager.mark_products_as_processed(new_products)
                    
                    # Exportar produtos da categoria
                    if normalized_products:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"logs/products_{url.split('/')[-1]}_{timestamp}.json"
                        self.extractor.export_to_json(normalized_products, filename)
                    
                    # Registrar estatísticas
                    category_time = time.time() - category_start
                    self.url_manager.record_scraping_stats(
                        url, len(normalized_products), len(new_products), 
                        category_time, "success"
                    )
                    
                    # Atualizar contadores
                    total_products_found += len(normalized_products)
                    total_new_products += len(new_products)
                    
                    processed_categories.append({
                        'url': url,
                        'total_products': len(normalized_products),
                        'new_products': len(new_products),
                        'execution_time': category_time,
                        'status': 'success'
                    })
                    
                    logger.info(f"✅ Categoria processada: {len(new_products)}/{len(normalized_products)} produtos novos")
                    
                    # Delay entre categorias para não sobrecarregar o servidor
                    if i < len(category_urls):
                        time.sleep(2)
                    
                except Exception as e:
                    error_msg = f"Erro ao processar categoria {url}: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                    
                    # Registrar erro nas estatísticas
                    self.url_manager.record_scraping_stats(
                        url, 0, 0, 0, "error"
                    )
                    
                    processed_categories.append({
                        'url': url,
                        'total_products': 0,
                        'new_products': 0,
                        'status': 'error',
                        'error': str(e)
                    })
                    continue
            
            # Calcular tempo total
            total_time = time.time() - start_time
            
            # Gerar relatório final
            report = {
                'status': 'success' if not errors else 'partial_success',
                'total_categories': len(category_urls),
                'processed_categories': len(processed_categories),
                'total_products_found': total_products_found,
                'total_new_products': total_new_products,
                'execution_time': total_time,
                'categories_detail': processed_categories,
                'errors': errors,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Log do resultado final
            success_rate = (len([c for c in processed_categories if c['status'] == 'success']) / 
                          len(category_urls) * 100) if category_urls else 0
            
            logger.info(f"🎯 Scraping concluído: {total_new_products} produtos novos "
                       f"de {total_products_found} encontrados em {total_time:.1f}s "
                       f"({success_rate:.1f}% sucesso)")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro fatal no scraping: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        finally:
            # Fechar conexões
            self.scraper.close()
    
    def run_single_category_scraping(self, url: str) -> Dict[str, Any]:
        """
        Executa scraping de uma categoria específica
        
        Args:
            url: URL da categoria para processar
            
        Returns:
            Relatório do processamento
        """
        logger.info(f"🕷️ Iniciando scraping da categoria: {url}")
        
        start_time = time.time()
        
        try:
            # Fazer scraping
            raw_products = self.scraper.scrape_category(url)
            
            if not raw_products:
                return {
                    'status': 'empty',
                    'message': 'Nenhum produto encontrado',
                    'url': url,
                    'total_products': 0,
                    'new_products': 0
                }
            
            # Normalizar produtos
            normalized_products = self.extractor.normalize_products_batch(raw_products)
            
            # Filtrar novos produtos
            new_products = self.url_manager.filter_new_products(normalized_products)
            
            # Marcar como processados
            if new_products:
                self.url_manager.mark_products_as_processed(new_products)
            
            # Exportar resultados
            if normalized_products:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"logs/products_single_{timestamp}.json"
                exported_file = self.extractor.export_to_json(normalized_products, filename)
            else:
                exported_file = ""
            
            # Registrar estatísticas
            execution_time = time.time() - start_time
            self.url_manager.record_scraping_stats(
                url, len(normalized_products), len(new_products), 
                execution_time, "success"
            )
            
            report = {
                'status': 'success',
                'url': url,
                'total_products': len(normalized_products),
                'new_products': len(new_products),
                'execution_time': execution_time,
                'exported_file': exported_file,
                'summary': self.extractor.generate_summary(normalized_products),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"✅ Categoria processada: {len(new_products)}/{len(normalized_products)} produtos novos")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro no scraping da categoria: {e}")
            
            # Registrar erro
            self.url_manager.record_scraping_stats(url, 0, 0, 0, "error")
            
            return {
                'status': 'error',
                'url': url,
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        finally:
            self.scraper.close()
    
    def get_scraping_status(self) -> Dict[str, Any]:
        """
        Retorna status atual do sistema de scraping
        
        Returns:
            Status e estatísticas do sistema
        """
        try:
            # Estatísticas do URL Manager
            url_summary = self.url_manager.get_summary()
            
            # Estatísticas recentes
            recent_stats = self.url_manager.get_scraping_stats(days=7)
            
            # Status geral
            status = {
                'scraper_status': 'ready',
                'urls_configuradas': url_summary.get('total_urls_configuradas', 0),
                'produtos_processados': url_summary.get('total_produtos_processados', 0),
                'ultima_execucao': recent_stats[0] if recent_stats else None,
                'estatisticas_7_dias': {
                    'total_execucoes': len(recent_stats),
                    'produtos_encontrados': sum(s.get('total_produtos', 0) for s in recent_stats),
                    'produtos_novos': sum(s.get('novos_produtos', 0) for s in recent_stats),
                    'tempo_medio': (sum(s.get('tempo_execucao', 0) for s in recent_stats) / 
                                  len(recent_stats)) if recent_stats else 0
                },
                'urls_categorias': url_summary.get('urls_categorias', []),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {
                'scraper_status': 'error',
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Limpa dados antigos do sistema
        
        Args:
            days: Dias para manter os dados
            
        Returns:
            Relatório da limpeza
        """
        try:
            logger.info(f"🧹 Iniciando limpeza de dados com mais de {days} dias")
            
            removed_count = self.url_manager.cleanup_old_records(days)
            
            return {
                'status': 'success',
                'records_removed': removed_count,
                'days_kept': days,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def test_connection(self, url: str = None) -> Dict[str, Any]:
        """
        Testa conexão com o site
        
        Args:
            url: URL específica para testar (opcional)
            
        Returns:
            Resultado do teste
        """
        test_url = url or "https://www.creativecopias.com.br/impressoras"
        
        try:
            logger.info(f"🔍 Testando conexão com: {test_url}")
            
            start_time = time.time()
            html = self.scraper.load_page(test_url)
            load_time = time.time() - start_time
            
            if html:
                page_size = len(str(html))
                has_products = len(self.scraper.parse_product_list(html)) > 0
                
                return {
                    'status': 'success',
                    'url': test_url,
                    'load_time': load_time,
                    'page_size': page_size,
                    'has_products': has_products,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'status': 'failed',
                    'url': test_url,
                    'message': 'Falha ao carregar página',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de conexão: {e}")
            return {
                'status': 'error',
                'url': test_url,
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        finally:
            self.scraper.close() 
 
 
 
 