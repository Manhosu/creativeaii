#!/usr/bin/env python3
"""
Active Categories Manager
Gerencia as categorias ativas para scraping, geração e publicação
"""

import sqlite3
import asyncio
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from loguru import logger
from pathlib import Path

# from ..scraper.category_discovery import CategoryDiscovery  # Import opcional


class ActiveCategoriesManager:
    """Manager para categorias ativas do sistema"""
    
    def __init__(self, db_path: str = "src/database/config.db"):
        self.db_path = db_path
        self.base_url = os.getenv("SITE_BASE_URL", "https://www.creativecopias.com.br")
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados com a tabela de categorias ativas"""
        try:
            # Garantir que o diretório existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Executar migração
            migration_path = Path("src/database/migrations/create_active_categories.sql")
            if migration_path.exists():
                with open(migration_path, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                    cursor.executescript(migration_sql)
            else:
                # Fallback: criar tabela manualmente
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS active_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_key TEXT NOT NULL UNIQUE,
                    category_name TEXT NOT NULL,
                    category_url TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 0,
                    auto_detected BOOLEAN DEFAULT FALSE,
                    products_count INTEGER DEFAULT 0,
                    last_scraped TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Inserir categorias padrão
                default_categories = [
                    ('impressoras', 'Impressoras Creative Cópias', 'https://www.creativecopias.com.br/impressoras', True, 1, True),
                    ('cartuchos-de-toner', 'Cartuchos de Toner Creative Cópias', 'https://www.creativecopias.com.br/cartuchos-de-toner', True, 2, True),
                    ('cartuchos-de-tinta', 'Cartuchos de Tinta Creative Cópias', 'https://www.creativecopias.com.br/cartuchos-de-tinta', True, 3, True),
                    ('refil-de-toner', 'Refil de Toner Creative Cópias', 'https://www.creativecopias.com.br/refil-de-toner', True, 4, True),
                    ('refil-de-tinta', 'Refil de Tinta Creative Cópias', 'https://www.creativecopias.com.br/refil-de-tinta', True, 5, True),
                    ('papel-fotografico', 'Papel Fotográfico Creative Cópias', 'https://www.creativecopias.com.br/papel-fotografico', True, 6, True),
                    ('multifuncional', 'Multifuncionais Creative Cópias', 'https://www.creativecopias.com.br/impressoras/tipo/multifuncional', True, 7, True)
                ]
                
                for category in default_categories:
                    cursor.execute('''
                    INSERT OR IGNORE INTO active_categories 
                    (category_key, category_name, category_url, is_active, priority, auto_detected)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', category)
            
            conn.commit()
            conn.close()
            logger.info("✅ Banco de categorias ativas inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de categorias ativas: {e}")
            raise
    
    def get_active_categories(self) -> List[Dict[str, Any]]:
        """Retorna todas as categorias ativas ordenadas por prioridade"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM active_categories 
            WHERE is_active = TRUE 
            ORDER BY priority ASC, category_name ASC
            ''')
            
            categories = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.debug(f"📋 {len(categories)} categorias ativas carregadas")
            return categories
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar categorias ativas: {e}")
            return []
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Retorna todas as categorias (ativas e inativas)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM active_categories 
            ORDER BY is_active DESC, priority ASC, category_name ASC
            ''')
            
            categories = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return categories
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar todas as categorias: {e}")
            return []
    
    def update_category_status(self, category_key: str, is_active: bool) -> bool:
        """Atualiza o status ativo/inativo de uma categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE active_categories 
            SET is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE category_key = ?
            ''', (is_active, category_key))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            status = "ativada" if is_active else "desativada"
            logger.info(f"✅ Categoria '{category_key}' {status}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar categoria '{category_key}': {e}")
            return False
    
    def update_categories_batch(self, categories_status: Dict[str, bool]) -> bool:
        """Atualiza múltiplas categorias em lote"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for category_key, is_active in categories_status.items():
                cursor.execute('''
                UPDATE active_categories 
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category_key = ?
                ''', (is_active, category_key))
            
            conn.commit()
            conn.close()
            
            active_count = sum(1 for active in categories_status.values() if active)
            total_count = len(categories_status)
            
            logger.info(f"✅ Atualização em lote: {active_count}/{total_count} categorias ativas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na atualização em lote: {e}")
            return False
    
    def update_category_priority(self, category_key: str, priority: int) -> bool:
        """Atualiza a prioridade de uma categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE active_categories 
            SET priority = ?, updated_at = CURRENT_TIMESTAMP
            WHERE category_key = ?
            ''', (priority, category_key))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Prioridade da categoria '{category_key}' atualizada para {priority}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar prioridade da categoria '{category_key}': {e}")
            return False
    
    def update_category_stats(self, category_key: str, products_count: int) -> bool:
        """Atualiza estatísticas de uma categoria após scraping"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE active_categories 
            SET products_count = ?, last_scraped = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE category_key = ?
            ''', (products_count, category_key))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                logger.debug(f"📊 Stats atualizadas para '{category_key}': {products_count} produtos")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar stats da categoria '{category_key}': {e}")
            return False
    
    async def discover_and_update_categories(self) -> int:
        """Descobre automaticamente novas categorias do site e atualiza o banco"""
        try:
            logger.info("🔍 Iniciando descoberta automática de categorias...")
            
            discovery = CategoryDiscovery(self.base_url)
            discovered_categories = await discovery.discover_categories()
            
            if not discovered_categories:
                logger.warning("⚠️ Nenhuma categoria descoberta automaticamente")
                return 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_categories = 0
            for category in discovered_categories:
                # Extrair chave da categoria da URL
                category_key = category['url'].replace(self.base_url + '/', '').replace('/', '-')
                
                cursor.execute('''
                INSERT OR IGNORE INTO active_categories 
                (category_key, category_name, category_url, is_active, auto_detected, priority)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    category_key,
                    category['name'],
                    category['url'],
                    True,  # Novas categorias começam ativas
                    True,  # Marcada como auto-detectada
                    99     # Prioridade baixa para novas categorias
                ))
                
                if cursor.rowcount > 0:
                    new_categories += 1
                    logger.info(f"➕ Nova categoria adicionada: {category['name']}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Descoberta concluída: {new_categories} novas categorias adicionadas")
            return new_categories
            
        except Exception as e:
            logger.error(f"❌ Erro na descoberta de categorias: {e}")
            return 0
    
    def get_active_urls(self) -> List[str]:
        """Retorna apenas URLs das categorias ativas"""
        active_categories = self.get_active_categories()
        return [cat['category_url'] for cat in active_categories]
    
    def get_active_category_keys(self) -> List[str]:
        """Retorna apenas as chaves das categorias ativas"""
        active_categories = self.get_active_categories()
        return [cat['category_key'] for cat in active_categories]
    
    def is_category_active(self, category_key: str) -> bool:
        """Verifica se uma categoria específica está ativa"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT is_active FROM active_categories 
            WHERE category_key = ?
            ''', (category_key,))
            
            result = cursor.fetchone()
            conn.close()
            
            return bool(result and result[0]) if result else False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar categoria '{category_key}': {e}")
            return False
    
    def get_categories_summary(self) -> Dict[str, Any]:
        """Retorna resumo das categorias para dashboard"""
        try:
            categories = self.get_all_categories()
            
            active_categories = [cat for cat in categories if cat['is_active']]
            inactive_categories = [cat for cat in categories if not cat['is_active']]
            
            total_products = sum(cat.get('products_count', 0) for cat in active_categories)
            
            return {
                'total_categories': len(categories),
                'active_categories': len(active_categories),
                'inactive_categories': len(inactive_categories),
                'total_products': total_products,
                'categories': categories,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo de categorias: {e}")
            return {
                'total_categories': 0,
                'active_categories': 0,
                'inactive_categories': 0,
                'total_products': 0,
                'categories': [],
                'last_update': datetime.now().isoformat()
            }
    
    def add_category(self, category_key: str, category_name: str, category_url: str, 
                    priority: int = 0, is_active: bool = True) -> bool:
        """Adicionar nova categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR IGNORE INTO active_categories 
            (category_key, category_name, category_url, is_active, priority, auto_detected)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (category_key, category_name, category_url, is_active, priority, False))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                logger.info(f"✅ Categoria '{category_name}' adicionada")
            else:
                logger.warning(f"⚠️ Categoria '{category_name}' já existe")
            
            return True  # Retorna True mesmo se já existe
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar categoria: {e}")
            return False
    
    def get_category(self, category_key: str) -> dict:
        """Buscar categoria específica"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM active_categories WHERE category_key = ?', (category_key,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar categoria: {e}")
            return None
    
    def update_category(self, category_key: str, update_data: dict) -> bool:
        """Atualizar categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query dinâmica
            fields = []
            values = []
            
            for field, value in update_data.items():
                if field in ['category_name', 'category_url', 'is_active', 'priority']:
                    fields.append(f"{field} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(category_key)
            
            query = f"UPDATE active_categories SET {', '.join(fields)} WHERE category_key = ?"
            cursor.execute(query, values)
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar categoria: {e}")
            return False
    
    def remove_category(self, category_key: str) -> bool:
        """Remover categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM active_categories WHERE category_key = ?', (category_key,))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover categoria: {e}")
            return False
    
    def update_products_count_from_scraper(self) -> bool:
        """Atualizar contagem de produtos baseada nos dados reais do scraper"""
        try:
            import json
            import os
            from pathlib import Path
            
            logger.info("🔄 Atualizando contagem de produtos por categoria...")
            
            # Buscar arquivos de produtos do scraper
            products_dir = Path("logs")
            if not products_dir.exists():
                logger.warning("⚠️ Diretório de logs não encontrado")
                return False
            
            # 🚨 CORREÇÃO CRÍTICA: Usar mesma lógica para evitar duplicatas
            category_files = {}
            category_counts = {}
            
            # Primeiro, identificar arquivos únicos (preferir _CORRIGIDO)
            for file_path in products_dir.glob("products_*.json"):
                file_name = file_path.stem
                category_slug = file_name.replace("products_", "").split("_")[0]
                
                if 'CORRIGIDO' in file_name:
                    # Arquivo corrigido tem prioridade
                    category_files[category_slug] = file_path
                elif category_slug not in category_files:
                    # Primeiro arquivo desta categoria
                    category_files[category_slug] = file_path
                # Ignorar arquivos duplicados
            
            logger.info(f"📊 CORREÇÃO: {len(category_files)} categorias únicas (eliminando duplicatas)")
            
            # Agora contar produtos únicos apenas dos arquivos selecionados
            for category_slug, file_path in category_files.items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Contar produtos únicos por nome
                        unique_products = set()
                        if isinstance(data, dict) and 'produtos' in data:
                            for product in data['produtos']:
                                if product.get('nome'):
                                    unique_products.add(product['nome'])
                            category_counts[category_slug] = len(unique_products)
                        elif isinstance(data, list):
                            for product in data:
                                if product.get('nome'):
                                    unique_products.add(product['nome'])
                            category_counts[category_slug] = len(unique_products)
                            
                        logger.debug(f"✅ {category_slug}: {len(unique_products)} produtos únicos ({file_path.name})")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao ler arquivo {file_path}: {e}")
                    continue
            
            # Mapear para as categorias configuradas
            category_final_counts = {}
            
            # Conectar ao banco
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT category_key, category_url, category_name FROM active_categories')
            categories = cursor.fetchall()
            
            # Criar mapeamento slug -> chave
            slug_to_key = {}
            for cat in categories:
                # Mapear por slug (derivado da URL)
                url_parts = cat['category_url'].split('/')
                if url_parts:
                    url_slug = url_parts[-1]  # última parte da URL
                    slug_to_key[url_slug] = cat['category_key']
                
                category_final_counts[cat['category_key']] = 0
            
            # Mapear contagens do arquivo para as categorias
            for file_slug, count in category_counts.items():
                mapped = False
                
                # Tentar mapear por slug exato
                if file_slug in slug_to_key:
                    category_final_counts[slug_to_key[file_slug]] = count
                    mapped = True
                    
                # Tentar mapear por slug similar
                if not mapped:
                    for url_slug, cat_key in slug_to_key.items():
                        if file_slug in url_slug or url_slug in file_slug:
                            category_final_counts[cat_key] = count
                            mapped = True
                            break
                
                # Log se não conseguiu mapear
                if not mapped:
                    logger.warning(f"⚠️ Não foi possível mapear categoria do arquivo: {file_slug}")
            
            # Atualizar banco de dados
            for category_key, count in category_final_counts.items():
                cursor.execute('''
                UPDATE active_categories 
                SET products_count = ?, last_scraped = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE category_key = ?
                ''', (count, category_key))
            
            conn.commit()
            conn.close()
            
            # Log dos resultados
            total_counted = sum(category_final_counts.values())
            logger.success(f"✅ Contagem atualizada: {total_counted} produtos distribuídos em {len(category_final_counts)} categorias")
            
            for cat_key, count in category_final_counts.items():
                if count > 0:
                    logger.info(f"  📊 {cat_key}: {count} produtos")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar contagem de produtos: {e}")
            return False
    
    def get_category_product_count(self, category_key: str) -> int:
        """Obter contagem específica de produtos de uma categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT products_count FROM active_categories WHERE category_key = ?', (category_key,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter contagem da categoria {category_key}: {e}")
            return 0 