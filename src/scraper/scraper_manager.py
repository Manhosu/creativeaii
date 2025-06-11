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
from .availability_checker import AvailabilityChecker

class ScraperManager:
    """Gerenciador principal do módulo de scraping"""
    
    def __init__(self):
        """Inicializa o gerenciador de scraping"""
        self.scraper = CreativeScraper()
        self.extractor = ProductExtractor()
        self.url_manager = URLManager()
        self.availability_checker = AvailabilityChecker()
        
        logger.info("🚀 Scraper Manager inicializado com sucesso")
    
    def run_full_scraping(self, use_pagination: bool = True, discover_categories: bool = False, max_products_per_category: int = 0) -> Dict[str, Any]:
        """
        Executa scraping completo de todas as categorias configuradas
        
        Args:
            use_pagination: Se deve usar paginação automática
            discover_categories: Se deve descobrir categorias automaticamente antes do scraping
            
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
            # Atualizar URLs das configurações antes de começar
            logger.info("🔄 Atualizando URLs das configurações...")
            self.url_manager.refresh_category_urls()
            
            # Descobrir categorias automaticamente se solicitado
            if discover_categories:
                logger.info("🔍 Descobrindo categorias automaticamente...")
                discovery_result = self.url_manager.auto_discover_categories()
                if discovery_result['status'] == 'success':
                    self.url_manager.update_category_urls_from_discovery()
                    logger.info(f"✅ {discovery_result['total_discovered']} categorias descobertas e adicionadas")
                else:
                    logger.warning(f"⚠️ Erro na descoberta: {discovery_result.get('message', '')}")
            
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
                # Verificar timeout global (30 minutos máximo)
                elapsed_time = time.time() - start_time
                if elapsed_time > 1800:  # 30 minutos
                    logger.warning(f"⏰ TIMEOUT: Processo interrompido após {elapsed_time/60:.1f} minutos")
                    break
                
                try:
                    logger.info(f"🕷️ Processando categoria {i}/{len(category_urls)}: {url}")
                    
                    category_start = time.time()
                    
                    # Fazer scraping da categoria (com ou sem paginação)
                    if use_pagination:
                        raw_products = self.scraper.scrape_category_with_pagination(url)
                    else:
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
                    
                    # PROTEÇÃO CONTRA LOOP: Limite máximo absoluto de 300 produtos por categoria
                    if len(normalized_products) > 300:
                        logger.warning(f"⚠️ LIMITE MÁXIMO: Reduzindo de {len(normalized_products)} para 300 produtos (proteção contra loop)")
                        normalized_products = normalized_products[:300]
                    elif max_products_per_category > 0 and len(normalized_products) > max_products_per_category:
                        logger.info(f"⚡ LIMITANDO produtos de {len(normalized_products)} para {max_products_per_category} (modo teste)")
                        normalized_products = normalized_products[:max_products_per_category]
                    else:
                        logger.info(f"📦 Processando TODOS os {len(normalized_products)} produtos encontrados (busca completa)")
                    
                    # Verificar disponibilidade dos produtos
                    logger.info(f"🔍 Verificando disponibilidade de {len(normalized_products)} produtos")
                    available_products = self.availability_checker.check_products_batch(
                        normalized_products, 
                        delay=0.1,  # Reduzido de 0.5s para 0.1s
                        max_workers=15,  # Aumentado para 15 workers
                        use_parallel=True  # Forçar modo paralelo
                    )
                    
                    # Filtrar apenas produtos novos (agora já com verificação de disponibilidade)
                    new_products = self.url_manager.filter_new_products(available_products)
                    
                    # Marcar produtos como processados
                    if new_products:
                        self.url_manager.mark_products_as_processed(new_products)
                    
                    # Exportar produtos da categoria (apenas os disponíveis)
                    if available_products:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"logs/products_{url.split('/')[-1]}_{timestamp}.json"
                        self.extractor.export_to_json(available_products, filename)
                    
                    # Registrar estatísticas
                    category_time = time.time() - category_start
                    self.url_manager.record_scraping_stats(
                        url, len(available_products), len(new_products), 
                        category_time, "success"
                    )
                    
                    # Atualizar contadores
                    total_products_found += len(available_products)
                    total_new_products += len(new_products)
                    
                    processed_categories.append({
                        'url': url,
                        'total_products_found': len(normalized_products),
                        'available_products': len(available_products),
                        'new_products': len(new_products),
                        'execution_time': category_time,
                        'status': 'success'
                    })
                    
                    logger.info(f"✅ Categoria processada: {len(available_products)}/{len(normalized_products)} produtos disponíveis, {len(new_products)} novos")
                    
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
            self.availability_checker.close()
    
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
            
            # Sem limitação para categoria única - processar todos os produtos
            logger.info(f"📦 Processando TODOS os {len(normalized_products)} produtos da categoria")
            
            # Verificar disponibilidade dos produtos
            logger.info(f"🔍 Verificando disponibilidade de {len(normalized_products)} produtos")
            available_products = self.availability_checker.check_products_batch(
                normalized_products, 
                delay=0.1,  # Reduzido de 0.5s para 0.1s
                max_workers=15,  # Aumentado para 15 workers
                use_parallel=True  # Forçar modo paralelo
            )
            
            # Filtrar novos produtos (agora já com verificação de disponibilidade)
            new_products = self.url_manager.filter_new_products(available_products)
            
            # Marcar como processados
            if new_products:
                self.url_manager.mark_products_as_processed(new_products)
            
            # Exportar resultados (apenas produtos disponíveis)
            if available_products:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"logs/products_single_{timestamp}.json"
                exported_file = self.extractor.export_to_json(available_products, filename)
            else:
                exported_file = ""
            
            # Registrar estatísticas
            execution_time = time.time() - start_time
            self.url_manager.record_scraping_stats(
                url, len(available_products), len(new_products), 
                execution_time, "success"
            )
            
            report = {
                'status': 'success',
                'url': url,
                'total_products_found': len(normalized_products),
                'available_products': len(available_products),
                'new_products': len(new_products),
                'execution_time': execution_time,
                'exported_file': exported_file,
                'summary': self.extractor.generate_summary(available_products),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"✅ Categoria processada: {len(available_products)}/{len(normalized_products)} produtos disponíveis, {len(new_products)} novos")
            
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
            self.availability_checker.close()
    
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
 
 
 
 