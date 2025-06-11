"""
Template Manager
Gerenciamento de templates específicos por tipo de produto
OTIMIZADO PARA YOAST SEO - ESTRUTURA HTML E LINKS
"""

from typing import Dict, Any, List
from loguru import logger
import re
import random

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
                1. Introdução (1 parágrafo de 60-80 palavras, frases curtas)
                   - "A [KEYWORD] é uma solução ideal para escritórios modernos."
                   - "Além disso, oferece qualidade profissional a preço justo."
                   - "Portanto, representa um investimento inteligente."
                   - Link para Creative Cópias no primeiro parágrafo
                
                2. H2: "Principais Benefícios da [KEYWORD]" (lista com transições)
                   - "Em primeiro lugar, garante impressões nítidas."
                   - "Além disso, economiza tinta significativamente."
                   - "Também oferece conectividade wireless."
                   - "Finalmente, possui design compacto."
                   
                3. H2: "Para Quem é Indicada" (2 parágrafos de 80-100 palavras cada)
                   - Primeiro parágrafo: uso empresarial
                   - "Esta impressora atende empresas pequenas e médias."
                   - "No entanto, também funciona bem em home offices."
                   - Segundo parágrafo: especificações técnicas
                   - "Por outro lado, oferece velocidade superior."
                   
                4. H3: "Recursos que Fazem a Diferença" (lista técnica simplificada)
                   - Frases máximo 15 palavras
                   - "Consequentemente, você economiza tempo e dinheiro."
                   - "Assim sendo, a produtividade aumenta."
                   
                5. Conclusão (1 parágrafo de 70-90 palavras)
                   - "Em suma, a [KEYWORD] é uma escolha acertada."
                   - "Por isso, recomendamos esta impressora."
                   - Call-to-action claro e direto
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
                1. Introdução - Versatilidade simplificada (1 parágrafo, 70-90 palavras)
                   - "A [KEYWORD] combina múltiplas funções em um só equipamento."
                   - "Além disso, economiza espaço e dinheiro."
                   - "Portanto, é perfeita para escritórios eficientes."
                   - Link Creative Cópias no primeiro parágrafo
                   
                2. H2: "Três Funções em Uma Máquina" (lista clara)
                   - "Primeiro, imprime com qualidade profissional."
                   - "Segundo, digitaliza documentos rapidamente."
                   - "Terceiro, copia páginas com nitidez."
                   - "Assim, você tem tudo em um aparelho."
                   
                3. H2: "Economia Inteligente" (2 parágrafos curtos, 80-100 palavras cada)
                   - Primeiro: economia de espaço
                   - "Esta multifuncional ocupa pouco espaço na mesa."
                   - "Consequentemente, libera área para outras atividades."
                   - Segundo: economia financeira
                   - "Por outro lado, reduz custos de manutenção."
                   
                4. H3: "Fácil de Usar e Conectar" (recursos simples)
                   - "Conecta facilmente via Wi-Fi."
                   - "Também funciona com cabo USB."
                   - "Dessa forma, atende diferentes necessidades."
                   
                5. Conclusão (1 parágrafo, 70-90 palavras)
                   - "Em resumo, a [KEYWORD] oferece versatilidade total."
                   - "Por isso, é um investimento inteligente."
                   - "Portanto, recomendamos esta solução completa."
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

    def _clean_template_variables(self, content: str) -> str:
        """
        Remove variáveis de template não substituídas que causam erro 404
        
        Args:
            content: Conteúdo HTML
            
        Returns:
            Conteúdo limpo sem variáveis não substituídas
        """
        try:
            # Remover tags <img> com {{ FEATURED_IMAGE_URL }}
            content = re.sub(r'<figure[^>]*>.*?{{ FEATURED_IMAGE_URL }}.*?</figure>', '', content, flags=re.DOTALL)
            content = re.sub(r'<img[^>]*{{ FEATURED_IMAGE_URL }}[^>]*>', '', content)
            
            # Remover outras variáveis de template não substituídas
            template_patterns = [
                r'{{ FEATURED_IMAGE_URL }}',
                r'{{{{ FEATURED_IMAGE_URL }}}}',
                r'{{ [A-Z_]+ }}',
                r'{{{{ [A-Z_]+ }}}}'
            ]
            
            for pattern in template_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Limpar tags vazias resultantes
            content = re.sub(r'<figure[^>]*>\s*</figure>', '', content)
            content = re.sub(r'<figcaption[^>]*>\s*</figcaption>', '', content)
            
            # Limpar linhas em branco extras
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            logger.debug("🧹 Variáveis de template não substituídas removidas")
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar variáveis de template: {e}")
            return content

    def apply_yoast_html_structure(self, content: str, product_name: str) -> str:
        """
        Aplica estrutura HTML semântica otimizada para Yoast SEO
        
        Args:
            content: Conteúdo HTML original
            product_name: Nome do produto para alt tags
            
        Returns:
            Conteúdo com estrutura HTML otimizada
        """
        try:
            logger.debug("🎯 Aplicando estrutura HTML para Yoast...")
            
            # 1. Garantir H1 como título principal
            content = self._ensure_h1_structure(content, product_name)
            
            # 2. Adicionar imagem destacada (se disponível)
            # Não adicionar imagem automática - apenas se fornecida explicitamente
            # content = self._add_featured_image(content, product_name, image_url=None)
            
            # 3. Otimizar parágrafos (máx 3-4 linhas)
            content = self._optimize_paragraph_structure(content)
            
            # 4. Adicionar subtítulos a cada 300 palavras
            content = self._add_headings_by_word_count(content, product_name)
            
            # 5. Converter listas simples em HTML semântico
            content = self._enhance_lists_semantic(content)
            
            # 6. Adicionar tags <strong> e <em> estratégicas
            content = self._add_emphasis_tags(content, product_name)
            
            # 7. Inserir palavras de transição quando faltarem
            content = self._inject_transition_words(content)
            
            # 8. Adicionar alt tags automáticas em imagens
            content = self._add_automatic_alt_tags(content, product_name)
            
            # 9. Garantir sentenças simples (máx 20 palavras)
            content = self._simplify_sentences(content)
            
            # 10. Limpar variáveis de template não substituídas
            content = self._clean_template_variables(content)
            
            logger.debug("✅ Estrutura HTML Yoast aplicada")
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro na estrutura HTML Yoast: {e}")
            return content
    
    def _ensure_h1_structure(self, content: str, product_name: str) -> str:
        """Garante que existe um H1 como título principal"""
        if '<h1>' not in content:
            # Se não tem H1, converter primeiro H2 em H1
            content = re.sub(r'<h2([^>]*)>(.*?)</h2>', r'<h1\1>\2</h1>', content, count=1)
        return content
    
    def _add_featured_image(self, content: str, product_name: str, image_url: str = None) -> str:
        """
        Adiciona imagem destacada no início do conteúdo
        
        Args:
            content: Conteúdo HTML
            product_name: Nome do produto para alt tag
            image_url: URL real da imagem (opcional)
            
        Returns:
            Conteúdo com imagem destacada ou conteúdo original se não houver imagem
        """
        try:
            # Verificar se já existe uma imagem no início
            if re.match(r'^\s*<img[^>]*>', content.strip()):
                logger.debug("📸 Imagem já presente no início do conteúdo")
                return content
            
            # Se não há URL de imagem, não adicionar placeholder
            if not image_url or image_url.strip() == "":
                logger.debug("📸 Nenhuma URL de imagem fornecida, pulando imagem destacada")
                return content
            
            # Gerar alt tag baseada no produto
            alt_tag = self._generate_alt_tag_from_product(product_name)
            
            # Criar HTML da imagem destacada com URL REAL
            featured_image_html = f'''<figure class="featured-image">
    <img src="{image_url}" alt="{alt_tag}" title="{product_name}" class="wp-image-featured" loading="lazy" />
    <figcaption>{product_name}</figcaption>
</figure>

'''
            
            # Inserir logo após o H1
            h1_pattern = r'(<h1[^>]*>.*?</h1>)'
            if re.search(h1_pattern, content, re.DOTALL):
                content = re.sub(h1_pattern, r'\1\n' + featured_image_html, content, count=1, flags=re.DOTALL)
            else:
                # Se não tem H1, inserir no início
                content = featured_image_html + content
            
            logger.debug(f"📸 Imagem destacada adicionada com URL: '{image_url}' e alt: '{alt_tag}'")
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar imagem destacada: {e}")
            return content
    
    def _generate_alt_tag_from_product(self, product_name: str) -> str:
        """Gera alt tag otimizada baseada no nome do produto"""
        if not product_name:
            return "Produto de escritório"
        
        # Extrair informações do nome
        name_lower = product_name.lower()
        
        # Identificar tipo
        tipo = 'Produto'
        if 'impressora' in name_lower:
            tipo = 'Impressora'
        elif 'multifuncional' in name_lower:
            tipo = 'Multifuncional'
        elif 'scanner' in name_lower:
            tipo = 'Scanner'
        elif 'toner' in name_lower:
            tipo = 'Toner'
        elif 'papel' in name_lower:
            tipo = 'Papel'
        
        # Identificar marca
        marcas = ['HP', 'Canon', 'Epson', 'Brother', 'Samsung', 'Xerox', 'Ricoh', 'Lexmark']
        marca_encontrada = None
        for marca in marcas:
            if marca.lower() in name_lower:
                marca_encontrada = marca
                break
        
        # Construir alt tag evitando duplicação
        alt_parts = []
        
        if tipo != 'Produto':
            alt_parts.append(tipo)
        
        if marca_encontrada:
            alt_parts.append(marca_encontrada)
        
        # Adicionar nome limpo (sem tipo e marca já incluídos)
        nome_limpo = product_name
        if marca_encontrada:
            nome_limpo = nome_limpo.replace(marca_encontrada, '').strip()
        if tipo != 'Produto':
            nome_limpo = nome_limpo.replace(tipo, '').replace(tipo.lower(), '').strip()
        
        # Limpar espaços extras
        nome_limpo = re.sub(r'\s+', ' ', nome_limpo).strip()
        
        if nome_limpo:
            alt_parts.append(nome_limpo)
        elif not alt_parts:  # Se não temos nada, usar nome completo
            alt_parts.append(product_name)
        
        alt_tag = ' '.join(alt_parts)
        
        # Limitar tamanho (125 caracteres é ideal)
        if len(alt_tag) > 125:
            alt_tag = alt_tag[:122] + "..."
        
        return alt_tag
    
    def _optimize_paragraph_structure(self, content: str) -> str:
        """Otimiza parágrafos para máximo 3-4 linhas (aproximadamente 150 palavras) preservando URLs"""
        def split_long_paragraph(match):
            paragraph_content = match.group(1)
            
            # Verificar se há URLs no parágrafo - se sim, não processar para evitar quebrar links
            if 'href=' in paragraph_content or 'http' in paragraph_content:
                return match.group(0)  # Manter original
            
            words = paragraph_content.split()
            
            if len(words) > 150:  # Parágrafo muito longo
                # Dividir em parágrafos menores
                chunks = []
                current_chunk = []
                
                for word in words:
                    current_chunk.append(word)
                    if len(current_chunk) >= 75:  # Ponto de divisão
                        # Procurar ponto final próximo
                        chunk_text = ' '.join(current_chunk)
                        last_period = chunk_text.rfind('.')
                        if last_period > 50:  # Se tem ponto final decente
                            chunks.append(chunk_text[:last_period+1])
                            current_chunk = chunk_text[last_period+1:].split()
                        else:
                            chunks.append(chunk_text)
                            current_chunk = []
                
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                return '</p>\n<p>'.join(f'<p>{chunk.strip()}' for chunk in chunks if chunk.strip()) + '</p>'
            
            return match.group(0)  # Manter original se não for muito longo
        
        return re.sub(r'<p>(.*?)</p>', split_long_paragraph, content, flags=re.DOTALL)
    
    def _add_headings_by_word_count(self, content: str, product_name: str) -> str:
        """Adiciona subtítulos a cada 300 palavras aproximadamente"""
        # Contar palavras no texto
        text_only = re.sub(r'<[^>]+>', '', content)
        word_count = len(text_only.split())
        
        if word_count > 300:
            # Calcular onde inserir headings
            paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
            current_words = 0
            heading_suggestions = [
                f"Características Avançadas do {product_name}",
                f"Benefícios Práticos da {product_name}",
                f"Aplicações Recomendadas",
                f"Vantagens Competitivas",
                f"Especificações Técnicas Detalhadas"
            ]
            
            modified_content = content
            heading_index = 0
            
            for i, paragraph in enumerate(paragraphs):
                paragraph_words = len(re.sub(r'<[^>]+>', '', paragraph).split())
                current_words += paragraph_words
                
                if current_words >= 300 and heading_index < len(heading_suggestions):
                    # Inserir heading após este parágrafo
                    heading = f"<h3>{heading_suggestions[heading_index]}</h3>"
                    old_p = f"<p>{paragraph}</p>"
                    new_p = f"<p>{paragraph}</p>\n{heading}"
                    modified_content = modified_content.replace(old_p, new_p, 1)
                    current_words = 0
                    heading_index += 1
            
            return modified_content
        
        return content
    
    def _enhance_lists_semantic(self, content: str) -> str:
        """Converte listas simples em HTML semântico com <ul> e <ol>"""
        # Detectar listas de traços/números e converter
        lines = content.split('\n')
        enhanced_lines = []
        in_list = False
        list_items = []
        list_type = None
        
        for line in lines:
            stripped = line.strip()
            
            # Detectar início de lista
            if re.match(r'^[-•*]\s+', stripped) or re.match(r'^\d+[.)]\s+', stripped):
                if not in_list:
                    in_list = True
                    list_type = 'ol' if re.match(r'^\d+[.)]\s+', stripped) else 'ul'
                    list_items = []
                
                # Extrair item da lista
                item_text = re.sub(r'^[-•*\d+.)]\s+', '', stripped)
                list_items.append(f"<li>{item_text}</li>")
            
            elif in_list and stripped == '':
                # Linha vazia pode continuar lista
                continue
            
            elif in_list:
                # Fim da lista
                list_html = f"<{list_type}>\n" + '\n'.join(list_items) + f"\n</{list_type}>"
                enhanced_lines.append(list_html)
                enhanced_lines.append(line)
                in_list = False
                list_items = []
            
            else:
                enhanced_lines.append(line)
        
        # Finalizar lista se terminou no final
        if in_list and list_items:
            list_html = f"<{list_type}>\n" + '\n'.join(list_items) + f"\n</{list_type}>"
            enhanced_lines.append(list_html)
        
        return '\n'.join(enhanced_lines)
    
    def _add_emphasis_tags(self, content: str, product_name: str) -> str:
        """Adiciona tags <strong> e <em> para termos importantes"""
        # Palavras-chave para destacar com <strong>
        strong_keywords = [
            product_name.lower(),
            'qualidade',
            'economia',
            'produtividade',
            'eficiência',
            'tecnologia',
            'performance',
            'rendimento'
        ]
        
        # Palavras para <em> (ênfase)
        em_keywords = [
            'ideal',
            'perfeito',
            'excelente',
            'superior',
            'avançado',
            'inovador'
        ]
        
        # Aplicar <strong> (máximo 3 por parágrafo)
        def add_strong_tags(match):
            paragraph = match.group(1)
            strong_count = 0
            
            for keyword in strong_keywords:
                if strong_count >= 3:
                    break
                if keyword in paragraph.lower() and f'<strong>{keyword}' not in paragraph.lower():
                    # Encontrar primeira ocorrência e substituir
                    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                    if pattern.search(paragraph):
                        paragraph = pattern.sub(f'<strong>{keyword}</strong>', paragraph, count=1)
                        strong_count += 1
            
            return f'<p>{paragraph}</p>'
        
        content = re.sub(r'<p>(.*?)</p>', add_strong_tags, content, flags=re.DOTALL)
        
        # Aplicar <em> de forma mais seletiva
        em_count = 0
        for keyword in em_keywords:
            if keyword in content.lower() and em_count < 2:  # Limitar uso de <em>
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                if pattern.search(content):
                    content = pattern.sub(f'<em>{keyword}</em>', content, count=1)
                    em_count += 1
        
        return content
    
    def _inject_transition_words(self, content: str) -> str:
        """Adiciona palavras de transição onde necessário"""
        transition_words = [
            'Além disso',
            'Portanto',
            'Consequentemente',
            'Por exemplo',
            'Em primeiro lugar',
            'Finalmente',
            'Dessa forma',
            'Assim sendo'
        ]
        
        paragraphs = content.split('</p>')
        enhanced_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if '<p>' in paragraph and i > 0:  # Não modificar primeiro parágrafo
                # Verificar se já tem palavra de transição
                paragraph_text = re.sub(r'<[^>]+>', '', paragraph).strip()
                has_transition = any(tw.lower() in paragraph_text.lower() for tw in transition_words)
                
                if not has_transition and len(paragraph_text) > 50:  # Só em parágrafos substanciais
                    # Adicionar palavra de transição aleatória
                    transition = random.choice(transition_words)
                    paragraph = paragraph.replace('<p>', f'<p>{transition}, ', 1)
            
            enhanced_paragraphs.append(paragraph)
        
        return '</p>'.join(enhanced_paragraphs)
    
    def _add_automatic_alt_tags(self, content: str, product_name: str) -> str:
        """Adiciona automaticamente alt tags em todas as imagens"""
        def add_alt_tag(match):
            img_tag = match.group(0)
            
            # Verificar se já tem alt tag
            if 'alt=' in img_tag:
                return img_tag  # Manter existente
            
            # Gerar alt tag baseado no produto
            alt_text = f"{product_name} - Equipamento de alta qualidade"
            
            # Inserir alt tag antes do fechamento da tag
            if img_tag.endswith('/>'):
                return img_tag[:-2] + f' alt="{alt_text}" />'
            elif img_tag.endswith('>'):
                return img_tag[:-1] + f' alt="{alt_text}">'
            
            return img_tag
        
        # Aplicar em todas as tags <img>
        return re.sub(r'<img[^>]*>', add_alt_tag, content, flags=re.IGNORECASE)
    
    def _simplify_sentences(self, content: str) -> str:
        """Simplifica sentenças muito longas (máximo 20 palavras) preservando URLs"""
        def simplify_paragraph(match):
            paragraph = match.group(1)
            
            # Verificar se há URLs no parágrafo - se sim, não processar para evitar quebrar links
            if 'href=' in paragraph or 'http' in paragraph:
                return f'<p>{paragraph}</p>'
            
            sentences = re.split(r'([.!?]+)', paragraph)
            simplified_sentences = []
            
            for i in range(0, len(sentences), 2):  # Pegar frases e pontuação
                sentence = sentences[i].strip()
                punctuation = sentences[i+1] if i+1 < len(sentences) else '.'
                
                if sentence:
                    words = sentence.split()
                    if len(words) > 20:
                        # Dividir frase longa
                        mid_point = len(words) // 2
                        part1 = ' '.join(words[:mid_point])
                        part2 = ' '.join(words[mid_point:])
                        simplified_sentences.append(f"{part1}. {part2}{punctuation}")
                    else:
                        simplified_sentences.append(f"{sentence}{punctuation}")
            
            return f'<p>{" ".join(simplified_sentences)}</p>'
        
        return re.sub(r'<p>(.*?)</p>', simplify_paragraph, content, flags=re.DOTALL)
    
    def generate_yoast_optimized_content(self, product_type: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera estrutura de conteúdo completamente otimizada para Yoast verde
        
        Args:
            product_type: Tipo do produto
            product_data: Dados do produto
            
        Returns:
            Estrutura HTML otimizada para Yoast
        """
        template = self.get_template(product_type)
        product_name = product_data.get('nome', 'produto')
        
        # Estrutura base otimizada
        content_structure = {
            'titulo': f"{product_name}: Análise Completa e Review",
            'meta_descricao': f"{product_name}: características, especificações, preços e onde comprar. Confira nossa análise detalhada e avaliação completa.",
            'focus_keyword': product_name.split()[0].lower() if product_name else 'produto',
            'conteudo': self._generate_optimized_html_content(product_name, template),
            'html_structure': {
                'headings_count': 4,
                'paragraphs_optimized': True,
                'lists_semantic': True,
                'images_with_alt': True,
                'transition_words': True,
                'emphasis_tags': True
            }
        }
        
        return content_structure
    
    def _generate_optimized_html_content(self, product_name: str, template: Dict[str, Any]) -> str:
        """Gera conteúdo HTML seguindo exatamente os critérios do Yoast"""
        content = f"""
<h1>{product_name}: Guia Completo de Características e Benefícios</h1>

<p>O <strong>{product_name}</strong> representa uma solução avançada para ambientes profissionais. Além disso, oferece características técnicas que garantem produtividade e economia. Portanto, é uma escolha inteligente para empresas que buscam <em>eficiência</em> e qualidade superior.</p>

<h2>Principais Características do {product_name}</h2>
<ul>
    <li>Tecnologia de impressão de <strong>alta resolução</strong></li>
    <li>Velocidade otimizada para volumes médios e altos</li>
    <li>Conectividade USB e rede para máxima flexibilidade</li>
    <li>Interface intuitiva para operação simplificada</li>
    <li>Ciclo de trabalho robusto para uso intensivo</li>
</ul>

<p>Consequentemente, estas características fazem do <strong>{product_name}</strong> uma opção <em>ideal</em> para escritórios modernos. Em primeiro lugar, a qualidade de impressão atende aos padrões mais exigentes.</p>

<h3>Benefícios Práticos para Seu Escritório</h3>
<p>O equipamento proporciona economia significativa de tempo e recursos. Dessa forma, sua empresa ganha em produtividade diária. Finalmente, o custo-benefício torna-se evidente no médio prazo.</p>

<h2>Aplicações Recomendadas</h2>
<ol>
    <li>Impressão de documentos corporativos</li>
    <li>Relatórios financeiros e apresentações</li>
    <li>Material promocional de alta qualidade</li>
    <li>Documentação técnica e manuais</li>
</ol>

<p>Por exemplo, em ambientes onde a <strong>qualidade</strong> é fundamental, o {product_name} demonstra sua superioridade. Assim sendo, atende desde pequenas empresas até corporações de grande porte.</p>

<h3>Especificações Técnicas Avançadas</h3>
<p>As especificações técnicas incluem conectividade universal e compatibilidade abrangente. Além disso, os recursos de segurança garantem proteção dos dados corporativos. Portanto, oferece tranquilidade total para o ambiente empresarial.</p>

        <p>Para adquirir o <strong>{product_name}</strong>, consulte nossa <a href="https://www.creativecopias.com.br/impressoras" target="_blank" rel="noopener">seleção completa de equipamentos</a> e encontre a melhor opção para sua empresa.</p>
"""
        
        return content.strip()

    # ... resto dos métodos existentes ...
 
 
 
 