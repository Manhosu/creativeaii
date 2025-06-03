"""
Config Manager - Sistema de Geração Automática de Conteúdo SEO
Gerenciador centralizado de configurações do sistema
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class ConfigManager:
    """Gerenciador centralizado de configurações do sistema"""
    
    def __init__(self, db_path: str = "data/config.db"):
        """Inicializa o gerenciador de configurações"""
        self.db_path = db_path
        self.config_cache = {}
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        # Carregar configurações padrão se for primeira execução
        self._load_default_configs()
        
        logger.info("⚙️ Config Manager inicializado")
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela principal de configurações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configurations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        section TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        data_type TEXT DEFAULT 'string',
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(section, key)
                    )
                """)
                
                # Tabela de URLs monitoradas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS monitored_urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        active BOOLEAN DEFAULT 1,
                        priority INTEGER DEFAULT 5,
                        last_scraped TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de templates
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS content_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_name TEXT NOT NULL UNIQUE,
                        product_type TEXT NOT NULL,
                        title_template TEXT,
                        content_template TEXT,
                        meta_description_template TEXT,
                        keywords_template TEXT,
                        active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de backups de configuração
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS config_backups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        backup_name TEXT NOT NULL,
                        backup_data TEXT NOT NULL,
                        backup_size INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("✅ Banco de dados de configurações inicializado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def _load_default_configs(self):
        """Carrega configurações padrão se for primeira execução"""
        try:
            # Verificar se já existem configurações
            existing_configs = self.get_all_configs()
            if existing_configs:
                return
            
            # Configurações padrão
            default_configs = {
                'scraper': {
                    'delay_between_requests': {
                        'value': '2',
                        'type': 'integer',
                        'description': 'Delay em segundos entre requisições'
                    },
                    'user_agent_rotation': {
                        'value': 'true',
                        'type': 'boolean',
                        'description': 'Rotacionar User-Agents'
                    },
                    'max_retries': {
                        'value': '3',
                        'type': 'integer',
                        'description': 'Máximo de tentativas por URL'
                    }
                },
                'generator': {
                    'openai_model': {
                        'value': 'gpt-4',
                        'type': 'string',
                        'description': 'Modelo OpenAI para geração'
                    },
                    'temperature': {
                        'value': '0.7',
                        'type': 'float',
                        'description': 'Criatividade da IA (0.0-1.0)'
                    },
                    'max_tokens': {
                        'value': '2000',
                        'type': 'integer',
                        'description': 'Máximo de tokens na resposta'
                    },
                    'tone': {
                        'value': 'profissional',
                        'type': 'string',
                        'description': 'Tom de voz padrão'
                    },
                    'simulation_mode': {
                        'value': 'true',
                        'type': 'boolean',
                        'description': 'Modo simulação (sem OpenAI API)'
                    },
                    'base_prompt': {
                        'value': 'Você é um especialista em redação SEO para e-commerce. Crie conteúdo otimizado, informativo e persuasivo.',
                        'type': 'text',
                        'description': 'Prompt base para geração de conteúdo'
                    }
                },
                'wordpress': {
                    'site_url': {
                        'value': '',
                        'type': 'string',
                        'description': 'URL do site WordPress'
                    },
                    'api_username': {
                        'value': '',
                        'type': 'string',
                        'description': 'Usuário da API WordPress'
                    },
                    'api_password': {
                        'value': '',
                        'type': 'password',
                        'description': 'Senha/Token da API WordPress'
                    },
                    'default_category': {
                        'value': '1',
                        'type': 'integer',
                        'description': 'Categoria padrão para posts'
                    },
                    'auto_publish': {
                        'value': 'false',
                        'type': 'boolean',
                        'description': 'Publicar automaticamente após aprovação'
                    }
                },
                'seo': {
                    'meta_title_max_length': {
                        'value': '60',
                        'type': 'integer',
                        'description': 'Máximo de caracteres no título SEO'
                    },
                    'meta_description_max_length': {
                        'value': '160',
                        'type': 'integer',
                        'description': 'Máximo de caracteres na meta description'
                    },
                    'keywords_per_article': {
                        'value': '10',
                        'type': 'integer',
                        'description': 'Máximo de palavras-chave por artigo'
                    },
                    'focus_keyword_density': {
                        'value': '2.5',
                        'type': 'float',
                        'description': 'Densidade da palavra-chave principal (%)'
                    }
                },
                'system': {
                    'backup_retention_days': {
                        'value': '30',
                        'type': 'integer',
                        'description': 'Dias para manter backups'
                    },
                    'log_level': {
                        'value': 'INFO',
                        'type': 'string',
                        'description': 'Nível de log (DEBUG, INFO, WARNING, ERROR)'
                    },
                    'max_articles_per_day': {
                        'value': '50',
                        'type': 'integer',
                        'description': 'Máximo de artigos gerados por dia'
                    }
                }
            }
            
            # Inserir configurações padrão
            for section, configs in default_configs.items():
                for key, config_data in configs.items():
                    self.set_config(
                        section=section,
                        key=key,
                        value=config_data['value'],
                        data_type=config_data['type'],
                        description=config_data['description']
                    )
            
            # URLs padrão para monitoramento
            default_urls = [
                {
                    'category': 'impressoras',
                    'name': 'Impressoras Creative Cópias',
                    'url': 'https://www.creativecopias.com.br/impressoras',
                    'priority': 10
                },
                {
                    'category': 'multifuncionais',
                    'name': 'Multifuncionais Creative Cópias',
                    'url': 'https://www.creativecopias.com.br/multifuncionais',
                    'priority': 9
                },
                {
                    'category': 'toners',
                    'name': 'Toners Creative Cópias',
                    'url': 'https://www.creativecopias.com.br/toners',
                    'priority': 8
                },
                {
                    'category': 'papel',
                    'name': 'Papel Creative Cópias',
                    'url': 'https://www.creativecopias.com.br/papel',
                    'priority': 7
                }
            ]
            
            for url_data in default_urls:
                self.add_monitored_url(**url_data)
            
            # Templates padrão
            default_templates = [
                {
                    'template_name': 'impressora_laser',
                    'product_type': 'impressora',
                    'title_template': '{nome}: {marca} - Soluções Profissionais de Impressão',
                    'content_template': 'Template para impressoras laser profissionais...',
                    'meta_description_template': 'Conheça a {nome} da {marca}. Impressão profissional com qualidade superior.',
                    'keywords_template': 'impressora, {marca}, {modelo}, impressão profissional'
                },
                {
                    'template_name': 'multifuncional',
                    'product_type': 'multifuncional',
                    'title_template': '{nome}: {marca} - Multifuncional Completa',
                    'content_template': 'Template para equipamentos multifuncionais...',
                    'meta_description_template': 'Multifuncional {nome} da {marca}. Imprima, copie e digitalize com eficiência.',
                    'keywords_template': 'multifuncional, {marca}, {modelo}, impressão, cópia, scanner'
                }
            ]
            
            for template_data in default_templates:
                self.add_content_template(**template_data)
            
            logger.info("✅ Configurações padrão carregadas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configurações padrão: {e}")
    
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Obter configuração específica"""
        try:
            cache_key = f"{section}.{key}"
            
            # Verificar cache primeiro
            if cache_key in self.config_cache:
                return self.config_cache[cache_key]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value, data_type FROM configurations WHERE section = ? AND key = ?",
                    (section, key)
                )
                result = cursor.fetchone()
                
                if result:
                    value, data_type = result
                    # Converter tipo de dados
                    converted_value = self._convert_value(value, data_type)
                    self.config_cache[cache_key] = converted_value
                    return converted_value
                else:
                    return default
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter configuração {section}.{key}: {e}")
            return default
    
    def set_config(self, section: str, key: str, value: Any, data_type: str = 'string', description: str = None):
        """Definir configuração"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO configurations 
                    (section, key, value, data_type, description, updated_at) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (section, key, str(value), data_type, description))
                conn.commit()
                
                # Atualizar cache
                cache_key = f"{section}.{key}"
                self.config_cache[cache_key] = self._convert_value(str(value), data_type)
                
                logger.debug(f"⚙️ Configuração atualizada: {section}.{key} = {value}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao definir configuração {section}.{key}: {e}")
            raise
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Obter todas as configurações organizadas por seção"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT section, key, value, data_type, description 
                    FROM configurations 
                    ORDER BY section, key
                """)
                results = cursor.fetchall()
                
                configs = {}
                for section, key, value, data_type, description in results:
                    if section not in configs:
                        configs[section] = {}
                    
                    configs[section][key] = {
                        'value': self._convert_value(value, data_type),
                        'type': data_type,
                        'description': description
                    }
                
                return configs
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter todas as configurações: {e}")
            return {}
    
    def update_configs(self, configs: Dict[str, Dict[str, Any]]):
        """Atualizar múltiplas configurações"""
        try:
            for section, section_configs in configs.items():
                for key, config_data in section_configs.items():
                    if isinstance(config_data, dict) and 'value' in config_data:
                        value = config_data['value']
                        data_type = config_data.get('type', 'string')
                        description = config_data.get('description')
                    else:
                        value = config_data
                        data_type = 'string'
                        description = None
                    
                    self.set_config(section, key, value, data_type, description)
            
            logger.info("✅ Configurações atualizadas em lote")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar configurações: {e}")
            raise
    
    def reset_config_section(self, section: str):
        """Resetar uma seção de configurações"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM configurations WHERE section = ?", (section,))
                conn.commit()
                
                # Limpar cache da seção
                keys_to_remove = [k for k in self.config_cache.keys() if k.startswith(f"{section}.")]
                for key in keys_to_remove:
                    del self.config_cache[key]
                
                logger.info(f"✅ Seção {section} resetada")
                
        except Exception as e:
            logger.error(f"❌ Erro ao resetar seção {section}: {e}")
            raise
    
    def add_monitored_url(self, category: str, name: str, url: str, priority: int = 5):
        """Adicionar URL para monitoramento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO monitored_urls 
                    (category, name, url, priority) 
                    VALUES (?, ?, ?, ?)
                """, (category, name, url, priority))
                conn.commit()
                
                logger.info(f"✅ URL adicionada: {name} ({url})")
                
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar URL: {e}")
            raise
    
    def get_monitored_urls(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obter URLs monitoradas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if active_only:
                    cursor.execute("""
                        SELECT id, category, name, url, priority, last_scraped, created_at 
                        FROM monitored_urls 
                        WHERE active = 1 
                        ORDER BY priority DESC, category, name
                    """)
                else:
                    cursor.execute("""
                        SELECT id, category, name, url, active, priority, last_scraped, created_at 
                        FROM monitored_urls 
                        ORDER BY priority DESC, category, name
                    """)
                
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                
                urls = []
                for result in results:
                    url_data = dict(zip(columns, result))
                    urls.append(url_data)
                
                return urls
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter URLs monitoradas: {e}")
            return []
    
    def remove_monitored_url(self, url_id: int):
        """Remover URL monitorada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM monitored_urls WHERE id = ?", (url_id,))
                conn.commit()
                
                logger.info(f"✅ URL removida (ID: {url_id})")
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover URL: {e}")
            raise
    
    def add_content_template(self, template_name: str, product_type: str, 
                           title_template: str, content_template: str,
                           meta_description_template: str = None, 
                           keywords_template: str = None):
        """Adicionar template de conteúdo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO content_templates 
                    (template_name, product_type, title_template, content_template, 
                     meta_description_template, keywords_template, updated_at) 
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (template_name, product_type, title_template, content_template,
                      meta_description_template, keywords_template))
                conn.commit()
                
                logger.info(f"✅ Template adicionado: {template_name}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar template: {e}")
            raise
    
    def get_content_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obter templates de conteúdo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if active_only:
                    cursor.execute("""
                        SELECT * FROM content_templates 
                        WHERE active = 1 
                        ORDER BY product_type, template_name
                    """)
                else:
                    cursor.execute("""
                        SELECT * FROM content_templates 
                        ORDER BY product_type, template_name
                    """)
                
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                
                templates = []
                for result in results:
                    template_data = dict(zip(columns, result))
                    templates.append(template_data)
                
                return templates
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter templates: {e}")
            return []
    
    def export_config(self) -> Dict[str, Any]:
        """Exportar todas as configurações"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'system_version': '1.0.0',
                'configurations': self.get_all_configs(),
                'monitored_urls': self.get_monitored_urls(active_only=False),
                'content_templates': self.get_content_templates(active_only=False)
            }
            
            logger.info("✅ Configurações exportadas")
            return export_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar configurações: {e}")
            raise
    
    def import_config(self, config_data: Dict[str, Any], overwrite: bool = False):
        """Importar configurações"""
        try:
            if overwrite:
                # Limpar configurações existentes
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM configurations")
                    cursor.execute("DELETE FROM monitored_urls")
                    cursor.execute("DELETE FROM content_templates")
                    conn.commit()
                
                # Limpar cache
                self.config_cache.clear()
            
            # Importar configurações
            if 'configurations' in config_data:
                self.update_configs(config_data['configurations'])
            
            # Importar URLs
            if 'monitored_urls' in config_data:
                for url_data in config_data['monitored_urls']:
                    self.add_monitored_url(
                        category=url_data['category'],
                        name=url_data['name'],
                        url=url_data['url'],
                        priority=url_data.get('priority', 5)
                    )
            
            # Importar templates
            if 'content_templates' in config_data:
                for template_data in config_data['content_templates']:
                    self.add_content_template(
                        template_name=template_data['template_name'],
                        product_type=template_data['product_type'],
                        title_template=template_data['title_template'],
                        content_template=template_data['content_template'],
                        meta_description_template=template_data.get('meta_description_template'),
                        keywords_template=template_data.get('keywords_template')
                    )
            
            logger.info("✅ Configurações importadas com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao importar configurações: {e}")
            raise
    
    def create_backup(self, backup_name: str = None) -> str:
        """Criar backup das configurações"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_data = self.export_config()
            backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO config_backups (backup_name, backup_data, backup_size) 
                    VALUES (?, ?, ?)
                """, (backup_name, backup_json, len(backup_json)))
                conn.commit()
            
            logger.info(f"✅ Backup criado: {backup_name}")
            return backup_name
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas do sistema de configuração"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar configurações por seção
                cursor.execute("""
                    SELECT section, COUNT(*) as count 
                    FROM configurations 
                    GROUP BY section
                """)
                config_counts = dict(cursor.fetchall())
                
                # Contar URLs por categoria
                cursor.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM monitored_urls 
                    WHERE active = 1
                    GROUP BY category
                """)
                url_counts = dict(cursor.fetchall())
                
                # Contar templates por tipo
                cursor.execute("""
                    SELECT product_type, COUNT(*) as count 
                    FROM content_templates 
                    WHERE active = 1
                    GROUP BY product_type
                """)
                template_counts = dict(cursor.fetchall())
                
                # Total de backups
                cursor.execute("SELECT COUNT(*) FROM config_backups")
                backup_count = cursor.fetchone()[0]
                
                return {
                    'config_sections': config_counts,
                    'url_categories': url_counts,
                    'template_types': template_counts,
                    'total_backups': backup_count,
                    'cache_size': len(self.config_cache),
                    'status': 'operational'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _convert_value(self, value: str, data_type: str) -> Any:
        """Converte valor string para o tipo apropriado"""
        try:
            if data_type == 'integer':
                return int(value)
            elif data_type == 'float':
                return float(value)
            elif data_type == 'boolean':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif data_type in ('text', 'password'):
                return value
            else:  # string
                return value
        except ValueError:
            logger.warning(f"⚠️ Erro ao converter valor '{value}' para {data_type}, retornando string")
            return value 