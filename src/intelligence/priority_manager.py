#!/usr/bin/env python3
"""
Sistema de Aprendizado e Priorização Inteligente
Aprende com base em aprovações/reprovações para otimizar futuras gerações
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriorityManager:
    """
    Gerencia prioridades de produtos/categorias baseado em feedback histórico
    """
    
    def __init__(self, db_path: str = "data/priority_intelligence.db"):
        """
        Inicializa o sistema de aprendizado
        
        Args:
            db_path: Caminho para o banco de dados de inteligência
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Configurações de aprendizado
        self.config = {
            'approval_bonus': 10,      # Pontos por aprovação
            'rejection_penalty': -15,  # Penalidade por reprovação
            'decay_factor': 0.95,      # Decaimento temporal (95% por semana)
            'min_score': -100,         # Pontuação mínima
            'max_score': 100,          # Pontuação máxima
            'learning_window_days': 90 # Janela de aprendizado (90 dias)
        }
        
        self._initialize_database()
        logger.info("🧠 Priority Manager inicializado - Sistema de Aprendizado Ativo")
    
    def _initialize_database(self):
        """Inicializa as tabelas do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    -- Tabela de feedback de artigos
                    CREATE TABLE IF NOT EXISTS article_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        product_category TEXT NOT NULL,
                        product_brand TEXT,
                        action TEXT NOT NULL, -- 'approved', 'rejected', 'edited'
                        feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_comments TEXT,
                        article_quality_score REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Tabela de prioridades calculadas
                    CREATE TABLE IF NOT EXISTS priority_scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        product_category TEXT NOT NULL,
                        product_brand TEXT,
                        priority_score REAL DEFAULT 0.0,
                        approval_count INTEGER DEFAULT 0,
                        rejection_count INTEGER DEFAULT 0,
                        total_generations INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(product_name, product_category)
                    );
                    
                    -- Tabela de tendências de categoria
                    CREATE TABLE IF NOT EXISTS category_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL UNIQUE,
                        trend_score REAL DEFAULT 0.0,
                        weekly_performance REAL DEFAULT 0.0,
                        monthly_performance REAL DEFAULT 0.0,
                        last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Índices para performance
                    CREATE INDEX IF NOT EXISTS idx_feedback_product ON article_feedback(product_name);
                    CREATE INDEX IF NOT EXISTS idx_feedback_category ON article_feedback(product_category);
                    CREATE INDEX IF NOT EXISTS idx_feedback_date ON article_feedback(feedback_date);
                    CREATE INDEX IF NOT EXISTS idx_priority_category ON priority_scores(product_category);
                    CREATE INDEX IF NOT EXISTS idx_priority_score ON priority_scores(priority_score DESC);
                """)
                
                logger.info("✅ Banco de dados de inteligência inicializado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def record_feedback(self, product_name: str, product_category: str, 
                       action: str, product_brand: str = None, 
                       user_comments: str = None, quality_score: float = 0.0) -> bool:
        """
        Registra feedback de aprovação/reprovação
        
        Args:
            product_name: Nome do produto
            product_category: Categoria do produto
            action: 'approved', 'rejected', 'edited'
            product_brand: Marca do produto (opcional)
            user_comments: Comentários do usuário (opcional)
            quality_score: Pontuação de qualidade do artigo (0-10)
            
        Returns:
            True se registrado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Registrar feedback
                conn.execute("""
                    INSERT INTO article_feedback 
                    (product_name, product_category, product_brand, action, 
                     user_comments, article_quality_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_name, product_category, product_brand, action, 
                      user_comments, quality_score))
                
                # Atualizar ou criar prioridade
                self._update_priority_score(conn, product_name, product_category, 
                                          product_brand, action)
                
                # Atualizar tendências de categoria
                self._update_category_trends(conn, product_category, action)
                
                logger.info(f"📊 Feedback registrado: {product_name} → {action}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar feedback: {e}")
            return False
    
    def _update_priority_score(self, conn: sqlite3.Connection, product_name: str, 
                              product_category: str, product_brand: str, action: str):
        """Atualiza pontuação de prioridade do produto"""
        
        # Verificar se produto já existe
        cursor = conn.execute("""
            SELECT priority_score, approval_count, rejection_count, total_generations
            FROM priority_scores 
            WHERE product_name = ? AND product_category = ?
        """, (product_name, product_category))
        
        result = cursor.fetchone()
        
        if result:
            # Produto existe - atualizar
            current_score, approvals, rejections, total = result
            
            # Calcular nova pontuação
            if action == 'approved':
                new_score = min(current_score + self.config['approval_bonus'], 
                              self.config['max_score'])
                approvals += 1
            elif action == 'rejected':
                new_score = max(current_score + self.config['rejection_penalty'], 
                              self.config['min_score'])
                rejections += 1
            else:  # 'edited'
                new_score = current_score + (self.config['approval_bonus'] * 0.5)
                approvals += 0.5  # Conta como meia aprovação
            
            total += 1
            success_rate = approvals / total if total > 0 else 0.0
            
            conn.execute("""
                UPDATE priority_scores 
                SET priority_score = ?, approval_count = ?, rejection_count = ?, 
                    total_generations = ?, success_rate = ?, last_updated = CURRENT_TIMESTAMP
                WHERE product_name = ? AND product_category = ?
            """, (new_score, approvals, rejections, total, success_rate, 
                  product_name, product_category))
            
        else:
            # Produto novo - criar entrada
            if action == 'approved':
                initial_score = self.config['approval_bonus']
                approvals, rejections = 1, 0
            elif action == 'rejected':
                initial_score = self.config['rejection_penalty']
                approvals, rejections = 0, 1
            else:  # 'edited'
                initial_score = self.config['approval_bonus'] * 0.5
                approvals, rejections = 0.5, 0
            
            success_rate = approvals / 1.0
            
            conn.execute("""
                INSERT INTO priority_scores 
                (product_name, product_category, product_brand, priority_score,
                 approval_count, rejection_count, total_generations, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (product_name, product_category, product_brand, initial_score,
                  approvals, rejections, 1, success_rate))
    
    def _update_category_trends(self, conn: sqlite3.Connection, category: str, action: str):
        """Atualiza tendências da categoria"""
        
        # Calcular performance da categoria na última semana
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        cursor = conn.execute("""
            SELECT 
                SUM(CASE WHEN action = 'approved' THEN 1 ELSE 0 END) as approvals,
                SUM(CASE WHEN action = 'rejected' THEN 1 ELSE 0 END) as rejections,
                COUNT(*) as total
            FROM article_feedback 
            WHERE product_category = ? AND feedback_date >= ?
        """, (category, week_ago))
        
        week_stats = cursor.fetchone()
        weekly_performance = 0.0
        
        if week_stats and week_stats[2] > 0:  # Total > 0
            weekly_performance = week_stats[0] / week_stats[2]  # % de aprovações
        
        # Calcular performance mensal
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        cursor = conn.execute("""
            SELECT 
                SUM(CASE WHEN action = 'approved' THEN 1 ELSE 0 END) as approvals,
                COUNT(*) as total
            FROM article_feedback 
            WHERE product_category = ? AND feedback_date >= ?
        """, (category, month_ago))
        
        month_stats = cursor.fetchone()
        monthly_performance = 0.0
        
        if month_stats and month_stats[1] > 0:
            monthly_performance = month_stats[0] / month_stats[1]
        
        # Calcular trend score (média ponderada: 70% mensal, 30% semanal)
        trend_score = (monthly_performance * 0.7) + (weekly_performance * 0.3)
        
        # Atualizar ou inserir
        conn.execute("""
            INSERT OR REPLACE INTO category_trends 
            (category, trend_score, weekly_performance, monthly_performance, last_calculated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (category, trend_score, weekly_performance, monthly_performance))
    
    def get_prioritized_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna lista de produtos priorizados para geração
        
        Args:
            limit: Número máximo de produtos a retornar
            
        Returns:
            Lista de produtos ordenados por prioridade
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT 
                        ps.product_name,
                        ps.product_category,
                        ps.product_brand,
                        ps.priority_score,
                        ps.success_rate,
                        ps.total_generations,
                        ct.trend_score,
                        ct.weekly_performance,
                        -- Calcular prioridade final
                        (ps.priority_score * 0.6 + 
                         COALESCE(ct.trend_score, 0.5) * 100 * 0.4) as final_priority
                    FROM priority_scores ps
                    LEFT JOIN category_trends ct ON ps.product_category = ct.category
                    ORDER BY final_priority DESC, ps.success_rate DESC
                    LIMIT ?
                """, (limit,))
                
                products = [dict(row) for row in cursor.fetchall()]
                
                logger.info(f"📊 {len(products)} produtos priorizados retornados")
                return products
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter produtos priorizados: {e}")
            return []
    
    def get_category_performance(self) -> Dict[str, Dict[str, float]]:
        """
        Retorna performance de todas as categorias
        
        Returns:
            Dicionário com performance por categoria
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT 
                        category,
                        trend_score,
                        weekly_performance,
                        monthly_performance
                    FROM category_trends
                    ORDER BY trend_score DESC
                """)
                
                performance = {}
                for row in cursor.fetchall():
                    performance[row['category']] = {
                        'trend_score': row['trend_score'],
                        'weekly_performance': row['weekly_performance'],
                        'monthly_performance': row['monthly_performance']
                    }
                
                return performance
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter performance de categorias: {e}")
            return {}
    
    def apply_time_decay(self) -> bool:
        """
        Aplica decaimento temporal às pontuações (executar semanalmente)
        
        Returns:
            True se aplicado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Aplicar decaimento a pontuações antigas
                conn.execute("""
                    UPDATE priority_scores 
                    SET priority_score = priority_score * ?
                    WHERE last_updated < datetime('now', '-7 days')
                """, (self.config['decay_factor'],))
                
                # Limpar dados muito antigos
                old_date = (datetime.now() - timedelta(days=self.config['learning_window_days'])).isoformat()
                
                conn.execute("""
                    DELETE FROM article_feedback 
                    WHERE feedback_date < ?
                """, (old_date,))
                
                affected_rows = conn.total_changes
                logger.info(f"✅ Decaimento temporal aplicado: {affected_rows} registros afetados")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar decaimento temporal: {e}")
            return False
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema de aprendizado
        
        Returns:
            Dicionário com estatísticas completas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas gerais
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_feedback,
                        SUM(CASE WHEN action = 'approved' THEN 1 ELSE 0 END) as total_approvals,
                        SUM(CASE WHEN action = 'rejected' THEN 1 ELSE 0 END) as total_rejections,
                        AVG(article_quality_score) as avg_quality
                    FROM article_feedback
                """)
                general_stats = cursor.fetchone()
                
                # Top produtos
                cursor = conn.execute("""
                    SELECT product_name, priority_score, success_rate
                    FROM priority_scores
                    ORDER BY priority_score DESC
                    LIMIT 5
                """)
                top_products = cursor.fetchall()
                
                # Categorias mais bem-sucedidas
                cursor = conn.execute("""
                    SELECT category, trend_score, monthly_performance
                    FROM category_trends
                    ORDER BY trend_score DESC
                    LIMIT 5
                """)
                top_categories = cursor.fetchall()
                
                return {
                    'total_feedback': general_stats[0] if general_stats else 0,
                    'total_approvals': general_stats[1] if general_stats else 0,
                    'total_rejections': general_stats[2] if general_stats else 0,
                    'avg_quality': round(general_stats[3], 2) if general_stats and general_stats[3] else 0.0,
                    'overall_success_rate': round(general_stats[1] / general_stats[0] * 100, 1) if general_stats and general_stats[0] > 0 else 0.0,
                    'top_products': [{'name': p[0], 'score': p[1], 'success_rate': p[2]} for p in top_products],
                    'top_categories': [{'name': c[0], 'trend': c[1], 'performance': c[2]} for c in top_categories],
                    'learning_config': self.config
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def reset_learning_data(self, confirm: bool = False) -> bool:
        """
        Reseta todos os dados de aprendizado (USE COM CUIDADO)
        
        Args:
            confirm: Confirmação obrigatória
            
        Returns:
            True se resetado com sucesso
        """
        if not confirm:
            logger.warning("⚠️ Reset cancelado: confirmação necessária")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    DELETE FROM article_feedback;
                    DELETE FROM priority_scores;
                    DELETE FROM category_trends;
                """)
                
                logger.warning("🗑️ Todos os dados de aprendizado foram resetados")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao resetar dados: {e}")
            return False 