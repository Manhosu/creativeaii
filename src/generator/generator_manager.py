"""
Generator Manager
Orquestrador principal que coordena todo o processo de geração de conteúdo
"""

import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

try:
    from .content_generator import ContentGenerator
    from ..scraper.availability_checker import AvailabilityChecker
except ImportError:
    # Fallback para imports absolutos quando executado diretamente
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from generator.content_generator import ContentGenerator
    from scraper.availability_checker import AvailabilityChecker

class GeneratorManager:
    """Gerenciador principal do módulo de geração de conteúdo"""
    
    def __init__(self, openai_api_key: str = None):
        """Inicializa o gerenciador de geração"""
        # Obter configurações do ambiente
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
        max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
        
        self.content_generator = ContentGenerator(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.availability_checker = AvailabilityChecker()
        self.generated_articles = []
        self.stats = {
            'total_generated': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'skipped_unavailable': 0,
            'simulation_mode': self.content_generator.simulation_mode
        }
        
        logger.info("🎨 Generator Manager inicializado com sucesso")
    
    def generate_article_from_product(self, product: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Gera artigo completo a partir de dados de produto"""
        try:
            produto_nome = product.get('nome', 'Produto')
            logger.info(f"🎨 Iniciando geração para: {produto_nome}")
            
            # Verificar disponibilidade do produto antes de gerar (se não foi verificado recentemente)
            if not kwargs.get('skip_availability_check', False):
                logger.info(f"🔍 Verificando disponibilidade do produto: {produto_nome}")
                availability_result = self.availability_checker.check_product_availability(product)
                
                if not availability_result.get('disponivel', False):
                    motivo = availability_result.get('motivo', 'Motivo desconhecido')
                    logger.warning(f"⚠️ Produto indisponível, pulando geração: {produto_nome} - {motivo}")
                    self.stats['skipped_unavailable'] += 1
                    return {
                        'status': 'skipped',
                        'motivo': f'Produto indisponível: {motivo}',
                        'produto': produto_nome,
                        'verificacao_disponibilidade': availability_result,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    logger.info(f"✅ Produto disponível, prosseguindo com geração: {produto_nome}")
                    # Adicionar info de verificação ao produto
                    product['verificacao_disponibilidade'] = availability_result
            
            start_time = time.time()
            # Remover skip_availability_check dos kwargs antes de passar para generate_article
            generator_kwargs = {k: v for k, v in kwargs.items() if k != 'skip_availability_check'}
            article = self.content_generator.generate_article(product, **generator_kwargs)
            
            if article:
                generation_time = time.time() - start_time
                article['generation_time'] = generation_time
                self.stats['successful_generations'] += 1
                self.generated_articles.append(article)
                logger.info(f"✅ Artigo gerado em {generation_time:.1f}s")
            else:
                self.stats['failed_generations'] += 1
                logger.error("❌ Falha na geração do artigo")
            
            self.stats['total_generated'] += 1
            return article
            
        except Exception as e:
            logger.error(f"❌ Erro na geração: {e}")
            self.stats['failed_generations'] += 1
            return {}
    
    def test_generation(self) -> Dict[str, Any]:
        """Testa geração com produto fictício"""
        mock_product = {
            'id': 'test_001',
            'nome': 'Impressora HP LaserJet Pro M404n',
            'marca': 'HP',
            'preco': {'texto': 'R$ 899,99'},
            'categoria_url': 'https://www.creativecopias.com.br/impressoras',
            'url': 'https://www.creativecopias.com.br/impressora-hp-laserjet-pro-m404n',
            'disponivel': True,
            'especificacoes': {
                'velocidade': '38 ppm',
                'conectividade': 'USB, Ethernet',
                'resolucao': '1200 x 1200 dpi'
            },
            'categoria': 'Impressoras Laser',
            'tipo': 'impressora'
        }
        
        # Forçar skip da verificação de disponibilidade para teste
        return self.generate_article_from_product(mock_product, skip_availability_check=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerador incluindo dados do banco"""
        try:
            # Tentar obter dados do sistema review
            review_stats = None
            try:
                from src.review.review_manager import ReviewManager
                review_manager = ReviewManager()
                review_data = review_manager.get_statistics()
                review_stats = review_data if review_data else None
            except Exception as e:
                logger.warning(f"Não foi possível obter dados do review: {e}")
            
            # Calcular estatísticas reais
            total_articles_db = review_stats.get('total_artigos', 0) if review_stats else 0
            approved_articles = review_stats.get('aprovados', 0) if review_stats else 0
            pending_articles = review_stats.get('pendentes', 0) if review_stats else 0
            rejected_articles = review_stats.get('rejeitados', 0) if review_stats else 0
            
            # Calcular taxa de sucesso (artigos aprovados/total)
            success_rate = round(((approved_articles + pending_articles) / total_articles_db * 100), 1) if total_articles_db > 0 else 100
            
            # Calcular palavras médias (estimativa baseada em artigos típicos)
            average_words = 850 if total_articles_db > 0 else 0
            
            # Stats atualizados
            updated_stats = {
                'total_generated': total_articles_db,
                'successful_generations': approved_articles + pending_articles,  # Gerados com sucesso
                'failed_generations': rejected_articles,
                'skipped_unavailable': self.stats['skipped_unavailable'],
                'simulation_mode': self.content_generator.simulation_mode,
                'success_rate': success_rate,
                'average_words': average_words
            }
            
            return {
                'manager_stats': updated_stats,
                'total_articles_in_memory': len(self.generated_articles),
                'total_articles_database': total_articles_db,
                'articles_breakdown': {
                    'approved': approved_articles,
                    'pending': pending_articles, 
                    'rejected': rejected_articles
                },
                'status': 'ready',
                'simulation_mode': self.content_generator.simulation_mode,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            # Fallback para stats básicos
            return {
                'manager_stats': self.stats,
                'total_articles_in_memory': len(self.generated_articles),
                'status': 'ready',
                'simulation_mode': self.content_generator.simulation_mode,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def close(self):
        """Fecha recursos do gerador"""
        try:
            self.availability_checker.close()
            logger.debug("🔒 Generator Manager recursos fechados")
        except:
            pass