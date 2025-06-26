"""
Sistema avançado de templates para geração de artigos SEO completos
"""

import os
import re
from typing import Dict, List, Any
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class AdvancedArticleTemplates:
    """Sistema avançado de templates para artigos SEO otimizados"""
    
    def __init__(self):
        """Inicializar templates avançados"""
        logger.info("🎨 Inicializando templates avançados de artigos SEO")
        
        # Mapeamento universal de categorias para URLs do site de vendas
        self.categoria_vendas_urls = {
            'impressoras': 'https://www.creativecopias.com.br/impressoras',
            'impressora': 'https://www.creativecopias.com.br/impressoras',
            'multifuncionais': 'https://www.creativecopias.com.br/impressoras',
            'multifuncional': 'https://www.creativecopias.com.br/impressoras',
            'cartuchos': 'https://www.creativecopias.com.br/cartuchos-de-tinta',
            'cartucho': 'https://www.creativecopias.com.br/cartuchos-de-tinta',
            'cartuchos-de-tinta': 'https://www.creativecopias.com.br/cartuchos-de-tinta',
            'cartuchos-de-toner': 'https://www.creativecopias.com.br/cartuchos-de-toner',
            'toner': 'https://www.creativecopias.com.br/cartuchos-de-toner',
            'toners': 'https://www.creativecopias.com.br/cartuchos-de-toner',
            'refil-de-toner': 'https://www.creativecopias.com.br/refil-de-toner',
            'refil-toner': 'https://www.creativecopias.com.br/refil-de-toner',
            'papel-fotografico': 'https://www.creativecopias.com.br/papel-fotografico',
            'papel': 'https://www.creativecopias.com.br/papel-fotografico',
            'scanner': 'https://www.creativecopias.com.br/scanner',
            'scanners': 'https://www.creativecopias.com.br/scanner',
            'suprimentos': 'https://www.creativecopias.com.br/suprimentos',
            'acessorios': 'https://www.creativecopias.com.br/acessorios',
            'acessorio': 'https://www.creativecopias.com.br/acessorios'
        }
    
    def get_categoria_url(self, categoria: str) -> str:
        """Retorna a URL correta do site de vendas para uma categoria"""
        categoria_slug = categoria.lower().replace(' ', '-')
        return self.categoria_vendas_urls.get(categoria_slug, f"https://www.creativecopias.com.br/{categoria_slug}")
    
    def _optimize_image_url(self, imagem_url: str, nome_produto: str) -> tuple:
        """
        Otimiza e valida URL da imagem garantindo URLs ABSOLUTAS
        
        Returns:
            tuple: (url_absoluta_otimizada, is_placeholder)
        """
        if not imagem_url or not imagem_url.strip():
            return None, False
            
        url = imagem_url.strip()
        
        # GARANTIR URL ABSOLUTA SEMPRE
        if not url.startswith('http'):
            base_url = "https://www.creativecopias.com.br"
            if url.startswith('/'):
                url = f"{base_url}{url}"
            else:
                url = f"{base_url}/{url}"
        
        # Verificar se a imagem realmente existe com validação inteligente
        try:
            import requests
            
            # URLs conhecidas e confiáveis não precisam validação completa
            trusted_domains = [
                'creativecopias.com.br',
                'via.placeholder.com', 
                'images.unsplash.com', 
                'picsum.photos',
                'localhost:3025'  # Para desenvolvimento
            ]
            is_trusted = any(domain in url for domain in trusted_domains)
            
            if is_trusted:
                logger.info(f"✅ Imagem de domínio confiável aceita: {url}")
                return url, False
            
            # Validação rápida para outras URLs (timeout reduzido)
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                # Verificar se é realmente uma imagem
                content_type = response.headers.get('content-type', '').lower()
                if any(img_type in content_type for img_type in ['image/', 'jpg', 'jpeg', 'png', 'gif', 'webp']):
                    logger.info(f"✅ Imagem validada (URL absoluta): {url}")
                    return url, False
                else:
                    logger.warning(f"⚠️ URL não é imagem válida - Content-Type: {content_type}")
            else:
                logger.warning(f"⚠️ Imagem não encontrada (HTTP {response.status_code}): {url}")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao validar imagem {url}: {e}")
        
        # Se chegou aqui, a imagem não é válida - retornar None para usar fallback
        logger.info(f"🔄 URL inválida, usando fallback para: {url}")
        return None, False
    
    def _generate_placeholder_image(self, categoria: str, nome_produto: str) -> str:
        """
        Retorna URL ABSOLUTA da imagem placeholder estática confiável
        Usa imagem local que sempre funciona
        """
        # USAR IMAGEM LOCAL GARANTIDA - sempre funciona
        return "https://blog.creativecopias.com.br/static/img/no-image.jpg"
    
    def _generate_image_html(self, imagem_url: str, nome_produto: str, is_placeholder: bool = False, is_small: bool = False) -> str:
        """Gera HTML otimizado para imagem com responsividade e fallback robusto"""
        if not imagem_url:
            return ""
        
        # Definir tamanhos baseado no contexto
        if is_small:
            style = "max-width: 200px; height: auto; margin-bottom: 15px; border-radius: 5px;"
            container_style = ""
        else:
            style = "max-width: 100%; height: auto; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"
            if is_placeholder:
                style += " opacity: 0.7; filter: grayscale(20%);"
            container_style = "text-align: center; margin: 20px 0; background: #f8f9fa; padding: 20px; border-radius: 8px;"
        
        # Texto alternativo e legenda
        alt_text = nome_produto
        title_text = f"{nome_produto} - {'Imagem ilustrativa' if is_placeholder else 'Imagem oficial do produto'}"
        caption = "Imagem ilustrativa - produto similar" if is_placeholder else "Imagem oficial do produto"
        
        # Sistema de fallback robusto - USAR ARQUIVO LOCAL GARANTIDO
        fallback_img = "https://blog.creativecopias.com.br/static/img/no-image.jpg"
        
        # HTML responsivo com fallback em caso de erro
        img_html = f"""<img src="{imagem_url}" 
         alt="{alt_text}" 
         itemprop="image" 
         style="{style}"
         loading="lazy"
         title="{title_text}"
         onerror="if(this.src!=='{fallback_img}'){{this.src='{fallback_img}'; this.alt='Produto - Imagem não disponível'; console.log('🔄 Fallback aplicado para:', '{nome_produto}');}}">"""
        
        if is_small:
            return img_html
        
        return f"""
<div style="{container_style}">
    {img_html}
    <p style="margin-top: 10px; font-size: 14px; color: #6c757d; font-style: italic;">{caption}</p>
</div>"""
    
    def generate_advanced_article(self, product_data: Dict[str, Any], categoria: str) -> Dict[str, Any]:
        """
        Gerar artigo super completo e otimizado para SEO
        
        Args:
            product_data: Dados do produto
            categoria: Categoria do produto
            
        Returns:
            Artigo completo e otimizado
        """
        try:
            # Extrair informações do produto
            nome = product_data.get('nome', 'Produto')
            marca = product_data.get('marca', 'N/A')
            preco = product_data.get('preco', {})
            preco_texto = self._format_price_for_template(preco)
            codigo = product_data.get('codigo', 'N/A')
            descricao_original = product_data.get('descricao', '')
            url_produto = product_data.get('url', '#')
            
            # Detectar tipo de produto e gerar conteúdo específico
            tipo_detalhes = self._detect_product_type(nome.lower())
            
            # Gerar título otimizado para SEO
            titulo_seo = self._generate_seo_title(nome, marca, tipo_detalhes['tipo'])
            
            # Gerar slug otimizado
            slug = self._generate_seo_slug(nome)
            
            # Gerar meta descrição otimizada
            meta_descricao = self._generate_meta_description(nome, marca, preco_texto, tipo_detalhes['tipo'])
            
            # Extrair URL da imagem
            imagem_produto = product_data.get('imagem', '')
            
            # Gerar conteúdo HTML completo
            conteudo_html = self._generate_complete_content(
                nome, marca, preco_texto, codigo, descricao_original, 
                url_produto, categoria, tipo_detalhes, imagem_produto
            )
            
            # Gerar tags SEO
            tags_seo = self._generate_seo_tags(nome, marca, categoria, tipo_detalhes['tipo'])
            
            logger.info(f"✅ Artigo avançado gerado: {titulo_seo}")
            
            return {
                'titulo': titulo_seo,
                'slug': slug,
                'meta_descricao': meta_descricao,
                'conteudo': conteudo_html,
                'tags': tags_seo,
                'wp_category': categoria,
                'produto_nome': nome,
                'produto_original': nome,
                'tipo_produto': categoria,
                'tom_usado': 'profissional',
                'status': 'pendente'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar artigo avançado: {e}")
            import traceback
            logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
            # Fallback para template básico
            return self._generate_basic_fallback(product_data, categoria)
    
    def _detect_product_type(self, nome_lower: str) -> Dict[str, Any]:
        """
        Detectar tipo de produto com ORDEM DE PRIORIDADE FIXA
        MESMA LÓGICA que _generate_seo_title para consistência
        """
        
        # PRIORIDADE 1: Multifuncionais (ANTES de impressora)
        if ('multifuncional' in nome_lower or 'mfc' in nome_lower or 
            'dcp' in nome_lower or 'all-in-one' in nome_lower):
            return {
                'tipo': 'multifuncional',
                'especificacoes': [
                    "Multifuncional 3 em 1 (Impressão, cópia, digitalização)",
                    "Conectividade avançada (USB, Wi-Fi, Ethernet)",
                    "Scanner de alta resolução integrado",
                    "Sistema de tanque de tinta ou laser",
                    "Painel de controle intuitivo",
                    "Impressão frente e verso automática"
                ],
                'beneficios': [
                    "Economia de espaço no escritório",
                    "Múltiplas funções em um único equipamento",
                    "Custo-benefício excepcional",
                    "Facilidade de uso e instalação",
                    "Qualidade profissional garantida"
                ],
                'aplicacoes': ["Escritórios pequenos", "Home office", "Empresas", "Estudantes", "Profissionais autônomos"],
                'palavras_chave': ["multifuncional", "3em1", "scanner", "copiadora", "impressora", "compacto"]
            }
        
        # PRIORIDADE 2: Cabeças de impressão (específico)
        elif 'cabeça' in nome_lower and 'impressão' in nome_lower:
            return {
                'tipo': 'cabeça de impressão',
                'especificacoes': [
                    "Tecnologia Precision Drop avançada",
                    "Múltiplos bicos de alta precisão",
                    "Compatibilidade específica garantida",
                    "Construção robusta e durável",
                    "Instalação plug-and-play simples",
                    "Controle de qualidade rigoroso"
                ],
                'beneficios': [
                    "Qualidade excepcional de impressão",
                    "Maior vida útil da impressora",
                    "Instalação rápida e fácil",
                    "Compatibilidade 100% assegurada",
                    "Melhoria significativa na qualidade"
                ],
                'aplicacoes': ["Manutenção preventiva", "Gráficas", "Escritórios", "Design profissional"],
                'palavras_chave': ["cabeça impressão", "precisão", "qualidade", "durabilidade", "compatível"]
            }
        
        # PRIORIDADE 3: Cartuchos e tintas (sem impressora no nome)
        elif ('cartucho' in nome_lower or 'tinta' in nome_lower) and 'impressora' not in nome_lower:
            return {
                'tipo': 'cartucho',
                'especificacoes': [
                    "Cartucho original de alta qualidade",
                    "Máximo rendimento de páginas",
                    "Compatibilidade 100% garantida",
                    "Pigmentação profissional resistente",
                    "Tecnologia anti-vazamento",
                    "Chip inteligente integrado"
                ],
                'beneficios': [
                    "Cores mais vivas e duradouras",
                    "Proteção completa da impressora",
                    "Máximo aproveitamento por página",
                    "Qualidade profissional constante",
                    "Garantia total do fabricante"
                ],
                'aplicacoes': ["Impressão profissional", "Documentos importantes", "Fotografias", "Marketing", "Escritórios"],
                'palavras_chave': ["cartucho", "original", "qualidade", "rendimento", "compatível", "tinta"]
            }
        
        # PRIORIDADE 4: Toners (sem impressora no nome)
        elif 'toner' in nome_lower and 'impressora' not in nome_lower:
            return {
                'tipo': 'toner',
                'especificacoes': [
                    "Toner laser de alta performance",
                    "Rendimento superior de páginas",
                    "Compatibilidade específica testada",
                    "Qualidade de impressão profissional",
                    "Fórmula avançada anti-desbotamento",
                    "Embalagem protetora lacrada"
                ],
                'beneficios': [
                    "Impressões nítidas e duradouras",
                    "Economia no custo por página",
                    "Velocidade de impressão mantida",
                    "Proteção do equipamento laser",
                    "Qualidade constante até o fim"
                ],
                'aplicacoes': ["Impressão laser", "Documentos corporativos", "Relatórios", "Apresentações", "Escritórios"],
                'palavras_chave': ["toner", "laser", "rendimento", "qualidade", "profissional", "economia"]
            }
        
        # PRIORIDADE 5: Papéis
        elif 'papel' in nome_lower:
            return {
                'tipo': 'papel',
                'especificacoes': [
                    "Papel de gramatura premium",
                    "Acabamento profissional superior",
                    "Compatibilidade universal testada",
                    "Resistência e durabilidade",
                    "Brancura e opacidade ideais",
                    "Certificação de qualidade ISO"
                ],
                'beneficios': [
                    "Impressões de qualidade excepcional",
                    "Durabilidade superior no tempo",
                    "Versatilidade para múltiplos usos",
                    "Acabamento profissional garantido",
                    "Excelente custo-benefício"
                ],
                'aplicacoes': ["Fotografias profissionais", "Documentos importantes", "Marketing", "Apresentações", "Arte"],
                'palavras_chave': ["papel", "qualidade", "fotografico", "impressão", "profissional", "premium"]
            }
        
        # PRIORIDADE 6: Scanners
        elif 'scanner' in nome_lower:
            return {
                'tipo': 'scanner',
                'especificacoes': [
                    "Alta resolução de digitalização",
                    "Velocidade de escaneamento otimizada",
                    "Conectividade múltipla (USB, Wi-Fi)",
                    "Software avançado incluído",
                    "Sensor CIS de alta precisão",
                    "Alimentador automático de documentos"
                ],
                'beneficios': [
                    "Digitalização profissional rápida",
                    "Qualidade de imagem superior",
                    "Facilidade de uso intuitiva",
                    "Produtividade aumentada",
                    "Versatilidade para todos os formatos"
                ],
                'aplicacoes': ["Escritórios", "Digitalização profissional", "Arquivamento", "Design", "Documentação"],
                'palavras_chave': ["scanner", "digitalização", "resolução", "qualidade", "profissional", "rápido"]
            }
        
        # PRIORIDADE 7: Impressoras reais (DEPOIS de multifuncionais e SOMENTE se for uma impressora de verdade)
        elif ('impressora' in nome_lower and 
              not any(word in nome_lower for word in ['suporte', 'cabo', 'mesa', 'stand', 'gaveta', 'bandeja', 'fita'])):
            return {
                'tipo': 'impressora',
                'especificacoes': [
                    "Tecnologia de impressão avançada",
                    "Alta velocidade e resolução",
                    "Conectividade completa (USB, Wi-Fi, Ethernet)",
                    "Sistema de tinta ou toner eficiente",
                    "Compatibilidade universal",
                    "Baixo consumo energético"
                ],
                'beneficios': [
                    "Impressões de qualidade profissional",
                    "Economia no custo por página",
                    "Rapidez para grandes volumes",
                    "Facilidade de instalação e uso",
                    "Durabilidade e confiabilidade"
                ],
                'aplicacoes': ["Escritórios", "Home office", "Empresas", "Estudantes", "Profissionais"],
                'palavras_chave': ["impressora", "qualidade", "rapidez", "economia", "profissional", "confiável"]
            }
        
        # FALLBACK: Produto genérico
        else:
            return {
                'tipo': 'produto',
                'especificacoes': [
                    "Material de primeira qualidade",
                    "Construção robusta e durável",
                    "Compatibilidade ampla testada",
                    "Garantia completa do fabricante",
                    "Suporte técnico especializado",
                    "Controle de qualidade rigoroso"
                ],
                'beneficios': [
                    "Excelente qualidade garantida",
                    "Ótimo custo-benefício comprovado",
                    "Facilidade de uso e instalação",
                    "Durabilidade superior testada",
                    "Suporte técnico completo"
                ],
                'aplicacoes': ["Uso profissional", "Empresas", "Escritórios", "Home office", "Estudantes"],
                'palavras_chave': ["produto", "qualidade", "profissional", "durabilidade", "confiável", "premium"]
            }
    
    def _generate_seo_title(self, nome: str, marca: str, tipo: str) -> str:
        """
        Gerar título SEO preciso e específico baseado no nome COMPLETO do produto
        ORDEM DE PRIORIDADE FIXA para evitar classificações incorretas
        """
        
        nome_lower = nome.lower()
        
        # PRIORIDADE 1: Multifuncionais (DEVE vir antes de impressora)
        if ('multifuncional' in nome_lower or 'mfc' in nome_lower or 
            'dcp' in nome_lower or 'all-in-one' in nome_lower):
            if 'tanque' in nome_lower and 'tinta' in nome_lower:
                return f"{nome[:45]}: Multifuncional Tanque de Tinta com Wireless"
            elif 'laser' in nome_lower:
                return f"{nome[:45]}: Multifuncional Laser Profissional"
            elif 'a3' in nome_lower:
                return f"{nome[:45]}: Multifuncional A3 de Alto Desempenho"
            else:
                return f"{nome[:45]}: Multifuncional 3 em 1 Completa"
        
        # PRIORIDADE 2: Cabeças de impressão (específico)
        elif 'cabeça' in nome_lower and 'impressão' in nome_lower:
            return f"{nome[:45]}: Cabeça de Impressão Original"
        
        # PRIORIDADE 3: Cartuchos e tintas 
        elif ('cartucho' in nome_lower or 'tinta' in nome_lower) and 'impressora' not in nome_lower:
            if 'kit' in nome_lower:
                return f"{nome[:45]}: Kit de Cartuchos Originais"
            elif 'tricolor' in nome_lower:
                return f"{nome[:45]}: Cartucho Tricolor Original"
            elif 'preto' in nome_lower or 'black' in nome_lower:
                return f"{nome[:45]}: Cartucho Preto de Alta Qualidade"
            else:
                return f"{nome[:45]}: Cartucho Original Compatível"
        
        # PRIORIDADE 4: Toners (específico)
        elif 'toner' in nome_lower and 'impressora' not in nome_lower:
            if 'kit' in nome_lower:
                return f"{nome[:45]}: Kit de Toners Compatíveis"
            elif 'original' in nome_lower:
                return f"{nome[:45]}: Toner Original de Alta Performance"
            else:
                return f"{nome[:45]}: Toner Compatível Premium"
        
        # PRIORIDADE 5: Papéis
        elif 'papel' in nome_lower:
            if 'fotografico' in nome_lower or 'photo' in nome_lower:
                return f"{nome[:45]}: Papel Fotográfico Premium"
            elif 'a4' in nome_lower:
                return f"{nome[:45]}: Papel A4 de Qualidade Superior"
            else:
                return f"{nome[:45]}: Papel Profissional Premium"
        
        # PRIORIDADE 6: Scanners
        elif 'scanner' in nome_lower:
            if 'workforce' in nome_lower:
                return f"{nome[:45]}: Scanner Profissional de Mesa"
            else:
                return f"{nome[:45]}: Scanner de Alta Resolução"
        
        # PRIORIDADE 7: Impressoras reais (DEPOIS de multifuncionais e SOMENTE se for uma impressora de verdade)
        elif ('impressora' in nome_lower and 
              not any(word in nome_lower for word in ['suporte', 'cabo', 'mesa', 'stand', 'gaveta', 'bandeja', 'fita'])):
            if 'tanque' in nome_lower and 'tinta' in nome_lower:
                return f"{nome[:45]}: Impressora Tanque de Tinta Econômica"
            elif 'laser' in nome_lower:
                return f"{nome[:45]}: Impressora Laser de Alta Velocidade"
            elif 'jato' in nome_lower:
                return f"{nome[:45]}: Impressora Jato de Tinta Profissional"
            elif 'a3' in nome_lower:
                return f"{nome[:45]}: Impressora A3 de Grande Formato"
        else:
                return f"{nome[:45]}: Impressora de Alta Qualidade"
        
        # FALLBACK: Usar nome completo + descrição genérica
        return f"{nome[:45]}: Análise Completa e Especificações"
    
    def _extract_key_features(self, nome: str) -> list:
        """Extrai características principais do produto"""
        features = []
        nome_lower = nome.lower()
        
        # Tecnologias
        if 'laser' in nome_lower:
            features.append('laser')
        if 'jato' in nome_lower or 'ink' in nome_lower:
            features.append('jato_tinta')
        if 'wireless' in nome_lower or 'wifi' in nome_lower:
            features.append('wireless')
        
        # Características
        if 'original' in nome_lower:
            features.append('original')
        if 'tricolor' in nome_lower or 'colorido' in nome_lower:
            features.append('colorido')
        if 'preto' in nome_lower or 'black' in nome_lower:
            features.append('preto')
        if 'duplex' in nome_lower:
            features.append('duplex')
        if 'multifuncional' in nome_lower:
            features.append('multifuncional')
            
        # Tamanhos
        if 'a4' in nome_lower:
            features.append('a4')
        if 'a3' in nome_lower:
            features.append('a3')
            
        return features
    
    def _simplify_product_name(self, nome: str, marca: str) -> str:
        """Simplifica o nome do produto mantendo o essencial"""
        # Remover palavras desnecessárias
        palavras_remover = [
            'produto', 'item', 'unidade', 'pacote', 'folhas', 'original',
            'compatível', 'tamanho', 'gramatura', 'qualidade', 'premium'
        ]
        
        nome_clean = nome
        for palavra in palavras_remover:
            nome_clean = nome_clean.replace(palavra.title(), '').replace(palavra.lower(), '')
        
        # Limpar espaços extras
        nome_clean = ' '.join(nome_clean.split())
        
        # Se ficou muito longo, pegar partes essenciais
        if len(nome_clean) > 35:
            palavras = nome_clean.split()
            # Pegar marca + modelo + característica principal
            partes_importantes = []
            
            for palavra in palavras:
                if marca and marca.upper() in palavra.upper():
                    partes_importantes.append(palavra)
                elif any(car in palavra.lower() for car in ['hp', 'canon', 'epson', 'brother']):
                    partes_importantes.append(palavra)
                elif any(num in palavra for num in ['664', '2774', '122', '60', '662', 'es-400']):
                    partes_importantes.append(palavra)
                elif palavra.lower() in ['laser', 'jato', 'tricolor', 'preto', 'a4', 'a3', 'glossy']:
                    partes_importantes.append(palavra)
                    
            if partes_importantes:
                nome_clean = ' '.join(partes_importantes[:3])  # Máximo 3 palavras
        
        return nome_clean.strip() or nome[:30]
    
    def _generate_seo_slug(self, nome: str) -> str:
        """Gerar slug SEO otimizado"""
        
        slug = nome.lower()
        # Remover caracteres especiais
        slug = re.sub(r'[^\w\s-]', '', slug)
        # Substituir espaços por hífens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remover hífens múltiplos
        slug = re.sub(r'-+', '-', slug)
        # Remover hífens do início e fim
        slug = slug.strip('-')
        
        return slug[:50]  # Limitar tamanho
    
    def _generate_meta_description(self, nome: str, marca: str, preco: str, tipo: str) -> str:
        """Gerar meta descrição otimizada (150-160 caracteres) - SEM PREÇOS"""
        
        if tipo == "impressora":
            base = f"Review completo da {nome}. Análise técnica, especificações e onde comprar."
        elif tipo == "cartucho":
            base = f"Cartucho {nome} original - Análise de qualidade, rendimento e compatibilidade."
        elif tipo == "cabeça de impressão":
            base = f"Cabeça de impressão {nome} - Review técnico, qualidade e instalação."
        else:
            base = f"{nome} - Review completo, especificações técnicas e análise detalhada."
        
        # Garantir que não passe de 160 caracteres
        if len(base) > 160:
            base = base[:157] + "..."
        
        return base
    
    def _generate_seo_tags(self, nome: str, marca: str, categoria: str, tipo: str) -> List[str]:
        """Gerar tags SEO otimizadas"""
        
        tags = [
            nome.lower().replace(' ', '-'),
            categoria.lower(),
            tipo.lower().replace(' ', '-'),
            "review-2025",
            "analise-tecnica",
            "custo-beneficio"
        ]
        
        if marca and marca != "N/A":
            tags.append(marca.lower())
        
        # Adicionar tags específicas por tipo
        if tipo == "impressora":
            tags.extend(["impressora-profissional", "qualidade-impressao", "escritorio"])
        elif tipo == "cartucho":
            tags.extend(["cartucho-original", "tinta-qualidade", "compatibilidade"])
        elif tipo == "cabeça de impressão":
            tags.extend(["cabeca-impressao", "precisao", "durabilidade"])
        
        return tags[:8]  # Limitar a 8 tags
    
    def _generate_complete_content(self, nome: str, marca: str, preco: str, codigo: str, 
                                 descricao: str, url: str, categoria: str, 
                                 tipo_detalhes: Dict[str, Any], imagem: str = None) -> str:
        """Gerar conteúdo HTML completo e otimizado"""
        
        tipo = tipo_detalhes['tipo']
        especificacoes = tipo_detalhes['especificacoes']
        beneficios = tipo_detalhes['beneficios']
        aplicacoes = tipo_detalhes['aplicacoes']
        
        # 🚨 CORREÇÃO CRÍTICA: Formatar preço logo no início
        preco_formatado = self._format_price_for_template(preco)
        
        # Descrição aprimorada se a original for muito básica
        if not descricao or len(descricao) < 50:
            descricao = f"O {nome} é um produto de alta qualidade, desenvolvido para atender às mais exigentes demandas do mercado. Com tecnologia de ponta e materiais premium, oferece desempenho excepcional e durabilidade comprovada."
        
        # Gerar seção de especificações
        spec_html = "\n".join([f"<li>{spec}</li>" for spec in especificacoes])
        
        # Gerar seção de benefícios
        beneficios_html = "\n".join([f"<li>{beneficio}</li>" for beneficio in beneficios])
        
        # CORREÇÃO: Gerar links funcionais usando método centralizado
        categoria_url_vendas = self.get_categoria_url(categoria)
        link_interno = f'<a href="{categoria_url_vendas}" target="_blank">Veja mais {categoria.lower()}</a>'
        
        # CORREÇÃO CRÍTICA: Usar URL real do produto se disponível
        url_produto_real = url.strip() if url else ''
        
        # CORREÇÃO CRÍTICA: Link externo baseado na marca correta
        if 'hp' in marca.lower():
            link_externo = '<a href="https://www.hp.com.br" rel="nofollow" target="_blank">Site oficial da HP</a>'
        elif 'canon' in marca.lower():
            link_externo = '<a href="https://www.canon.com.br" rel="nofollow" target="_blank">Site oficial da Canon</a>'
        elif 'epson' in marca.lower():
            link_externo = '<a href="https://www.epson.com.br" rel="nofollow" target="_blank">Site oficial da Epson</a>'
        elif 'brother' in marca.lower():
            link_externo = '<a href="https://www.brother.com.br" rel="nofollow" target="_blank">Site oficial da Brother</a>'
        elif 'samsung' in marca.lower():
            link_externo = '<a href="https://www.samsung.com.br" rel="nofollow" target="_blank">Site oficial da Samsung</a>'
        elif 'xerox' in marca.lower():
            link_externo = '<a href="https://www.xerox.com.br" rel="nofollow" target="_blank">Site oficial da Xerox</a>'
        else:
            # CORREÇÃO: Usar página inicial da Creative Cópias como fallback
            link_externo = '<a href="https://www.creativecopias.com.br" rel="nofollow" target="_blank">catálogo de produtos</a>'
        
        # CORREÇÃO: Priorizar URL real do produto, senão buscar nos dados, senão usar categoria
        if url_produto_real and 'creativecopias.com.br' in url_produto_real:
            # Garantir que a URL está correta
            if not url_produto_real.startswith('http'):
                url_produto_real = 'https://' + url_produto_real
            if 'www.' not in url_produto_real and 'creativecopias.com.br' in url_produto_real:
                url_produto_real = url_produto_real.replace('creativecopias.com.br', 'www.creativecopias.com.br')
            url_produto = url_produto_real
            logger.info(f"✅ Usando URL real do produto: {url_produto}")
        else:
            # Tentar buscar URL real nos dados armazenados
            found_url = self._search_product_url_in_data(nome)
            if found_url:
                url_produto = found_url
                logger.info(f"🔍 URL encontrada nos dados: {url_produto}")
            else:
                # Fallback para categoria
                url_produto = categoria_url_vendas
                logger.info(f"⚠️ Usando categoria como fallback: {url_produto}")
        
        # Preparar informações do produto (apenas as preenchidas) - SEM PREÇOS
        info_produto = []
        
        if categoria and categoria.strip() and categoria != 'N/A':
            info_produto.append(f'<strong>Categoria:</strong> <span itemprop="category">{categoria}</span>')
        
        # ❌ PREÇOS REMOVIDOS - Cliente solicitou remoção pois mudam constantemente
        
        if codigo and codigo.strip() and codigo != 'N/A':
            info_produto.append(f'<strong>Código:</strong> <span itemprop="sku">{codigo}</span>')
        
        if marca and marca.strip() and marca != 'N/A':
            info_produto.append(f'<strong>Marca:</strong> <span itemprop="brand" itemscope itemtype="https://schema.org/Brand"><span itemprop="name">{marca}</span></span>')
        
        # 🖼️ SISTEMA DE IMAGENS INTELIGENTE E ESTRATÉGICO
        imagem_url = None
        is_placeholder = False
        
        # ETAPA 1: Validar imagem fornecida
        if imagem and imagem.strip():
            imagem_otimizada, _ = self._optimize_image_url(imagem, nome)
            if imagem_otimizada:
                imagem_url = imagem_otimizada
                logger.info(f"✅ Usando imagem fornecida validada: {imagem_url}")
        
        # ETAPA 2: Se imagem não é válida, buscar imagem real inteligente
        if not imagem_url:
            logger.info(f"🔍 Buscando imagem real para: {nome}")
            imagem_url = self._search_real_product_image(nome, marca)
        
        # ETAPA 3: Gerar HTML da imagem
        if imagem_url:
            # Usar imagem real encontrada ou validada
            imagem_html = self._generate_image_html(imagem_url, nome, False, False)
            logger.info(f"🖼️ Imagem real implementada: {imagem_url}")
        else:
            # Fallback para placeholder apenas se nenhuma imagem real for encontrada
            logger.warning(f"⚠️ Usando placeholder para: {nome}")
            imagem_url = self._generate_placeholder_image(categoria, nome)
            is_placeholder = True
            imagem_html = self._generate_image_html(imagem_url, nome, True, False)

        # Gerar HTML das informações apenas se houver dados
        info_html = ""
        if info_produto:
            info_items = " • ".join(info_produto)
            info_html = f"""
<div style="background: #f8f9fa; border: 1px solid #e9ecef; padding: 20px; margin: 20px 0; border-radius: 5px;">
    <h3 style="margin-top: 0; color: #495057; font-size: 18px;">Informações do Produto</h3>
    <p style="margin-bottom: 0; line-height: 1.8;">{info_items}</p>
</div>"""

        # Template HTML completo - estilo sóbrio e profissional - SEM PREÇOS
        conteudo = f"""
<div itemscope itemtype="https://schema.org/Product">

<h1 itemprop="name">{nome}</h1>

{imagem_html}

{info_html}

<h2>Descrição</h2>
<div itemprop="description" style="margin: 20px 0;">
    <p style="line-height: 1.6; margin-bottom: 15px;">{descricao}</p>
    
    <p style="line-height: 1.6;">Este produto foi desenvolvido para proporcionar a melhor experiência ao usuário, combinando tecnologia avançada com facilidade de uso. Ideal para quem busca qualidade, confiabilidade e resultados superiores.</p>
</div>

<h2>Especificações Técnicas</h2>
<div style="background: #f8f9fa; border: 1px solid #e9ecef; padding: 20px; margin: 20px 0; border-radius: 5px;">
    <ul style="margin: 0; padding-left: 20px;">
        {spec_html}
    </ul>
</div>

<h2>Principais Diferenciais</h2>
<div style="margin: 20px 0;">
    <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
        {beneficios_html}
    </ul>
    
    <p style="margin-top: 20px;"><strong>Ideal para:</strong> {', '.join(aplicacoes)}</p>
    
    <p style="margin-top: 15px;">
        Para mais informações sobre produtos similares, {link_interno}. 
        Você também pode visitar o {link_externo} para conhecer toda a linha de produtos.
    </p>
</div>

<h2>Características do Produto</h2>
<div style="margin: 20px 0;">
    <p><strong>Qualidade Superior:</strong> Este produto oferece excelente desempenho e durabilidade, especialmente considerando sua qualidade superior e tecnologia avançada.</p>
    
    <p><strong>Facilidade de Uso:</strong> A instalação e configuração são simples e rápidas, não exigindo conhecimentos técnicos avançados. Vem com manual detalhado e suporte técnico disponível.</p>
</div>

<h2>Garantia e Suporte</h2>
<div style="background: #f8f9fa; border: 1px solid #e9ecef; padding: 20px; margin: 20px 0; border-radius: 5px;">
    <ul style="margin: 0; padding-left: 20px;">
        <li><strong>Garantia do fabricante</strong> - Produto com cobertura completa</li>
        <li><strong>Suporte técnico especializado</strong> - Equipe pronta para ajudar</li>
        <li><strong>Atendimento dedicado</strong> - Tire suas dúvidas quando precisar</li>
    </ul>
</div>

<h2>Onde Encontrar</h2>
<div style="background: #f8f9fa; border: 1px solid #e9ecef; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center;">
    {self._generate_image_html(imagem_url, nome, is_placeholder, True) if imagem_url else ''}
    <p style="margin-bottom: 15px;">Produto disponível para consulta de valores atualizados</p>
    <p style="margin: 15px 0;">
        <a href="{url_produto}" target="_blank" style="background: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
            Ver Produto no Site
        </a>
    </p>
    <p style="font-size: 14px; color: #6c757d; margin-top: 10px;">Entrega rápida • Pagamento seguro • Garantia incluída</p>
</div>

<h2>Perguntas Frequentes</h2>
<div style="margin: 20px 0;">
    <div style="margin-bottom: 20px;">
        <h3>Este produto tem garantia?</h3>
        <p>Sim, todos os nossos produtos possuem garantia do fabricante e suporte técnico especializado. A cobertura inclui defeitos de fabricação e problemas técnicos.</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3>Como é feita a entrega?</h3>
        <p>Entregamos em todo o Brasil com diferentes opções de frete. O prazo varia conforme sua localização, mas geralmente é de 3 a 7 dias úteis.</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3>Posso trocar se não gostar?</h3>
        <p>Claro! Temos política de troca e devolução conforme o Código de Defesa do Consumidor. Você tem até 7 dias para desistir da compra.</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3>Como consultar o preço atualizado?</h3>
        <p>Os preços são atualizados constantemente. Para obter o valor mais recente e condições de pagamento, acesse o produto em nosso site oficial.</p>
    </div>
    
    <div>
        <h3>Como entrar em contato?</h3>
        <p>Nossa equipe de suporte está sempre disponível para esclarecer dúvidas e oferecer o melhor atendimento. Entre em contato através do nosso site.</p>
    </div>
</div>

<h2>Conclusão</h2>
<div style="margin: 20px 0;">
    <p>O <strong>{nome}</strong> é uma excelente escolha para quem busca qualidade, durabilidade e bom custo-benefício. Com especificações técnicas superiores e suporte completo, é um investimento que vale a pena.</p>
    
    <p>Este produto está disponível agora e pode ser exatamente o que você precisa para melhorar seus resultados e ter a tranquilidade de uma compra segura.</p>
    
    <div style="text-align: center; margin-top: 20px;">
        <a href="{url_produto}" target="_blank" style="background: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
            Consultar Valores
        </a>
    </div>
</div>

</div>
"""
        
        return conteudo.strip()
    
    def _generate_basic_fallback(self, product_data: Dict[str, Any], categoria: str) -> Dict[str, Any]:
        """Template básico como fallback em caso de erro - SEM PREÇOS"""
        
        nome = product_data.get('nome', 'Produto')
        
        return {
            'titulo': f"Review: {nome}",
            'slug': nome.lower().replace(' ', '-'),
            'meta_descricao': f"Review do {nome} - Análise completa e onde encontrar",
            'conteudo': f"<h1>{nome}</h1><p>Produto de qualidade disponível para consulta de valores atualizados.</p>",
            'tags': [categoria, 'review'],
            'wp_category': categoria,
            'produto_nome': nome,
            'produto_original': nome,
            'tipo_produto': categoria,
            'tom_usado': 'profissional',
            'status': 'pendente'
        }
    
    def _search_real_product_image(self, nome_produto: str, marca: str = None) -> str:
        """
        Busca imagem real do produto usando produtos já scraped
        VERSÃO MELHORADA com busca exata priorizada + MAPEAMENTO ESPECÍFICO
        
        Args:
            nome_produto: Nome do produto para buscar
            marca: Marca do produto (opcional)
            
        Returns:
            URL da imagem real do produto ou None se não encontrar
        """
        try:
            import sqlite3
            import os
            import re
            
            # Limpar nome do produto
            nome_clean = nome_produto.strip()
            nome_lower = nome_clean.lower()
            
            logger.info(f"🔍 Buscando imagem para produto: '{nome_produto}'")
            
            # 🎯 MAPEAMENTO ESPECÍFICO PARA PRODUTOS CORRIGIDOS
            specific_mappings = {
                'cabo do painel de controle pantum m6800 m7100 m7200': 'https://www.creativecopias.com.br/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/1/1/11689_ampliada.jpg',
                'cabo painel pantum': 'https://www.creativecopias.com.br/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/1/1/11689_ampliada.jpg',
                'cabo do painel de controle pantum': 'https://www.creativecopias.com.br/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/1/1/11689_ampliada.jpg',
                '301022274001': 'https://www.creativecopias.com.br/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/1/1/11689_ampliada.jpg'
            }
            
            # Verificar mapeamento específico primeiro
            for key, image_url in specific_mappings.items():
                if key.lower() in nome_lower:
                    logger.info(f"🎯 MAPEAMENTO ESPECÍFICO encontrado para '{key}': {image_url}")
                    return image_url
            
            # Verificar arquivos JSON de produtos primeiro
            import glob
            json_files = glob.glob('logs/products_*.json')
            
            for json_file in json_files:
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Suportar tanto formato lista quanto formato com metadata
                    products = []
                    if isinstance(data, list):
                        products = data
                    elif isinstance(data, dict) and 'produtos' in data:
                        products = data['produtos']
                    elif isinstance(data, dict) and 'products' in data:
                        products = data['products']
                    else:
                        # Se é dict mas não tem produtos/products, pode ser um único produto
                        if data.get('nome') and data.get('imagem'):
                            products = [data]
                        
                    for product in products:
                        if isinstance(product, dict) and product.get('imagem'):
                            product_name = product.get('nome', '').strip()
                            product_name_lower = product_name.lower()
                            
                            # BUSCA EXATA PRIORIZADA (100% match) - NORMALIZAR ESPAÇOS
                            nome_normalized = ' '.join(nome_lower.split())
                            product_normalized = ' '.join(product_name_lower.split())
                            
                            if nome_normalized == product_normalized:
                                image_url = product['imagem']
                                if image_url and 'creativecopias.com.br' in image_url:
                                    valid_url, _ = self._optimize_image_url(image_url, nome_produto)
                                    if valid_url:
                                        logger.info(f"✅ MATCH EXATO encontrado em {json_file}: {valid_url}")
                                        return valid_url
                            
                            # BUSCA POR CÓDIGOS ESPECÍFICOS (BTD1003PK, etc.)
                            # Extrair códigos alfanuméricos específicos
                            codes_produto = re.findall(r'[A-Z]+\d+[A-Z]*', nome_produto.upper())
                            codes_db = re.findall(r'[A-Z]+\d+[A-Z]*', product_name.upper())
                            
                            if codes_produto and codes_db:
                                # Se tem códigos em comum, é muito provável ser o mesmo produto
                                common_codes = set(codes_produto) & set(codes_db)
                                if common_codes:
                                    image_url = product['imagem']
                                    if image_url and 'creativecopias.com.br' in image_url:
                                        valid_url, _ = self._optimize_image_url(image_url, nome_produto)
                                        if valid_url:
                                            logger.info(f"✅ MATCH POR CÓDIGO {common_codes} em {json_file}: {valid_url}")
                                            return valid_url
                            
                            # BUSCA POR SIMILARIDADE ALTA (75%+ de palavras em comum)
                            palavras_produto = set(re.findall(r'\w+', nome_lower))
                            palavras_db = set(re.findall(r'\w+', product_name_lower))
                            
                            # Remover palavras muito comuns
                            stop_words = {'de', 'da', 'do', 'com', 'para', 'e', 'em', 'original', 'compativel'}
                            palavras_produto = palavras_produto - stop_words
                            palavras_db = palavras_db - stop_words
                            
                            if palavras_produto and palavras_db:
                                intersecao = palavras_produto & palavras_db
                                uniao = palavras_produto | palavras_db
                                similaridade = len(intersecao) / len(uniao) if uniao else 0
                                
                                # Se similaridade alta (75%+), usar a imagem
                                if similaridade >= 0.75:
                                    image_url = product['imagem']
                                    if image_url and 'creativecopias.com.br' in image_url:
                                        valid_url, _ = self._optimize_image_url(image_url, nome_produto)
                                        if valid_url:
                                            logger.info(f"✅ MATCH ALTA SIMILARIDADE ({similaridade:.2%}) em {json_file}: {valid_url}")
                                            return valid_url
                                        
                except Exception as e:
                    logger.debug(f"Erro ao processar {json_file}: {e}")
                    continue
            
            # FALLBACK: Busca por palavras-chave importantes
            search_words = []
            
            # Extrair marca
            if marca:
                search_words.append(marca.lower())
            
            # Extrair códigos importantes
            codes = re.findall(r'[A-Z]+\d+[A-Z]*', nome_produto.upper())
            search_words.extend([code.lower() for code in codes])
            
            # Extrair números importantes
            numbers = re.findall(r'\d{3,}', nome_produto)  # Números de 3+ dígitos
            search_words.extend(numbers)
            
            # Extrair tipo de produto
            tipos = ['cartucho', 'toner', 'impressora', 'papel', 'scanner', 'multifuncional', 'tinta', 'garrafas', 'kit']
            for tipo in tipos:
                if tipo in nome_lower:
                    search_words.append(tipo)
            
            logger.info(f"🔍 Busca por palavras-chave: {search_words}")
            
            # Segunda passada com palavras-chave
            for json_file in json_files:
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    products = []
                    if isinstance(data, list):
                        products = data
                    elif isinstance(data, dict) and 'produtos' in data:
                        products = data['produtos']
                    elif isinstance(data, dict) and 'products' in data:
                        products = data['products']
                    else:
                        if data.get('nome') and data.get('imagem'):
                            products = [data]
                        
                    for product in products:
                        if isinstance(product, dict) and product.get('imagem'):
                            product_name = product.get('nome', '').lower()
                            
                            # Contar matches de palavras-chave importantes
                            score = 0
                            for word in search_words:
                                if word and len(word) > 2 and word.lower() in product_name:
                                    score += 1
                                    
                            # Se tem boa similaridade por palavras-chave (2+ matches)
                            if score >= 2:
                                image_url = product['imagem']
                                if image_url and 'creativecopias.com.br' in image_url:
                                    valid_url, _ = self._optimize_image_url(image_url, nome_produto)
                                    if valid_url:
                                        logger.info(f"✅ MATCH POR PALAVRAS-CHAVE (score {score}) em {json_file}: {valid_url}")
                                        return valid_url
                                        
                except Exception as e:
                    logger.debug(f"Erro ao processar {json_file}: {e}")
                    continue
            
            # Se não encontrou em JSON, tentar SQLite (mesmo algoritmo)
            db_paths = ['logs/products_cache.db', 'data/products.db']
            for db_path in db_paths:
                if not os.path.exists(db_path):
                    continue
                    
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    query = """
                    SELECT nome, imagem FROM products 
                    WHERE imagem IS NOT NULL AND imagem != ''
                    """
                    
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    for row in results:
                        product_name, image_url = row
                        if not product_name or not image_url:
                            continue
                            
                        # Mesma lógica de busca - NORMALIZAR ESPAÇOS
                        nome_normalized = ' '.join(nome_lower.split())
                        product_normalized = ' '.join(product_name.lower().split())
                        
                        if nome_normalized == product_normalized:
                            valid_url, _ = self._optimize_image_url(image_url, nome_produto)
                            if valid_url:
                                logger.info(f"✅ MATCH EXATO em BD: {valid_url}")
                                conn.close()
                                return valid_url
                    
                    conn.close()
                    
                except Exception as e:
                    logger.debug(f"Erro ao acessar BD {db_path}: {e}")
                    continue
                    
            logger.warning(f"⚠️ Nenhuma imagem real encontrada para: {nome_produto}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar imagem real: {e}")
            return None 
    
    def _format_price_for_template(self, preco: Any) -> str:
        """
        🚨 CORREÇÃO CRÍTICA: Formata preço para exibição correta nos templates
        
        Args:
            preco: Pode ser string ou dict com estrutura de preço
            
        Returns:
            String formatada para exibição (ex: "R$ 359,00")
        """
        try:
            if not preco:
                return "Consulte o preço"
            
            # Se é dicionário estruturado, usar campo 'texto'
            if isinstance(preco, dict):
                if 'texto' in preco and preco['texto']:
                    return str(preco['texto']).strip()
                elif 'valor' in preco:
                    valor = preco['valor']
                    moeda = preco.get('moeda', 'BRL')
                    if moeda == 'BRL':
                        return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
                    else:
                        return f"{valor:,.2f}"
                else:
                    return "Consulte o preço"
            
            # Se é string, retornar como está
            elif isinstance(preco, str):
                return preco.strip()
            
            # Se é número
            elif isinstance(preco, (int, float)):
                return f"R$ {preco:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
            
            # Fallback
            else:
                return str(preco)
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao formatar preço {preco}: {e}")
            return "Consulte o preço" 
    
    def _search_product_url_in_data(self, nome_produto: str) -> str:
        """
        Busca URL real do produto nos dados armazenados
        Similar à função do content_generator mas adaptada para templates
        
        Args:
            nome_produto: Nome do produto
            
        Returns:
            URL real do produto ou string vazia se não encontrar
        """
        try:
            import glob
            import json
            import re
            from difflib import SequenceMatcher
            
            # Limpar nome do produto para comparação
            product_clean = nome_produto.strip().lower()
            
            # Buscar arquivos de produtos
            json_files = glob.glob('logs/products_*.json')
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Suportar tanto formato lista quanto formato com metadata
                    products = []
                    if isinstance(data, list):
                        products = data
                    elif isinstance(data, dict) and 'produtos' in data:
                        products = data['produtos']
                    elif isinstance(data, dict) and 'products' in data:
                        products = data['products']
                    else:
                        # Se é dict mas não tem produtos/products, pode ser um único produto
                        if data.get('nome') and data.get('url'):
                            products = [data]
                    
                    for product in products:
                        if not isinstance(product, dict) or not product.get('url'):
                            continue
                            
                        stored_name = product.get('nome', '').strip().lower()
                        stored_url = product.get('url', '').strip()
                        
                        # BUSCA EXATA (100% match) - normalizar espaços
                        product_normalized = ' '.join(product_clean.split())
                        stored_normalized = ' '.join(stored_name.split())
                        
                        if product_normalized == stored_normalized:
                            logger.info(f"✅ TEMPLATE: MATCH EXATO encontrado: {stored_url}")
                            return stored_url
                        
                        # BUSCA POR SIMILARIDADE ALTA (85%+)
                        similarity = SequenceMatcher(None, product_normalized, stored_normalized).ratio()
                        if similarity >= 0.85:
                            logger.info(f"✅ TEMPLATE: MATCH ALTA SIMILARIDADE ({similarity:.2%}): {stored_url}")
                            return stored_url
                        
                        # BUSCA POR CÓDIGOS ESPECÍFICOS (ex: L6490, M404n)
                        codes_product = re.findall(r'[A-Z]+\d+[A-Z]*', nome_produto.upper())
                        codes_stored = re.findall(r'[A-Z]+\d+[A-Z]*', stored_name.upper())
                        
                        if codes_product and codes_stored:
                            common_codes = set(codes_product) & set(codes_stored)
                            if common_codes:
                                logger.info(f"✅ TEMPLATE: MATCH POR CÓDIGO {common_codes}: {stored_url}")
                                return stored_url
                        
                        # BUSCA POR PALAVRAS-CHAVE IMPORTANTES
                        # Extrair palavras significativas (3+ caracteres, não stop words)
                        stop_words = {'de', 'da', 'do', 'com', 'para', 'e', 'em', 'original', 'compativel'}
                        
                        product_words = set(re.findall(r'\w{3,}', product_clean)) - stop_words
                        stored_words = set(re.findall(r'\w{3,}', stored_name)) - stop_words
                        
                        if product_words and stored_words:
                            intersection = product_words & stored_words
                            union = product_words | stored_words
                            word_similarity = len(intersection) / len(union) if union else 0
                            
                            # Se tem 70%+ de palavras em comum
                            if word_similarity >= 0.70:
                                logger.info(f"✅ TEMPLATE: MATCH POR PALAVRAS ({word_similarity:.2%}): {stored_url}")
                                return stored_url
                        
                except Exception as e:
                    logger.debug(f"Erro ao processar {json_file}: {e}")
                    continue
            
            logger.warning(f"⚠️ TEMPLATE: URL não encontrada para produto: {nome_produto}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ TEMPLATE: Erro ao buscar URL do produto: {e}")
            return "" 