"""
Review Manager
Sistema de revisão humana de artigos antes da publicação
"""

import os
import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from loguru import logger
from ..scraper.availability_checker import AvailabilityChecker
from ..intelligence.priority_manager import PriorityManager
from pathlib import Path
import threading

class ReviewManager:
    """Gerenciador de revisão de artigos"""
    
    def __init__(self, db_path: str = "data/review_articles.db"):
        """Inicializa o gerenciador de revisão"""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.availability_checker = AvailabilityChecker()
        self.priority_manager = PriorityManager()
        
        # Garantir que o diretório existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Verificar e corrigir banco de dados
        self._verify_and_fix_database()
        
        # Inicializar banco
        self._init_database()
        
        # Executar migrações
        self._run_migrations()
        
        # Configurar logging
        logger.add(
            "logs/review.log",
            rotation="1 week",
            retention="30 days",
            level="INFO",
            format="{time} | {level} | {message}"
        )
        
        logger.info(f"✅ ReviewManager inicializado - DB: {self.db_path}")
    
    def _verify_and_fix_database(self):
        """Verifica se o banco está válido e corrige se necessário"""
        try:
            if Path(self.db_path).exists():
                # Tentar conectar e fazer uma query simples
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    # Se não tem a tabela articles, recriar
                    if not any('articles' in str(table) for table in tables):
                        logger.warning("⚠️ Tabela 'articles' não encontrada, recriando banco...")
                        self._recreate_database()
                    else:
                        logger.info("✅ Banco de dados verificado e válido")
                        
        except sqlite3.DatabaseError as e:
            logger.error(f"❌ Banco corrompido: {e}")
            logger.info("🔧 Recriando banco de dados...")
            self._recreate_database()
        except Exception as e:
            logger.error(f"❌ Erro ao verificar banco: {e}")
            self._recreate_database()
    
    def _recreate_database(self):
        """Recria o banco de dados do zero"""
        try:
            # Backup do arquivo atual se existir
            if Path(self.db_path).exists():
                backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                Path(self.db_path).rename(backup_path)
                logger.info(f"📦 Backup criado: {backup_path}")
            
            # Remover arquivo corrompido
            if Path(self.db_path).exists():
                Path(self.db_path).unlink()
                
            logger.info("🔧 Recriando banco de dados...")
            
        except Exception as e:
            logger.error(f"❌ Erro ao recriar banco: {e}")
    
    def _init_database(self):
        """Inicializa o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Criar tabela principal
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        slug TEXT,
                        meta_descricao TEXT,
                        conteudo TEXT NOT NULL,
                        tags TEXT DEFAULT '[]',
                        produto_id TEXT,
                        produto_nome TEXT,
                        status TEXT DEFAULT 'pendente',
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_revisao TIMESTAMP,
                        comentario_revisor TEXT,
                        revisor_nome TEXT,
                        score_seo INTEGER DEFAULT 0,
                        tipo_produto TEXT,
                        tom_usado TEXT DEFAULT 'profissional',
                        generation_data TEXT,
                        content_hash TEXT,
                        wp_category TEXT,
                        produto_original TEXT
                    )
                """)
                
                # Criar índices
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON articles(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_criacao ON articles(data_criacao)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_produto_id ON articles(produto_id)")
                
                conn.commit()
                
                # Verificar se há dados
                cursor.execute("SELECT COUNT(*) FROM articles")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    logger.info("📝 Banco vazio, pronto para novos artigos")
                    # self._create_sample_articles()  # Desabilitado para sistema zerado
                else:
                    logger.info(f"📊 Banco inicializado com {count} artigos")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
            raise
    
    def _run_migrations(self):
        """Executa migrações do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se existem as novas colunas
                cursor.execute("PRAGMA table_info(articles)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Adicionar coluna wp_category se não existir
                if 'wp_category' not in columns:
                    cursor.execute("ALTER TABLE articles ADD COLUMN wp_category TEXT")
                    logger.info("✅ Coluna 'wp_category' adicionada")
                
                # Adicionar coluna produto_original se não existir
                if 'produto_original' not in columns:
                    cursor.execute("ALTER TABLE articles ADD COLUMN produto_original TEXT")
                    logger.info("✅ Coluna 'produto_original' adicionada")
                
                conn.commit()
                logger.info("🔄 Migrações de banco executadas com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar migrações: {e}")
    
    def _create_sample_articles(self):
        """Cria artigos de exemplo para teste"""
        try:
            sample_articles = [
                {
                    'titulo': 'Impressora HP LaserJet Pro M404n: Review Completo 2025',
                    'slug': 'impressora-hp-laserjet-pro-m404n-review',
                    'meta_descricao': 'Análise completa da HP LaserJet Pro M404n. Especificações, prós e contras, e vale a pena comprar em 2025.',
                    'conteudo': '''# Impressora HP LaserJet Pro M404n: Review Completo

## Introdução
A HP LaserJet Pro M404n é uma impressora laser monocromática projetada para pequenos escritórios e uso doméstico profissional.

## Especificações Técnicas
- **Velocidade**: Até 38 ppm
- **Resolução**: 1200 x 1200 dpi
- **Conectividade**: USB, Ethernet
- **Capacidade**: 250 folhas

## Prós e Contras
**Prós:**
- Alta velocidade de impressão
- Qualidade de texto excelente
- Conectividade de rede

**Contras:**
- Apenas monocromática
- Sem WiFi integrado

## Conclusão
Excelente opção para quem precisa de impressões rápidas e de qualidade em preto e branco.''',
                    'tags': '["impressora", "hp", "laser", "escritório"]',
                    'produto_nome': 'Impressora HP LaserJet Pro M404n',
                    'status': 'pendente',
                    'tipo_produto': 'impressora',
                    'tom_usado': 'profissional'
                },
                {
                    'titulo': 'Mouse Gamer Logitech G502 HERO: Vale a Pena?',
                    'slug': 'mouse-gamer-logitech-g502-hero-review',
                    'meta_descricao': 'Review do mouse gamer Logitech G502 HERO. Especificações, performance em jogos e custo-benefício.',
                    'conteudo': '''# Mouse Gamer Logitech G502 HERO: Análise Detalhada

## Características Principais
O Logitech G502 HERO é um mouse gamer com sensor HERO 25K de alta precisão.

## Performance
- **DPI**: Até 25.600
- **Aceleração**: 40G
- **Velocidade**: 400 IPS

## Design e Ergonomia
Mouse com design ergonômico, ideal para destros, com 11 botões programáveis.

## Conclusão
Uma das melhores opções para gamers que buscam precisão e customização.''',
                    'tags': '["mouse", "gamer", "logitech", "periférico"]',
                    'produto_nome': 'Mouse Gamer Logitech G502 HERO',
                    'status': 'pendente',
                    'tipo_produto': 'periférico',
                    'tom_usado': 'profissional'
                }
            ]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for article in sample_articles:
                    cursor.execute("""
                        INSERT INTO articles (
                            titulo, slug, meta_descricao, conteudo, tags,
                            produto_nome, status, tipo_produto, tom_usado
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article['titulo'], article['slug'], article['meta_descricao'],
                        article['conteudo'], article['tags'], article['produto_nome'],
                        article['status'], article['tipo_produto'], article['tom_usado']
                    ))
                
                conn.commit()
                logger.info(f"✅ {len(sample_articles)} artigos de exemplo criados")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar artigos de exemplo: {e}")
    
    def save_article_for_review(self, article_data: Dict[str, Any], allow_duplicates: bool = True) -> int:
        """
        Salva artigo gerado para revisão - PERMITE MÚLTIPLOS ARTIGOS DO MESMO PRODUTO
        
        Args:
            article_data: Dados do artigo gerado pelo Generator
            allow_duplicates: Se True, permite salvar mesmo se for duplicata (padrão: True)
            
        Returns:
            ID do artigo no sistema de revisão
        """
        try:
            # 🔄 SISTEMA INTELIGENTE: Permitir múltiplos artigos por padrão
            produto_nome = article_data.get('produto_nome', '')
            
            # Verificação apenas se explicitamente não permitir duplicatas
            if not allow_duplicates:
                # Verificar duplicatas apenas por hash de conteúdo idêntico
                if self._is_exact_duplicate(article_data):
                    logger.warning(f"🚫 Conteúdo idêntico detectado: {article_data.get('titulo', 'Sem título')}")
                    
                    existing_id = self._get_existing_article_id(article_data)
                    if existing_id:
                        logger.info(f"💡 Sugestão: Atualize o artigo existente ID {existing_id} ou use allow_duplicates=True")
                    
                    raise ValueError("Conteúdo idêntico detectado - use allow_duplicates=True para forçar")
                
                logger.info(f"✅ Novo artigo para produto existente: {produto_nome}")
            
            # Log informativo sobre produtos com múltiplos artigos
            if self._count_articles_for_product(produto_nome) > 0:
                count = self._count_articles_for_product(produto_nome) + 1
                logger.info(f"📚 Este será o {count}º artigo para o produto: {produto_nome}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Preparar dados
                tags_json = json.dumps(article_data.get('tags', []))
                generation_json = json.dumps(article_data)
                
                # Calcular hash para verificação de duplicatas
                content_hash = self._calculate_content_hash(article_data)
                
                cursor.execute("""
                    INSERT INTO articles (
                        titulo, slug, meta_descricao, conteudo, tags,
                        produto_id, produto_nome, tipo_produto, tom_usado, status,
                        score_seo, generation_data, content_hash, wp_category, produto_original
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data.get('titulo', ''),
                    article_data.get('slug', ''),
                    article_data.get('meta_descricao', ''),
                    article_data.get('conteudo', ''),
                    tags_json,
                    article_data.get('produto_id'),
                    article_data.get('produto_nome'),
                    article_data.get('tipo_produto'),
                    article_data.get('tom_usado'),
                    article_data.get('status', 'pendente'),
                    article_data.get('seo_score', 0),
                    generation_json,
                    content_hash,
                    article_data.get('wp_category'),
                    article_data.get('produto_original')
                ))
                
                article_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"✅ Artigo salvo para revisão: ID {article_id} - {article_data.get('titulo', 'Sem título')}")
                return article_id
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar artigo para revisão: {e}")
            raise
    
    def _is_duplicate_article(self, article_data: Dict[str, Any]) -> bool:
        """
        Verifica se artigo é duplicata antes de salvar
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            True se é duplicata
        """
        try:
            content_hash = self._calculate_content_hash(article_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar por hash
                cursor.execute("SELECT id FROM articles WHERE content_hash = ?", (content_hash,))
                if cursor.fetchone():
                    return True
                
                # Verificar por título similar (caso hash falhe)
                titulo = article_data.get('titulo', '')
                if titulo:
                    cursor.execute("SELECT id FROM articles WHERE titulo = ?", (titulo,))
                    if cursor.fetchone():
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na verificação de duplicata: {e}")
            return False
    
    def _calculate_content_hash(self, article_data: Dict[str, Any]) -> str:
        """
        Calcula hash único do conteúdo do artigo
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            Hash MD5 do conteúdo
        """
        import hashlib
        
        # Combinar título + início do conteúdo para hash único
        titulo = article_data.get('titulo', '')
        conteudo = article_data.get('conteudo', '')
        
        content_for_hash = f"{titulo}{conteudo[:200] if conteudo else ''}"
        return hashlib.md5(content_for_hash.encode('utf-8')).hexdigest()
    
    def _is_exact_duplicate(self, article_data: Dict[str, Any]) -> bool:
        """
        Verifica se artigo é duplicata EXATA (mesmo conteúdo) antes de salvar
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            True se é duplicata exata
        """
        try:
            content_hash = self._calculate_content_hash(article_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar apenas por hash de conteúdo (conteúdo idêntico)
                cursor.execute("SELECT id FROM articles WHERE content_hash = ?", (content_hash,))
                return cursor.fetchone() is not None
                
        except Exception as e:
            logger.error(f"❌ Erro na verificação de duplicata exata: {e}")
            return False
    
    def _count_articles_for_product(self, produto_nome: str) -> int:
        """
        Conta quantos artigos existem para um produto específico
        
        Args:
            produto_nome: Nome do produto
            
        Returns:
            Número de artigos existentes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM articles WHERE produto_nome = ?", (produto_nome,))
                count = cursor.fetchone()[0]
                return count
                
        except Exception as e:
            logger.error(f"❌ Erro ao contar artigos do produto: {e}")
            return 0

    def _get_existing_article_id(self, article_data: Dict[str, Any]) -> Optional[int]:
        """
        Busca ID de artigo existente baseado no hash de conteúdo
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            ID do artigo existente ou None
        """
        try:
            content_hash = self._calculate_content_hash(article_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar por hash de conteúdo (duplicata exata)
                cursor.execute("SELECT id FROM articles WHERE content_hash = ?", (content_hash,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar artigo existente: {e}")
            return None
    
    def list_articles(self, status: str = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista artigos para revisão
        
        Args:
            status: Filtrar por status (pendente, aprovado, rejeitado)
            limit: Número máximo de artigos
            offset: Offset para paginação
            
        Returns:
            Lista de artigos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = """
                    SELECT id, titulo, slug, meta_descricao, conteudo, tags, produto_nome,
                           status, data_criacao, data_revisao, comentario_revisor,
                           score_seo, tipo_produto, tom_usado
                    FROM articles
                """
                params = []
                
                if status:
                    query += " WHERE status = ?"
                    params.append(status)
                
                query += " ORDER BY data_criacao DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                articles = []
                for row in rows:
                    article = dict(row)
                    # Handle tags field safely
                    if article['tags']:
                        try:
                            # Try to parse as JSON first
                            article['tags'] = json.loads(article['tags'])
                        except (json.JSONDecodeError, TypeError):
                            # If not JSON, treat as comma-separated string
                            if isinstance(article['tags'], str):
                                article['tags'] = [tag.strip() for tag in article['tags'].split(',') if tag.strip()]
                            else:
                                article['tags'] = []
                    else:
                        article['tags'] = []
                    articles.append(article)
                
                logger.debug(f"📋 Listados {len(articles)} artigos (status: {status})")
                return articles
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar artigos: {e}")
            return []
    
    def get_article(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Retorna artigo completo por ID
        
        Args:
            article_id: ID do artigo
            
        Returns:
            Dados completos do artigo ou None se não encontrado
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"⚠️ Artigo não encontrado: ID {article_id}")
                    return None
                
                article = dict(row)
                # Handle tags field safely
                if article['tags']:
                    try:
                        # Try to parse as JSON first
                        article['tags'] = json.loads(article['tags'])
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, treat as comma-separated string
                        if isinstance(article['tags'], str):
                            article['tags'] = [tag.strip() for tag in article['tags'].split(',') if tag.strip()]
                        else:
                            article['tags'] = []
                else:
                    article['tags'] = []
                
                # Tentar carregar dados de geração
                try:
                    if article['generation_data']:
                        article['generation_info'] = json.loads(article['generation_data'])
                except:
                    article['generation_info'] = {}
                
                logger.debug(f"📄 Artigo carregado: ID {article_id}")
                return article
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar artigo {article_id}: {e}")
            return None
    
    def update_article(self, article_id: int, updates: Dict[str, Any], revisor: str = "Sistema") -> bool:
        """
        Atualiza dados do artigo
        
        Args:
            article_id: ID do artigo
            updates: Campos a atualizar
            revisor: Nome do revisor
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            # Campos permitidos para atualização
            allowed_fields = [
                'titulo', 'slug', 'meta_descricao', 'conteudo', 'tags',
                'comentario_revisor', 'status'
            ]
            
            # Filtrar apenas campos permitidos
            valid_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not valid_updates:
                logger.warning(f"⚠️ Nenhum campo válido para atualizar no artigo {article_id}")
                return False
            
            # Converter tags para JSON se necessário
            if 'tags' in valid_updates:
                if isinstance(valid_updates['tags'], list):
                    valid_updates['tags'] = json.dumps(valid_updates['tags'])
            
            # Montar query dinâmica
            set_clause = ", ".join([f"{field} = ?" for field in valid_updates.keys()])
            values = list(valid_updates.values())
            values.extend([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), revisor, article_id])
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = f"""
                    UPDATE articles 
                    SET {set_clause}, data_revisao = ?, revisor_nome = ?
                    WHERE id = ?
                """
                
                cursor.execute(query, values)
                
                if cursor.rowcount == 0:
                    logger.warning(f"⚠️ Artigo não encontrado para atualização: ID {article_id}")
                    return False
                
                conn.commit()
                
                # REGISTRAR FEEDBACK NO SISTEMA DE APRENDIZADO (se status mudou)
                if 'status' in valid_updates:
                    try:
                        # Buscar dados do artigo atualizado
                        article = self.get_article(article_id)
                        if article:
                            new_status = valid_updates['status']
                            
                            # Só registrar feedback para mudanças de status significativas
                            if new_status in ['aprovado', 'rejeitado']:
                                product_category = self._extract_category_from_tipo(article.get('tipo_produto', 'produto_generico'))
                                product_brand = self._extract_brand_from_name(article.get('produto_nome', ''))
                                
                                # Calcular qualidade baseada no comentário e dados do artigo
                                quality_score = self._calculate_article_quality(article, valid_updates.get('comentario_revisor', ''))
                                
                                # Determinar ação
                                action = 'approved' if new_status == 'aprovado' else 'rejected'
                                
                                # Registrar feedback
                                self.priority_manager.record_feedback(
                                    product_name=article.get('produto_nome', ''),
                                    product_category=product_category,
                                    action=action,
                                    product_brand=product_brand,
                                    user_comments=valid_updates.get('comentario_revisor', ''),
                                    quality_score=quality_score
                                )
                                
                                logger.info(f"🧠 Feedback registrado: {article.get('produto_nome', '')} → {action} (Qualidade: {quality_score:.1f})")
                                
                    except Exception as e:
                        logger.error(f"❌ Erro ao registrar feedback: {e}")
                
                logger.info(f"✅ Artigo atualizado: ID {article_id} por {revisor}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar artigo {article_id}: {e}")
            return False
    
    def approve_article(self, article_id: int, revisor: str = "Sistema", comentario: str = "", 
                       wp_category: str = None, produto_original: str = None, 
                       skip_availability_check: bool = False) -> bool:
        """
        Aprova artigo para publicação
        
        Args:
            article_id: ID do artigo
            revisor: Nome do revisor
            comentario: Comentário opcional
            wp_category: Categoria WordPress selecionada manualmente
            produto_original: Nome do produto original associado
            skip_availability_check: Pular verificação de disponibilidade
            
        Returns:
            True se aprovado com sucesso
        """
        # Verificar disponibilidade do produto antes de aprovar (se não foi pulado)
        if not skip_availability_check:
            article = self.get_article(article_id)
            if article and article.get('generation_data'):
                try:
                    generation_data = json.loads(article['generation_data'])
                    produto_data = generation_data.get('produto', {})
                    
                    if produto_data.get('url'):
                        logger.info(f"🔍 Verificando disponibilidade antes de aprovar artigo {article_id}")
                        availability_result = self.availability_checker.check_product_availability(produto_data)
                        
                        if not availability_result.get('disponivel', False):
                            motivo = availability_result.get('motivo', 'Motivo desconhecido')
                            logger.warning(f"⚠️ Produto indisponível, rejeitando artigo {article_id}: {motivo}")
                            
                            # Rejeitar automaticamente por indisponibilidade
                            return self.reject_article(
                                article_id, 
                                f"Produto indisponível: {motivo}", 
                                "Sistema de Verificação"
                            )
                        else:
                            logger.info(f"✅ Produto disponível, prosseguindo com aprovação do artigo {article_id}")
                    else:
                        logger.info(f"⚠️ Artigo {article_id} não possui URL do produto, pulando verificação de disponibilidade")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao verificar disponibilidade para artigo {article_id}: {e}")
                    logger.debug(f"Generation data: {article.get('generation_data')}")
                    # Continuar com aprovação mesmo com erro na verificação
            else:
                logger.info(f"⚠️ Artigo {article_id} não possui dados de geração, pulando verificação de disponibilidade")
        
        updates = {
            'status': 'aprovado',
            'comentario_revisor': comentario
        }
        
        # Adicionar categoria WordPress se especificada
        if wp_category:
            updates['wp_category'] = wp_category
            
        # Adicionar produto original se especificado
        if produto_original:
            updates['produto_original'] = produto_original
        
        success = self.update_article(article_id, updates, revisor)
        
        if success:
            logger.info(f"✅ Artigo aprovado: ID {article_id} por {revisor}")
            if wp_category:
                logger.info(f"📂 Categoria WP selecionada: {wp_category}")
            if produto_original:
                logger.info(f"🔗 Produto associado: {produto_original}")
        
        return success
    
    def reject_article(self, article_id: int, motivo: str, revisor: str = "Sistema") -> bool:
        """
        Rejeita artigo e registra aprendizado automaticamente
        
        Args:
            article_id: ID do artigo
            motivo: Motivo da rejeição
            revisor: Nome do revisor
            
        Returns:
            True se rejeitado com sucesso
        """
        updates = {
            'status': 'rejeitado',
            'comentario_revisor': motivo
        }
        
        success = self.update_article(article_id, updates, revisor)
        
        if success:
            logger.info(f"❌ Artigo rejeitado: ID {article_id} por {revisor} - {motivo}")
            
            # 🧠 REGISTRAR APRENDIZADO AUTOMÁTICO
            try:
                from src.intelligence.learning_manager import LearningManager
                learning_manager = LearningManager()
                
                learning_success = learning_manager.handle_article_rejection(
                    article_id=article_id,
                    rejection_reason=motivo,
                    reviewer=revisor
                )
                
                if learning_success:
                    logger.info(f"🧠 Aprendizado registrado automaticamente para artigo {article_id}")
                else:
                    logger.warning(f"⚠️ Falha ao registrar aprendizado para artigo {article_id}")
                    
            except Exception as learning_error:
                logger.error(f"❌ Erro no sistema de aprendizado: {learning_error}")
                # Não falhar a rejeição por erro no aprendizado
        
        return success
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema de revisão
        
        Returns:
            Estatísticas gerais
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contadores por status
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM articles 
                    GROUP BY status
                """)
                status_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Total geral
                cursor.execute("SELECT COUNT(*) FROM articles")
                total = cursor.fetchone()[0]
                
                # Artigos recentes (últimos 7 dias)
                cursor.execute("""
                    SELECT COUNT(*) FROM articles 
                    WHERE data_criacao >= datetime('now', '-7 days')
                """)
                recent = cursor.fetchone()[0]
                
                # Artigos por tipo de produto
                cursor.execute("""
                    SELECT tipo_produto, COUNT(*) as count 
                    FROM articles 
                    WHERE tipo_produto IS NOT NULL 
                    GROUP BY tipo_produto 
                    ORDER BY count DESC
                """)
                product_types = {row[0]: row[1] for row in cursor.fetchall()}
                
                stats = {
                    'total_artigos': total,
                    'pendentes': status_counts.get('pendente', 0),
                    'aprovados': status_counts.get('aprovado', 0),
                    'rejeitados': status_counts.get('rejeitado', 0),
                    'recentes_7_dias': recent,
                    'por_tipo_produto': product_types,
                    'status_counts': status_counts
                }
                
                logger.debug("📊 Estatísticas de revisão calculadas")
                return stats
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {
                'total_artigos': 0,
                'pendentes': 0,
                'aprovados': 0,
                'rejeitados': 0,
                'recentes_7_dias': 0,
                'por_tipo_produto': {},
                'status_counts': {}
            }
    
    def get_approved_articles_for_publishing(self) -> List[Dict[str, Any]]:
        """
        Retorna artigos aprovados prontos para publicação
        
        Returns:
            Lista de artigos aprovados
        """
        return self.list_articles(status='aprovado', limit=100)
    
    def mark_as_published(self, article_id: int, publish_url: str = None) -> bool:
        """
        Marca artigo como publicado
        
        Args:
            article_id: ID do artigo
            publish_url: URL onde foi publicado
            
        Returns:
            True se marcado com sucesso
        """
        updates = {
            'status': 'publicado'
        }
        
        if publish_url:
            updates['comentario_revisor'] = f"Publicado em: {publish_url}"
        
        success = self.update_article(article_id, updates, "Publisher")
        
        if success:
            logger.info(f"🚀 Artigo marcado como publicado: ID {article_id}")
        
        return success
    
    def delete_article(self, article_id: int, revisor: str = "Sistema") -> bool:
        """
        Remove artigo do sistema
        
        Args:
            article_id: ID do artigo
            revisor: Nome do revisor
            
        Returns:
            True se removido com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
                
                if cursor.rowcount == 0:
                    logger.warning(f"⚠️ Artigo não encontrado para remoção: ID {article_id}")
                    return False
                
                conn.commit()
                logger.info(f"🗑️ Artigo removido: ID {article_id} por {revisor}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover artigo {article_id}: {e}")
            return False
    
    def cleanup_old_articles(self, days: int = 90) -> int:
        """
        Remove artigos antigos do sistema
        
        Args:
            days: Artigos mais antigos que X dias
            
        Returns:
            Número de artigos removidos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM articles 
                    WHERE data_criacao < datetime('now', '-{} days')
                    AND status IN ('rejeitado', 'publicado')
                """.format(days))
                
                removed_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"🧹 Limpeza concluída: {removed_count} artigos antigos removidos")
                return removed_count
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de artigos antigos: {e}")
            return 0
    
    def _extract_category_from_tipo(self, tipo_produto: str) -> str:
        """Extrai categoria padrão do tipo de produto"""
        category_mapping = {
            'impressora': 'impressora',
            'multifuncional': 'multifuncional', 
            'toner': 'toner',
            'scanner': 'scanner',
            'papel': 'papel',
            'copiadora': 'copiadora',
            'suprimento': 'suprimento'
        }
        return category_mapping.get(tipo_produto.lower() if tipo_produto else 'produto_generico', 'produto_generico')
    
    def _extract_brand_from_name(self, product_name: str) -> str:
        """Extrai marca do nome do produto"""
        brands = ['HP', 'Canon', 'Brother', 'Epson', 'Samsung', 'Xerox', 'Ricoh', 'Lexmark']
        
        for brand in brands:
            if brand.lower() in product_name.lower():
                return brand
        
        return 'Genérica'
    
    def _calculate_article_quality(self, article: Dict[str, Any], comentario: str) -> float:
        """Calcula qualidade do artigo baseado em critérios"""
        quality_score = 5.0  # Base média
        
        try:
            # Fatores de qualidade
            titulo_len = len(article.get('titulo', ''))
            conteudo_len = len(article.get('conteudo', ''))
            meta_len = len(article.get('meta_descricao', ''))
            
            # Título otimizado (30-60 chars)
            if 30 <= titulo_len <= 60:
                quality_score += 1.0
            elif titulo_len > 60:
                quality_score -= 0.5
            
            # Conteúdo substantivo (>500 chars)
            if conteudo_len > 1500:
                quality_score += 1.5
            elif conteudo_len > 500:
                quality_score += 0.5
            else:
                quality_score -= 1.0
            
            # Meta description otimizada (120-155 chars)
            if 120 <= meta_len <= 155:
                quality_score += 1.0
            elif meta_len > 155:
                quality_score -= 0.5
            
            # Analisar comentário do revisor
            if comentario:
                positive_words = ['bom', 'ótimo', 'excelente', 'aprovado', 'qualidade']
                negative_words = ['ruim', 'problema', 'erro', 'inadequado', 'falta']
                
                comentario_lower = comentario.lower()
                if any(word in comentario_lower for word in positive_words):
                    quality_score += 0.5
                elif any(word in comentario_lower for word in negative_words):
                    quality_score -= 1.0
            
            # Garantir range válido (0-10)
            quality_score = max(0.0, min(10.0, quality_score))
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular qualidade: {e}")
            quality_score = 5.0
        
        return quality_score

    def close(self):
        """Fecha recursos do review manager"""
        try:
            self.availability_checker.close()
            logger.debug("🔒 Review Manager recursos fechados")
        except:
            pass
 
    def update_or_create_article(self, article_data: Dict[str, Any], force_update: bool = False) -> Tuple[int, bool]:
        """
        Atualiza artigo existente ou cria um novo se não existir
        
        Args:
            article_data: Dados do artigo
            force_update: Se True, força atualização mesmo se rejeitado
            
        Returns:
            Tupla (article_id, was_updated)
        """
        try:
            # Verificar se artigo já existe
            existing_id = self._get_existing_article_id(article_data)
            
            if existing_id:
                # Artigo existe - verificar se pode ser atualizado
                existing_article = self.get_article(existing_id)
                
                if existing_article:
                    status = existing_article.get('status', '')
                    
                    # Só atualizar se não estiver rejeitado ou se for forçado
                    if status != 'rejeitado' or force_update:
                        logger.info(f"🔄 Atualizando artigo existente ID {existing_id}")
                        
                        # Preparar dados para atualização
                        update_data = {
                            'titulo': article_data.get('titulo', ''),
                            'slug': article_data.get('slug', ''),
                            'meta_descricao': article_data.get('meta_descricao', ''),
                            'conteudo': article_data.get('conteudo', ''),
                            'tags': article_data.get('tags', [])
                        }
                        
                        # Atualizar artigo
                        if self.update_article(existing_id, update_data):
                            logger.info(f"✅ Artigo ID {existing_id} atualizado com sucesso")
                            return existing_id, True
                        else:
                            logger.error(f"❌ Falha ao atualizar artigo ID {existing_id}")
                            raise Exception("Falha ao atualizar artigo existente")
                    else:
                        logger.warning(f"⚠️ Artigo ID {existing_id} foi rejeitado - use force_update=True para forçar atualização")
                        raise ValueError(f"Artigo rejeitado (ID {existing_id}) - não será atualizado automaticamente")
            
            # Artigo não existe - criar novo
            logger.info(f"🆕 Criando novo artigo: {article_data.get('titulo', 'Sem título')}")
            article_id = self.save_article_for_review(article_data, allow_duplicates=True)
            return article_id, False
            
        except Exception as e:
            logger.error(f"❌ Erro em update_or_create_article: {e}")
            raise
 
 
 
 