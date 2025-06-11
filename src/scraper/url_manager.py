"""
URL Manager
Gerencia URLs de categorias e controle de produtos processados
"""

import os
import json
import sqlite3
from typing import List, Dict, Set, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import hashlib
from .category_discovery import CategoryDiscovery
from ..config.active_categories_manager import ActiveCategoriesManager

class URLManager:
    """Gerenciador de URLs e cache de produtos processados"""
    
    def __init__(self, db_path: str = "logs/products_cache.db"):
        """
        Inicializa o gerenciador de URLs
        
        Args:
            db_path: Caminho para banco de dados SQLite
        """
        self.db_path = db_path
        self.category_urls = []
        self.processed_products = set()
        self.discovered_categories = []  # Cache de categorias descobertas
        
        # Inicializar gerenciador de categorias ativas
        self.active_categories_manager = ActiveCategoriesManager()
        
        # Inicializar banco de dados
        self._init_database()
        
        # Carregar URLs das configurias ativas apenas
        self._load_category_urls()
        
        # Carregar produtos já processados
        self._load_processed_products()
        
        # Inicializar descobridor de categorias
        self.category_discovery = CategoryDiscovery()
        
        logger.info(f"🔗 URL Manager inicializado com {len(self.category_urls)} URLs")
    
    def _init_database(self):
        """Inicializa banco de dados SQLite"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de produtos processados
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processed_products (
                        id TEXT PRIMARY KEY,
                        nome TEXT NOT NULL,
                        url TEXT,
                        categoria_url TEXT,
                        data_processed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        hash_content TEXT,
                        status TEXT DEFAULT 'processed'
                    )
                ''')
                
                # Tabela de estatísticas de scraping
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scraping_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        categoria_url TEXT NOT NULL,
                        total_produtos INTEGER,
                        novos_produtos INTEGER,
                        data_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tempo_execucao REAL,
                        status TEXT
                    )
                ''')
                
                # Índices para performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_id ON processed_products(id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_categoria_url ON processed_products(categoria_url)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_processed ON processed_products(data_processed)')
                
                conn.commit()
                
            logger.info("✅ Banco de dados inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
    
    def _load_category_urls(self):
        """Carrega URLs apenas das categorias ativas"""
        try:
            # Carregar URLs das categorias ativas
            active_urls = self.active_categories_manager.get_active_urls()
            
            if active_urls:
                self.category_urls = active_urls
                active_categories = self.active_categories_manager.get_active_categories()
                logger.info(f"📋 {len(self.category_urls)} URLs carregadas das categorias ativas:")
                for category in active_categories:
                    logger.info(f"  ✅ {category['category_name']}: {category['category_url']}")
                return
            else:
                logger.warning("⚠️ Nenhuma categoria ativa encontrada!")
                    
                # Fallback: carregar URLs do ConfigManager (compatibilidade)
                try:
                    from ..config.config_manager import ConfigManager
                    config_manager = ConfigManager()
                    monitored_urls = config_manager.get_monitored_urls(active_only=True)
                    
                    if monitored_urls:
                        self.category_urls = [url['url'] for url in monitored_urls]
                        logger.info(f"🔧 Fallback: {len(self.category_urls)} URLs do ConfigManager")
                        
                except Exception as config_error:
                    logger.warning(f"⚠️ Erro no fallback ConfigManager: {config_error}")
            
                # URLs padrão se nada funcionar
            self.category_urls = [
                "https://www.creativecopias.com.br/impressoras",
                "https://www.creativecopias.com.br/cartuchos-de-toner"
            ]
            
            logger.info(f"🔧 Usando URLs padrão: {len(self.category_urls)} URLs")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar URLs das categorias ativas: {e}")
            self.category_urls = []
    
    def _load_processed_products(self):
        """Carrega lista de produtos já processados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM processed_products')
                results = cursor.fetchall()
                
                self.processed_products = set(row[0] for row in results)
                
            logger.info(f"📦 {len(self.processed_products)} produtos já processados carregados")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar produtos processados: {e}")
            self.processed_products = set()
    
    def get_category_urls(self) -> List[str]:
        """
        Retorna lista de URLs de categorias
        
        Returns:
            Lista de URLs
        """
        return self.category_urls.copy()
    
    def refresh_category_urls(self):
        """Recarrega URLs das configurações"""
        logger.info("🔄 Recarregando URLs das configurações...")
        old_count = len(self.category_urls)
        self._load_category_urls()
        new_count = len(self.category_urls)
        logger.info(f"📊 URLs atualizadas: {old_count} → {new_count}")
    
    def add_category_url(self, url: str) -> bool:
        """
        Adiciona nova URL de categoria
        
        Args:
            url: URL para adicionar
            
        Returns:
            True se adicionada com sucesso
        """
        try:
            if url not in self.category_urls:
                self.category_urls.append(url)
                logger.info(f"➕ URL adicionada: {url}")
                return True
            else:
                logger.warning(f"⚠️ URL já existe: {url}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar URL: {e}")
            return False
    
    def remove_category_url(self, url: str) -> bool:
        """
        Remove URL de categoria
        
        Args:
            url: URL para remover
            
        Returns:
            True se removida com sucesso
        """
        try:
            if url in self.category_urls:
                self.category_urls.remove(url)
                logger.info(f"➖ URL removida: {url}")
                return True
            else:
                logger.warning(f"⚠️ URL não encontrada: {url}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao remover URL: {e}")
            return False
    
    def is_product_processed(self, product_id: str) -> bool:
        """
        Verifica se produto já foi processado
        
        Args:
            product_id: ID do produto
            
        Returns:
            True se já foi processado
        """
        return product_id in self.processed_products
    
    def mark_product_as_processed(self, product: Dict[str, Any]) -> bool:
        """
        Marca produto como processado
        
        Args:
            product: Dados do produto
            
        Returns:
            True se marcado com sucesso
        """
        try:
            product_id = product.get('id')
            if not product_id:
                logger.error("❌ Produto sem ID não pode ser marcado como processado")
                return False
            
            # Gerar hash do conteúdo para detectar mudanças
            content_hash = self._generate_content_hash(product)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO processed_products 
                    (id, nome, url, categoria_url, hash_content, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    product_id,
                    product.get('nome', ''),
                    product.get('url', ''),
                    product.get('categoria_url', ''),
                    content_hash,
                    'processed'
                ))
                
                conn.commit()
            
            # Adicionar ao cache em memória
            self.processed_products.add(product_id)
            
            logger.debug(f"✅ Produto marcado como processado: {product.get('nome', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao marcar produto como processado: {e}")
            return False
    
    def mark_products_as_processed(self, products: List[Dict[str, Any]]) -> int:
        """
        Marca múltiplos produtos como processados
        
        Args:
            products: Lista de produtos
            
        Returns:
            Número de produtos marcados com sucesso
        """
        success_count = 0
        
        for product in products:
            if self.mark_product_as_processed(product):
                success_count += 1
        
        logger.info(f"✅ {success_count}/{len(products)} produtos marcados como processados")
        return success_count
    
    def filter_new_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra apenas produtos novos (não processados)
        
        Args:
            products: Lista de produtos
            
        Returns:
            Lista de produtos novos
        """
        new_products = []
        
        for product in products:
            product_id = product.get('id')
            if product_id and not self.is_product_processed(product_id):
                new_products.append(product)
            elif product_id:
                # Verificar se o conteúdo mudou
                if self._has_product_changed(product):
                    new_products.append(product)
                    logger.debug(f"🔄 Produto atualizado detectado: {product.get('nome', 'N/A')}")
        
        logger.info(f"🆕 {len(new_products)}/{len(products)} produtos novos encontrados")
        return new_products
    
    def _has_product_changed(self, product: Dict[str, Any]) -> bool:
        """
        Verifica se produto foi alterado desde último processamento
        
        Args:
            product: Dados do produto
            
        Returns:
            True se foi alterado
        """
        try:
            product_id = product.get('id')
            if not product_id:
                return True
            
            # Buscar hash anterior
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT hash_content FROM processed_products WHERE id = ?', (product_id,))
                result = cursor.fetchone()
                
                if not result:
                    return True  # Produto novo
                
                old_hash = result[0]
                new_hash = self._generate_content_hash(product)
                
                return old_hash != new_hash
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar mudanças no produto: {e}")
            return True  # Em caso de erro, considerar como alterado
    
    def _generate_content_hash(self, product: Dict[str, Any]) -> str:
        """
        Gera hash do conteúdo do produto para detectar mudanças
        
        Args:
            product: Dados do produto
            
        Returns:
            Hash MD5 do conteúdo
        """
        # Campos relevantes para detectar mudanças
        relevant_fields = ['nome', 'preco', 'descricao', 'disponivel']
        content_string = ""
        
        for field in relevant_fields:
            value = product.get(field, '')
            if value:
                content_string += str(value)
        
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def record_scraping_stats(self, categoria_url: str, total_produtos: int, 
                            novos_produtos: int, tempo_execucao: float, 
                            status: str = "success") -> bool:
        """
        Registra estatísticas do scraping
        
        Args:
            categoria_url: URL da categoria processada
            total_produtos: Total de produtos encontrados
            novos_produtos: Produtos novos processados
            tempo_execucao: Tempo em segundos
            status: Status da operação
            
        Returns:
            True se registrado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO scraping_stats 
                    (categoria_url, total_produtos, novos_produtos, tempo_execucao, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (categoria_url, total_produtos, novos_produtos, tempo_execucao, status))
                
                conn.commit()
            
            logger.info(f"📊 Estatísticas registradas: {novos_produtos}/{total_produtos} produtos novos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar estatísticas: {e}")
            return False
    
    def get_scraping_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Recupera estatísticas de scraping dos últimos dias
        
        Args:
            days: Número de dias para buscar
            
        Returns:
            Lista de estatísticas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                date_limit = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT categoria_url, total_produtos, novos_produtos, 
                           data_scraping, tempo_execucao, status
                    FROM scraping_stats 
                    WHERE data_scraping >= ?
                    ORDER BY data_scraping DESC
                ''', (date_limit,))
                
                results = cursor.fetchall()
                
                stats = []
                for row in results:
                    stats.append({
                        'categoria_url': row[0],
                        'total_produtos': row[1],
                        'novos_produtos': row[2],
                        'data_scraping': row[3],
                        'tempo_execucao': row[4],
                        'status': row[5]
                    })
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar estatísticas: {e}")
            return []
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Remove registros antigos do banco
        
        Args:
            days: Manter apenas registros dos últimos X dias
            
        Returns:
            Número de registros removidos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                date_limit = datetime.now() - timedelta(days=days)
                
                # Limpar estatísticas antigas
                cursor.execute('DELETE FROM scraping_stats WHERE data_scraping < ?', (date_limit,))
                stats_removed = cursor.rowcount
                
                # Limpar produtos muito antigos (manter últimos 90 dias)
                old_date_limit = datetime.now() - timedelta(days=90)
                cursor.execute('DELETE FROM processed_products WHERE data_processed < ?', (old_date_limit,))
                products_removed = cursor.rowcount
                
                conn.commit()
                
                # Recarregar produtos processados
                self._load_processed_products()
                
                total_removed = stats_removed + products_removed
                logger.info(f"🧹 Limpeza concluída: {total_removed} registros removidos")
                
                return total_removed
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de registros: {e}")
            return 0
    
    def export_processed_products(self, filename: str = None) -> str:
        """
        Exporta lista de produtos processados
        
        Args:
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/processed_products_{timestamp}.json"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, nome, url, categoria_url, data_processed, status
                    FROM processed_products 
                    ORDER BY data_processed DESC
                ''')
                
                results = cursor.fetchall()
                
                products = []
                for row in results:
                    products.append({
                        'id': row[0],
                        'nome': row[1],
                        'url': row[2],
                        'categoria_url': row[3],
                        'data_processed': row[4],
                        'status': row[5]
                    })
                
                export_data = {
                    'total_produtos': len(products),
                    'data_export': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'produtos': products
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"💾 Produtos processados exportados para: {filename}")
                return filename
                
        except Exception as e:
            logger.error(f"❌ Erro ao exportar produtos processados: {e}")
            return ""
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do gerenciador de URLs
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar produtos reais dos arquivos JSON
                import glob
                import json
                import os
                
                total_processed = 0
                categories = {}
                
                # Buscar todos os arquivos JSON de produtos
                json_files = glob.glob("logs/products_*.json")
                
                for json_file in json_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Extrair categoria do nome do arquivo
                            filename = os.path.basename(json_file)
                            categoria_key = filename.replace('products_', '').split('_')[0]
                            
                            # Contar produtos
                            if isinstance(data, list):
                                count = len(data)
                                total_processed += count
                                categories[categoria_key] = categories.get(categoria_key, 0) + count
                            elif isinstance(data, dict) and 'produtos' in data:
                                count = len(data['produtos'])
                                total_processed += count
                                categories[categoria_key] = categories.get(categoria_key, 0) + count
                    except Exception as e:
                        logger.warning(f"Erro ao ler arquivo {json_file}: {e}")
                        continue
                
                # Últimas estatísticas (manter do banco de dados)
                cursor.execute('''
                    SELECT SUM(total_produtos), SUM(novos_produtos), AVG(tempo_execucao)
                    FROM scraping_stats 
                    WHERE data_scraping >= date('now', '-7 days')
                ''')
                recent_stats = cursor.fetchone()
                
                summary = {
                    'total_urls_configuradas': len(self.category_urls),
                    'urls_categorias': self.category_urls,
                    'total_produtos_processados': total_processed,
                    'produtos_por_categoria': categories,
                    'ultimos_7_dias': {
                        'total_produtos_encontrados': recent_stats[0] or 0,
                        'novos_produtos': recent_stats[1] or 0,
                        'tempo_medio_execucao': recent_stats[2] or 0
                    },
                    'status': 'ativo',
                    'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                return summary
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return {'status': 'erro', 'mensagem': str(e)}
    
    def auto_discover_categories(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Descobre automaticamente todas as categorias disponíveis
        
        Args:
            force_refresh: Se deve forçar nova descoberta mesmo com cache
            
        Returns:
            Resultado da descoberta
        """
        logger.info("🔍 Iniciando descoberta automática de categorias...")
        
        # Se já tem categorias descobertas e não é para forçar, usar cache
        if self.discovered_categories and not force_refresh:
            logger.info(f"📋 Usando cache: {len(self.discovered_categories)} categorias descobertas")
            return {
                'status': 'cache',
                'categories': self.discovered_categories,
                'total_discovered': len(self.discovered_categories)
            }
        
        try:
            # Descobrir categorias
            discovery_result = self.category_discovery.discover_all_categories()
            
            if discovery_result['status'] == 'success':
                self.discovered_categories = discovery_result['categories']
                
                # Salvar no banco para persistência
                self._save_discovered_categories(self.discovered_categories)
                
                logger.info(f"✅ Descoberta concluída: {len(self.discovered_categories)} categorias encontradas")
                
                return {
                    'status': 'success',
                    'categories': self.discovered_categories,
                    'total_discovered': len(self.discovered_categories),
                    'execution_time': discovery_result.get('execution_time', 0)
                }
            else:
                logger.error(f"❌ Erro na descoberta: {discovery_result.get('message', 'Erro desconhecido')}")
                return discovery_result
                
        except Exception as e:
            logger.error(f"❌ Erro na descoberta automática: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'categories': []
            }
    
    def update_category_urls_from_discovery(self, categories: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Atualiza lista de URLs com categorias descobertas
        
        Args:
            categories: Lista de categorias (ou usar descobertas em cache)
            
        Returns:
            Resultado da atualização
        """
        if not categories:
            categories = self.discovered_categories
        
        if not categories:
            logger.warning("⚠️ Nenhuma categoria descoberta para atualizar URLs")
            return {
                'status': 'warning',
                'message': 'Nenhuma categoria descoberta. Execute auto_discover_categories() primeiro.'
            }
        
        try:
            old_count = len(self.category_urls)
            new_urls = []
            
            # Adicionar URLs das categorias descobertas
            for category in categories:
                url = category.get('url')
                if url and url not in self.category_urls:
                    self.category_urls.append(url)
                    new_urls.append(url)
            
            new_count = len(self.category_urls)
            added_count = len(new_urls)
            
            logger.info(f"📋 URLs atualizadas: {old_count} → {new_count} ({added_count} novas)")
            
            return {
                'status': 'success',
                'old_count': old_count,
                'new_count': new_count,
                'added_count': added_count,
                'new_urls': new_urls
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar URLs: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def validate_all_category_urls(self) -> Dict[str, Any]:
        """
        Valida todas as URLs de categorias (configuradas + descobertas)
        
        Returns:
            Resultado da validação
        """
        logger.info("🔍 Validando todas as URLs de categorias...")
        
        all_urls = list(set(self.category_urls))  # Remove duplicatas
        
        valid_urls = []
        invalid_urls = []
        
        for url in all_urls:
            try:
                import requests
                response = requests.head(url, timeout=10)
                if response.status_code < 400:
                    valid_urls.append(url)
                    logger.debug(f"✅ URL válida: {url}")
                else:
                    invalid_urls.append({'url': url, 'status_code': response.status_code})
                    logger.warning(f"⚠️ URL inválida ({response.status_code}): {url}")
            except Exception as e:
                invalid_urls.append({'url': url, 'error': str(e)})
                logger.warning(f"❌ Erro ao validar {url}: {e}")
        
        # Atualizar lista apenas com URLs válidas
        self.category_urls = valid_urls
        
        result = {
            'status': 'success',
            'total_checked': len(all_urls),
            'valid_urls': len(valid_urls),
            'invalid_urls': len(invalid_urls),
            'valid_list': valid_urls,
            'invalid_list': invalid_urls
        }
        
        logger.info(f"✅ Validação concluída: {len(valid_urls)}/{len(all_urls)} URLs válidas")
        
        return result
    
    def _save_discovered_categories(self, categories: List[Dict[str, Any]]):
        """Salva categorias descobertas no banco para cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Criar tabela se não existir
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS discovered_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        source TEXT,
                        has_products BOOLEAN,
                        status TEXT,
                        discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Limpar registros antigos
                cursor.execute('DELETE FROM discovered_categories')
                
                # Inserir novas categorias
                for category in categories:
                    cursor.execute('''
                        INSERT INTO discovered_categories 
                        (name, url, source, has_products, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        category.get('name', ''),
                        category.get('url', ''),
                        category.get('source', ''),
                        category.get('has_products', False),
                        category.get('status', '')
                    ))
                
                conn.commit()
                logger.debug(f"💾 {len(categories)} categorias salvas no cache")
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar categorias descobertas: {e}")
    
    def close(self):
        """Fecha conexões"""
        if hasattr(self, 'category_discovery'):
            self.category_discovery.close() 
 
 
 
 