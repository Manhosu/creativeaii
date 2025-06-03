"""
Prompt Builder
Construção de prompts inteligentes para geração de conteúdo com IA
"""

from typing import Dict, List, Optional, Any
from loguru import logger

class PromptBuilder:
    """Construtor de prompts para IA"""
    
    def __init__(self):
        """Inicializa o construtor de prompts"""
        self.base_instructions = """
        Você é um especialista em redação publicitária e SEO para produtos de escritório, 
        especialmente impressoras, multifuncionais, toners e suprimentos.
        
        Seu objetivo é criar artigos envolventes que:
        1. Sejam otimizados para SEO
        2. Tenham tom profissional mas acessível
        3. Destaquem benefícios práticos
        4. Incluam call-to-action sutil
        5. Sejam únicos e originais
        """
        
        self.tone_variations = {
            "profissional": {
                "style": "formal e técnico",
                "voice": "autoridade no assunto",
                "approach": "dados técnicos e benefícios empresariais"
            },
            "vendedor": {
                "style": "persuasivo e convincente", 
                "voice": "consultivo e entusiástico",
                "approach": "benefícios diretos e urgência"
            },
            "amigável": {
                "style": "casual e acessível",
                "voice": "próximo e prestativo", 
                "approach": "linguagem simples e exemplos práticos"
            }
        }
        
        logger.info("✍️ Prompt Builder inicializado")
    
    def build_prompt(self, product: Dict[str, Any], 
                    template: Dict[str, Any],
                    custom_keywords: List[str] = None,
                    custom_instructions: str = None,
                    tone: str = "profissional") -> str:
        """
        Constrói prompt completo para geração de artigo
        
        Args:
            product: Dados do produto
            template: Template específico para tipo de produto
            custom_keywords: Palavras-chave extras
            custom_instructions: Instruções personalizadas
            tone: Tom do artigo
            
        Returns:
            Prompt completo para IA
        """
        try:
            # Extrair dados do produto
            nome = product.get('nome', 'Produto')
            marca = product.get('marca', '')
            preco = self._format_price(product.get('preco'))
            descricao = product.get('descricao', '')
            categoria_url = product.get('categoria_url', '')
            
            # Determinar categoria
            categoria = self._extract_category_from_url(categoria_url)
            
            # Obter configurações de tom
            tone_config = self.tone_variations.get(tone, self.tone_variations["profissional"])
            
            # Construir seções do prompt
            context_section = self._build_context_section(product, categoria)
            instructions_section = self._build_instructions_section(tone_config, template)
            content_requirements = self._build_content_requirements(product, custom_keywords)
            format_requirements = self._build_format_requirements()
            
            # Instruções personalizadas
            custom_section = ""
            if custom_instructions:
                custom_section = f"\n\n## INSTRUÇÕES PERSONALIZADAS:\n{custom_instructions}"
            
            # Montar prompt final
            prompt = f"""
{self.base_instructions}

{context_section}

{instructions_section}

{content_requirements}

{format_requirements}

{custom_section}

## DADOS DO PRODUTO:
- Nome: {nome}
- Marca: {marca if marca else 'N/A'}
- Preço: {preco}
- Descrição: {descricao if descricao else 'N/A'}
- Categoria: {categoria}

IMPORTANTE: Retorne APENAS um JSON válido com a estrutura especificada, sem texto adicional antes ou depois.
            """
            
            logger.debug(f"✍️ Prompt construído: {len(prompt)} caracteres")
            return prompt.strip()
            
        except Exception as e:
            logger.error(f"❌ Erro ao construir prompt: {e}")
            return self._build_fallback_prompt(product)
    
    def _build_context_section(self, product: Dict[str, Any], categoria: str) -> str:
        """Constrói seção de contexto do prompt"""
        nome = product.get('nome', 'Produto')
        
        return f"""
## CONTEXTO:
Você está criando um artigo sobre "{nome}" para o site Creative Cópias, 
uma empresa especializada em soluções para escritório.

O público-alvo são:
- Empresários e gestores de escritório
- Profissionais liberais
- Responsáveis por compras corporativas
- Pessoas que trabalham em home office

A categoria do produto é: {categoria}
        """
    
    def _build_instructions_section(self, tone_config: Dict[str, str], template: Dict[str, Any]) -> str:
        """Constrói seção de instruções baseada no tom"""
        return f"""
## INSTRUÇÕES DE REDAÇÃO AVANÇADA:

### Tom e Estilo:
- Estilo: {tone_config['style']}
- Voz: {tone_config['voice']}
- Abordagem: {tone_config['approach']}

### DIRETRIZES SEO PREMIUM:

1. **TÍTULO IRRESISTÍVEL:**
   - Comece com a palavra-chave principal
   - Use números quando possível ("5 Motivos", "Top 7")
   - Inclua ano atual (2025) para frescor
   - Máximo 60 caracteres EXATOS
   - EXEMPLOS: "HP LaserJet Pro M404n: 5 Benefícios que Você Precisa Conhecer"

2. **META DESCRIÇÃO MAGNÉTICA:**
   - 120-155 caracteres para visualização perfeita
   - Comece com verbo de ação ("Descubra", "Conheça", "Aprenda")
   - Inclua benefício único e específico
   - Termine com urgência ("Veja agora!", "Confira já!")
   - EXEMPLO: "Descubra a HP LaserJet Pro M404n: economia de 50% + velocidade profissional. Ideal para escritórios modernos. Veja já!"

3. **ESTRUTURA HTML TÉCNICA:**
   - **H1**: Repetir título exato (SEO fundamental)
   - **H2**: Mínimo 4 subtítulos com palavras-chave
   - **H3**: Para subdivisões quando necessário
   - **Parágrafos**: Máximo 4 linhas cada
   - **Listas**: Pelo menos 2 listas (UL ou OL)
   - **Strong**: 5-8 palavras destacadas estrategicamente

4. **COPYWRITING PERSUASIVO:**
   - Use "você" para conectar com o leitor
   - Inclua benefícios emocionais, não só técnicos
   - Crie senso de urgência sutil
   - Adicione prova social quando possível
   - Termine seções com micro-CTAs

5. **DENSIDADE DE PALAVRA-CHAVE:**
   - Palavra-chave principal: 1-2% do texto total
   - Variações e sinônimos espalhados naturalmente
   - Long-tail keywords nos subtítulos
   - Evite keyword stuffing (nunca forçar)

6. **ELEMENTOS DE CONVERSÃO:**
   - Pain points específicos do público
   - Benefícios únicos e diferenciados
   - Comparações sutis com concorrência
   - Caso de uso específico e detalhado
   - Call-to-action no final

### ✅ **REGRAS YOAST SEO VERDE (OBRIGATÓRIAS):**

        🎯 **CONTEÚDO MÍNIMO:**
        - **300+ palavras** no texto principal (sem contar HTML)
        - Artigos de produtos devem ter 350-450 palavras idealmente
        - Se necessário, expanda com especificações técnicas, comparações, casos de uso

        🔗 **LINKS OBRIGATÓRIOS:**
        - **1 LINK INTERNO** para Creative Cópias: "confira nossa seleção completa de [categoria]"
        - **1 LINK EXTERNO** para site oficial da marca com rel="nofollow"
        - Links devem ter target="_blank" para abertura em nova aba

        🖼️ **IMAGENS:** Não incluir imagens automáticas nos artigos

        📝 **FRASE-CHAVE (FOCUS KEYWORD):**
        - Extrair 2-3 palavras principais do nome do produto
        - EXEMPLOS: "HP LaserJet Pro" (não "HP LaserJet Pro M404n Impressora Multifuncional...")
        - Usar nos primeiros 100 caracteres do texto
        - Incluir em pelo menos 1 H2
        - Densidade: 0.5-2.5% do texto total

        ⚡ **LEGIBILIDADE YOAST:**
        - **Frases ≤ 20 palavras** (75% das frases)
        - **Palavras de transição** em 30% das frases: "além disso", "portanto", "por exemplo"
        - **Parágrafos ≤ 100 palavras** cada
        - **Voz ativa** predominante: "oferece" em vez de "é oferecido"
        - **Listas com 3+ itens** reais e específicos

        📏 **COMPRIMENTOS EXATOS:**
        - **Título:** 30-60 caracteres (incluindo palavra-chave no início)
        - **Meta descrição:** 120-155 caracteres (incluindo palavra-chave no início)
        - **Slug:** gerado automaticamente, mas otimizado

### ESTRUTURA OBRIGATÓRIA:

```html
<h1>[TÍTULO EXATO COM KEYWORD NO INÍCIO]</h1>

<p>Escolha o artigo correto (A/O) baseado no produto. [PRODUTO] é uma excelente opção para [contexto]. [Continuação com benefício principal]. Além disso, [benefício secundário]. Para mais opções, <a href="https://blog.creativecopias.com.br/categoria/impressoras/" target="_blank">confira nossa seleção completa de impressoras</a>. Mais informações técnicas estão disponíveis no <a href="[SITE_OFICIAL_MARCA]" target="_blank" rel="nofollow">site oficial da [MARCA]</a>.</p>

<h2>Principais Características do [KEYWORD]</h2>
<!-- Imagem removida conforme solicitação -->
<ul>
    <li>[Característica 1 específica]</li>
    <li>[Característica 2 específica]</li>
    <li>[Característica 3 específica]</li>
    <li>[Característica 4 específica]</li>
</ul>
<p>[Parágrafo explicativo ≤100 palavras]. Consequentemente, [resultado]. Por exemplo, [caso de uso].</p>

<h2>Ideal para Qual Ambiente de Trabalho</h2>
<p>[Descrição específica ≤100 palavras]. Portanto, [benefício]. Em primeiro lugar, [vantagem principal]. Assim, [resultado esperado].</p>

<h3>Especificações Técnicas do [KEYWORD]</h3>
<ol>
    <li>[Spec técnica 1]</li>
    <li>[Spec técnica 2]</li>
    <li>[Spec técnica 3]</li>
</ol>

<h2>Vale a Pena Investir no [KEYWORD]?</h2>
<p>[Conclusão ≤100 palavras]. Em suma, [resumo do valor]. Finalmente, [call to action sutil].</p>
```

### ELEMENTOS TÉCNICOS AVANÇADOS:

- **LSI Keywords**: Use sinônimos naturais (impressora = equipamento, dispositivo)
- **Semântica**: Conecte conceitos relacionados
- **User Intent**: Atenda exatamente o que o usuário busca
- **Featured Snippets**: Structure para conquistar posição zero
- **Tempo de Leitura**: 3-5 minutos ideal (800-1200 palavras)

### EVITAR ABSOLUTAMENTE:
- Repetição excessiva de palavras-chave
- Promessas impossíveis ou exageradas  
- Linguagem muito técnica sem explicação
- Parágrafos longos (máximo 4 linhas)
- Falta de call-to-action
- Conteúdo genérico sem personalidade

### Estrutura Recomendada:
{template.get('structure_guide', self._get_default_structure())}

### INSTRUÇÕES CRÍTICAS PARA URLs:

**ATENÇÃO - URLs DEVEM ESTAR SEMPRE CORRETAS:**
- NUNCA adicione espaços em URLs
- URLs devem ser: https://blog.creativecopias.com.br/categoria/impressoras/
- JAMAIS: https://blog. creativecopias. com. br/categoria/impressoras/
- JAMAIS: https://www. hp. com/br-pt/
- SEMPRE: https://www.hp.com/br-pt/

### ESTRUTURA OBRIGATÓRIA:
        """
    
    def _build_content_requirements(self, product: Dict[str, Any], custom_keywords: List[str]) -> str:
        """Constrói requisitos específicos de conteúdo"""
        nome = product.get('nome', 'Produto')
        marca = product.get('marca', '')
        
        # Palavras-chave automáticas
        auto_keywords = [nome, marca] if marca else [nome]
        auto_keywords.extend(['impressora', 'escritório', 'qualidade', 'eficiência'])
        
        # Adicionar palavras-chave personalizadas
        all_keywords = auto_keywords
        if custom_keywords:
            all_keywords.extend(custom_keywords)
        
        # Remover duplicatas e vazios
        keywords = list(set([kw for kw in all_keywords if kw]))
        
        return f"""
## REQUISITOS DE CONTEÚDO:

### Palavras-chave para incluir naturalmente:
{', '.join(keywords[:10])}

### Tópicos obrigatórios:
1. Principais benefícios do produto
2. Para quem é indicado
3. Diferenciais competitivos
4. Aplicações práticas no dia a dia

### Evitar:
- Informações técnicas excessivamente complexas
- Promessas impossíveis ou exageradas
- Repetição excessiva de palavras-chave
- Conteúdo genérico demais
        """
    
    def _build_format_requirements(self) -> str:
        """Constrói requisitos de formatação"""
        return """
## FORMATO DE RESPOSTA OBRIGATÓRIO:

Retorne um JSON válido com exatamente esta estrutura:

{
    "titulo": "Título chamativo e otimizado para SEO (máximo 60 caracteres)",
    "meta_descricao": "Descrição para mecanismos de busca (máximo 155 caracteres)",
    "conteudo": "Conteúdo HTML do artigo com tags <h1>, <h2>, <h3>, <p>, <ul>, <li>, <strong>",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]
}

### REQUISITOS SEO PREMIUM:

**Título (CRUCIAL para SEO):**
- MÁXIMO 60 caracteres (incluindo espaços)
- Incluir palavra-chave principal NO INÍCIO
- Usar números quando possível ("5 Motivos", "Top 10")
- Incluir termos como "Melhor", "2025", "Guia Completo"
- Ser clicável e criar curiosidade
- EXEMPLOS: "HP LaserJet Pro: 5 Motivos para Escolher em 2025"

**Meta Descrição (FUNDAMENTAL):**
- MÁXIMO 155 caracteres precisos
- Incluir palavra-chave principal
- Incluir call-to-action ("Descubra", "Conheça", "Veja")
- Mencionar benefício único
- Usar urgência sutil ("Agora", "Hoje")
- EXEMPLO: "Descubra a HP LaserJet Pro M404n: economia de até 50% em impressões. Ideal para escritórios modernos. Veja agora!"

**Conteúdo HTML SUPER OTIMIZADO:**

ESTRUTURA OBRIGATÓRIA:
1. <h1>Título Principal</h1> (repetir o título)
2. Parágrafo introdutório (150-200 palavras) com palavra-chave nos primeiros 100 caracteres
3. <h2>Por que Escolher [PRODUTO]? Os 5 Principais Motivos</h2>
4. Lista <ul> com 5-6 benefícios únicos
5. <h2>Características Técnicas que Fazem a Diferença</h2>
6. Tabela ou lista detalhada
7. <h2>Para Quem é Indicado o [PRODUTO]?</h2>
8. Parágrafos com casos de uso específicos
9. <h2>Comparativo: [PRODUTO] vs Concorrência</h2>
10. <h2>Como Instalar e Configurar [PRODUTO]</h2>
11. <h2>Preço e Onde Comprar [PRODUTO]</h2>
12. Conclusão com CTA forte

**ELEMENTOS SEO AVANÇADOS:**
- Usar <strong> nas palavras-chave importantes
- Densidade de palavra-chave: 1-2% (não mais!)
- Incluir variações da palavra-chave (sinônimos)
- Usar LSI keywords (palavras relacionadas)
- Parágrafos de 2-4 linhas máximo
- Listas numeradas e com bullets
- Mínimo 500 palavras, ideal 800-1200
- Incluir preço quando disponível
- Mencionar marca nos subtítulos

**Tags/Palavras-chave:**
- MÍNIMO 5, MÁXIMO 8 tags
- Incluir: palavra-chave principal, marca, categoria, benefício principal
- Usar long-tail keywords
- Incluir variações regionais
- EXEMPLO: ["hp laserjet pro", "impressora escritorio", "hp impressora", "impressora laser", "multifuncional hp", "impressora empresarial"]

**DENSIDADE E FREQUÊNCIA:**
- Palavra-chave principal: aparecer em título, primeiro parágrafo, 2-3 subtítulos
- Sinônimos e variações espalhados naturalmente
- Não repetir a mesma palavra-chave excessivamente
- Usar conectivos e transições naturais
        """
    
    def _get_default_structure(self) -> str:
        """Estrutura padrão para artigos"""
        return """
1. Introdução atrativa (1 parágrafo)
2. Principais benefícios (H2 + lista ou parágrafos)
3. Para quem é indicado (H2 + parágrafo)
4. Diferenciais técnicos (H2 + lista)
5. Conclusão com call-to-action (1 parágrafo)
        """
    
    def _extract_category_from_url(self, url: str) -> str:
        """Extrai categoria da URL"""
        if not url:
            return "produtos para escritório"
        
        category_mapping = {
            'impressoras': 'impressoras',
            'multifuncionais': 'multifuncionais',
            'toner': 'toners e cartuchos',
            'papel': 'papéis e materiais',
            'scanner': 'scanners',
            'copiadora': 'copiadoras'
        }
        
        url_lower = url.lower()
        for key, category in category_mapping.items():
            if key in url_lower:
                return category
        
        return "produtos para escritório"
    
    def _format_price(self, price_data: Any) -> str:
        """Formata dados de preço"""
        if not price_data:
            return "Consulte o preço"
        
        if isinstance(price_data, dict):
            return price_data.get('texto', 'Consulte o preço')
        elif isinstance(price_data, str):
            return price_data
        else:
            return str(price_data)
    
    def _build_fallback_prompt(self, product: Dict[str, Any]) -> str:
        """Prompt de fallback em caso de erro"""
        nome = product.get('nome', 'Produto')
        
        return f"""
Crie um artigo sobre "{nome}" no formato JSON:

{{
    "titulo": "Título para {nome}",
    "meta_descricao": "Descrição do {nome}",
    "conteudo": "<h2>Sobre o {nome}</h2><p>Conteúdo do artigo...</p>",
    "tags": ["tag1", "tag2", "tag3"]
}}

Use tom profissional e foque nos benefícios para empresas.
        """
    
    def get_template_prompts(self) -> Dict[str, str]:
        """Retorna prompts específicos por tipo de produto"""
        return {
            "impressora": """
            Foque em: qualidade de impressão, velocidade, economia de tinta/toner,
            facilidade de uso, conectividade, adequação para volume de impressão.
            """,
            
            "multifuncional": """
            Destaque: versatilidade (imprimir, copiar, escanear), economia de espaço,
            recursos de conectividade, qualidade de digitalização, facilidade de operação.
            """,
            
            "toner": """
            Enfatize: rendimento, qualidade de impressão, compatibilidade,
            custo-benefício, facilidade de instalação, garantia.
            """,
            
            "produto_generico": """
            Destaque: benefícios principais, aplicações práticas,
            diferenciais competitivos, adequação ao ambiente corporativo.
            """
        } 
 
 
 
 