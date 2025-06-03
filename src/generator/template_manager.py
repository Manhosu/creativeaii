"""
Template Manager
Gerenciamento de templates específicos por tipo de produto
OTIMIZADO PARA YOAST SEO - ESTRUTURA HTML E LINKS
"""

from typing import Dict, Any, List
from loguru import logger

class TemplateManager:
    """Gerenciador de templates para diferentes tipos de produtos - Otimizado para Yoast"""
    
    def __init__(self):
        """Inicializa o gerenciador de templates"""
        self.templates = self._load_templates()
        logger.info("📄 Template Manager inicializado - Otimizado para Yoast SEO")
    
    def get_template(self, product_type: str) -> Dict[str, Any]:
        """
        Retorna template específico para tipo de produto
        
        Args:
            product_type: Tipo do produto
            
        Returns:
            Template configurado para Yoast SEO
        """
        template = self.templates.get(product_type, self.templates['produto_generico'])
        logger.debug(f"📄 Template selecionado: {product_type}")
        return template
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Carrega todos os templates disponíveis otimizados para Yoast"""
        return {
            'impressora': {
                'structure_guide': """
                1. Introdução (1 parágrafo de 50-100 palavras)
                   - Por que uma boa impressora é essencial
                   - Mencionar marca/modelo específico
                   - Link externo obrigatório para Creative Cópias
                
                2. H2: "Principais Características da [KEYWORD]" (lista com 4-6 benefícios)
                   - Itens com máximo 15 palavras cada
                   - Use palavras de transição: "Além disso", "Também", "Principalmente"
                   
                3. H2: "Ideal para Qual Ambiente" (1-2 parágrafos de 80-120 palavras)
                   - Descrição de uso específico
                   - Voz ativa: "oferece", "proporciona", "garante"
                   
                4. H3: "Vantagens Técnicas da [KEYWORD]" (especificações em lista)
                   - Máximo 150 palavras total
                   - Sentenças de 10-18 palavras
                   
                5. Conclusão e Call-to-Action (1 parágrafo de 60-100 palavras)
                   - Reforce palavra-chave
                   - Link interno ou externo
                """,
                'key_topics': [
                    'qualidade_impressao',
                    'velocidade',
                    'economia_tinta', 
                    'conectividade',
                    'facilidade_uso',
                    'volume_impressao',
                    'durabilidade'
                ],
                'content_focus': 'produtividade e economia para empresas',
                'tone_emphasis': 'benefícios técnicos e ROI',
                'target_audience': 'escritórios e empresas',
                'seo_keywords': ['impressora', 'escritório', 'produtividade', 'economia'],
                'content_length': 'medium',  # 400-600 palavras
                'technical_level': 'intermediate',
                'required_links': [
                    {'anchor': 'impressora', 'url': 'https://creativecopias.com.br', 'type': 'external'},
                    {'anchor': 'equipamento de escritório', 'url': 'interno', 'type': 'internal'}
                ],
                'html_structure': {
                    'max_paragraph_words': 150,
                    'max_sentence_words': 20,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong', 'a']
                }
            },
            
            'multifuncional': {
                'structure_guide': """
                1. Introdução - Versatilidade da multifuncional (1 parágrafo)
                   - Máximo 100 palavras
                   - Link externo obrigatório no primeiro parágrafo
                   
                2. H2: "Múltiplas Funções em Um Só [KEYWORD]" (lista)
                   - 4-6 itens em lista HTML <ul>
                   - Cada item: máximo 12 palavras
                   
                3. H2: "Economia de Espaço e Recursos" (2 parágrafos)
                   - Primeiro parágrafo: 80-120 palavras
                   - Segundo parágrafo: 60-100 palavras
                   - Use transições: "Além disso", "Portanto"
                   
                4. H3: "Conectividade e Facilidade de Uso" (recursos)
                   - Lista de recursos técnicos
                   - Voz ativa predominante
                   
                5. Conclusão - Solução Completa (1 parágrafo)
                   - Reforce keyword principal
                   - Call-to-action final
                """,
                'key_topics': [
                    'versatilidade',
                    'economia_espaco',
                    'imprimir_copiar_escanear',
                    'conectividade_wireless',
                    'facilidade_operacao',
                    'qualidade_digitalizacao',
                    'custo_beneficio'
                ],
                'content_focus': 'versatilidade e economia de espaço',
                'tone_emphasis': 'solução completa e praticidade',
                'target_audience': 'escritórios pequenos e médios',
                'seo_keywords': ['multifuncional', 'impressora scanner', 'all-in-one', 'escritório'],
                'content_length': 'medium',
                'technical_level': 'basic',
                'required_links': [
                    {'anchor': 'multifuncional', 'url': 'https://creativecopias.com.br', 'type': 'external'}
                ],
                'html_structure': {
                    'max_paragraph_words': 120,
                    'max_sentence_words': 18,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong', 'a']
                }
            },
            
            'toner': {
                'structure_guide': """
                1. Introdução - Importância do toner de qualidade (1 parágrafo)
                   - 70-100 palavras
                   - Link externo obrigatório
                   
                2. H2: "Alto Rendimento e Economia da [KEYWORD]" (números/benefícios)
                   - Lista com dados específicos
                   - Use números concretos quando possível
                   
                3. H2: "Qualidade de Impressão Superior" (características)
                   - 2 parágrafos curtos (60-90 palavras cada)
                   - Transições: "Consequentemente", "Dessa forma"
                   
                4. H3: "Compatibilidade e Facilidade de Instalação" (instruções)
                   - Lista de passos simples
                   - Voz ativa: "você instala", "você conecta"
                   
                5. Conclusão - Investimento Inteligente (1 parágrafo)
                   - 60-80 palavras
                   - Reforce benefício principal
                """,
                'key_topics': [
                    'rendimento_paginas',
                    'qualidade_impressao',
                    'compatibilidade',
                    'custo_pagina',
                    'facilidade_instalacao',
                    'garantia_qualidade',
                    'economia_longo_prazo'
                ],
                'content_focus': 'economia e qualidade de impressão',
                'tone_emphasis': 'custo-benefício e rendimento',
                'target_audience': 'usuários de impressoras laser',
                'seo_keywords': ['toner', 'cartucho', 'rendimento', 'economia'],
                'content_length': 'short',  # 300-400 palavras
                'technical_level': 'basic',
                'required_links': [
                    {'anchor': 'toner', 'url': 'https://creativecopias.com.br', 'type': 'external'}
                ],
                'html_structure': {
                    'max_paragraph_words': 100,
                    'max_sentence_words': 16,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong']
                }
            },
            
            'papel': {
                'structure_guide': """
                1. Introdução - Papel certo para cada necessidade (1 parágrafo)
                   - 80-120 palavras
                   - Link para Creative Cópias
                   
                2. H2: "Qualidade e Especificações do [KEYWORD]" (características)
                   - Lista técnica organizada
                   - Gramatura, brancura, formato
                   
                3. H2: "Aplicações Recomendadas" (usos práticos)
                   - 2 parágrafos: 70-100 palavras cada
                   - Exemplos concretos de uso
                   
                4. H3: "Vantagens da Qualidade Superior" (benefícios)
                   - Lista de 4-5 benefícios
                   - Sentenças diretas e objetivas
                   
                5. Conclusão - Escolha Inteligente (1 parágrafo)
                   - Reforce qualidade e versatilidade
                """,
                'key_topics': [
                    'gramatura',
                    'brancura',
                    'qualidade_impressao',
                    'resistencia',
                    'aplicacoes_diversas',
                    'compatibilidade_impressoras',
                    'acabamento_profissional'
                ],
                'content_focus': 'qualidade de impressão e versatilidade',
                'tone_emphasis': 'qualidade do resultado final',
                'target_audience': 'usuários exigentes com qualidade',
                'seo_keywords': ['papel', 'impressão', 'qualidade', 'escritório'],
                'content_length': 'short',
                'technical_level': 'basic',
                'required_links': [
                    {'anchor': 'papel de qualidade', 'url': 'https://creativecopias.com.br', 'type': 'external'}
                ],
                'html_structure': {
                    'max_paragraph_words': 120,
                    'max_sentence_words': 16,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong']
                }
            },
            
            'scanner': {
                'structure_guide': """
                1. Introdução - Digitalização eficiente de documentos (1 parágrafo)
                   - 90-130 palavras
                   - Link externo obrigatório
                   
                2. H2: "Qualidade de Digitalização da [KEYWORD]" (especificações)
                   - Lista técnica: DPI, velocidade, formatos
                   - Dados específicos e números
                   
                3. H2: "Velocidade e Praticidade" (recursos)
                   - 2 parágrafos: produtividade e facilidade
                   - Transições claras entre ideias
                   
                4. H3: "Conectividade e Software Incluído" (facilidades)
                   - Lista de recursos de conectividade
                   - Software e compatibilidade
                   
                5. Conclusão - Produtividade Digital (1 parágrafo)
                   - Benefícios consolidados
                   - Call-to-action
                """,
                'key_topics': [
                    'qualidade_digitalizacao',
                    'velocidade_scan',
                    'resolucao_dpi',
                    'conectividade',
                    'software_incluido',
                    'facilidade_uso',
                    'formatos_arquivo'
                ],
                'content_focus': 'digitalização profissional e eficiência',
                'tone_emphasis': 'produtividade e qualidade digital',
                'target_audience': 'escritórios que digitalizam documentos',
                'seo_keywords': ['scanner', 'digitalização', 'documentos', 'produtividade'],
                'content_length': 'medium',
                'technical_level': 'intermediate',
                'required_links': [
                    {'anchor': 'scanner', 'url': 'https://creativecopias.com.br', 'type': 'external'}
                ],
                'html_structure': {
                    'max_paragraph_words': 130,
                    'max_sentence_words': 18,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong', 'a']
                }
            },
            
            'copiadora': {
                'structure_guide': """
                1. Introdução - Reprodução eficiente de documentos (1 parágrafo)
                   - Apresentação da necessidade
                   - Link para produto original
                   
                2. H2: "Velocidade e Volume de Cópias da [KEYWORD]" (capacidades)
                   - Dados de desempenho
                   - Volume mensal recomendado
                   
                3. H2: "Qualidade de Reprodução" (características)
                   - Resolução e fidelidade
                   - Tipos de documentos compatíveis
                   
                4. H3: "Recursos Avançados" (funcionalidades)
                   - Lista de recursos especiais
                   - Facilidades operacionais
                   
                5. Conclusão - Eficiência Garantida (1 parágrafo)
                   - Benefícios consolidados para empresas
                """,
                'key_topics': [
                    'velocidade_copia',
                    'volume_mensal',
                    'qualidade_reproducao',
                    'recursos_avancados',
                    'facilidade_operacao',
                    'durabilidade',
                    'custo_operacional'
                ],
                'content_focus': 'eficiência e volume de produção',
                'tone_emphasis': 'produtividade empresarial',
                'target_audience': 'empresas com alto volume de cópias',
                'seo_keywords': ['copiadora', 'reprodução', 'eficiência', 'volume'],
                'content_length': 'medium',
                'technical_level': 'intermediate',
                'required_links': [
                    {'anchor': 'copiadora', 'url': 'https://creativecopias.com.br', 'type': 'external'}
                ],
                'html_structure': {
                    'max_paragraph_words': 140,
                    'max_sentence_words': 20,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong']
                }
            },
            
            'produto_generico': {
                'structure_guide': """
                1. Introdução - Apresentação do produto (1 parágrafo)
                   - 80-120 palavras
                   - Link externo obrigatório para Creative Cópias
                   
                2. H2: "Principais Características do [KEYWORD]" (benefícios)
                   - Lista organizada de benefícios
                   - 4-6 itens principais
                   
                3. H2: "Aplicações e Benefícios" (uso prático)
                   - Como o produto resolve problemas
                   - Cenários de uso específicos
                   
                4. H3: "Especificações Técnicas" (detalhes)
                   - Informações técnicas relevantes
                   - Compatibilidade e requisitos
                   
                5. Conclusão - Escolha Inteligente (1 parágrafo)
                   - Síntese dos benefícios
                   - Reforce a palavra-chave principal
                """,
                'key_topics': [
                    'qualidade',
                    'eficiencia',
                    'praticidade',
                    'economia',
                    'produtividade',
                    'confiabilidade'
                ],
                'content_focus': 'benefícios gerais e praticidade',
                'tone_emphasis': 'qualidade e confiabilidade',
                'target_audience': 'usuários profissionais',
                'seo_keywords': ['produto', 'qualidade', 'escritório', 'profissional'],
                'content_length': 'medium',
                'technical_level': 'basic',
                'required_links': [
                    {'anchor': 'produto', 'url': 'https://creativecopias.com.br', 'type': 'external'}
                ],
                'html_structure': {
                    'max_paragraph_words': 120,
                    'max_sentence_words': 18,
                    'min_headings': 3,
                    'required_elements': ['ul', 'strong']
                }
            }
        }
    
    def get_content_guidelines(self, product_type: str) -> Dict[str, str]:
        """
        Retorna diretrizes específicas de conteúdo para Yoast
        
        Args:
            product_type: Tipo do produto
            
        Returns:
            Diretrizes otimizadas para Yoast SEO
        """
        template = self.get_template(product_type)
        
        return {
            'length_target': self._get_word_count_target(template['content_length']),
            'tone': template['tone_emphasis'],
            'audience': template['target_audience'],
            'focus': template['content_focus'],
            'technical_level': template['technical_level'],
            'readability_rules': {
                'max_sentence_words': template['html_structure']['max_sentence_words'],
                'max_paragraph_words': template['html_structure']['max_paragraph_words'],
                'required_transition_percentage': 30,
                'active_voice_percentage': 80,
                'min_headings': template['html_structure']['min_headings']
            },
            'seo_requirements': {
                'keyword_in_title': True,
                'keyword_in_h2': True,
                'external_links_min': 1,
                'internal_links_suggested': 1,
                'meta_description_length': '120-155',
                'title_length': '30-60'
            }
        }
    
    def get_seo_recommendations(self, product_type: str) -> Dict[str, Any]:
        """
        Retorna recomendações específicas de SEO para o tipo de produto
        
        Args:
            product_type: Tipo do produto
            
        Returns:
            Recomendações otimizadas para Yoast
        """
        template = self.get_template(product_type)
        
        return {
            'primary_keywords': template['seo_keywords'],
            'title_patterns': self._generate_title_suggestions(product_type),
            'meta_description_template': self._get_meta_description_template(product_type),
            'heading_suggestions': self._generate_heading_suggestions(product_type),
            'required_links': template.get('required_links', []),
            'html_structure': template['html_structure'],
            'content_length': template['content_length'],
            'keyword_density_target': '0.5-2.5%',
            'readability_target': 'Yoast Green Score'
        }
    
    def _get_word_count_target(self, length_category: str) -> Dict[str, int]:
        """Retorna contagem de palavras alvo baseada na categoria"""
        targets = {
            'short': {'min': 300, 'ideal': 400, 'max': 500},
            'medium': {'min': 400, 'ideal': 550, 'max': 700},
            'long': {'min': 600, 'ideal': 800, 'max': 1000}
        }
        return targets.get(length_category, targets['medium'])
    
    def _generate_heading_suggestions(self, product_type: str) -> List[str]:
        """Gera sugestões de headings otimizados com palavra-chave"""
        base_suggestions = {
            'impressora': [
                "Principais Características da {keyword}",
                "Benefícios da {keyword} para Escritório", 
                "Como a {keyword} Aumenta Produtividade",
                "Especificações Técnicas da {keyword}",
                "Por Que Escolher Esta {keyword}"
            ],
            'multifuncional': [
                "Funcionalidades da {keyword}",
                "Vantagens da {keyword} All-in-One",
                "Como a {keyword} Economiza Espaço",
                "Conectividade da {keyword}",
                "Benefícios da {keyword} para Pequenas Empresas"
            ],
            'toner': [
                "Rendimento do {keyword}",
                "Qualidade de Impressão do {keyword}",
                "Economia com {keyword} Original",
                "Compatibilidade do {keyword}",
                "Instalação Fácil do {keyword}"
            ],
            'scanner': [
                "Qualidade de Digitalização do {keyword}",
                "Velocidade do {keyword}",
                "Software Incluído com {keyword}",
                "Conectividade do {keyword}",
                "Formatos Suportados pelo {keyword}"
            ]
        }
        
        return base_suggestions.get(product_type, [
            "Características Principais da {keyword}",
            "Benefícios da {keyword}",
            "Como Usar a {keyword}",
            "Especificações da {keyword}"
        ])
    
    def _get_meta_description_template(self, product_type: str) -> str:
        """Retorna template de meta descrição para o tipo de produto"""
        templates = {
            'impressora': "Conheça a {keyword} e suas características. Ideal para escritório, oferece qualidade e economia. Veja especificações e benefícios.",
            'multifuncional': "Descubra a {keyword} multifuncional: imprime, copia e digitaliza. Perfeita para empresas. Confira recursos e vantagens.",
            'toner': "Toner {keyword} com alto rendimento e qualidade superior. Economia garantida para sua impressora. Veja características.",
            'scanner': "Scanner {keyword} com alta resolução e velocidade. Ideal para digitalização profissional. Descubra funcionalidades.",
            'papel': "Papel {keyword} com qualidade superior para todas as impressões. Ideal para escritório. Conheça especificações."
        }
        
        return templates.get(product_type, "Conheça a {keyword} e suas principais características. Ideal para uso profissional. Veja benefícios e especificações.")
    
    def validate_template(self, product_type: str, generated_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida se o conteúdo gerado atende aos critérios do template Yoast
        
        Args:
            product_type: Tipo do produto
            generated_content: Conteúdo gerado para validar
            
        Returns:
            Relatório de validação com pontuação Yoast estimada
        """
        template = self.get_template(product_type)
        validation_results = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'suggestions': [],
            'yoast_compliance': {}
        }
        
        # Validar estrutura HTML
        content = generated_content.get('conteudo', '')
        title = generated_content.get('titulo', '')
        meta_desc = generated_content.get('meta_descricao', '')
        keyword = generated_content.get('primary_keyword', '')
        
        # 1. Validar título (20 pontos)
        title_score = 0
        if title:
            if 30 <= len(title) <= 60:
                title_score += 15
                validation_results['yoast_compliance']['title_length'] = 'green'
            else:
                validation_results['issues'].append(f"Título deve ter 30-60 caracteres (atual: {len(title)})")
                validation_results['yoast_compliance']['title_length'] = 'red'
            
            if keyword.lower() in title.lower():
                title_score += 5
                validation_results['yoast_compliance']['keyword_in_title'] = 'green'
            else:
                validation_results['issues'].append("Palavra-chave deve aparecer no título")
                validation_results['yoast_compliance']['keyword_in_title'] = 'red'
        
        validation_results['score'] += title_score
        
        # 2. Validar meta descrição (20 pontos)
        meta_score = 0
        if meta_desc:
            if 120 <= len(meta_desc) <= 155:
                meta_score += 15
                validation_results['yoast_compliance']['meta_length'] = 'green'
            else:
                validation_results['issues'].append(f"Meta descrição deve ter 120-155 caracteres (atual: {len(meta_desc)})")
                validation_results['yoast_compliance']['meta_length'] = 'orange'
            
            if keyword.lower() in meta_desc.lower():
                meta_score += 5
                validation_results['yoast_compliance']['keyword_in_meta'] = 'green'
            else:
                validation_results['issues'].append("Palavra-chave deve aparecer na meta descrição")
                validation_results['yoast_compliance']['keyword_in_meta'] = 'red'
        
        validation_results['score'] += meta_score
        
        # 3. Validar estrutura de conteúdo (30 pontos)
        content_score = 0
        if content:
            # Verificar headings
            import re
            h2_count = len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE))
            h3_count = len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE))
            
            if h2_count >= 2:
                content_score += 10
                validation_results['yoast_compliance']['headings'] = 'green'
            else:
                validation_results['issues'].append("Deve haver pelo menos 2 subtítulos H2")
                validation_results['yoast_compliance']['headings'] = 'orange'
            
            # Verificar palavra-chave em headings
            headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', content, re.IGNORECASE)
            has_keyword_in_heading = any(keyword.lower() in heading.lower() for heading in headings)
            if has_keyword_in_heading:
                content_score += 10
                validation_results['yoast_compliance']['keyword_in_headings'] = 'green'
            else:
                validation_results['issues'].append("Palavra-chave deve aparecer em pelo menos um subtítulo")
                validation_results['yoast_compliance']['keyword_in_headings'] = 'red'
            
            # Verificar links externos
            if 'href=' in content and 'target="_blank"' in content:
                content_score += 10
                validation_results['yoast_compliance']['external_links'] = 'green'
            else:
                validation_results['issues'].append("Deve haver pelo menos 1 link externo")
                validation_results['yoast_compliance']['external_links'] = 'red'
        
        validation_results['score'] += content_score
        
        # 4. Validar legibilidade (30 pontos)
        readability_score = 0
        if content:
            # Remover HTML para análise
            text_content = re.sub(r'<[^>]+>', '', content)
            sentences = re.split(r'[.!?]+', text_content)
            
            # Verificar comprimento das sentenças
            long_sentences = sum(1 for s in sentences if len(s.split()) > 20)
            if len(sentences) > 0:
                long_sentence_percentage = (long_sentences / len(sentences)) * 100
                if long_sentence_percentage <= 25:  # 75% das sentenças são curtas
                    readability_score += 15
                    validation_results['yoast_compliance']['sentence_length'] = 'green'
                else:
                    validation_results['suggestions'].append("Reduza o tamanho das sentenças (máx 20 palavras)")
                    validation_results['yoast_compliance']['sentence_length'] = 'orange'
            
            # Verificar palavras de transição (simplificado)
            transition_words = ['além disso', 'portanto', 'por exemplo', 'no entanto', 'então', 'assim']
            transition_count = sum(1 for tw in transition_words if tw in text_content.lower())
            if transition_count >= 3:
                readability_score += 15
                validation_results['yoast_compliance']['transitions'] = 'green'
            else:
                validation_results['suggestions'].append("Adicione mais palavras de transição")
                validation_results['yoast_compliance']['transitions'] = 'orange'
        
        validation_results['score'] += readability_score
        
        # Determinar status geral
        final_score = validation_results['score']
        if final_score >= 80:
            validation_results['status'] = 'green'
            validation_results['message'] = "Excelente! Atende critérios Yoast para pontuação verde"
        elif final_score >= 60:
            validation_results['status'] = 'orange'  
            validation_results['message'] = "Bom, mas pode melhorar para atingir pontuação verde"
        else:
            validation_results['status'] = 'red'
            validation_results['message'] = "Precisa de melhorias significativas para Yoast"
        
        return validation_results

    # ... resto dos métodos existentes ...
 
 
 
 