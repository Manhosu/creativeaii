"""
Review Manager
Sistema de revisão humana de artigos antes da publicação
"""

import os
import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from pathlib import Path

class ReviewManager:
    """Gerenciador de revisão de artigos"""
    
    def __init__(self, db_path: str = "data/review_articles.db"):
        """Inicializa o gerenciador de revisão"""
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
        
        # Configurar logging
        logger.add(
            "logs/review.log",
            rotation="1 week",
            retention="30 days",
            level="INFO",
            format="{time} | {level} | {message}"
        )
        
        logger.info("📝 Review Manager inicializado")
    
    def ensure_data_directory(self):
        """Garante que o diretório de dados existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Inicializa banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        slug TEXT NOT NULL,
                        meta_descricao TEXT,
                        conteudo TEXT NOT NULL,
                        tags TEXT,  -- JSON array
                        produto_id TEXT,
                        produto_nome TEXT,
                        status TEXT DEFAULT 'pendente',  -- pendente, aprovado, rejeitado
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_revisao TIMESTAMP,
                        comentario_revisor TEXT,
                        revisor_nome TEXT,
                        score_seo INTEGER DEFAULT 0,
                        tipo_produto TEXT,
                        tom_usado TEXT,
                        generation_data TEXT  -- JSON com dados completos da geração
                    )
                """)
                
                # Criar índices para performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON articles(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_data_criacao ON articles(data_criacao)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_produto_id ON articles(produto_id)")
                
                conn.commit()
                logger.info("✅ Banco de dados de revisão inicializado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def save_article_for_review(self, article_data: Dict[str, Any]) -> int:
        """
        Salva artigo gerado para revisão
        
        Args:
            article_data: Dados do artigo gerado pelo Generator
            
        Returns:
            ID do artigo no sistema de revisão
        """
        try:
            # VERIFICAR DUPLICATAS ANTES DE SALVAR
            if self._is_duplicate_article(article_data):
                logger.warning(f"🚫 Artigo duplicado detectado: {article_data.get('titulo', 'Sem título')}")
                raise ValueError("Artigo duplicado - não será salvo")
            
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
                        produto_id, produto_nome, tipo_produto, tom_usado,
                        score_seo, generation_data, content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    article_data.get('seo_score', 0),
                    generation_json,
                    content_hash
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
                    article['tags'] = json.loads(article['tags']) if article['tags'] else []
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
                article['tags'] = json.loads(article['tags']) if article['tags'] else []
                
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
                logger.info(f"✅ Artigo atualizado: ID {article_id} por {revisor}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar artigo {article_id}: {e}")
            return False
    
    def approve_article(self, article_id: int, revisor: str = "Sistema", comentario: str = "") -> bool:
        """
        Aprova artigo para publicação
        
        Args:
            article_id: ID do artigo
            revisor: Nome do revisor
            comentario: Comentário opcional
            
        Returns:
            True se aprovado com sucesso
        """
        updates = {
            'status': 'aprovado',
            'comentario_revisor': comentario
        }
        
        success = self.update_article(article_id, updates, revisor)
        
        if success:
            logger.info(f"✅ Artigo aprovado: ID {article_id} por {revisor}")
        
        return success
    
    def reject_article(self, article_id: int, motivo: str, revisor: str = "Sistema") -> bool:
        """
        Rejeita artigo
        
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
 
 
 
 