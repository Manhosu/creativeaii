"""
Sistema de Aprendizado de IA para Melhoria Automática de Artigos
Armazena rejeições e usa feedback para gerar artigos melhores
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from src.intelligence.ai_learning import AILearning
from src.review.review_manager import ReviewManager

class LearningManager:
    """
    Gerenciador central do sistema de aprendizado inteligente
    Coordena entre aprendizado, verificação de pendências e melhorias
    """
    
    def __init__(self):
        """Inicializa o gerenciador de aprendizado"""
        self.ai_learning = AILearning()
        self.review_manager = ReviewManager()
        logger.info("🎓 Gerenciador de aprendizado inicializado")
    
    def check_product_status(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica status de um produto antes de gerar artigo
        
        Args:
            product_data: Dados do produto
            
        Returns:
            Status e ações recomendadas
        """
        try:
            produto_nome = product_data.get('nome', '')
            categoria = product_data.get('categoria_nome', 'produtos')
            
            # 1. Verificar se há artigos pendentes
            pending_article = self._check_pending_articles(produto_nome)
            
            if pending_article:
                return {
                    'status': 'has_pending',
                    'action': 'redirect',
                    'article_id': pending_article['id'],
                    'message': f'Já existe um artigo pendente para este produto (ID: {pending_article["id"]})',
                    'redirect_url': f'/review/{pending_article["id"]}/view',
                    'article_title': pending_article['titulo']
                }
            
            # 2. Verificar histórico de rejeições
            has_rejections = self.ai_learning.has_previous_rejections(produto_nome, categoria)
            
            if has_rejections:
                last_reason = self.ai_learning.get_last_rejection_reason(produto_nome)
                suggestions = self.ai_learning.get_improvement_suggestions(produto_nome, categoria)
                
                return {
                    'status': 'has_rejections',
                    'action': 'generate_with_learning',
                    'last_rejection': last_reason,
                    'suggestions': suggestions,
                    'message': f'Produto foi rejeitado antes. IA aplicará melhorias baseadas no aprendizado.',
                    'warning': f'⚠️ Último motivo de rejeição: {last_reason}'
                }
            
            # 3. Status limpo - pode gerar normalmente
            return {
                'status': 'clean',
                'action': 'generate_normal',
                'message': 'Produto sem histórico de problemas. Pode gerar artigo normalmente.'
            }
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status do produto: {e}")
            return {
                'status': 'error',
                'action': 'generate_normal',
                'message': 'Erro na verificação. Gerando artigo normalmente.',
                'error': str(e)
            }
    
    def handle_article_rejection(self, article_id: int, rejection_reason: str, reviewer: str = "Sistema") -> bool:
        """
        Processa rejeição de artigo e registra aprendizado
        
        Args:
            article_id: ID do artigo rejeitado
            rejection_reason: Motivo da rejeição
            reviewer: Nome do revisor
            
        Returns:
            True se processado com sucesso
        """
        try:
            # Buscar dados do artigo
            article_data = self.review_manager.get_article(article_id)
            
            if not article_data:
                logger.error(f"❌ Artigo {article_id} não encontrado para aprendizado")
                return False
            
            # Extrair informações para aprendizado
            produto_nome = article_data.get('produto_nome', '')
            categoria = article_data.get('tipo_produto', '')
            
            # Registrar aprendizado
            success = self.ai_learning.learn_from_rejection(
                produto_nome=produto_nome,
                categoria=categoria,
                article_id=article_id,
                motivo_rejeicao=rejection_reason,
                metadata={
                    'reviewer': reviewer,
                    'article_title': article_data.get('titulo', ''),
                    'rejection_date': article_data.get('data_revisao', ''),
                    'article_score': article_data.get('score_seo', 0)
                }
            )
            
            if success:
                logger.info(f"📚 Aprendizado registrado para rejeição do artigo {article_id}")
                return True
            else:
                logger.error(f"❌ Falha ao registrar aprendizado para artigo {article_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar rejeição do artigo {article_id}: {e}")
            return False
    
    def generate_smart_content_improvements(self, product_data: Dict[str, Any], base_content: str) -> str:
        """
        Aplica melhorias inteligentes no conteúdo baseadas no aprendizado
        
        Args:
            product_data: Dados do produto
            base_content: Conteúdo base gerado
            
        Returns:
            Conteúdo melhorado com sugestões da IA
        """
        try:
            produto_nome = product_data.get('nome', '')
            categoria = product_data.get('categoria_nome', 'produtos')
            
            # Buscar sugestões de melhoria
            suggestions = self.ai_learning.get_improvement_suggestions(produto_nome, categoria)
            
            if not suggestions:
                return base_content
            
            # Aplicar melhorias no conteúdo
            improved_content = base_content
            
            # Adicionar seção de melhorias baseadas em IA
            ai_section = self._generate_ai_improvement_section(suggestions)
            
            # Inserir seção após o primeiro H2
            if '<h2>' in improved_content:
                parts = improved_content.split('<h2>', 1)
                improved_content = parts[0] + ai_section + '<h2>' + parts[1]
                else:
                improved_content = ai_section + improved_content
            
            logger.info(f"🤖 Melhorias de IA aplicadas ao conteúdo de {produto_nome}")
            return improved_content
                
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar melhorias inteligentes: {e}")
            return base_content
    
    def _check_pending_articles(self, produto_nome: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se há artigos pendentes para um produto
        
        Args:
            produto_nome: Nome do produto
            
        Returns:
            Dados do artigo pendente ou None
        """
        try:
            pending_articles = self.review_manager.list_articles(status='pendente', limit=100)
            
            for article in pending_articles:
                if (article.get('produto_nome', '').lower() == produto_nome.lower() or 
                    produto_nome.lower() in article.get('titulo', '').lower()):
                    return article
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar artigos pendentes: {e}")
            return None
    
    def _generate_ai_improvement_section(self, suggestions: List[Dict[str, Any]]) -> str:
        """
        Gera seção HTML com melhorias sugeridas pela IA
        
        Args:
            suggestions: Lista de sugestões da IA
            
        Returns:
            HTML com seção de melhorias
        """
        if not suggestions:
            return ""
        
        # Filtrar sugestões mais importantes
        important_suggestions = [s for s in suggestions if s.get('severity', 0) >= 3][:3]
        
        if not important_suggestions:
            return ""
        
        html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
           color: white; padding: 20px; margin: 20px 0; border-radius: 10px; 
           box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
    <h3 style="color: white; margin-top: 0;">🧠 Melhorias Baseadas em IA</h3>
    <p style="margin-bottom: 15px; opacity: 0.9;">
        Este conteúdo foi otimizado com base no aprendizado de rejeições anteriores:
    </p>
    <ul style="margin-bottom: 0;">
"""
        
        for suggestion in important_suggestions:
            severity_icon = "🔴" if suggestion.get('severity', 0) >= 4 else "🟡"
            html += f"""
        <li style="margin-bottom: 8px;">
            {severity_icon} <strong>{suggestion.get('type', 'geral').upper()}:</strong> 
            {suggestion.get('suggestion', 'Melhoria aplicada')}
        </li>
"""
        
        html += """
    </ul>
</div>
"""
        
        return html
    
    def get_product_learning_summary(self, produto_nome: str) -> Dict[str, Any]:
        """
        Obtém resumo do aprendizado para um produto específico
        
        Args:
            produto_nome: Nome do produto
            
        Returns:
            Resumo do aprendizado
        """
        try:
            has_rejections = self.ai_learning.has_previous_rejections(produto_nome)
            
            if not has_rejections:
                return {
                    'has_learning': False,
                    'message': 'Produto sem histórico de rejeições'
                }
            
            last_reason = self.ai_learning.get_last_rejection_reason(produto_nome)
            suggestions = self.ai_learning.get_improvement_suggestions(produto_nome, '')
            
            return {
                'has_learning': True,
                'last_rejection': last_reason,
                'suggestions_count': len(suggestions),
                'top_suggestions': suggestions[:3],
                'risk_level': self._calculate_risk_level(suggestions),
                'message': f'Produto tem {len(suggestions)} sugestões de melhoria baseadas em rejeições anteriores'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo de aprendizado: {e}")
            return {
                'has_learning': False,
                'error': str(e)
            }
    
    def _calculate_risk_level(self, suggestions: List[Dict[str, Any]]) -> str:
        """Calcula nível de risco baseado nas sugestões"""
        if not suggestions:
            return 'baixo'
        
        avg_severity = sum(s.get('severity', 1) for s in suggestions) / len(suggestions)
        
        if avg_severity >= 4:
            return 'alto'
        elif avg_severity >= 3:
            return 'medio'
        else:
            return 'baixo'
    
    def cleanup_old_learning_data(self, days: int = 180) -> int:
        """
        Limpa dados de aprendizado antigos
        
        Args:
            days: Dias para manter os dados
            
        Returns:
            Número de registros removidos
        """
        try:
            import sqlite3
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.ai_learning.db_path) as conn:
                cursor = conn.cursor()
                
                # Remover rejeições antigas que já foram corrigidas
                cursor.execute("""
                    DELETE FROM rejection_learning 
                    WHERE data_rejeicao < ? AND corrigido = TRUE
                """, (cutoff_date,))
                
                removed_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"🧹 Limpeza de aprendizado: {removed_count} registros antigos removidos")
                return removed_count
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de dados de aprendizado: {e}")
            return 0 