"""
SEO Optimizer
Otimização de conteúdo para SEO: slugs, meta tags, headings
OTIMIZADO PARA YOAST SEO - PONTUAÇÃO VERDE
"""

import re
import unicodedata
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime
import os

class SEOOptimizer:
    """Otimizador de SEO para artigos - Compatível com Yoast SEO"""
    
    def __init__(self):
        """Inicializa o otimizador SEO"""
        # Configurações Yoast SEO otimizadas
        self.max_meta_description_length = 155
        self.min_meta_description_length = 120
        self.max_title_length = 60
        self.min_title_length = 30
        self.max_slug_length = 50
        
        # Banco de dados para verificar duplicatas
        self.db_path = "data/review_articles.db"
        
        # Palavras de transição para melhorar legibilidade
        self.transition_words = [
            'além disso', 'portanto', 'por fim', 'ou seja', 'no entanto', 
            'assim sendo', 'por outro lado', 'em primeiro lugar', 'finalmente',
            'consequentemente', 'por exemplo', 'dessa forma', 'contudo',
            'sobretudo', 'por isso', 'em suma', 'ainda assim', 'logo',
            'principalmente', 'então', 'para isso', 'entretanto', 'ainda',
            'mas', 'porém', 'todavia', 'assim', 'também'
        ]
        
        # Palavras irrelevantes para slug
        self.stop_words = [
            'a', 'e', 'o', 'de', 'da', 'do', 'para', 'com', 'em', 'na', 'no',
            'por', 'até', 'como', 'mais', 'muito', 'sem', 'seu', 'sua', 'seus',
            'suas', 'que', 'qual', 'quando', 'onde', 'porque', 'como', 'um',
            'uma', 'uns', 'umas', 'isso', 'essa', 'esta', 'este', 'estas',
            'estes', 'ela', 'ele', 'elas', 'eles', 'ser', 'ter', 'estar'
        ]
        
        # Templates de títulos diferenciados por tipo
        self.title_templates = {
            'impressora': [
                "{produto}: Análise Completa e Especificações",
                "{produto}: Review Detalhado {ano}",
                "{produto}: Características e Performance",
                "{produto}: Vale a Pena? Análise Técnica",
                "{produto}: Especificações e Comparativo"
            ],
            'multifuncional': [
                "{produto}: Análise Completa da Multifuncional",
                "{produto}: Review da Impressora All-in-One",
                "{produto}: Especificações e Características",
                "{produto}: Multifuncional Profissional - Review",
                "{produto}: Análise Técnica Detalhada"
            ],
            'toner': [
                "{produto}: Análise do Toner Original",
                "{produto}: Review do Cartucho {marca}",
                "{produto}: Rendimento e Qualidade",
                "{produto}: Toner Original vs Compatível",
                "{produto}: Especificações do Toner"
            ],
            'scanner': [
                "{produto}: Scanner Profissional Review",
                "{produto}: Digitalização de Alta Qualidade",
                "{produto}: Scanner {marca} - Análise",
                "{produto}: Especificações de Escaneamento",
                "{produto}: Scanner para Escritório"
            ],
            'papel': [
                "{produto}: Papel de Qualidade Superior",
                "{produto}: Análise do Papel {marca}",
                "{produto}: Especificações Técnicas",
                "{produto}: Papel para Impressora Laser",
                "{produto}: Qualidade Profissional"
            ],
            'suprimento': [
                "{produto}: Suprimento Original {marca}",
                "{produto}: Análise de Qualidade",
                "{produto}: Especificações do Suprimento",
                "{produto}: Original vs Compatível",
                "{produto}: Suprimento Profissional"
            ]
        }
        
        logger.info("🔍 SEO Optimizer inicializado - Compatível com Yoast SEO")
    
    def optimize_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Otimiza artigo completo para SEO (Yoast Green Score)
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            Artigo otimizado para Yoast SEO
        """
        try:
            optimized_article = article_data.copy()
            
            # Extrair palavra-chave principal do título/produto
            primary_keyword = self._extract_primary_keyword(optimized_article)
            optimized_article['primary_keyword'] = primary_keyword
            
            # NOVO: Gerar título único e descritivo
            if 'titulo' in optimized_article:
                # Usar nova função de título único
                optimized_article['titulo'] = self.generate_unique_title(optimized_article)
            else:
                # Fallback se não tem título
                optimized_article['titulo'] = self.generate_unique_title(optimized_article)
            
            # NOVO: Gerar slug único baseado no título
            optimized_article['slug'] = self.generate_unique_slug(optimized_article['titulo'], optimized_article)
            
            # Otimizar meta descrição (120-155 chars + keyword)
            if 'meta_descricao' in optimized_article:
                optimized_article['meta_descricao'] = self.optimize_meta_description_yoast(
                    optimized_article['meta_descricao'], primary_keyword
                )
            elif 'conteudo' in optimized_article:
                optimized_article['meta_descricao'] = self.generate_meta_description_yoast(
                    optimized_article['conteudo'], primary_keyword
                )
            
            # Otimizar conteúdo para legibilidade Yoast
            if 'conteudo' in optimized_article:
                optimized_article['conteudo'] = self.optimize_content_readability(
                    optimized_article['conteudo'], primary_keyword
                )
            
            # Otimizar tags
            if 'tags' in optimized_article:
                optimized_article['tags'] = self.optimize_tags_yoast(optimized_article['tags'], primary_keyword)
            
            # Adicionar dados estruturados
            optimized_article['seo_data'] = self.generate_structured_data_yoast(optimized_article)
            
            # NOVO: Gerar alt tag automática para imagem destacada
            if 'produto_imagem' in optimized_article or 'imagem' in optimized_article:
                optimized_article['imagem_alt'] = self.generate_automatic_alt_tag(optimized_article)
            
            # Validar pontuação Yoast
            optimized_article['yoast_score'] = self.calculate_yoast_score(optimized_article)
            
            logger.debug("✅ Artigo otimizado para Yoast SEO - Pontuação Verde")
            return optimized_article
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização SEO: {e}")
            return article_data
    
    def _extract_primary_keyword(self, article_data: Dict[str, Any]) -> str:
        """Extrai palavra-chave principal do artigo"""
        title = article_data.get('titulo', '')
        product_name = article_data.get('produto_nome', '')
        
        # Priorizar nome do produto
        if product_name:
            # Pegar primeiras 2-3 palavras significativas
            words = product_name.lower().split()
            keywords = [w for w in words if w not in self.stop_words and len(w) > 2]
            return ' '.join(keywords[:2]) if keywords else product_name.lower()
        
        # Fallback para título
        if title:
            words = title.lower().split()
            keywords = [w for w in words if w not in self.stop_words and len(w) > 2]
            return ' '.join(keywords[:2]) if keywords else title.lower()
        
        return "produto"
    
    def optimize_title_yoast(self, title: str, keyword: str) -> str:
        """
        Otimiza título para Yoast SEO (máx 60 chars + keyword)
        ATUALIZADO: Agora usa geração de título único
        
        Args:
            title: Título original
            keyword: Palavra-chave principal
            
        Returns:
            Título otimizado para Yoast
        """
        # Se título vier vazio, usar keyword
        if not title:
            title = f"{keyword.title()}: Características e Benefícios"
        
        # Garantir que a keyword está no título
        if keyword.lower() not in title.lower():
            # Adicionar keyword no início se possível
            title = f"{keyword.title()}: {title}"
        
        # Limitar a 60 caracteres
        if len(title) > self.max_title_length:
            # Tentar cortar mantendo a palavra-chave
            if keyword.lower() in title[:self.max_title_length].lower():
                # Keyword está na parte que será mantida
                words = title.split()
                optimized_title = ""
                
                for word in words:
                    test_length = len(optimized_title + " " + word) if optimized_title else len(word)
                    if test_length <= self.max_title_length:
                        optimized_title += (" " if optimized_title else "") + word
                    else:
                        break
                
                title = optimized_title
            else:
                # Keyword não está na parte mantida, reformular
                title = f"{keyword.title()}: {title.split(':')[-1].strip()}"
                if len(title) > self.max_title_length:
                    title = title[:self.max_title_length-3] + "..."
        
        return title.strip()
    
    def generate_seo_slug(self, text: str, keyword: str) -> str:
        """
        Gera slug otimizado com palavra-chave
        ATUALIZADO: Agora usa geração de slug único
        
        Args:
            text: Texto para converter em slug
            keyword: Palavra-chave principal
            
        Returns:
            Slug otimizado para SEO
        """
        # Criar dados simulados para compatibilidade
        product_data = {
            'produto_nome': text or keyword,
            'nome': text or keyword
        }
        
        # Usar a nova função de slug único
        return self.generate_unique_slug(text or keyword, product_data)
    
    def optimize_meta_description_yoast(self, meta_desc: str, keyword: str) -> str:
        """
        Otimiza meta descrição para Yoast (120-155 chars + keyword)
        
        Args:
            meta_desc: Meta descrição original
            keyword: Palavra-chave principal
            
        Returns:
            Meta descrição otimizada
        """
        if not meta_desc:
            return f"Conheça {keyword} e suas principais características. Ideal para escritório e alta produtividade. Confira benefícios e especificações."
        
        # Remover HTML se houver
        meta_desc = re.sub(r'<[^>]+>', '', meta_desc)
        
        # Garantir que keyword está presente
        if keyword.lower() not in meta_desc.lower():
            meta_desc = f"{keyword.title()}: {meta_desc}"
        
        # Ajustar tamanho (120-155 caracteres)
        if len(meta_desc) < self.min_meta_description_length:
            # Expandir com call-to-action
            cta_options = [
                " Confira características e benefícios.",
                " Ideal para escritório e empresas.",
                " Descubra especificações e vantagens.",
                " Saiba mais sobre funcionalidades."
            ]
            for cta in cta_options:
                if len(meta_desc + cta) <= self.max_meta_description_length:
                    meta_desc += cta
                    break
        
        elif len(meta_desc) > self.max_meta_description_length:
            # Cortar mantendo keyword
            words = meta_desc.split()
            optimized_desc = ""
            
            for word in words:
                test_length = len(optimized_desc + " " + word) if optimized_desc else len(word)
                if test_length <= self.max_meta_description_length - 3:
                    optimized_desc += (" " if optimized_desc else "") + word
                else:
                    break
            
            meta_desc = optimized_desc + "..."
        
        return meta_desc.strip()
    
    def generate_meta_description_yoast(self, content: str, keyword: str) -> str:
        """
        Gera meta descrição otimizada a partir do conteúdo
        
        Args:
            content: Conteúdo HTML
            keyword: Palavra-chave principal
            
        Returns:
            Meta descrição otimizada para Yoast
        """
        # Remover HTML
        text = re.sub(r'<[^>]+>', '', content)
        
        # Pegar primeiro parágrafo significativo
        paragraphs = text.split('\n')
        first_paragraph = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) > 50:  # Parágrafo significativo
                first_paragraph = paragraph
                break
        
        if first_paragraph:
            # Usar primeiro parágrafo como base
            meta_desc = f"{keyword.title()}: {first_paragraph[:100]}"
        else:
            # Fallback
            meta_desc = f"Conheça {keyword} e suas principais características. Ideal para escritório e alta produtividade."
        
        return self.optimize_meta_description_yoast(meta_desc, keyword)
    
    def optimize_content_readability(self, content: str, keyword: str) -> str:
        """
        Otimiza conteúdo para legibilidade Yoast (pontuação verde)
        
        Args:
            content: Conteúdo HTML
            keyword: Palavra-chave principal
            
        Returns:
            Conteúdo otimizado para legibilidade
        """
        try:
            # USAR NOVA VERSÃO MELHORADA
            return self.optimize_content_readability_enhanced(content, keyword)
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização de legibilidade: {e}")
            return content
    
    def optimize_content_readability_enhanced(self, content: str, keyword: str) -> str:
        """
        NOVA VERSÃO MELHORADA - Otimiza conteúdo para legibilidade Yoast verde
        
        Args:
            content: Conteúdo HTML/texto
            keyword: Palavra-chave principal
            
        Returns:
            Conteúdo otimizado para Yoast verde
        """
        try:
            logger.debug("🔍 Aplicando otimizações avançadas de legibilidade Yoast...")
            
            # 1. Corrigir erros linguísticos básicos
            content = self._fix_linguistic_errors_enhanced(content)
            
            # 2. Otimizar frases para máximo 20 palavras
            content = self._optimize_sentence_length_enhanced(content)
            
            # 3. Adicionar palavras de transição (30% das frases)
            content = self._add_transition_words_enhanced(content)
            
            # 4. Otimizar listas com conteúdo real (mín. 3 itens)
            content = self._optimize_lists_enhanced(content, keyword)
            
            # 5. Garantir parágrafos ≤ 100 palavras
            content = self._optimize_paragraph_length_enhanced(content)
            
            # 6. Converter para voz ativa
            content = self._improve_active_voice_enhanced(content)
            
            # 7. Garantir keyword nos primeiros 100 caracteres
            content = self._ensure_keyword_in_intro(content, keyword)
            
            # 8. CRÍTICO: Limpar URLs malformadas como último passo
            content = self._clean_urls_final(content)
            
            logger.debug("✅ Otimizações avançadas de legibilidade aplicadas")
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização avançada: {e}")
            return content
    
    def _fix_linguistic_errors_enhanced(self, content: str) -> str:
        """Corrige erros linguísticos para Yoast verde"""
        if not content:
            return content
        
        # Corrigir maiúsculas desnecessárias (exceto início de frases)
        corrections = [
            (r'(?<!^)(?<!\. )(?<!\n)(Além Disso)', 'além disso'),
            (r'(?<!^)(?<!\. )(?<!\n)(Em Um)', 'em um'),
            (r'(?<!^)(?<!\. )(?<!\n)(Em Uma)', 'em uma'),
            (r'(?<!^)(?<!\. )(?<!\n)(Por Isso)', 'por isso'),
            (r'(?<!^)(?<!\. )(?<!\n)(Por Exemplo)', 'por exemplo'),
            (r'(?<!^)(?<!\. )(?<!\n)(Dessa Forma)', 'dessa forma'),
            (r'(?<!^)(?<!\. )(?<!\n)(No Entanto)', 'no entanto'),
            (r'(?<!^)(?<!\. )(?<!\n)(Por Outro Lado)', 'por outro lado'),
            (r'(?<!^)(?<!\. )(?<!\n)(De Forma Geral)', 'de forma geral'),
            (r'(?<!^)(?<!\. )(?<!\n)(Em Comparação)', 'em comparação'),
            (r'(?<!^)(?<!\. )(?<!\n)(Em Resumo)', 'em resumo'),
            (r'(?<!^)(?<!\. )(?<!\n)(Ou Seja)', 'ou seja'),
        ]
        
        for pattern, replacement in corrections:
            content = re.sub(pattern, replacement, content)
        
        # Corrigir concordância de artigos
        article_corrections = [
            (r'\bo Impressora\b', 'a Impressora'),
            (r'\bo impressora\b', 'a impressora'),
            (r'\bo multifuncional\b', 'a multifuncional'),
            (r'\bo Multifuncional\b', 'a Multifuncional'),
            (r'\ba toner\b', 'o toner'),
            (r'\ba Toner\b', 'o Toner'),
            (r'\ba papel\b', 'o papel'),
            (r'\ba Papel\b', 'o Papel'),
        ]
        
        for pattern, replacement in article_corrections:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _optimize_sentence_length_enhanced(self, content: str) -> str:
        """Limita frases a máximo 20 palavras (Yoast verde)"""
        if not content:
            return content
        
        # Trabalhar com parágrafos
        paragraphs = content.split('\n')
        optimized_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip() or '<' in paragraph:
                optimized_paragraphs.append(paragraph)
                continue
            
            # Dividir em frases
            sentences = re.split(r'([.!?])', paragraph)
            optimized_sentences = []
            
            i = 0
            while i < len(sentences) - 1:
                sentence = sentences[i].strip()
                punctuation = sentences[i + 1] if i + 1 < len(sentences) else ''
                
                if not sentence:
                    i += 2
                    continue
                
                words = sentence.split()
                
                if len(words) > 20:
                    # Dividir frase longa
                    split_point = self._find_best_split_point(words)
                    
                    if split_point:
                        first_part = ' '.join(words[:split_point])
                        second_part = ' '.join(words[split_point:])
                        
                        # Adicionar transição na segunda parte
                        transitions = ['Além disso', 'Dessa forma', 'Também', 'Ainda']
                        transition = transitions[len(optimized_sentences) % len(transitions)]
                        
                        optimized_sentences.extend([first_part, '.', f' {transition}, {second_part.lower()}', punctuation])
                    else:
                        # Dividir no meio se não encontrar ponto ideal
                        mid = len(words) // 2
                        first_part = ' '.join(words[:mid])
                        second_part = ' '.join(words[mid:])
                        
                        optimized_sentences.extend([first_part, '.', f' {second_part.capitalize()}', punctuation])
                else:
                    optimized_sentences.extend([sentence, punctuation])
                
                i += 2
            
            optimized_paragraphs.append(''.join(optimized_sentences))
        
        return '\n'.join(optimized_paragraphs)
    
    def _find_best_split_point(self, words: list) -> int:
        """Encontra o melhor ponto para dividir uma frase"""
        # Procurar conectivos em posições viáveis
        connectors = ['e', 'mas', 'porém', 'contudo', 'entretanto', 'no entanto', 
                     'que', 'porque', 'quando', 'onde', 'como', 'para que']
        
        # Procurar entre posições 8 e len-3
        for i in range(8, min(len(words) - 3, 20)):
            if words[i].lower() in connectors:
                return i
        
        # Se não encontrou conectivo, procurar vírgulas
        for i in range(8, min(len(words) - 3, 20)):
            if words[i].endswith(','):
                return i + 1
        
        return None
    
    def _add_transition_words_enhanced(self, content: str) -> str:
        """Adiciona palavras de transição para atingir 30% das frases"""
        import random
        
        paragraphs = content.split('\n')
        optimized_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip() or '<' in paragraph:
                optimized_paragraphs.append(paragraph)
                continue
            
            sentences = re.split(r'([.!?])', paragraph)
            sentence_pairs = []
            
            # Agrupar frases com pontuação
            for i in range(0, len(sentences) - 1, 2):
                sentence = sentences[i].strip()
                punctuation = sentences[i + 1] if i + 1 < len(sentences) else ''
                if sentence:
                    sentence_pairs.append((sentence, punctuation))
            
            if len(sentence_pairs) <= 1:
                optimized_paragraphs.append(paragraph)
                continue
            
            # Adicionar transições em 30% das frases (exceto primeira)
            num_transitions = max(1, int(len(sentence_pairs) * 0.3))
            
            # Selecionar frases para modificar
            indices_to_modify = random.sample(range(1, len(sentence_pairs)), 
                                            min(num_transitions, len(sentence_pairs) - 1))
            
            optimized_sentences = []
            for i, (sentence, punct) in enumerate(sentence_pairs):
                if i in indices_to_modify:
                    # Verificar se já tem transição
                    has_transition = any(tw in sentence.lower() for tw in self.transition_words)
                    
                    if not has_transition:
                        # Escolher transição apropriada
                        if i == 1:
                            transition = random.choice(['Além disso', 'Também', 'Adicionalmente'])
                        elif i == len(sentence_pairs) - 1:
                            transition = random.choice(['Por fim', 'Finalmente', 'Em suma'])
                        else:
                            transition = random.choice(['Dessa forma', 'Portanto', 'Consequentemente'])
                        
                        sentence = f"{transition}, {sentence.lower()}"
                
                optimized_sentences.append(sentence + punct)
            
            optimized_paragraphs.append(' '.join(optimized_sentences))
        
        return '\n'.join(optimized_paragraphs)
    
    def _optimize_lists_enhanced(self, content: str, keyword: str) -> str:
        """Otimiza listas garantindo mínimo 3 itens com conteúdo real"""
        # Buscar listas existentes
        list_pattern = r'<ul[^>]*>(.*?)</ul>'
        
        def improve_list(match):
            list_content = match.group(1)
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL)
            
            # Limpar itens existentes
            clean_items = []
            for item in items:
                clean_text = re.sub(r'<[^>]+>', '', item).strip()
                if clean_text and len(clean_text.split()) <= 15:  # Max 15 palavras
                    clean_items.append(clean_text)
            
            # Garantir pelo menos 3 itens
            if len(clean_items) < 3:
                additional_items = self._generate_product_specific_features(keyword, 3 - len(clean_items))
                clean_items.extend(additional_items)
            
            # Reconstruir lista
            new_list = '<ul>\n'
            for item in clean_items[:6]:  # Máximo 6 itens
                new_list += f'    <li>{item}</li>\n'
            new_list += '</ul>'
            
            return new_list
        
        return re.sub(list_pattern, improve_list, content, flags=re.DOTALL)
    
    def _generate_product_specific_features(self, keyword: str, count: int) -> list:
        """Gera características específicas baseadas no tipo de produto"""
        keyword_lower = keyword.lower()
        
        if 'impressora' in keyword_lower:
            features = [
                'Impressão rápida de até 38 páginas por minuto',
                'Conectividade USB e Ethernet integrada',
                'Compatibilidade com Windows, Mac e Linux',
                'Baixo consumo de energia em standby',
                'Bandeja com capacidade para 250 folhas',
                'Resolução até 1200 x 1200 dpi'
            ]
        elif 'multifuncional' in keyword_lower:
            features = [
                'Impressão, cópia e scan em um equipamento',
                'Scanner com resolução óptica de 600 dpi',
                'Copiadora com zoom de 25% a 400%',
                'Conectividade Wi-Fi para uso sem fio',
                'Alimentador automático de documentos',
                'Software de digitalização incluído'
            ]
        elif 'toner' in keyword_lower:
            features = [
                'Alto rendimento com até 2.300 páginas',
                'Qualidade de impressão profissional',
                'Instalação rápida e sem complicações',
                'Compatível com múltiplos modelos',
                'Tinta resistente e de longa duração',
                'Garantia de qualidade comprovada'
            ]
        elif 'papel' in keyword_lower:
            features = [
                'Gramatura 75g/m² para impressão de qualidade',
                'Brancura superior para textos nítidos',
                'Formato A4 padrão universal',
                'Papel sem ácido para durabilidade',
                'Compatível com jato de tinta e laser',
                'Embalagem resistente à umidade'
            ]
        else:
            features = [
                'Qualidade superior comprovada',
                'Excelente custo-benefício',
                'Garantia de satisfação total',
                'Compatibilidade com equipamentos modernos',
                'Instalação e configuração simples',
                'Design moderno e funcional'
            ]
        
        return features[:count]
    
    def _optimize_paragraph_length_enhanced(self, content: str) -> str:
        """Garante parágrafos com máximo 100 palavras"""
        paragraphs = content.split('\n')
        optimized_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip() or '<' in paragraph:
                optimized_paragraphs.append(paragraph)
                continue
            
            words = paragraph.split()
            
            if len(words) <= 100:
                optimized_paragraphs.append(paragraph)
            else:
                # Dividir parágrafo longo
                chunks = []
                current_chunk = []
                
                for word in words:
                    current_chunk.append(word)
                    
                    if len(current_chunk) >= 85:  # Procurar ponto para quebrar
                        chunk_text = ' '.join(current_chunk)
                        last_period = chunk_text.rfind('.')
                        
                        if last_period > 50:
                            # Quebrar no ponto
                            chunks.append(chunk_text[:last_period + 1])
                            remaining = chunk_text[last_period + 1:].strip()
                            current_chunk = remaining.split() if remaining else []
                        elif len(current_chunk) >= 100:
                            # Forçar quebra
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                optimized_paragraphs.extend(chunks)
        
        return '\n\n'.join(optimized_paragraphs)
    
    def _improve_active_voice_enhanced(self, content: str) -> str:
        """Converte frases passivas para ativas (melhoria Yoast)"""
        passive_to_active = [
            (r'é oferecido por', 'oferece'),
            (r'são oferecidos por', 'oferecem'),
            (r'é proporcionado por', 'proporciona'),
            (r'são proporcionados por', 'proporcionam'),
            (r'é garantido por', 'garante'),
            (r'são garantidos por', 'garantem'),
            (r'é recomendado', 'recomendamos'),
            (r'são recomendados', 'recomendamos'),
            (r'é utilizado', 'utiliza'),
            (r'são utilizados', 'utilizam'),
            (r'pode ser usado', 'você pode usar'),
            (r'podem ser usados', 'você pode usar'),
            (r'será beneficiado', 'você se beneficia'),
            (r'serão beneficiados', 'vocês se beneficiam'),
            (r'foi desenvolvido', 'desenvolvemos'),
            (r'foram desenvolvidos', 'desenvolvemos'),
        ]
        
        for passive, active in passive_to_active:
            content = re.sub(passive, active, content, flags=re.IGNORECASE)
        
        return content
    
    def _ensure_keyword_in_intro(self, content: str, keyword: str) -> str:
        """Garante keyword nos primeiros 100 caracteres"""
        # Extrair primeiro parágrafo
        first_paragraph = content.split('\n')[0] if '\n' in content else content[:200]
        
        # Verificar se keyword está nos primeiros 100 caracteres
        if keyword.lower() not in first_paragraph[:100].lower():
            # Criar nova introdução com keyword
            intro_templates = [
                f"A {keyword} é uma solução essencial para quem busca qualidade e eficiência.",
                f"O {keyword} oferece recursos avançados e desempenho superior.",
                f"Conheça as principais características do {keyword} e seus benefícios.",
            ]
            
            # Escolher template baseado no gênero da palavra
            if any(word in keyword.lower() for word in ['impressora', 'multifuncional']):
                new_intro = intro_templates[0]  # A
            else:
                new_intro = intro_templates[1]  # O
            
            # Inserir no início
            if content.startswith(first_paragraph):
                content = new_intro + ' ' + content
            else:
                content = new_intro + '\n\n' + content
        
        return content
    
    def _clean_urls_final(self, content: str) -> str:
        """
        Limpeza FINAL de URLs - Remove espaços que podem ter sido inseridos
        
        Args:
            content: Conteúdo HTML
            
        Returns:
            Conteúdo com URLs limpas
        """
        if not content:
            return content
        
        # Função para corrigir URLs
        def fix_url_spaces(match):
            url = match.group(1)
            
            # Remover TODOS os espaços da URL
            fixed_url = re.sub(r'\s+', '', url)
            
            # Garantir que pontos não tenham espaços
            fixed_url = re.sub(r'\s*\.\s*', '.', fixed_url)
            
            # Garantir que barras não tenham espaços
            fixed_url = re.sub(r'\s*/\s*', '/', fixed_url)
            
            return f'href="{fixed_url}"'
        
        # Aplicar correção em TODAS as URLs
        cleaned_content = re.sub(r'href="([^"]*)"', fix_url_spaces, content)
        
        return cleaned_content

    def optimize_tags_yoast(self, tags: List[str], keyword: str) -> List[str]:
        """
        Otimiza tags incluindo palavra-chave
        
        Args:
            tags: Lista de tags original
            keyword: Palavra-chave principal
            
        Returns:
            Tags otimizadas
        """
        optimized_tags = list(tags) if tags else []
        
        # Garantir que keyword está nas tags
        keyword_variations = [
            keyword,
            keyword.replace(' ', '-'),
            keyword.split()[0] if ' ' in keyword else keyword
        ]
        
        for variation in keyword_variations:
            if not any(variation.lower() in tag.lower() for tag in optimized_tags):
                optimized_tags.insert(0, variation)  # Adicionar no início
                break
        
        # Limitar a 8 tags para não sobrecarregar
        return optimized_tags[:8]
    
    def generate_structured_data_yoast(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera dados estruturados compatíveis com Yoast
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            Dados estruturados otimizados
        """
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_data.get('titulo', ''),
            "description": article_data.get('meta_descricao', ''),
            "author": {
                "@type": "Organization",
                "name": "Creative Cópias"
            },
            "publisher": {
                "@type": "Organization", 
                "name": "Creative Cópias",
                "url": "https://creativecopias.com.br"
            },
            "mainEntity": {
                "@type": "Product",
                "name": article_data.get('produto_nome', ''),
                "description": article_data.get('meta_descricao', ''),
                "url": article_data.get('produto_url', '')
            },
            "keywords": article_data.get('primary_keyword', '') + ', ' + ', '.join(article_data.get('tags', [])),
            "wordCount": len(re.sub(r'<[^>]+>', '', article_data.get('conteudo', '')).split()),
            "inLanguage": "pt-BR"
        }
    
    def calculate_yoast_score(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula pontuação Yoast estimada
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            Pontuações estimadas
        """
        seo_score = 0
        readability_score = 0
        details = {
            'seo_checks': {},
            'readability_checks': {}
        }
        
        # Verificações SEO
        title = article_data.get('titulo', '')
        meta_desc = article_data.get('meta_descricao', '')
        content = article_data.get('conteudo', '')
        keyword = article_data.get('primary_keyword', '')
        
        # 1. Keyword no título
        if keyword.lower() in title.lower():
            seo_score += 20
            details['seo_checks']['keyword_in_title'] = 'green'
        else:
            details['seo_checks']['keyword_in_title'] = 'red'
        
        # 2. Comprimento do título
        if 30 <= len(title) <= 60:
            seo_score += 15
            details['seo_checks']['title_length'] = 'green'
        else:
            details['seo_checks']['title_length'] = 'orange' if len(title) < 70 else 'red'
        
        # 3. Meta descrição
        if 120 <= len(meta_desc) <= 155 and keyword.lower() in meta_desc.lower():
            seo_score += 20
            details['seo_checks']['meta_description'] = 'green'
        else:
            details['seo_checks']['meta_description'] = 'orange'
        
        # 4. Keyword no conteúdo
        content_text = re.sub(r'<[^>]+>', '', content).lower()
        keyword_count = content_text.count(keyword.lower())
        word_count = len(content_text.split())
        keyword_density = (keyword_count / word_count * 100) if word_count > 0 else 0
        
        if 0.5 <= keyword_density <= 2.5:
            seo_score += 15
            details['seo_checks']['keyword_density'] = 'green'
        else:
            details['seo_checks']['keyword_density'] = 'orange'
        
        # 5. Link externo
        if 'href=' in content and 'target="_blank"' in content:
            seo_score += 10
            details['seo_checks']['external_links'] = 'green'
        else:
            details['seo_checks']['external_links'] = 'red'
        
        # 6. Headings com keyword
        headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', content, re.IGNORECASE)
        has_keyword_in_heading = any(keyword.lower() in heading.lower() for heading in headings)
        if has_keyword_in_heading:
            seo_score += 20
            details['seo_checks']['keyword_in_headings'] = 'green'
        else:
            details['seo_checks']['keyword_in_headings'] = 'red'
        
        # Verificações de Legibilidade
        sentences = re.split(r'[.!?]+', content_text)
        
        # 1. Comprimento das sentenças
        long_sentences = sum(1 for s in sentences if len(s.split()) > 20)
        sentence_score = max(0, 100 - (long_sentences / len(sentences) * 100))
        if sentence_score >= 75:
            readability_score += 25
            details['readability_checks']['sentence_length'] = 'green'
        else:
            details['readability_checks']['sentence_length'] = 'orange'
        
        # 2. Palavras de transição
        transition_count = sum(1 for tw in self.transition_words if tw in content_text)
        if transition_count >= 3:
            readability_score += 25
            details['readability_checks']['transition_words'] = 'green'
        else:
            details['readability_checks']['transition_words'] = 'orange'
        
        # 3. Voz ativa (simplificado)
        passive_markers = ['é usado', 'foi feito', 'pode ser', 'são conhecidos']
        passive_count = sum(1 for marker in passive_markers if marker in content_text)
        if passive_count <= 2:
            readability_score += 25
            details['readability_checks']['passive_voice'] = 'green'
        else:
            details['readability_checks']['passive_voice'] = 'orange'
        
        # 4. Distribuição de subtítulos
        if len(headings) >= 2:
            readability_score += 25
            details['readability_checks']['subheading_distribution'] = 'green'
        else:
            details['readability_checks']['subheading_distribution'] = 'orange'
        
        return {
            'seo_score': min(100, seo_score),
            'readability_score': min(100, readability_score),
            'seo_status': 'green' if seo_score >= 70 else 'orange' if seo_score >= 50 else 'red',
            'readability_status': 'green' if readability_score >= 70 else 'orange' if readability_score >= 50 else 'red',
            'details': details
        }

    def generate_unique_title(self, product_data: Dict[str, Any]) -> str:
        """
        Gera título único e descritivo evitando duplicação
        
        Args:
            product_data: Dados do produto
            
        Returns:
            Título otimizado e único
        """
        try:
            produto_nome = product_data.get('produto_nome') or product_data.get('nome', '')
            tipo_produto = product_data.get('tipo_produto', 'produto')
            marca = self._extract_brand(produto_nome)
            ano_atual = datetime.now().year
            
            # Extrair características diferenciadoras
            caracteristicas = self._extract_product_features(produto_nome)
            
            # Selecionar template baseado no tipo
            templates = self.title_templates.get(tipo_produto, self.title_templates['impressora'])
            
            # Gerar variações de título
            title_candidates = []
            
            for template in templates:
                # Substituir variáveis no template
                title = template.format(
                    produto=produto_nome,
                    marca=marca,
                    ano=ano_atual
                )
                
                # Adicionar características se o título for muito curto
                if len(title) < 45 and caracteristicas:
                    title = f"{title} {caracteristicas[0]}"
                
                # Limitar tamanho
                if len(title) > self.max_title_length:
                    title = title[:57] + "..."
                
                title_candidates.append(title)
            
            # Verificar unicidade e selecionar o primeiro disponível
            for title in title_candidates:
                if self.is_title_unique(title):
                    logger.debug(f"✅ Título único gerado: {title}")
                    return title
            
            # Se nenhum for único, adicionar identificador
            base_title = title_candidates[0]
            unique_title = self._make_title_unique(base_title, product_data)
            
            logger.debug(f"✅ Título com identificador único: {unique_title}")
            return unique_title
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de título único: {e}")
            # Fallback
            produto = product_data.get('nome', 'produto')
            return f"{produto}: Review Completo {datetime.now().year}"

    def _extract_brand(self, product_name: str) -> str:
        """Extrai marca do nome do produto"""
        if not product_name:
            return "Marca"
        
        # Marcas conhecidas
        brands = ['HP', 'Canon', 'Epson', 'Brother', 'Samsung', 'Xerox', 'Ricoh', 'Kyocera']
        
        for brand in brands:
            if brand.lower() in product_name.lower():
                return brand
        
        # Se não encontrar marca conhecida, usar primeira palavra
        words = product_name.split()
        return words[0] if words else "Marca"

    def _extract_product_features(self, product_name: str) -> List[str]:
        """Extrai características do produto para diferenciar título"""
        features = []
        
        if not product_name:
            return features
        
        name_lower = product_name.lower()
        
        # Características técnicas
        if 'laser' in name_lower:
            features.append('Laser')
        if 'jato de tinta' in name_lower or 'inkjet' in name_lower:
            features.append('Jato de Tinta')
        if 'multifuncional' in name_lower:
            features.append('All-in-One')
        if 'wifi' in name_lower or 'wireless' in name_lower:
            features.append('WiFi')
        if 'duplex' in name_lower:
            features.append('Frente e Verso')
        if 'colorida' in name_lower or 'color' in name_lower:
            features.append('Colorida')
        if 'monocromática' in name_lower or 'mono' in name_lower:
            features.append('Monocromática')
        
        # Modelos específicos
        if re.search(r'[mp]\d+', name_lower):
            model_match = re.search(r'([mp]\d+[a-z]*)', name_lower)
            if model_match:
                features.append(model_match.group(1).upper())
        
        return features

    def _make_title_unique(self, base_title: str, product_data: Dict[str, Any]) -> str:
        """Torna título único adicionando identificador"""
        produto_id = product_data.get('produto_id', '')
        codigo = product_data.get('codigo', '')
        
        # Tentar com código do produto
        if codigo:
            unique_title = f"{base_title} ({codigo})"
            if len(unique_title) <= self.max_title_length and self.is_title_unique(unique_title):
                return unique_title
        
        # Tentar com ID do produto
        if produto_id:
            unique_title = f"{base_title} (ID: {produto_id})"
            if len(unique_title) <= self.max_title_length and self.is_title_unique(unique_title):
                return unique_title
        
        # Usar hash curto como último recurso
        hash_short = hashlib.md5(base_title.encode()).hexdigest()[:6]
        unique_title = f"{base_title} (#{hash_short})"
        
        return unique_title

    def is_title_unique(self, title: str) -> bool:
        """
        Verifica se o título é único no banco de dados
        
        Args:
            title: Título a verificar
            
        Returns:
            True se for único
        """
        try:
            if not os.path.exists(self.db_path):
                return True  # Se não existe DB, é único
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM articles WHERE titulo = ?", (title,))
                result = cursor.fetchone()
                
                return result is None
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar unicidade do título: {e}")
            return True  # Em caso de erro, assumir que é único

    def generate_unique_slug(self, title: str, product_data: Dict[str, Any]) -> str:
        """
        Gera slug único e descritivo
        
        Args:
            title: Título do artigo
            product_data: Dados do produto
            
        Returns:
            Slug único e otimizado
        """
        try:
            # Gerar slug base a partir do título
            base_slug = self._create_base_slug(title)
            
            # Verificar se é único
            if self.is_slug_unique(base_slug):
                logger.debug(f"✅ Slug único gerado: {base_slug}")
                return base_slug
            
            # Se não for único, adicionar identificadores
            unique_slug = self._make_slug_unique(base_slug, product_data)
            
            logger.debug(f"✅ Slug com identificador único: {unique_slug}")
            return unique_slug
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de slug único: {e}")
            # Fallback
            fallback_slug = f"produto-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return fallback_slug

    def _create_base_slug(self, title: str) -> str:
        """Cria slug base a partir do título"""
        if not title:
            return "produto"
        
        # Converter para minúsculas
        slug = title.lower()
        
        # Remover acentos
        slug = unicodedata.normalize('NFD', slug)
        slug = ''.join(char for char in slug if unicodedata.category(char) != 'Mn')
        
        # Substituir caracteres especiais por hífens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        
        # Remover palavras irrelevantes mantendo as importantes
        words = slug.split('-')
        meaningful_words = []
        
        for word in words:
            if (word not in self.stop_words and 
                len(word) > 2 and 
                word.isalpha()):
                meaningful_words.append(word)
        
        # Manter máximo 6 palavras para não ficar muito longo
        if len(meaningful_words) > 6:
            meaningful_words = meaningful_words[:6]
        
        slug = '-'.join(meaningful_words) if meaningful_words else 'produto'
        
        # Limitar tamanho
        if len(slug) > self.max_slug_length:
            words = slug.split('-')
            truncated_words = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= self.max_slug_length:
                    truncated_words.append(word)
                    current_length += len(word) + 1
                else:
                    break
            
            slug = '-'.join(truncated_words)
        
        return slug.strip('-')

    def _make_slug_unique(self, base_slug: str, product_data: Dict[str, Any]) -> str:
        """Torna slug único adicionando identificadores"""
        # Estratégia 1: Adicionar código do produto
        codigo = product_data.get('codigo', '')
        if codigo:
            # Limpar código para slug
            codigo_clean = re.sub(r'[^\w-]', '', codigo.lower())
            unique_slug = f"{base_slug}-{codigo_clean}"
            
            if len(unique_slug) <= self.max_slug_length and self.is_slug_unique(unique_slug):
                return unique_slug
        
        # Estratégia 2: Adicionar ID do produto
        produto_id = product_data.get('produto_id', '')
        if produto_id:
            id_clean = str(produto_id).replace('/', '-').replace(' ', '-').lower()
            unique_slug = f"{base_slug}-{id_clean}"
            
            if len(unique_slug) <= self.max_slug_length and self.is_slug_unique(unique_slug):
                return unique_slug
        
        # Estratégia 3: Adicionar timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_slug = f"{base_slug}-{timestamp}"
        
        if len(unique_slug) <= self.max_slug_length and self.is_slug_unique(unique_slug):
            return unique_slug
        
        # Estratégia 4: Hash curto como último recurso
        hash_short = hashlib.md5(base_slug.encode()).hexdigest()[:6]
        unique_slug = f"{base_slug}-{hash_short}"
        
        # Se ainda for muito longo, truncar base_slug
        if len(unique_slug) > self.max_slug_length:
            max_base_length = self.max_slug_length - len(f"-{hash_short}")
            base_truncated = base_slug[:max_base_length]
            unique_slug = f"{base_truncated}-{hash_short}"
        
        return unique_slug

    def is_slug_unique(self, slug: str) -> bool:
        """
        Verifica se o slug é único no banco de dados
        
        Args:
            slug: Slug a verificar
            
        Returns:
            True se for único
        """
        try:
            if not os.path.exists(self.db_path):
                return True  # Se não existe DB, é único
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM articles WHERE slug = ?", (slug,))
                result = cursor.fetchone()
                
                return result is None
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar unicidade do slug: {e}")
            return True  # Em caso de erro, assumir que é único

    def generate_automatic_alt_tag(self, product_data: Dict[str, Any]) -> str:
        """
        Gera alt tag automática baseada no produto
        
        Args:
            product_data: Dados do produto
            
        Returns:
            Alt tag otimizada para SEO
        """
        try:
            # Extrair informações básicas
            nome = product_data.get('produto_nome', '') or product_data.get('titulo', '')
            tipo = self._extract_product_type(nome)
            marca = self._extract_brand(nome)
            
            # Construir alt tag
            alt_parts = []
            
            # Adicionar tipo se identificado
            if tipo and tipo not in ['produto', 'generico']:
                alt_parts.append(tipo.title())
            
            # Adicionar marca se identificada
            if marca and marca != 'Genérica':
                alt_parts.append(marca)
            
            # Adicionar nome limpo (sem marca/tipo já incluídos)
            nome_limpo = nome
            if marca:
                nome_limpo = nome_limpo.replace(marca, '').strip()
            if tipo:
                nome_limpo = nome_limpo.replace(tipo.title(), '').replace(tipo.lower(), '').strip()
            
            # Limpar caracteres extras
            nome_limpo = re.sub(r'\s+', ' ', nome_limpo).strip()
            
            if nome_limpo:
                alt_parts.append(nome_limpo)
            
            # Se ainda não temos nada, usar nome completo
            if not alt_parts:
                alt_parts = [nome or 'Produto']
            
            # Construir alt tag final
            alt_tag = ' '.join(alt_parts)
            
            # Limitar tamanho (125 caracteres é ideal para SEO)
            if len(alt_tag) > 125:
                alt_tag = alt_tag[:122] + "..."
            
            # Garantir que termina sem pontuação desnecessária
            alt_tag = alt_tag.rstrip('.,;:')
            
            logger.debug(f"🖼️ Alt tag gerada: '{alt_tag}'")
            return alt_tag
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar alt tag: {e}")
            # Fallback básico
            nome = product_data.get('produto_nome', '') or product_data.get('titulo', '') or 'Produto'
            return nome[:125]
    
    def _extract_product_type(self, product_name: str) -> str:
        """
        Extrai tipo do produto baseado no nome
        
        Args:
            product_name: Nome do produto
            
        Returns:
            Tipo identificado
        """
        if not product_name:
            return 'produto'
        
        name_lower = product_name.lower()
        
        # Tipos específicos com alta prioridade
        type_patterns = {
            'impressora': ['impressora', 'printer'],
            'multifuncional': ['multifuncional', 'multifuncion', 'all-in-one', 'all in one'],
            'scanner': ['scanner', 'digitalizador'],
            'toner': ['toner', 'cartucho'],
            'papel': ['papel', 'sulfite', 'folha'],
            'copiadora': ['copiadora', 'copiador'],
            'suprimento': ['suprimento', 'consumivel'],
            'fax': ['fax'],
            'plotter': ['plotter']
        }
        
        for tipo, patterns in type_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return tipo
        
        return 'produto'
    
    def validate_readability_score(self, content: str, keyword: str = None) -> Dict[str, Any]:
        """
        Valida pontuação de legibilidade Yoast SEO
        
        Args:
            content: Conteúdo HTML a ser validado
            keyword: Palavra-chave principal (opcional)
            
        Returns:
            Dicionário com pontuação e detalhes de legibilidade
        """
        try:
            # Extrair texto puro
            text_content = re.sub(r'<[^>]+>', '', content)
            words = text_content.split()
            sentences = re.split(r'[.!?]+', text_content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Critérios de validação
            validation_results = {}
            
            # 1. VALIDAR PARÁGRAFOS CURTOS (máx 120 palavras)
            paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
            paragraph_scores = []
            
            for para in paragraphs:
                para_text = re.sub(r'<[^>]+>', '', para)
                para_words = len(para_text.split())
                paragraph_scores.append(para_words <= 120)
            
            validation_results['short_paragraphs'] = {
                'score': sum(paragraph_scores) / len(paragraph_scores) * 100 if paragraph_scores else 100,
                'total_paragraphs': len(paragraphs),
                'compliant_paragraphs': sum(paragraph_scores),
                'passed': all(paragraph_scores) if paragraph_scores else True
            }
            
            # 2. VALIDAR FRASES CURTAS (máx 20 palavras)
            sentence_scores = []
            for sentence in sentences:
                sentence_words = len(sentence.split())
                sentence_scores.append(sentence_words <= 20)
            
            validation_results['short_sentences'] = {
                'score': sum(sentence_scores) / len(sentence_scores) * 100 if sentence_scores else 100,
                'total_sentences': len(sentences),
                'compliant_sentences': sum(sentence_scores),
                'passed': sum(sentence_scores) / len(sentence_scores) >= 0.75 if sentence_scores else True
            }
            
            # 3. VALIDAR PALAVRAS DE TRANSIÇÃO (mín 30%)
            transition_count = 0
            for word in self.transition_words:
                transition_count += text_content.lower().count(word.lower())
            
            total_sentences = len(sentences)
            transition_percentage = (transition_count / total_sentences * 100) if total_sentences > 0 else 0
            
            validation_results['transition_words'] = {
                'score': min(transition_percentage * 3.33, 100),  # 30% = 100 pontos
                'transition_count': transition_count,
                'total_sentences': total_sentences,
                'percentage': transition_percentage,
                'passed': transition_percentage >= 30
            }
            
            # 4. VALIDAR VOZ ATIVA (mín 60%)
            passive_indicators = [
                'foi', 'foram', 'são', 'é', 'está', 'estão', 'sendo', 'sido',
                'foi feito', 'foi realizado', 'foi desenvolvido', 'é considerado'
            ]
            
            passive_count = 0
            for indicator in passive_indicators:
                passive_count += text_content.lower().count(indicator)
            
            active_voice_percentage = max(0, 100 - (passive_count / total_sentences * 100)) if total_sentences > 0 else 100
            
            validation_results['active_voice'] = {
                'score': active_voice_percentage,
                'passive_indicators': passive_count,
                'total_sentences': total_sentences,
                'percentage': active_voice_percentage,
                'passed': active_voice_percentage >= 60
            }
            
            # 5. VALIDAR SUBTÍTULOS (a cada 300 palavras)
            total_words = len(words)
            headings = len(re.findall(r'<h[2-6][^>]*>', content))
            expected_headings = max(1, total_words // 300)
            
            validation_results['heading_distribution'] = {
                'score': min(headings / expected_headings * 100, 100) if expected_headings > 0 else 100,
                'total_headings': headings,
                'expected_headings': expected_headings,
                'total_words': total_words,
                'passed': headings >= expected_headings
            }
            
            # 6. VALIDAR DENSIDADE DE PALAVRA-CHAVE (0.5-2.5%)
            keyword_density = 0
            if keyword:
                keyword_count = text_content.lower().count(keyword.lower())
                keyword_density = (keyword_count / len(words) * 100) if words else 0
            
            validation_results['keyword_density'] = {
                'score': 100 if 0.5 <= keyword_density <= 2.5 else max(0, 100 - abs(keyword_density - 1.5) * 20),
                'keyword_count': text_content.lower().count(keyword.lower()) if keyword else 0,
                'total_words': len(words),
                'density_percentage': keyword_density,
                'passed': 0.5 <= keyword_density <= 2.5 if keyword else True
            }
            
            # CALCULAR PONTUAÇÃO GERAL
            all_scores = [
                validation_results['short_paragraphs']['score'],
                validation_results['short_sentences']['score'],
                validation_results['transition_words']['score'],
                validation_results['active_voice']['score'],
                validation_results['heading_distribution']['score'],
                validation_results['keyword_density']['score']
            ]
            
            overall_score = sum(all_scores) / len(all_scores)
            all_passed = all([
                validation_results['short_paragraphs']['passed'],
                validation_results['short_sentences']['passed'],
                validation_results['transition_words']['passed'],
                validation_results['active_voice']['passed'],
                validation_results['heading_distribution']['passed'],
                validation_results['keyword_density']['passed']
            ])
            
            # Determinar nível Yoast
            if overall_score >= 90 and all_passed:
                yoast_level = 'GREEN'
                yoast_message = 'Excelente legibilidade!'
            elif overall_score >= 70:
                yoast_level = 'ORANGE'
                yoast_message = 'Boa legibilidade, mas pode melhorar.'
            else:
                yoast_level = 'RED'
                yoast_message = 'Legibilidade precisa de melhorias.'
            
            return {
                'overall_score': round(overall_score, 1),
                'yoast_level': yoast_level,
                'yoast_message': yoast_message,
                'all_criteria_passed': all_passed,
                'detailed_results': validation_results,
                'recommendations': self._generate_readability_recommendations(validation_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de legibilidade: {e}")
            return {
                'overall_score': 0,
                'yoast_level': 'ERROR',
                'yoast_message': 'Erro na validação',
                'all_criteria_passed': False,
                'detailed_results': {},
                'recommendations': ['Erro na análise de legibilidade']
            }
    
    def _generate_readability_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        if not results['short_paragraphs']['passed']:
            recommendations.append(f"Reduza parágrafos longos: {results['short_paragraphs']['total_paragraphs'] - results['short_paragraphs']['compliant_paragraphs']} parágrafos têm mais de 120 palavras")
        
        if not results['short_sentences']['passed']:
            recommendations.append(f"Encurte frases longas: {results['short_sentences']['total_sentences'] - results['short_sentences']['compliant_sentences']} frases têm mais de 20 palavras")
        
        if not results['transition_words']['passed']:
            recommendations.append(f"Adicione mais palavras de transição: apenas {results['transition_words']['percentage']:.1f}% das frases as usam (mínimo 30%)")
        
        if not results['active_voice']['passed']:
            recommendations.append(f"Use mais voz ativa: apenas {results['active_voice']['percentage']:.1f}% do texto está em voz ativa (mínimo 60%)")
        
        if not results['heading_distribution']['passed']:
            recommendations.append(f"Adicione mais subtítulos: {results['heading_distribution']['total_headings']} encontrados, {results['heading_distribution']['expected_headings']} esperados")
        
        if not results['keyword_density']['passed']:
            if results['keyword_density']['density_percentage'] < 0.5:
                recommendations.append("Aumente a densidade da palavra-chave (mínimo 0.5%)")
            elif results['keyword_density']['density_percentage'] > 2.5:
                recommendations.append("Reduza a densidade da palavra-chave (máximo 2.5%)")
        
        return recommendations

    # ... resto dos métodos existentes ...
 
 
 
 