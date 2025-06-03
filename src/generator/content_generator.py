"""
Content Generator
Gerador principal de conteúdo SEO com IA para produtos
OTIMIZADO PARA YOAST LEGIBILIDADE - PONTUAÇÃO VERDE
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
import random

try:
    from openai import OpenAI
except ImportError:
    logger.warning("⚠️ OpenAI não instalada. Rodando em modo simulação.")
    OpenAI = None

from .prompt_builder import PromptBuilder
from .seo_optimizer import SEOOptimizer
from .template_manager import TemplateManager
from .product_database import ProductDatabase

class ContentGenerator:
    """Gerador principal de conteúdo SEO com IA"""
    
    def __init__(self, api_key: str = None, model: str = None, temperature: float = 0.7, max_tokens: int = 2000):
        """
        Inicializa o gerador de conteúdo
        
        Args:
            api_key: Chave da API OpenAI (ou usa variável de ambiente)
            model: Modelo da OpenAI a usar
            temperature: Criatividade da IA (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
        """
        # Configurar API OpenAI
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # Usar modelo da variável de ambiente ou padrão
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        # FORÇAR USO DA API REAL (desabilitar simulação)
        # Usuário confirmou que adicionou a API key
        self.simulation_mode = False
        
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY não encontrada nas variáveis de ambiente.")
            logger.info("🔧 Tentando usar API key fornecida diretamente ou configurada manualmente...")
            # Ainda assim, vamos tentar usar a API real
            self.simulation_mode = False
        
        # Sempre tentar inicializar o cliente OpenAI
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✅ Cliente OpenAI inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente OpenAI: {e}")
            logger.warning("🎭 Voltando para modo simulação como fallback")
            self.simulation_mode = True
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Inicializar componentes
        self.prompt_builder = PromptBuilder()
        self.seo_optimizer = SEOOptimizer()
        self.template_manager = TemplateManager()
        self.product_database = ProductDatabase()  # NOVO: Base de produtos variados
        
        # Palavras de transição para legibilidade Yoast
        self.transition_words = [
            'além disso', 'portanto', 'por fim', 'ou seja', 'no entanto', 
            'assim sendo', 'por outro lado', 'em primeiro lugar', 'finalmente',
            'consequentemente', 'por exemplo', 'dessa forma', 'contudo',
            'sobretudo', 'por isso', 'em suma', 'ainda assim', 'logo',
            'principalmente', 'então', 'para isso', 'entretanto', 'ainda',
            'de forma geral', 'em comparação', 'em resumo', 'adicionalmente'
        ]
        
        # Configurar logging
        logger.add(
            "logs/generator.log",
            rotation="1 week",
            retention="30 days",
            level="INFO",
            format="{time} | {level} | {message}"
        )
        
        logger.info("🤖 Content Generator inicializado - Otimizado para Yoast Legibilidade")
        logger.info(f"📝 Modelo: {self.model} | Temperatura: {self.temperature} | Max Tokens: {self.max_tokens}")
        logger.info(f"🔧 Modo: {'Simulação' if self.simulation_mode else 'OpenAI API'}")
        
        # Log da base de produtos
        stats = self.product_database.get_statistics()
        logger.info(f"📦 {stats['total_produtos']} produtos disponíveis: {stats['por_marca']}")
    
    def generate_article(self, product: Dict[str, Any], 
                        custom_keywords: List[str] = None,
                        custom_instructions: str = None,
                        tone: str = "profissional") -> Dict[str, Any]:
        """
        Gera artigo completo para um produto
        
        Args:
            product: Dados do produto extraído pelo scraper
            custom_keywords: Palavras-chave extras
            custom_instructions: Instruções personalizadas
            tone: Tom do artigo (profissional, vendedor, amigável)
            
        Returns:
            Dicionário com artigo gerado
        """
        try:
            logger.info(f"🤖 Iniciando geração de artigo para: {product.get('nome', 'Produto Desconhecido')}")
            
            # Validar produto
            if not self._validate_product(product):
                logger.error("❌ Produto inválido para geração de conteúdo")
                return {}
            
            # Determinar categoria/tipo do produto
            product_type = self._determine_product_type(product)
            logger.debug(f"📂 Tipo do produto identificado: {product_type}")
            
            # Obter template baseado no tipo
            template = self.template_manager.get_template(product_type)
            
            # Construir prompt
            prompt = self.prompt_builder.build_prompt(
                product=product,
                template=template,
                custom_keywords=custom_keywords,
                custom_instructions=custom_instructions,
                tone=tone
            )
            
            # Gerar conteúdo com IA
            if self.simulation_mode:
                ai_content = self._generate_simulated_content(product, template)
            else:
                ai_content = self._generate_ai_content(prompt)
                
                # Se falhou na API, usar simulação como fallback
                if not ai_content:
                    logger.warning("🎭 API falhou, usando conteúdo simulado como fallback")
                    ai_content = self._generate_simulated_content(product, template)
            
            if not ai_content:
                logger.error("❌ Falha na geração de conteúdo")
                return {}
            
            # Processar e estruturar resposta
            article_data = self._process_ai_response(ai_content, product)
            
            # NOVA OTIMIZAÇÃO: Aplicar melhorias de legibilidade Yoast
            article_data = self._optimize_readability_yoast(article_data)
            
            # Otimizar SEO
            article_data = self.seo_optimizer.optimize_article(article_data)
            
            # Adicionar metadados
            article_data.update({
                'produto_id': product.get('id'),
                'produto_nome': product.get('nome'),
                'produto_url': product.get('url'),
                'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'tipo_produto': product_type,
                'tom_usado': tone,
                'modelo_ia': self.model,
                'status': 'gerado'
            })
            
            logger.info(f"✅ Artigo gerado com sucesso: {len(article_data.get('conteudo', ''))} caracteres")
            return article_data
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do artigo: {e}")
            return {}
    
    def _optimize_readability_yoast(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica todas as otimizações de legibilidade para Yoast verde
        
        Args:
            article_data: Dados do artigo
            
        Returns:
            Artigo otimizado para legibilidade Yoast
        """
        try:
            logger.debug("🔍 Aplicando otimizações de legibilidade Yoast...")
            
            optimized = article_data.copy()
            
            # Otimizar conteúdo principal
            if 'conteudo' in optimized:
                content = optimized['conteudo']
                
                # CRITICO 1: Garantir conteúdo mínimo de 300 palavras
                content = self._ensure_minimum_content_length(content, optimized.get('produto_nome', ''))
                
                # CRITICO 2: Adicionar links internos obrigatórios
                content = self._add_mandatory_internal_links(content)
                
                # CRITICO 3: Garantir links externos obrigatórios
                content = self._ensure_external_links(content, optimized.get('produto_nome', ''))
                
                # CRITICO 4: Adicionar imagens com ALT contendo keyword
                content = self._add_images_with_keyword_alt(content, optimized.get('produto_nome', ''))
                
                # CRITICO 5: Garantir focus keyword no primeiro parágrafo
                content = self._ensure_keyword_in_first_paragraph(content, optimized.get('produto_nome', ''))
                
                # CRITICO 6: Limpar URLs malformadas (espaços extras)
                content = self._clean_urls_in_content(content)
                
                # Aplicar otimizações de legibilidade existentes
                content = self._optimize_sentence_length_yoast(content)
                content = self._fix_unnecessary_capitals(content)
                content = self._fix_article_gender_agreement(content)
                content = self._add_transition_words_yoast(content)
                content = self._optimize_lists_yoast(content, optimized.get('produto_nome', ''))
                content = self._optimize_paragraph_length_yoast(content)
                content = self._convert_to_active_voice(content)
                
                optimized['conteudo'] = content
            
            # Otimizar título
            if 'titulo' in optimized:
                optimized['titulo'] = self._optimize_title_for_yoast_green(optimized['titulo'], optimized.get('produto_nome', ''))
            
            # Otimizar meta description
            if 'meta_descricao' in optimized:
                optimized['meta_descricao'] = self._optimize_meta_for_yoast_green(optimized['meta_descricao'], optimized.get('produto_nome', ''))
            
            # Gerar focus keyword otimizada - USAR PRODUTO_NOME CORRETO
            product_name = optimized.get('produto_nome', '')
            if not product_name:
                # Se produto_nome não existe, tentar outras fontes
                product_name = optimized.get('nome', '') or optimized.get('title', '') or optimized.get('titulo', '')
            
            optimized['focus_keyword'] = self._generate_focus_keyword_yoast(product_name)
            
            logger.debug("✅ Otimizações de legibilidade Yoast aplicadas")
            return optimized
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização Yoast: {e}")
            return article_data
    
    def _ensure_minimum_content_length(self, content: str, product_name: str) -> str:
        """
        Garante que o conteúdo tenha pelo menos 300 palavras
        
        Args:
            content: Conteúdo HTML
            product_name: Nome do produto
            
        Returns:
            Conteúdo expandido se necessário
        """
        # Contar palavras no texto (sem HTML)
        text_only = re.sub(r'<[^>]+>', '', content)
        word_count = len(text_only.split())
        
        if word_count < 300:
            # Adicionar conteúdo extra para atingir 300+ palavras
            additional_content = self._generate_additional_content(product_name, 300 - word_count)
            
            # Inserir antes da conclusão ou no final
            if '</h2>' in content:
                # Encontrar última seção e adicionar antes
                parts = content.rsplit('</h2>', 1)
                if len(parts) == 2:
                    content = parts[0] + '</h2>' + additional_content + parts[1]
                else:
                    content += additional_content
        
        return content

    def _generate_additional_content(self, product_name: str, words_needed: int) -> str:
        """Gera conteúdo adicional para atingir contagem mínima"""
        sections = [
            f"""
            <h3>Vantagens do {product_name} para Seu Escritório</h3>
            <p>O {product_name} oferece benefícios específicos para ambientes profissionais. Além disso, sua 
            tecnologia avançada garante produtividade constante. Portanto, é uma escolha inteligente para 
            empresas que buscam eficiência. Em primeiro lugar, destaca-se pela confiabilidade operacional.</p>
            """,
            f"""
            <h3>Especificações Técnicas Detalhadas</h3>
            <ul>
                <li>Tecnologia de impressão laser de alta precisão</li>
                <li>Velocidade otimizada para volumes médios e altos</li>
                <li>Conectividade USB e rede Ethernet</li>
                <li>Compatibilidade universal com sistemas Windows e Mac</li>
                <li>Ciclo de trabalho mensal robusto</li>
            </ul>
            <p>Essas características técnicas fazem do {product_name} uma solução completa. Consequentemente, 
            atende às demandas mais exigentes do mercado corporativo.</p>
            """,
            f"""
            <h3>Comparativo com Concorrentes</h3>
            <p>Em comparação com outros modelos do mercado, o {product_name} se destaca. Por exemplo, 
            oferece melhor custo-benefício na categoria. Também apresenta menor consumo energético. 
            Finalmente, sua manutenção é mais simples e econômica.</p>
            """
        ]
        
        # Selecionar seções baseado nas palavras necessárias
        result = ""
        for section in sections:
            result += section
            section_words = len(re.sub(r'<[^>]+>', '', section).split())
            words_needed -= section_words
            if words_needed <= 0:
                break
        
        return result

    def _add_mandatory_internal_links(self, content: str) -> str:
        """
        Adiciona pelo menos 1 link interno obrigatório
        
        Args:
            content: Conteúdo HTML
            
        Returns:
            Conteúdo com link interno
        """
        # Verificar se já tem link interno
        if 'blog.creativecopias.com.br' in content or 'creativecopias.com.br' in content:
            return content
        
        # Links internos para adicionar
        internal_links = [
            'confira nossa <a href="https://blog.creativecopias.com.br/categoria/impressoras/" target="_blank">seleção completa de impressoras</a>',
            'veja também nossos <a href="https://blog.creativecopias.com.br/categoria/multifuncionais/" target="_blank">equipamentos multifuncionais</a>',
            'encontre <a href="https://blog.creativecopias.com.br/categoria/suprimentos/" target="_blank">suprimentos originais</a>',
            '<a href="https://blog.creativecopias.com.br/contato/" target="_blank">entre em contato conosco</a> para mais informações'
        ]
        
        link_to_add = random.choice(internal_links)
        
        # Inserir no primeiro parágrafo que tenha conteúdo suficiente
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        if paragraphs:
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.split()) > 15:  # Parágrafo com conteúdo suficiente
                    # Adicionar link no final do parágrafo
                    enhanced_p = paragraph.rstrip() + f'. Para mais opções, {link_to_add}.'
                    content = content.replace(f'<p>{paragraph}</p>', f'<p>{enhanced_p}</p>', 1)
                    break
        else:
            # Se não encontrar parágrafos, adicionar no final
            content += f'<p>Para mais opções, {link_to_add}.</p>'
        
        return content

    def _ensure_external_links(self, content: str, product_name: str) -> str:
        """
        Garante pelo menos 1 link externo obrigatório
        
        Args:
            content: Conteúdo HTML
            product_name: Nome do produto
            
        Returns:
            Conteúdo com link externo
        """
        # Verificar se já tem link externo não Creative Cópias
        external_links_present = re.findall(r'href="(https?://[^"]+)"', content)
        has_external = any(link for link in external_links_present if 'creativecopias.com' not in link)
        
        if has_external:
            return content
        
        # Determinar link externo baseado na marca
        brand_links = {
            'hp': 'https://www.hp.com/br-pt/',
            'canon': 'https://www.canon.com.br/',
            'epson': 'https://epson.com.br/',
            'brother': 'https://www.brother.com.br/',
            'samsung': 'https://www.samsung.com/br/',
            'xerox': 'https://www.xerox.com.br/'
        }
        
        # Detectar marca no nome do produto
        brand = 'hp'  # Default
        for brand_name in brand_links.keys():
            if brand_name.lower() in product_name.lower():
                brand = brand_name
                break
        
        external_link = f'<a href="{brand_links[brand]}" target="_blank" rel="nofollow">site oficial da {brand.upper()}</a>'
        
        # Inserir no segundo parágrafo se disponível
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        if len(paragraphs) >= 2 and len(paragraphs[1].split()) > 10:
            # Adicionar no final do segundo parágrafo
            second_p = paragraphs[1]
            enhanced_p = second_p.rstrip() + f' Mais detalhes técnicos estão disponíveis no {external_link}.'
            content = content.replace(f'<p>{second_p}</p>', f'<p>{enhanced_p}</p>', 1)
        elif paragraphs and len(paragraphs[0].split()) > 10:
            # Se só tem um parágrafo, adicionar nele
            first_p = paragraphs[0]
            enhanced_p = first_p.rstrip() + f' Consulte também o {external_link} para informações adicionais.'
            content = content.replace(f'<p>{first_p}</p>', f'<p>{enhanced_p}</p>', 1)
        else:
            # Se não encontrar parágrafos adequados, adicionar no final
            content += f'<p>Consulte o {external_link} para mais informações técnicas.</p>'
        
        return content

    def _add_images_with_keyword_alt(self, content: str, product_name: str) -> str:
        """
        Adiciona pelo menos 1 imagem com ALT contendo a keyword
        
        Args:
            content: Conteúdo HTML
            product_name: Nome do produto (keyword)
            
        Returns:
            Conteúdo com imagem e ALT otimizado
        """
        # REMOVIDO: Lógica de imagens automáticas (conforme solicitado pelo usuário)
        # Não adicionar nem modificar imagens automaticamente
        return content

    def _ensure_keyword_in_first_paragraph(self, content: str, product_name: str) -> str:
        """
        Garante que a keyword aparece no primeiro parágrafo (primeiros 100 caracteres)
        
        Args:
            content: Conteúdo HTML
            product_name: Nome do produto
            
        Returns:
            Conteúdo com keyword no início
        """
        keyword = self._extract_keyword_from_product(product_name)
        
        # Encontrar primeiro parágrafo
        first_p_match = re.search(r'<p>(.*?)</p>', content, re.DOTALL)
        if first_p_match:
            first_p = first_p_match.group(1).strip()
            
            # Verificar se keyword já está nos primeiros 100 caracteres
            first_100 = first_p[:100].lower()
            if keyword.lower() not in first_100:
                # Reformular primeira frase para incluir keyword com link de compra
                sentences = first_p.split('. ')
                if sentences:
                    # Corrigir o artigo baseado no tipo de produto
                    if any(word in product_name.lower() for word in ['impressora', 'multifuncional', 'copiadora']):
                        article = "A"
                    else:
                        article = "O"
                    
                    # Gerar link de compra do produto
                    product_slug = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
                    buy_link = f'<a href="https://creativecopias.com.br/produto/{product_slug}" target="_blank" rel="noopener"><strong>Comprar {product_name}</strong></a>'
                    
                    # VALIDAÇÃO CRÍTICA: Verificar se product_name não está vazio
                    if not product_name or product_name.strip() == "":
                        product_name = "equipamento"
                    if len(product_name.strip()) < 3:
                        product_name = "equipamento multifuncional"
                    
                    new_first_sentence = f"{article} {product_name} é uma excelente opção para quem busca qualidade e desempenho"
                    if len(sentences) > 1:
                        enhanced_p = new_first_sentence + '. ' + '. '.join(sentences[1:]) + f' Para adquirir este produto, acesse: {buy_link}.'
                    else:
                        enhanced_p = new_first_sentence + '. ' + sentences[0] + f' Para comprar, acesse: {buy_link}.'
                    
                    content = content.replace(f'<p>{first_p}</p>', f'<p>{enhanced_p}</p>', 1)
        
        return content

    def _optimize_title_for_yoast_green(self, title: str, product_name: str) -> str:
        """
        Otimiza título para Yoast VERDE (30-60 chars + keyword no início)
        
        Args:
            title: Título original
            product_name: Nome do produto
            
        Returns:
            Título otimizado para Yoast verde
        """
        keyword = self._extract_keyword_from_product(product_name)
        
        # Usar o produto completo no título, não só keyword
        if not title.lower().startswith(product_name.lower()[:20]):  # Primeiras palavras do produto
            title = f"{product_name}: {title}"
        
        # Ajustar para 30-60 caracteres
        if len(title) < 30:
            # Muito curto, expandir
            title = f"{product_name}: Análise e Review Completo"
        elif len(title) > 60:
            # Muito longo, cortar mantendo produto
            if ':' in title:
                parts = title.split(':', 1)
                remaining_chars = 60 - len(parts[0]) - 2  # -2 para ': '
                if remaining_chars > 10:
                    title = f"{parts[0]}: {parts[1].strip()[:remaining_chars]}"
                else:
                    title = parts[0][:57] + "..."
            else:
                title = title[:57] + "..."
        
        return title.strip()

    def _optimize_meta_for_yoast_green(self, meta_desc: str, product_name: str) -> str:
        """
        Otimiza meta description para Yoast VERDE (120-155 chars + keyword)
        
        Args:
            meta_desc: Meta description original
            product_name: Nome do produto
            
        Returns:
            Meta description otimizada
        """
        keyword = self._extract_keyword_from_product(product_name)
        
        # Usar produto completo, mas limitar tamanho
        product_short = product_name[:30] if len(product_name) > 30 else product_name
        
        # Garantir que produto está no início
        if not meta_desc.lower().startswith(product_short.lower()):
            meta_desc = f"{product_short}: {meta_desc}"
        
        # Ajustar para 120-155 caracteres
        if len(meta_desc) < 120:
            # Muito curta, expandir
            meta_desc = f"{product_short}: análise completa, especificações técnicas, preços e onde comprar. Confira review detalhado e avaliação."
        elif len(meta_desc) > 155:
            # Muito longa, cortar mantendo produto
            meta_desc = meta_desc[:152] + "..."
        
        return meta_desc.strip()

    def _generate_focus_keyword_yoast(self, product_name: str) -> str:
        """
        Gera focus keyword otimizada para Yoast
        
        Args:
            product_name: Nome do produto
            
        Returns:
            Focus keyword otimizada
        """
        return self._extract_keyword_from_product(product_name)

    def _extract_keyword_from_product(self, product_name: str) -> str:
        """
        Extrai keyword principal do nome do produto
        
        Args:
            product_name: Nome completo do produto
            
        Returns:
            Keyword otimizada (2-3 palavras principais)
        """
        if not product_name:
            return "produto"
        
        # Limpar espaços e converter para minúsculas
        clean_name = product_name.strip().lower()
        
        # Para produtos HP LaserJet, extrair marca + modelo específico
        if 'hp' in clean_name and 'laserjet' in clean_name:
            # Extrair modelo específico (ex: M404n, M404dn, etc.)
            import re
            model_match = re.search(r'(m\d+\w*)', clean_name)
            if model_match:
                return f"hp laserjet {model_match.group(1)}"
            else:
                return 'hp laserjet'
        
        # Para outros produtos, extrair palavras significativas
        words = clean_name.split()
        
        # Remover palavras irrelevantes
        stop_words = ['a', 'o', 'de', 'da', 'do', 'com', 'para', 'em', 'na', 'no', 'impressora', 'multifuncional']
        significant_words = []
        
        for word in words:
            if (word not in stop_words and 
                len(word) > 2 and 
                not word.isdigit() and 
                word.isalpha()):  # Apenas palavras, não números/símbolos
                significant_words.append(word)
        
        # Retornar 2 palavras principais
        if len(significant_words) >= 2:
            return ' '.join(significant_words[:2])
        elif significant_words:
            # Se só tem uma palavra significativa, tentar pegar do produto completo
            # Priorizar marca + primeira palavra técnica
            if 'hp' in words:
                tech_words = [w for w in words if w not in stop_words and w != 'hp' and len(w) > 3]
                if tech_words:
                    return f"hp {tech_words[0]}"
                else:
                    return 'hp impressora'
            return significant_words[0]
        else:
            # Último fallback: extrair primeiras palavras do nome original
            first_words = product_name.split()[:2]
            return ' '.join(first_words).lower()
    
    def _optimize_sentence_length_yoast(self, content: str) -> str:
        """Limita frases a máximo 20 palavras para Yoast verde"""
        if not content:
            return content
        
        # Dividir em parágrafos
        paragraphs = content.split('\n')
        optimized_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                optimized_paragraphs.append(paragraph)
                continue
            
            # Dividir em frases
            sentences = re.split(r'[.!?]+', paragraph)
            optimized_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                words = sentence.split()
                
                # Se a frase tem mais de 20 palavras, dividir
                if len(words) > 20:
                    # Tentar dividir em conjunções
                    connectors = ['e', 'mas', 'porém', 'contudo', 'entretanto', 'no entanto', 'todavia']
                    
                    for i, word in enumerate(words):
                        if word.lower() in connectors and i > 8 and i < len(words) - 3:
                            # Dividir aqui
                            first_part = ' '.join(words[:i])
                            second_part = ' '.join(words[i+1:])
                            
                            # Adicionar palavra de transição na segunda parte
                            transition = random.choice(['Além disso', 'Dessa forma', 'Também'])
                            second_part = f"{transition}, {second_part.lower()}"
                            
                            optimized_sentences.append(first_part + '.')
                            optimized_sentences.append(second_part + '.')
                            break
                    else:
                        # Se não conseguir dividir naturalmente, cortar em 20 palavras
                        first_part = ' '.join(words[:20])
                        remaining = ' '.join(words[20:])
                        
                        optimized_sentences.append(first_part + '.')
                        if remaining:
                            transition = random.choice(['Além disso', 'Também', 'Ainda'])
                            optimized_sentences.append(f"{transition}, {remaining.lower()}.")
                else:
                    optimized_sentences.append(sentence + '.')
            
            optimized_paragraphs.append(' '.join(optimized_sentences))
        
        return '\n'.join(optimized_paragraphs)
    
    def _fix_unnecessary_capitals(self, content: str) -> str:
        """Corrige maiúsculas desnecessárias no meio de frases"""
        if not content:
            return content
        
        # Padrões a corrigir
        patterns = [
            (r'\b(Além Disso)\b', 'Além disso'),
            (r'\b(Em Um)\b', 'Em um'),
            (r'\b(Em Uma)\b', 'Em uma'),
            (r'\b(Por Isso)\b', 'Por isso'),
            (r'\b(Por Exemplo)\b', 'Por exemplo'),
            (r'\b(Dessa Forma)\b', 'Dessa forma'),
            (r'\b(No Entanto)\b', 'No entanto'),
            (r'\b(Por Outro Lado)\b', 'Por outro lado'),
            (r'\b(De Forma Geral)\b', 'De forma geral'),
            (r'\b(Em Comparação)\b', 'Em comparação'),
            (r'\b(Em Resumo)\b', 'Em resumo'),
            (r'\b(Ou Seja)\b', 'Ou seja'),
            (r'\b(Assim Sendo)\b', 'Assim sendo'),
        ]
        
        # Aplicar correções (exceto no início de frases)
        for pattern, replacement in patterns:
            # Não corrigir se estiver no início de uma frase (após ponto/quebra de linha)
            content = re.sub(fr'(?<!^)(?<!\. )(?<!\n){pattern}', replacement, content)
        
        return content
    
    def _fix_article_gender_agreement(self, content: str) -> str:
        """Corrige concordância de artigos com substantivos"""
        if not content:
            return content
        
        # Correções específicas comuns
        corrections = [
            (r'\bo Impressora\b', 'a Impressora'),
            (r'\bo impressora\b', 'a impressora'),
            (r'\bo multifuncional\b', 'a multifuncional'),
            (r'\bo Multifuncional\b', 'a Multifuncional'),
            (r'\bo escaner\b', 'o scanner'),
            (r'\bo Escaner\b', 'o Scanner'),
            (r'\ba toner\b', 'o toner'),
            (r'\ba Toner\b', 'o Toner'),
            (r'\ba papel\b', 'o papel'),
            (r'\ba Papel\b', 'o Papel'),
        ]
        
        for pattern, replacement in corrections:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _add_transition_words_yoast(self, content: str) -> str:
        """Adiciona palavras de transição para atingir 30% das frases (Yoast verde)"""
        if not content:
            return content
        
        paragraphs = content.split('\n')
        optimized_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip() or '<' in paragraph:  # Pular parágrafos vazios ou HTML
                optimized_paragraphs.append(paragraph)
                continue
            
            sentences = re.split(r'[.!?]+', paragraph)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 1:
                optimized_paragraphs.append(paragraph)
                continue
            
            # Adicionar transições em 30% das frases (exceto a primeira)
            transition_count = max(1, int(len(sentences) * 0.3))
            
            # Selecionar frases aleatórias para adicionar transições (exceto a primeira)
            sentences_to_modify = random.sample(range(1, len(sentences)), min(transition_count, len(sentences)-1))
            
            for i in sentences_to_modify:
                sentence = sentences[i]
                
                # Verificar se já tem palavra de transição
                has_transition = any(trans in sentence.lower() for trans in self.transition_words)
                
                if not has_transition:
                    # Escolher transição baseada na posição
                    if i == 1:
                        transition = random.choice(['Além disso', 'Também', 'Adicionalmente'])
                    elif i == len(sentences) - 1:
                        transition = random.choice(['Por fim', 'Finalmente', 'Em suma'])
                    else:
                        transition = random.choice(['Dessa forma', 'Portanto', 'Consequentemente', 'Ainda assim'])
                    
                    # Adicionar transição
                    sentences[i] = f"{transition}, {sentence.lower()}"
            
            optimized_paragraphs.append('. '.join(sentences) + '.')
        
        return '\n'.join(optimized_paragraphs)
    
    def _optimize_lists_yoast(self, content: str, product_name: str) -> str:
        """Otimiza listas com pelo menos 3 bullets e conteúdo real"""
        if not content:
            return content
        
        # Buscar listas existentes e melhorá-las
        list_pattern = r'<ul>(.*?)</ul>'
        
        def improve_list(match):
            list_content = match.group(1)
            items = re.findall(r'<li>(.*?)</li>', list_content)
            
            if len(items) < 3:
                # Adicionar mais itens baseado no tipo de produto
                if 'impressora' in product_name.lower():
                    additional_items = [
                        'Conectividade USB e Ethernet integrada',
                        'Baixo consumo de energia em modo standby',
                        'Compatibilidade com sistemas Windows e Mac'
                    ]
                elif 'multifuncional' in product_name.lower():
                    additional_items = [
                        'Scanner com resolução óptica superior',
                        'Copiadora com zoom automático',
                        'Fax com memória de documentos'
                    ]
                elif 'toner' in product_name.lower():
                    additional_items = [
                        'Alto rendimento de páginas por cartucho',
                        'Qualidade de impressão profissional',
                        'Instalação rápida e sem complicações'
                    ]
                else:
                    additional_items = [
                        'Qualidade superior comprovada',
                        'Excelente custo-benefício',
                        'Garantia de satisfação'
                    ]
                
                # Adicionar itens até ter pelo menos 3
                needed = 3 - len(items)
                items.extend(additional_items[:needed])
            
            # Garantir que cada item tem máximo 15 palavras
            optimized_items = []
            for item in items:
                words = item.split()
                if len(words) > 15:
                    item = ' '.join(words[:15]) + '...'
                optimized_items.append(item)
            
            # Reconstruir lista
            new_list = '<ul>\n'
            for item in optimized_items:
                new_list += f'   <li>{item}</li>\n'
            new_list += '</ul>'
            
            return new_list
        
        content = re.sub(list_pattern, improve_list, content, flags=re.DOTALL)
        
        return content
    
    def _optimize_paragraph_length_yoast(self, content: str) -> str:
        """Garante que parágrafos tenham máximo 100 palavras"""
        if not content:
            return content
        
        paragraphs = content.split('\n')
        optimized_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip() or '<' in paragraph:  # Pular vazios ou HTML
                optimized_paragraphs.append(paragraph)
                continue
            
            words = paragraph.split()
            
            if len(words) <= 100:
                optimized_paragraphs.append(paragraph)
            else:
                # Dividir em parágrafos menores
                chunks = []
                current_chunk = []
                
                for word in words:
                    current_chunk.append(word)
                    
                    if len(current_chunk) >= 90:
                        # Procurar ponto para quebrar
                        chunk_text = ' '.join(current_chunk)
                        last_period = chunk_text.rfind('.')
                        
                        if last_period > 50:  # Se encontrou um ponto em posição razoável
                            chunks.append(chunk_text[:last_period + 1])
                            remaining = chunk_text[last_period + 1:].strip()
                            current_chunk = remaining.split() if remaining else []
                        elif len(current_chunk) >= 100:
                            # Forçar quebra se não encontrou ponto
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                optimized_paragraphs.extend(chunks)
        
        return '\n\n'.join(optimized_paragraphs)
    
    def _convert_to_active_voice(self, content: str) -> str:
        """Converte frases para voz ativa quando possível"""
        if not content:
            return content
        
        # Padrões de voz passiva para ativa
        patterns = [
            (r'é oferecido', 'oferece'),
            (r'são oferecidos', 'oferecem'),
            (r'é proporcionado', 'proporciona'),
            (r'são proporcionados', 'proporcionam'),
            (r'é garantido', 'garante'),
            (r'são garantidos', 'garantem'),
            (r'é recomendado', 'recomendamos'),
            (r'são recomendados', 'recomendamos'),
            (r'é utilizado', 'utiliza'),
            (r'são utilizados', 'utilizam'),
            (r'é considerado', 'consideramos'),
            (r'são considerados', 'consideramos'),
            (r'pode ser usado', 'você pode usar'),
            (r'podem ser usados', 'você pode usar'),
            (r'será beneficiado', 'você se beneficia'),
            (r'serão beneficiados', 'vocês se beneficiam'),
        ]
        
        for passive, active in patterns:
            content = re.sub(passive, active, content, flags=re.IGNORECASE)
        
        return content
    
    def _optimize_title_length_yoast(self, title: str) -> str:
        """Otimiza título para máximo 60 caracteres"""
        if not title or len(title) <= 60:
            return title
        
        # Tentar cortar mantendo palavras completas
        words = title.split()
        optimized = ""
        
        for word in words:
            test_length = len(optimized + " " + word) if optimized else len(word)
            if test_length <= 57:  # Deixar espaço para pontuação
                optimized += (" " if optimized else "") + word
            else:
                break
        
        return optimized
    
    def _optimize_meta_description_length_yoast(self, meta_desc: str) -> str:
        """Otimiza meta descrição para 120-155 caracteres"""
        if not meta_desc:
            return meta_desc
        
        if len(meta_desc) < 120:
            # Muito curta, adicionar mais informação
            meta_desc += " Confira características, benefícios e onde comprar."
        
        if len(meta_desc) > 155:
            # Muito longa, cortar mantendo palavras completas
            words = meta_desc.split()
            optimized = ""
            
            for word in words:
                test_length = len(optimized + " " + word) if optimized else len(word)
                if test_length <= 152:  # Deixar espaço para pontuação
                    optimized += (" " if optimized else "") + word
                else:
                    break
            
            meta_desc = optimized + "..."
        
        return meta_desc
    
    def generate_articles_batch(self, products: List[Dict[str, Any]], 
                               **kwargs) -> List[Dict[str, Any]]:
        """
        Gera artigos para múltiplos produtos
        
        Args:
            products: Lista de produtos
            **kwargs: Argumentos para generate_article
            
        Returns:
            Lista de artigos gerados
        """
        logger.info(f"🔄 Iniciando geração em lote de {len(products)} artigos")
        
        articles = []
        for i, product in enumerate(products, 1):
            try:
                logger.info(f"📝 Gerando artigo {i}/{len(products)}")
                
                article = self.generate_article(product, **kwargs)
                if article:
                    articles.append(article)
                else:
                    logger.warning(f"⚠️ Falha na geração do artigo {i}")
                
                # Delay entre gerações para não sobrecarregar API
                if not self.simulation_mode and i < len(products):
                    import time
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Erro no artigo {i}: {e}")
                continue
        
        success_rate = len(articles) / len(products) * 100 if products else 0
        logger.info(f"✅ Geração em lote concluída: {len(articles)}/{len(products)} artigos ({success_rate:.1f}%)")
        
        return articles
    
    def _validate_product(self, product: Dict[str, Any]) -> bool:
        """Valida se produto tem dados suficientes para gerar conteúdo"""
        required_fields = ['nome']
        return all(product.get(field) for field in required_fields)
    
    def _determine_product_type(self, product: Dict[str, Any]) -> str:
        """Determina o tipo/categoria do produto baseado nos dados"""
        nome = product.get('nome', '').lower()
        descricao = product.get('descricao', '').lower()
        text = f"{nome} {descricao}"
        
        # Mapeamento de palavras-chave para tipos
        type_keywords = {
            'impressora': ['impressora', 'printer'],
            'multifuncional': ['multifuncional', 'multifun', 'all-in-one'],
            'toner': ['toner', 'cartucho'],
            'papel': ['papel', 'resma'],
            'scanner': ['scanner', 'digitalizador'],
            'copiadora': ['copiadora', 'copier'],
            'fax': ['fax'],
            'suprimento': ['suprimento', 'supply']
        }
        
        for product_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return product_type
        
        return 'produto_generico'
    
    def _generate_ai_content(self, prompt: str) -> Optional[str]:
        """Gera conteúdo usando OpenAI API"""
        try:
            logger.info("🤖 Enviando prompt para OpenAI...")
            logger.debug(f"📝 Modelo: {self.model}, Temperatura: {self.temperature}, Max Tokens: {self.max_tokens}")
            
            if not self.client:
                logger.error("❌ Cliente OpenAI não inicializado!")
                return None
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em redação publicitária e SEO para produtos de escritório, especialmente impressoras e suprimentos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"✅ Resposta da OpenAI recebida: {len(content)} caracteres")
            logger.debug(f"📄 Conteúdo: {content[:200]}...")
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro na API OpenAI: {type(e).__name__}: {e}")
            logger.debug(f"🔍 Detalhes do erro: {str(e)}")
            
            # Se der erro, usar fallback
            logger.warning("🎭 Usando conteúdo simulado como fallback")
            return None
    
    def _generate_simulated_content(self, product: Dict[str, Any], template: Dict[str, Any]) -> str:
        """Gera conteúdo simulado para testes (quando API não disponível)"""
        nome = product.get('nome', 'Produto')
        marca = product.get('marca', 'Marca')
        preco = product.get('preco', {})
        preco_texto = preco.get('texto', 'Consulte o preço') if isinstance(preco, dict) else str(preco)
        
        # VARIAÇÕES DE TÍTULOS PARA EVITAR DUPLICATAS
        title_variations = [
            f"{nome}: Análise Completa 2025",
            f"{nome}: Guia de Compra Definitivo",
            f"{nome}: Vale a Pena? Review Detalhado",
            f"{nome}: Características e Benefícios",
            f"Review: {nome} - Prós e Contras",
            f"Como Escolher: {nome}",
            f"Tudo Sobre o {nome}",
            f"{nome}: Especificações Técnicas",
            f"Análise: {nome} da {marca}",
            f"{nome}: Melhor Custo-Benefício?"
        ]
        
        # Escolher título aleatório
        titulo_seo = random.choice(title_variations)
        
        # VARIAÇÕES DE META DESCRIÇÃO
        meta_variations = [
            f"Descubra tudo sobre o {nome}: análise completa, especificações técnicas e onde comprar com melhor preço.",
            f"Review detalhado do {nome}: características, benefícios e comparação com concorrentes. Confira!",
            f"Guia completo do {nome}: vale a pena? Análise de prós, contras e custo-benefício.",
            f"Conheça o {nome}: especificações, preços e avaliação especializada. Tudo que você precisa saber.",
            f"Análise técnica do {nome}: performance, qualidade e comparativo de preços no mercado."
        ]
        
        meta_desc = random.choice(meta_variations)
        
        # VARIAÇÕES DE ESTRUTURA DE CONTEÚDO
        content_structures = [
            # Estrutura 1: Foco em benefícios
            f"""<h1>{titulo_seo}</h1>
            
            <h2>Por que escolher o {nome}?</h2>
            <p>O {nome} da {marca} se destaca no mercado por oferecer uma combinação única de qualidade, performance e custo-benefício. Com tecnologia avançada e design moderno, este produto atende às necessidades de usuários exigentes.</p>
            
            <h2>Principais Características</h2>
            <ul>
                <li><strong>Tecnologia Avançada:</strong> Equipado com os mais modernos recursos</li>
                <li><strong>Design Ergonômico:</strong> Pensado para máximo conforto de uso</li>
                <li><strong>Eficiência Energética:</strong> Consumo otimizado e sustentável</li>
                <li><strong>Conectividade:</strong> Múltiplas opções de conexão</li>
                <li><strong>Durabilidade:</strong> Construção robusta para uso intensivo</li>
            </ul>
            
            <h2>Benefícios para o Usuário</h2>
            <p>Ao escolher o {nome}, você investe em produtividade e qualidade. Este equipamento oferece resultados superiores, reduzindo custos operacionais e aumentando a eficiência do trabalho.</p>
            
            <h3>Economia Garantida</h3>
            <p>Com tecnologia de ponta, o {nome} proporciona economia de até 40% nos custos operacionais, tornando-se um investimento inteligente para empresas e usuários domésticos.</p>
            
            <h2>Onde Comprar</h2>
            <p>O {nome} está disponível nas principais lojas especializadas. Preço atual: {preco_texto}. Aproveite as condições especiais e garante já o seu!</p>""",
            
            # Estrutura 2: Foco técnico
            f"""<h1>{titulo_seo}</h1>
            
            <h2>Especificações Técnicas do {nome}</h2>
            <p>O {nome} representa o que há de mais moderno em tecnologia. Desenvolvido pela {marca}, este produto incorpora inovações que garantem performance superior e confiabilidade.</p>
            
            <h2>Recursos Avançados</h2>
            <h3>Tecnologia de Ponta</h3>
            <p>Equipado com processamento avançado e componentes de alta qualidade, o {nome} oferece desempenho excepcional em todas as condições de uso.</p>
            
            <h3>Conectividade Inteligente</h3>
            <ul>
                <li>Conexão Wi-Fi integrada</li>
                <li>Compatibilidade universal</li>
                <li>Interface intuitiva</li>
                <li>Configuração simplificada</li>
            </ul>
            
            <h2>Performance e Qualidade</h2>
            <p>Com velocidade otimizada e qualidade superior, o {nome} atende às demandas mais exigentes do mercado profissional e doméstico.</p>
            
            <h3>Sustentabilidade</h3>
            <p>Desenvolvido com foco na sustentabilidade, o {nome} utiliza tecnologias eco-friendly que reduzem o impacto ambiental sem comprometer a performance.</p>
            
            <h2>Investimento Inteligente</h2>
            <p>Por {preco_texto}, o {nome} oferece excelente custo-benefício, combinando tecnologia avançada com preço competitivo.</p>""",
            
            # Estrutura 3: Foco comparativo
            f"""<h1>{titulo_seo}</h1>
            
            <h2>O {nome} é a Melhor Escolha?</h2>
            <p>Em um mercado competitivo, o {nome} da {marca} se destaca pela combinação única de recursos, qualidade e preço acessível.</p>
            
            <h2>Vantagens Competitivas</h2>
            <h3>Superioridade Técnica</h3>
            <p>Comparado aos concorrentes, o {nome} oferece recursos exclusivos que garantem melhor desempenho e maior durabilidade.</p>
            
            <h3>Custo-Benefício Imbatível</h3>
            <ul>
                <li><strong>Preço competitivo:</strong> {preco_texto}</li>
                <li><strong>Baixo custo operacional:</strong> Economia de até 50%</li>
                <li><strong>Manutenção reduzida:</strong> Componentes duráveis</li>
                <li><strong>Garantia estendida:</strong> Proteção total</li>
            </ul>
            
            <h2>Por que Escolher o {nome}?</h2>
            <p>A escolha do {nome} representa um investimento seguro em tecnologia e qualidade. Com recursos avançados e suporte técnico especializado, você tem a garantia de um produto confiável.</p>
            
            <h3>Satisfação Garantida</h3>
            <p>Milhares de usuários já comprovaram a qualidade do {nome}. Junte-se a eles e experimente a diferença que um produto de qualidade pode fazer.</p>
            
            <h2>Conclusão</h2>
            <p>O {nome} é mais que um produto - é uma solução completa que combina inovação, qualidade e preço justo. Não perca tempo e garante já o seu!</p>"""
        ]
        
        # Escolher estrutura aleatória
        content_html = random.choice(content_structures)
        
        # TAGS VARIADAS E ESPECÍFICAS
        tag_sets = [
            [nome.lower().replace(' ', '-'), marca.lower(), "equipamento-escritorio", "tecnologia-avancada", "custo-beneficio", "review-2025"],
            [nome.lower().replace(' ', '-'), marca.lower(), "analise-tecnica", "especificacoes", "comparativo", "melhor-preco"],
            [nome.lower().replace(' ', '-'), marca.lower(), "guia-compra", "caracteristicas", "beneficios", "onde-comprar"],
            [nome.lower().replace(' ', '-'), marca.lower(), "review-completo", "pros-contras", "vale-a-pena", "investimento"],
            [nome.lower().replace(' ', '-'), marca.lower(), "tecnologia-2025", "inovacao", "sustentabilidade", "economia"]
        ]
        
        tags_seo = random.choice(tag_sets)
        
        # Criar estrutura de dados diretamente
        article_data = {
            "titulo": titulo_seo,
            "meta_descricao": meta_desc,
            "conteudo": content_html.strip(),
            "tags": tags_seo
        }
        
        # Converter para JSON para consistência com API
        content = json.dumps(article_data, ensure_ascii=False, indent=2)
        
        logger.info(f"🎭 Conteúdo simulado SEO otimizado gerado: {titulo_seo}")
        return content
    
    def _process_ai_response(self, ai_content: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta da IA e extrai dados estruturados"""
        try:
            # Tentar extrair JSON da resposta
            json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                article_data = json.loads(json_str)
            else:
                # Se não for JSON, estruturar manualmente
                article_data = self._parse_text_response(ai_content, product)
            
            # Validar campos obrigatórios
            required_fields = ['titulo', 'conteudo']
            for field in required_fields:
                if not article_data.get(field):
                    logger.warning(f"⚠️ Campo obrigatório '{field}' não encontrado, usando fallback")
                    article_data[field] = self._generate_fallback_content(field, product)
            
            return article_data
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Resposta da IA não está em JSON válido, fazendo parsing manual")
            return self._parse_text_response(ai_content, product)
        except Exception as e:
            logger.error(f"❌ Erro ao processar resposta da IA: {e}")
            return self._generate_fallback_article(product)
    
    def _parse_text_response(self, text: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """Parse manual de resposta em texto livre"""
        # Implementação básica para extrair título e conteúdo
        lines = text.split('\n')
        
        titulo = product.get('nome', 'Produto')
        conteudo = text
        
        # Tentar extrair título da primeira linha
        if lines and len(lines[0].strip()) > 0:
            first_line = lines[0].strip()
            if len(first_line) < 100:  # Provavelmente é um título
                titulo = first_line
                conteudo = '\n'.join(lines[1:])
        
        return {
            'titulo': titulo,
            'conteudo': conteudo,
            'meta_descricao': f"Conheça {titulo}. Soluções profissionais para seu escritório.",
            'tags': [product.get('marca', ''), 'impressora', 'escritório']
        }
    
    def _generate_fallback_content(self, field: str, product: Dict[str, Any]) -> str:
        """Gera conteúdo de fallback para campos obrigatórios"""
        nome = product.get('nome', 'Produto')
        
        fallbacks = {
            'titulo': f"{nome}: Soluções Profissionais",
            'conteudo': f"<h2>{nome}</h2><p>Produto de alta qualidade para seu escritório.</p>",
            'meta_descricao': f"Conheça {nome}. Ideal para profissionais.",
            'tags': [product.get('marca', ''), 'produto', 'escritório']
        }
        
        return fallbacks.get(field, '')
    
    def _generate_fallback_article(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Gera artigo completo de fallback em caso de erro"""
        nome = product.get('nome', 'Produto')
        marca = product.get('marca', 'Marca')
        
        return {
            'titulo': f"{nome}: Soluções Profissionais",
            'slug': self.seo_optimizer.generate_slug(f"{nome} soluções profissionais"),
            'meta_descricao': f"Conheça {nome} da {marca}. Ideal para escritórios.",
            'conteudo': f"<h2>{nome}</h2><p>Produto de alta qualidade da {marca}.</p>",
            'tags': [marca, 'produto', 'escritório']
        }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerador"""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'simulation_mode': self.simulation_mode,
            'status': 'ready' if self.api_key or self.simulation_mode else 'no_api_key'
        } 
    
    def generate_article_from_random_product(self, **kwargs) -> Dict[str, Any]:
        """
        Gera artigo usando produto aleatório da base de dados
        
        Args:
            **kwargs: Argumentos para generate_article
            
        Returns:
            Dicionário com artigo gerado
        """
        try:
            # FORÇAR RESET DOS PRODUTOS USADOS para garantir variedade
            self.product_database.reset_used_products()
            
            # Obter produto aleatório
            product = self.product_database.get_random_product(exclude_used=True)
            logger.info(f"🎲 Produto aleatório selecionado: {product['nome']} ({product['marca']})")
            
            # Gerar artigo
            return self.generate_article(product, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Erro na geração com produto aleatório: {e}")
            return {}
    
    def generate_articles_varied_batch(self, count: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Gera lote de artigos com produtos variados
        
        Args:
            count: Número de artigos a gerar
            **kwargs: Argumentos para generate_article
            
        Returns:
            Lista de artigos gerados
        """
        logger.info(f"🔄 Gerando lote de {count} artigos com produtos variados")
        
        articles = []
        for i in range(count):
            try:
                logger.info(f"📝 Gerando artigo {i+1}/{count}")
                
                article = self.generate_article_from_random_product(**kwargs)
                if article:
                    articles.append(article)
                    logger.info(f"✅ Artigo {i+1} gerado: {article.get('titulo', 'Sem título')[:50]}...")
                else:
                    logger.warning(f"⚠️ Falha na geração do artigo {i+1}")
                
                # Delay entre gerações
                if not self.simulation_mode and i < count - 1:
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Erro no artigo {i+1}: {e}")
                continue
        
        success_rate = len(articles) / count * 100 if count > 0 else 0
        logger.info(f"✅ Lote concluído: {len(articles)}/{count} artigos ({success_rate:.1f}%)")
        
        return articles

    def _clean_urls_in_content(self, content: str) -> str:
        """
        Remove espaços extras dos URLs que a IA pode ter inserido
        
        Args:
            content: Conteúdo HTML com URLs potencialmente malformadas
            
        Returns:
            Conteúdo com URLs corrigidas
        """
        if not content:
            return content
        
        # Primeira passada: Corrigir padrões específicos conhecidos
        url_fixes = [
            # Corrigir espaços específicos conhecidos
            (r'blog\. creativecopias\. com\. br', 'blog.creativecopias.com.br'),
            (r'creativecopias\. com\. br', 'creativecopias.com.br'),
            (r'www\. hp\. com', 'www.hp.com'),
            (r'www\. canon\. com', 'www.canon.com'),
            (r'www\. brother\. com', 'www.brother.com'),
            (r'www\. epson\. com', 'www.epson.com'),
            (r'www\. samsung\. com', 'www.samsung.com'),
            
            # Corrigir padrões mais gerais
            (r'(https?://[^"\s]*)\.\s+([^"\s/]*)\.\s+([^"\s/]*)', r'\1.\2.\3'),
            (r'(https?://[^"\s]*)\.\s+([^"\s/]*)', r'\1.\2'),
            
            # Corrigir espaços dentro de URLs (mais agressivo)
            (r'(https?://[^"]*?)\s+([a-zA-Z0-9\-]+)\s+\.\s+([a-zA-Z0-9\-]+)\s+\.\s+([a-zA-Z]{2,})', r'\1\2.\3.\4'),
            (r'(https?://[^"]*?)\s+([a-zA-Z0-9\-]+)\s+\.\s+([a-zA-Z]{2,})', r'\1\2.\3'),
            
            # Corrigir padrão específico que aparece: "blog . creativecopias . com . br"
            (r'blog\s*\.\s*creativecopias\s*\.\s*com\s*\.\s*br', 'blog.creativecopias.com.br'),
            (r'creativecopias\s*\.\s*com\s*\.\s*br', 'creativecopias.com.br'),
            (r'www\s*\.\s*hp\s*\.\s*com', 'www.hp.com'),
            (r'www\s*\.\s*canon\s*\.\s*com', 'www.canon.com'),
            (r'www\s*\.\s*brother\s*\.\s*com', 'www.brother.com'),
            (r'www\s*\.\s*epson\s*\.\s*com', 'www.epson.com'),
        ]
        
        cleaned_content = content
        
        # Aplicar todas as correções
        for pattern, replacement in url_fixes:
            cleaned_content = re.sub(pattern, replacement, cleaned_content, flags=re.IGNORECASE)
        
        # Segunda passada: Remover qualquer espaço restante em URLs
        # Encontrar todas as URLs e corrigir espaços internos
        def fix_url_spaces(match):
            url = match.group(1)
            # Remover todos os espaços da URL
            fixed_url = re.sub(r'\s+', '', url)
            return f'href="{fixed_url}"'
        
        # Aplicar correção em todas as URLs encontradas
        cleaned_content = re.sub(r'href="([^"]*)"', fix_url_spaces, cleaned_content)
        
        return cleaned_content

    def generate_articles_diverse_brands(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Gera artigos garantindo diversidade de marcas
        
        Args:
            count: Número de artigos a gerar
            
        Returns:
            Lista de artigos com marcas diferentes
        """
        logger.info(f"🎨 Gerando {count} artigos com marcas diversas")
        
        articles = []
        used_brands = set()
        
        # Resetar produtos usados
        self.product_database.reset_used_products()
        
        # Obter estatísticas
        stats = self.product_database.get_statistics()
        available_brands = list(stats['por_marca'].keys())
        
        logger.info(f"📊 Marcas disponíveis: {available_brands}")
        
        for i in range(count):
            try:
                # Tentar conseguir produto de marca ainda não usada
                product = None
                attempts = 0
                max_attempts = 10
                
                while attempts < max_attempts:
                    candidate_product = self.product_database.get_random_product(exclude_used=True)
                    
                    # Se a marca ainda não foi usada, ou se já tentamos muito, usar este produto
                    if candidate_product['marca'] not in used_brands or attempts >= 5:
                        product = candidate_product
                        break
                    
                    attempts += 1
                
                if not product:
                    logger.warning(f"⚠️ Não foi possível encontrar produto único para artigo {i+1}")
                    continue
                
                # Marcar marca como usada
                used_brands.add(product['marca'])
                
                logger.info(f"📝 Artigo {i+1}/{count}: {product['marca']} {product['nome']}")
                
                # Gerar artigo
                article = self.generate_article(product)
                if article:
                    articles.append(article)
                else:
                    logger.warning(f"⚠️ Falha na geração do artigo {i+1}")
                
                # Delay entre gerações
                if not self.simulation_mode and i < count - 1:
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Erro no artigo {i+1}: {e}")
                continue
        
        success_rate = len(articles) / count * 100 if count > 0 else 0
        logger.info(f"✅ Geração diversa concluída: {len(articles)}/{count} artigos ({success_rate:.1f}%)")
        logger.info(f"🏷️ Marcas utilizadas: {sorted(used_brands)}")
        
        return articles
 
 
 