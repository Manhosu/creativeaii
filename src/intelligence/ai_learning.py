import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class AILearning:
    """
    Sistema inteligente de aprendizado que:
    1. Aprende com rejeições de artigos
    2. Sugere melhorias baseadas no histórico
    3. Evita repetir erros passados
    4. Detecta padrões de rejeição
    """
    
    def __init__(self, db_path: str = "data/ai_learning.db"):
        """
        Inicializa o sistema de aprendizado
        
        Args:
            db_path: Caminho para o banco de dados de aprendizado
        """
        self.db_path = db_path
        self._init_database()
        logger.info("🧠 Sistema de aprendizado da IA inicializado")
    
    def _init_database(self):
        """Inicializa as tabelas de aprendizado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de rejeições e aprendizado
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rejection_learning (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto_nome TEXT NOT NULL,
                        categoria TEXT,
                        article_id INTEGER,
                        motivo_rejeicao TEXT NOT NULL,
                        motivo_categoria TEXT,
                        data_rejeicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        palavras_chave TEXT,
                        severidade INTEGER DEFAULT 1,
                        corrigido BOOLEAN DEFAULT FALSE,
                        metadata TEXT
                    )
                """)
                
                # Tabela de padrões identificados
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        pattern_description TEXT NOT NULL,
                        occurrence_count INTEGER DEFAULT 1,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        suggested_fix TEXT,
                        active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                conn.commit()
                logger.info("✅ Tabelas de aprendizado criadas/verificadas")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de aprendizado: {e}")
    
    def learn_from_rejection(self, 
                           produto_nome: str, 
                           categoria: str,
                           article_id: int,
                           motivo_rejeicao: str,
                           metadata: Dict[str, Any] = None) -> bool:
        """
        Aprende com uma rejeição de artigo
        
        Args:
            produto_nome: Nome do produto rejeitado
            categoria: Categoria do produto
            article_id: ID do artigo rejeitado
            motivo_rejeicao: Motivo detalhado da rejeição
            metadata: Dados extras sobre o artigo
            
        Returns:
            True se aprendeu com sucesso
        """
        try:
            # Analisar o motivo da rejeição
            motivo_categoria = self._categorize_rejection_reason(motivo_rejeicao)
            palavras_chave = self._extract_keywords_from_reason(motivo_rejeicao)
            severidade = self._calculate_severity(motivo_rejeicao)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Salvar rejeição
                cursor.execute("""
                    INSERT INTO rejection_learning (
                        produto_nome, categoria, article_id, motivo_rejeicao,
                        motivo_categoria, palavras_chave, severidade, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    produto_nome, categoria, article_id, motivo_rejeicao,
                    motivo_categoria, json.dumps(palavras_chave), severidade,
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                
                # Identificar e salvar padrões
                self._identify_and_save_patterns(produto_nome, categoria, motivo_rejeicao, motivo_categoria)
                
                logger.info(f"🧠 Aprendizado registrado: {produto_nome} - {motivo_categoria}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao aprender com rejeição: {e}")
            return False
    
    def get_improvement_suggestions(self, 
                                  produto_nome: str, 
                                  categoria: str) -> List[Dict[str, Any]]:
        """
        Obtém sugestões de melhoria baseadas no histórico de rejeições
        
        Args:
            produto_nome: Nome do produto
            categoria: Categoria do produto
            
        Returns:
            Lista de sugestões para melhoria
        """
        try:
            suggestions = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar rejeições específicas do produto
                cursor.execute("""
                    SELECT motivo_rejeicao, motivo_categoria, severidade, 
                           palavras_chave, data_rejeicao
                    FROM rejection_learning 
                    WHERE produto_nome LIKE ? OR categoria = ?
                    ORDER BY data_rejeicao DESC
                    LIMIT 10
                """, (f'%{produto_nome}%', categoria))
                
                rejections = cursor.fetchall()
                
                for rejection in rejections:
                    motivo, cat, sev, keywords_json, data = rejection
                    keywords = json.loads(keywords_json) if keywords_json else []
                    
                    # Criar sugestão específica
                    suggestion = {
                        'type': cat,
                        'severity': sev,
                        'issue': motivo,
                        'keywords': keywords,
                        'suggestion': self._generate_specific_suggestion(cat, motivo, keywords),
                        'date': data,
                        'priority': sev * 2 if produto_nome.lower() in motivo.lower() else sev
                    }
                    suggestions.append(suggestion)
                
                # Buscar padrões gerais
                cursor.execute("""
                    SELECT pattern_description, suggested_fix, occurrence_count
                    FROM learning_patterns
                    WHERE active = TRUE
                    ORDER BY occurrence_count DESC
                    LIMIT 5
                """)
                
                patterns = cursor.fetchall()
                for pattern in patterns:
                    desc, fix, count = pattern
                    suggestions.append({
                        'type': 'pattern',
                        'severity': min(count, 5),
                        'issue': desc,
                        'suggestion': fix,
                        'pattern_count': count,
                        'priority': count
                    })
                
                # Ordenar por prioridade
                suggestions.sort(key=lambda x: x.get('priority', 0), reverse=True)
                
                logger.info(f"💡 {len(suggestions)} sugestões geradas para {produto_nome}")
                return suggestions[:5]  # Top 5 sugestões
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar sugestões: {e}")
            return []
    
    def has_previous_rejections(self, produto_nome: str, categoria: str = None) -> bool:
        """
        Verifica se um produto já foi rejeitado antes
        
        Args:
            produto_nome: Nome do produto
            categoria: Categoria (opcional)
            
        Returns:
            True se já foi rejeitado
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if categoria:
                    cursor.execute("""
                        SELECT COUNT(*) FROM rejection_learning 
                        WHERE produto_nome LIKE ? OR categoria = ?
                    """, (f'%{produto_nome}%', categoria))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM rejection_learning 
                        WHERE produto_nome LIKE ?
                    """, (f'%{produto_nome}%',))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar rejeições anteriores: {e}")
            return False
    
    def get_last_rejection_reason(self, produto_nome: str) -> Optional[str]:
        """
        Obtém o último motivo de rejeição para um produto específico
        
        Args:
            produto_nome: Nome do produto
            
        Returns:
            Último motivo de rejeição ou None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT motivo_rejeicao 
                    FROM rejection_learning 
                    WHERE produto_nome LIKE ?
                    ORDER BY data_rejeicao DESC 
                    LIMIT 1
                """, (f'%{produto_nome}%',))
                
                result = cursor.fetchone()
                return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar último motivo de rejeição: {e}")
            return None
    
    def _categorize_rejection_reason(self, motivo: str) -> str:
        """Categoriza o motivo da rejeição automaticamente"""
        motivo_lower = motivo.lower()
        
        # Categorias baseadas em palavras-chave
        if any(word in motivo_lower for word in ['seo', 'meta', 'título', 'palavra-chave', 'otimização']):
            return 'seo'
        elif any(word in motivo_lower for word in ['conteúdo', 'texto', 'informação', 'descrição', 'detalhe']):
            return 'conteudo'
        elif any(word in motivo_lower for word in ['formatação', 'html', 'estrutura', 'layout']):
            return 'formatacao'
        elif any(word in motivo_lower for word in ['imagem', 'foto', 'visual']):
            return 'imagem'
        elif any(word in motivo_lower for word in ['preço', 'valor', 'custo', 'disponibilidade']):
            return 'produto_info'
        else:
            return 'geral'
    
    def _extract_keywords_from_reason(self, motivo: str) -> List[str]:
        """Extrai palavras-chave importantes do motivo da rejeição"""
        # Remover pontuação e dividir em palavras
        words = re.findall(r'\b\w+\b', motivo.lower())
        
        # Palavras irrelevantes (stop words)
        stop_words = {'o', 'a', 'os', 'as', 'de', 'da', 'do', 'das', 'dos', 'e', 'ou', 'que', 'para', 'com', 'em', 'por', 'é', 'são', 'foi', 'ser', 'ter', 'não', 'muito', 'mais', 'este', 'essa', 'isso'}
        
        # Filtrar palavras relevantes (> 3 caracteres e não stop words)
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return list(set(keywords))[:10]  # Top 10 palavras únicas
    
    def _calculate_severity(self, motivo: str) -> int:
        """Calcula severidade da rejeição (1-5)"""
        motivo_lower = motivo.lower()
        
        # Palavras que indicam alta severidade
        high_severity = ['crítico', 'grave', 'inaceitável', 'péssimo', 'horrível']
        medium_severity = ['problema', 'erro', 'incorreto', 'ruim']
        
        if any(word in motivo_lower for word in high_severity):
            return 5
        elif any(word in motivo_lower for word in medium_severity):
            return 3
        elif len(motivo) > 100:  # Motivos longos indicam problemas complexos
            return 4
        else:
            return 2
    
    def _identify_and_save_patterns(self, produto_nome: str, categoria: str, motivo: str, motivo_categoria: str):
        """Identifica e salva padrões de rejeição"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se já existe padrão similar
                cursor.execute("""
                    SELECT id, occurrence_count FROM learning_patterns
                    WHERE pattern_type = ? AND pattern_description LIKE ?
                """, (motivo_categoria, f'%{motivo[:50]}%'))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Incrementar contador
                    cursor.execute("""
                        UPDATE learning_patterns 
                        SET occurrence_count = occurrence_count + 1,
                            last_seen = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (existing[0],))
                else:
                    # Criar novo padrão
                    suggestion = self._generate_pattern_suggestion(motivo_categoria, motivo)
                    cursor.execute("""
                        INSERT INTO learning_patterns (
                            pattern_type, pattern_description, suggested_fix
                        ) VALUES (?, ?, ?)
                    """, (motivo_categoria, motivo[:200], suggestion))
                
                conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Erro ao identificar padrões: {e}")
    
    def _generate_specific_suggestion(self, categoria: str, motivo: str, keywords: List[str]) -> str:
        """Gera sugestão específica baseada na categoria e motivo"""
        suggestions = {
            'seo': {
                'default': 'Melhorar otimização SEO: títulos, meta descriptions e palavras-chave',
                'título': 'Revisar título: deve ser atrativo e conter palavras-chave relevantes',
                'meta': 'Criar meta description mais atrativa e descritiva (150-160 caracteres)',
                'palavra-chave': 'Incluir palavras-chave mais relevantes e específicas'
            },
            'conteudo': {
                'default': 'Melhorar qualidade do conteúdo: mais detalhes e informações úteis',
                'informação': 'Adicionar mais informações técnicas e detalhes do produto',
                'descrição': 'Expandir descrição com características mais específicas',
                'texto': 'Revisar e enriquecer o texto com mais detalhes relevantes'
            },
            'formatacao': {
                'default': 'Corrigir formatação: estrutura HTML e organização do conteúdo',
                'html': 'Verificar tags HTML e estrutura do documento',
                'estrutura': 'Melhorar organização com subtítulos e listas',
                'layout': 'Ajustar layout para melhor legibilidade'
            },
            'imagem': {
                'default': 'Revisar imagens: qualidade, alt text e relevância',
                'foto': 'Usar imagens de melhor qualidade e mais relevantes',
                'visual': 'Melhorar aspecto visual com imagens apropriadas'
            },
            'produto_info': {
                'default': 'Atualizar informações do produto: preço, disponibilidade e especificações',
                'preço': 'Verificar e atualizar informações de preço',
                'disponibilidade': 'Confirmar disponibilidade atual do produto'
            }
        }
        
        category_suggestions = suggestions.get(categoria, {'default': 'Revisar e melhorar conforme feedback'})
        
        # Procurar sugestão específica baseada em palavras-chave
        for keyword in keywords:
            if keyword in category_suggestions:
                return category_suggestions[keyword]
        
        return category_suggestions['default']
    
    def _generate_pattern_suggestion(self, categoria: str, motivo: str) -> str:
        """Gera sugestão para padrão identificado"""
        base_suggestions = {
            'seo': 'Implementar checklist SEO: título otimizado, meta description, estrutura H1-H6',
            'conteudo': 'Usar template de conteúdo mais robusto com seções obrigatórias',
            'formatacao': 'Aplicar formatação padrão: HTML válido, estrutura consistente',
            'imagem': 'Usar sistema de imagens automático com fallbacks e alt text',
            'produto_info': 'Validar dados do produto antes da geração do artigo'
        }
        
        return base_suggestions.get(categoria, 'Revisar processo de geração para esta categoria') 