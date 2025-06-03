"""
SEO Optimizer
Otimização de conteúdo para SEO: slugs, meta tags, headings
OTIMIZADO PARA YOAST SEO - PONTUAÇÃO VERDE
"""

import re
import unicodedata
from typing import Dict, List, Optional, Any
from loguru import logger

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
            optimized = article_data.copy()
            
            # Extrair palavra-chave principal do título/produto
            primary_keyword = self._extract_primary_keyword(optimized)
            optimized['primary_keyword'] = primary_keyword
            
            # Otimizar título SEO (máx 60 chars + keyword)
            if 'titulo' in optimized:
                optimized['titulo'] = self.optimize_title_yoast(optimized['titulo'], primary_keyword)
            
            # Gerar/otimizar slug com keyword
            optimized['slug'] = self.generate_seo_slug(optimized.get('titulo', ''), primary_keyword)
            
            # Otimizar meta descrição (120-155 chars + keyword)
            if 'meta_descricao' in optimized:
                optimized['meta_descricao'] = self.optimize_meta_description_yoast(
                    optimized['meta_descricao'], primary_keyword
                )
            elif 'conteudo' in optimized:
                optimized['meta_descricao'] = self.generate_meta_description_yoast(
                    optimized['conteudo'], primary_keyword
                )
            
            # Otimizar conteúdo para legibilidade Yoast
            if 'conteudo' in optimized:
                optimized['conteudo'] = self.optimize_content_readability(
                    optimized['conteudo'], primary_keyword
                )
            
            # Otimizar tags
            if 'tags' in optimized:
                optimized['tags'] = self.optimize_tags_yoast(optimized['tags'], primary_keyword)
            
            # Adicionar dados estruturados
            optimized['seo_data'] = self.generate_structured_data_yoast(optimized)
            
            # Validar pontuação Yoast
            optimized['yoast_score'] = self.calculate_yoast_score(optimized)
            
            logger.debug("✅ Artigo otimizado para Yoast SEO - Pontuação Verde")
            return optimized
            
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
        
        Args:
            title: Título original
            keyword: Palavra-chave principal
            
        Returns:
            Título otimizado para Yoast
        """
        if not title:
            return f"{keyword.title()}: Características e Benefícios"
        
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
        
        Args:
            text: Texto para converter em slug
            keyword: Palavra-chave principal
            
        Returns:
            Slug otimizado para SEO
        """
        if not text and not keyword:
            return "produto"
        
        # Usar keyword como base se texto não disponível
        if not text:
            text = keyword
        
        # Converter para minúsculas
        slug = text.lower()
        
        # Remover acentos
        slug = unicodedata.normalize('NFD', slug)
        slug = ''.join(char for char in slug if unicodedata.category(char) != 'Mn')
        
        # Substituir espaços e caracteres especiais por hífens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        
        # Garantir que keyword está no slug
        keyword_slug = re.sub(r'[^\w\s-]', '', keyword.lower())
        keyword_slug = re.sub(r'[\s_-]+', '-', keyword_slug)
        
        if keyword_slug not in slug:
            # Adicionar keyword no início
            slug = f"{keyword_slug}-{slug}"
        
        # Remover palavras irrelevantes (mas manter keyword)
        words = slug.split('-')
        meaningful_words = []
        keyword_words = keyword_slug.split('-')
        
        for word in words:
            if word in keyword_words or (word not in self.stop_words and len(word) > 2):
                meaningful_words.append(word)
        
        if meaningful_words:
            slug = '-'.join(meaningful_words[:6])  # Máximo 6 palavras
        
        # Limitar tamanho
        if len(slug) > self.max_slug_length:
            words = slug.split('-')
            # Manter keyword no início
            keyword_count = len(keyword_words)
            remaining_words = words[keyword_count:keyword_count+3]  # 3 palavras extras
            slug = '-'.join(keyword_words + remaining_words)
        
        # Limpar início e fim
        slug = slug.strip('-')
        
        return slug or "produto"
    
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

    # ... resto dos métodos existentes ...
 
 
 
 