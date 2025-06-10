#!/usr/bin/env python3
"""
Sistema de Monitoramento de Publicações
Detecta e avisa sobre publicações pendentes no WordPress
"""

import os
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublicationMonitor:
    """
    Monitora status de publicações e detecta problemas
    """
    
    def __init__(self, db_path: str = "data/publication_monitor.db"):
        """
        Inicializa o monitor de publicações
        
        Args:
            db_path: Caminho para o banco de dados de monitoramento
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Configurações WordPress
        self.wp_auto_publish = os.getenv('WP_AUTO_PUBLISH', 'false').lower() == 'true'
        self.wp_default_status = os.getenv('WP_DEFAULT_STATUS', 'draft')
        
        # Configurações de monitoramento
        self.config = {
            'check_interval_minutes': 30,  # Verificar a cada 30 minutos
            'pending_threshold_hours': 2,  # Alertar após 2 horas pendente
            'max_retry_attempts': 3,       # Máximo de tentativas
            'notification_cooldown_hours': 6  # Cooldown entre notificações
        }
        
        self._initialize_database()
        logger.info("📊 Publication Monitor inicializado")
    
    def _initialize_database(self):
        """Inicializa as tabelas do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    -- Tabela de status de publicações
                    CREATE TABLE IF NOT EXISTS publication_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        article_id INTEGER NOT NULL,
                        wp_post_id INTEGER,
                        title TEXT NOT NULL,
                        slug TEXT NOT NULL,
                        expected_status TEXT NOT NULL, -- 'publish', 'draft', 'pending'
                        actual_status TEXT,
                        wp_url TEXT,
                        publish_attempt_date TIMESTAMP,
                        last_check_date TIMESTAMP,
                        status_mismatch BOOLEAN DEFAULT FALSE,
                        retry_count INTEGER DEFAULT 0,
                        error_message TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Tabela de alertas/notificações
                    CREATE TABLE IF NOT EXISTS publication_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        article_id INTEGER NOT NULL,
                        alert_type TEXT NOT NULL, -- 'pending', 'failed', 'mismatch'
                        alert_message TEXT NOT NULL,
                        severity TEXT DEFAULT 'warning', -- 'info', 'warning', 'error'
                        notified BOOLEAN DEFAULT FALSE,
                        notification_date TIMESTAMP,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Tabela de configurações de publicação
                    CREATE TABLE IF NOT EXISTS publication_config_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        wp_auto_publish BOOLEAN,
                        wp_default_status TEXT,
                        config_check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        issues_found TEXT -- JSON com problemas encontrados
                    );
                    
                    -- Índices para performance
                    CREATE INDEX IF NOT EXISTS idx_article_id ON publication_status(article_id);
                    CREATE INDEX IF NOT EXISTS idx_wp_post_id ON publication_status(wp_post_id);
                    CREATE INDEX IF NOT EXISTS idx_status_mismatch ON publication_status(status_mismatch);
                    CREATE INDEX IF NOT EXISTS idx_alert_type ON publication_alerts(alert_type);
                    CREATE INDEX IF NOT EXISTS idx_resolved ON publication_alerts(resolved);
                """)
                
                logger.info("✅ Banco de dados de monitoramento inicializado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def check_wordpress_config(self) -> Dict[str, Any]:
        """
        Verifica configurações do WordPress para publicação automática
        
        Returns:
            Resultado da verificação de configuração
        """
        try:
            issues = []
            warnings = []
            
            # Verificar WP_AUTO_PUBLISH
            if not self.wp_auto_publish:
                issues.append("WP_AUTO_PUBLISH está desabilitado - artigos podem ficar como rascunho")
            
            # Verificar WP_DEFAULT_STATUS
            if self.wp_default_status.lower() != 'publish':
                if self.wp_default_status.lower() in ['draft', 'pending']:
                    warnings.append(f"WP_DEFAULT_STATUS='{self.wp_default_status}' - artigos precisarão de aprovação manual")
                else:
                    issues.append(f"WP_DEFAULT_STATUS='{self.wp_default_status}' é inválido")
            
            # Verificar variáveis de ambiente necessárias
            required_vars = ['WP_SITE_URL', 'WP_USERNAME', 'WP_PASSWORD']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                issues.append(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
            
            # Determinar status geral
            config_status = 'ok' if not issues else 'error' if issues else 'warning'
            
            result = {
                'status': config_status,
                'wp_auto_publish': self.wp_auto_publish,
                'wp_default_status': self.wp_default_status,
                'issues': issues,
                'warnings': warnings,
                'recommendation': self._get_config_recommendation(issues, warnings)
            }
            
            # Salvar log da verificação
            self._save_config_check(result)
            
            logger.info(f"🔍 Configuração WordPress: {config_status.upper()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar configuração WordPress: {e}")
            return {
                'status': 'error',
                'issues': [f'Erro na verificação: {str(e)}'],
                'warnings': [],
                'recommendation': 'Verificar logs para detalhes do erro'
            }
    
    def _get_config_recommendation(self, issues: List[str], warnings: List[str]) -> str:
        """Gera recomendação baseada nos problemas encontrados"""
        if not issues and not warnings:
            return "✅ Configuração ideal para publicação automática"
        
        recommendations = []
        
        if any('WP_AUTO_PUBLISH' in issue for issue in issues):
            recommendations.append("Definir WP_AUTO_PUBLISH=true no arquivo .env")
        
        if any('WP_DEFAULT_STATUS' in issue for issue in issues):
            recommendations.append("Definir WP_DEFAULT_STATUS=publish no arquivo .env")
        
        if any('Variáveis de ambiente' in issue for issue in issues):
            recommendations.append("Configurar credenciais WordPress no arquivo .env")
        
        if any('WP_DEFAULT_STATUS' in warning for warning in warnings):
            recommendations.append("Para publicação automática, usar WP_DEFAULT_STATUS=publish")
        
        return "; ".join(recommendations) if recommendations else "Verificar configurações WordPress"
    
    def _save_config_check(self, result: Dict[str, Any]):
        """Salva resultado da verificação de configuração"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO publication_config_log 
                    (wp_auto_publish, wp_default_status, issues_found)
                    VALUES (?, ?, ?)
                """, (
                    self.wp_auto_publish,
                    self.wp_default_status,
                    json.dumps({'issues': result['issues'], 'warnings': result['warnings']})
                ))
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar log de configuração: {e}")
    
    def register_publication_attempt(self, article_id: int, title: str, slug: str,
                                   expected_status: str = 'publish', wp_post_id: int = None,
                                   wp_url: str = None) -> bool:
        """
        Registra tentativa de publicação para monitoramento
        
        Args:
            article_id: ID do artigo
            title: Título do artigo
            slug: Slug do artigo
            expected_status: Status esperado ('publish', 'draft', 'pending')
            wp_post_id: ID do post no WordPress (se conhecido)
            wp_url: URL do post (se conhecido)
            
        Returns:
            True se registrado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Verificar se já existe registro
                cursor = conn.execute("""
                    SELECT id FROM publication_status 
                    WHERE article_id = ?
                """, (article_id,))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Atualizar registro existente
                    conn.execute("""
                        UPDATE publication_status 
                        SET title = ?, slug = ?, expected_status = ?, wp_post_id = ?,
                            wp_url = ?, publish_attempt_date = CURRENT_TIMESTAMP,
                            retry_count = retry_count + 1, updated_at = CURRENT_TIMESTAMP
                        WHERE article_id = ?
                    """, (title, slug, expected_status, wp_post_id, wp_url, article_id))
                else:
                    # Criar novo registro
                    conn.execute("""
                        INSERT INTO publication_status 
                        (article_id, title, slug, expected_status, wp_post_id, wp_url, publish_attempt_date)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (article_id, title, slug, expected_status, wp_post_id, wp_url))
                
                logger.info(f"📝 Publicação registrada para monitoramento: {title}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar publicação: {e}")
            return False
    
    def check_pending_publications(self) -> Dict[str, Any]:
        """
        Verifica publicações pendentes e gera alertas
        
        Returns:
            Relatório de publicações pendentes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Buscar publicações não resolvidas
                cursor = conn.execute("""
                    SELECT * FROM publication_status 
                    WHERE resolved = FALSE 
                    AND publish_attempt_date IS NOT NULL
                    ORDER BY publish_attempt_date DESC
                """)
                
                publications = [dict(row) for row in cursor.fetchall()]
                
                pending_count = 0
                failed_count = 0
                alerts_created = 0
                
                for pub in publications:
                    # Calcular tempo desde tentativa de publicação
                    attempt_time = datetime.fromisoformat(pub['publish_attempt_date'])
                    hours_since = (datetime.now() - attempt_time).total_seconds() / 3600
                    
                    # Verificar se precisa de alerta
                    if hours_since > self.config['pending_threshold_hours']:
                        alert_type = 'pending'
                        severity = 'warning'
                        
                        if pub['retry_count'] >= self.config['max_retry_attempts']:
                            alert_type = 'failed'
                            severity = 'error'
                            failed_count += 1
                        else:
                            pending_count += 1
                        
                        # Criar alerta se não existe
                        if self._create_alert_if_needed(pub['article_id'], alert_type, 
                                                      pub['title'], severity, hours_since):
                            alerts_created += 1
                
                # Buscar alertas ativos
                cursor = conn.execute("""
                    SELECT alert_type, COUNT(*) as count 
                    FROM publication_alerts 
                    WHERE resolved = FALSE 
                    GROUP BY alert_type
                """)
                
                active_alerts = {row['alert_type']: row['count'] for row in cursor.fetchall()}
                
                result = {
                    'total_monitored': len(publications),
                    'pending_publications': pending_count,
                    'failed_publications': failed_count,
                    'alerts_created': alerts_created,
                    'active_alerts': active_alerts,
                    'config_issues': self.check_wordpress_config(),
                    'recommendations': self._generate_recommendations(pending_count, failed_count, active_alerts)
                }
                
                logger.info(f"📊 Verificação concluída: {pending_count} pendentes, {failed_count} falharam")
                return result
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar publicações pendentes: {e}")
            return {
                'error': str(e),
                'total_monitored': 0,
                'pending_publications': 0,
                'failed_publications': 0
            }
    
    def _create_alert_if_needed(self, article_id: int, alert_type: str, 
                               title: str, severity: str, hours_pending: float) -> bool:
        """Cria alerta se necessário (evita spam)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Verificar se já existe alerta recente
                cooldown_hours = self.config['notification_cooldown_hours']
                cutoff_time = datetime.now() - timedelta(hours=cooldown_hours)
                
                cursor = conn.execute("""
                    SELECT id FROM publication_alerts 
                    WHERE article_id = ? AND alert_type = ? 
                    AND created_at > ? AND resolved = FALSE
                """, (article_id, alert_type, cutoff_time.isoformat()))
                
                if cursor.fetchone():
                    return False  # Alerta recente já existe
                
                # Criar novo alerta
                if alert_type == 'pending':
                    message = f"Artigo '{title}' está pendente há {hours_pending:.1f} horas"
                elif alert_type == 'failed':
                    message = f"Publicação de '{title}' falhou após múltiplas tentativas"
                else:
                    message = f"Problema com publicação de '{title}'"
                
                conn.execute("""
                    INSERT INTO publication_alerts 
                    (article_id, alert_type, alert_message, severity)
                    VALUES (?, ?, ?, ?)
                """, (article_id, alert_type, message, severity))
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar alerta: {e}")
            return False
    
    def _generate_recommendations(self, pending: int, failed: int, 
                                active_alerts: Dict[str, int]) -> List[str]:
        """Gera recomendações baseadas no status atual"""
        recommendations = []
        
        if pending > 0:
            recommendations.append(f"Verificar {pending} publicações pendentes no WordPress")
        
        if failed > 0:
            recommendations.append(f"Investigar {failed} publicações que falharam")
        
        if active_alerts.get('pending', 0) > 5:
            recommendations.append("Muitas publicações pendentes - verificar configuração WP_AUTO_PUBLISH")
        
        if active_alerts.get('failed', 0) > 2:
            recommendations.append("Múltiplas falhas - verificar credenciais e conectividade WordPress")
        
        if not recommendations:
            recommendations.append("✅ Todas as publicações estão funcionando normalmente")
        
        return recommendations
    
    def get_pending_articles_dashboard(self) -> Dict[str, Any]:
        """
        Retorna dados para dashboard de artigos pendentes
        
        Returns:
            Dados formatados para exibição no painel
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Artigos pendentes
                cursor = conn.execute("""
                    SELECT ps.*, pa.alert_message, pa.severity
                    FROM publication_status ps
                    LEFT JOIN publication_alerts pa ON ps.article_id = pa.article_id 
                        AND pa.resolved = FALSE
                    WHERE ps.resolved = FALSE 
                    AND ps.publish_attempt_date IS NOT NULL
                    ORDER BY ps.publish_attempt_date DESC
                    LIMIT 20
                """)
                
                pending_articles = []
                for row in cursor.fetchall():
                    article = dict(row)
                    
                    # Calcular tempo pendente
                    attempt_time = datetime.fromisoformat(article['publish_attempt_date'])
                    hours_pending = (datetime.now() - attempt_time).total_seconds() / 3600
                    
                    article['hours_pending'] = round(hours_pending, 1)
                    article['status_display'] = self._get_status_display(article, hours_pending)
                    
                    pending_articles.append(article)
                
                # Estatísticas gerais
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN resolved = FALSE THEN 1 ELSE 0 END) as pending,
                        SUM(CASE WHEN retry_count >= ? THEN 1 ELSE 0 END) as failed
                    FROM publication_status
                    WHERE publish_attempt_date IS NOT NULL
                """, (self.config['max_retry_attempts'],))
                
                stats = dict(cursor.fetchone())
                
                # Configuração atual
                config_check = self.check_wordpress_config()
                
                return {
                    'pending_articles': pending_articles,
                    'statistics': stats,
                    'config_status': config_check,
                    'last_check': datetime.now().isoformat(),
                    'auto_publish_enabled': self.wp_auto_publish,
                    'default_status': self.wp_default_status
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dashboard: {e}")
            return {
                'error': str(e),
                'pending_articles': [],
                'statistics': {'total': 0, 'pending': 0, 'failed': 0}
            }
    
    def _get_status_display(self, article: Dict[str, Any], hours_pending: float) -> Dict[str, str]:
        """Gera display de status para o dashboard"""
        if article['retry_count'] >= self.config['max_retry_attempts']:
            return {
                'status': 'failed',
                'label': 'Falhou',
                'color': 'red',
                'message': f"Falhou após {article['retry_count']} tentativas"
            }
        elif hours_pending > self.config['pending_threshold_hours']:
            return {
                'status': 'warning',
                'label': 'Pendente',
                'color': 'orange',
                'message': f"Pendente há {hours_pending:.1f}h"
            }
        else:
            return {
                'status': 'processing',
                'label': 'Processando',
                'color': 'blue',
                'message': f"Em processamento ({hours_pending:.1f}h)"
            }
    
    def resolve_alert(self, article_id: int, alert_type: str = None) -> bool:
        """
        Marca alerta como resolvido
        
        Args:
            article_id: ID do artigo
            alert_type: Tipo específico de alerta (opcional)
            
        Returns:
            True se resolvido com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if alert_type:
                    conn.execute("""
                        UPDATE publication_alerts 
                        SET resolved = TRUE, notification_date = CURRENT_TIMESTAMP
                        WHERE article_id = ? AND alert_type = ? AND resolved = FALSE
                    """, (article_id, alert_type))
                else:
                    conn.execute("""
                        UPDATE publication_alerts 
                        SET resolved = TRUE, notification_date = CURRENT_TIMESTAMP
                        WHERE article_id = ? AND resolved = FALSE
                    """, (article_id,))
                
                # Marcar publicação como resolvida também
                conn.execute("""
                    UPDATE publication_status 
                    SET resolved = TRUE, updated_at = CURRENT_TIMESTAMP
                    WHERE article_id = ?
                """, (article_id,))
                
                logger.info(f"✅ Alerta resolvido para artigo {article_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao resolver alerta: {e}")
            return False
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de monitoramento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas de publicações
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_monitored,
                        SUM(CASE WHEN resolved = FALSE THEN 1 ELSE 0 END) as active_monitoring,
                        AVG(retry_count) as avg_retries
                    FROM publication_status
                """)
                pub_stats = dict(cursor.fetchone())
                
                # Estatísticas de alertas
                cursor = conn.execute("""
                    SELECT 
                        alert_type,
                        COUNT(*) as count,
                        SUM(CASE WHEN resolved = FALSE THEN 1 ELSE 0 END) as active
                    FROM publication_alerts
                    GROUP BY alert_type
                """)
                alert_stats = {row[0]: {'total': row[1], 'active': row[2]} 
                              for row in cursor.fetchall()}
                
                return {
                    'publication_stats': pub_stats,
                    'alert_stats': alert_stats,
                    'config': self.config,
                    'wp_config': {
                        'auto_publish': self.wp_auto_publish,
                        'default_status': self.wp_default_status
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {} 