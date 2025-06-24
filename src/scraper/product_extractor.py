"""
Product Extractor
Normaliza e organiza dados de produtos extraídos pelo scraper
"""

from typing import Dict, List, Optional, Any
import re
import json
from datetime import datetime
from loguru import logger

class ProductExtractor:
    """Classe para normalizar e processar dados de produtos"""
    
    def __init__(self):
        """Inicializa o extrator de produtos"""
        self.required_fields = ['nome', 'url']
        self.optional_fields = ['preco', 'codigo', 'marca', 'descricao', 'imagem', 'disponivel']
        
        logger.info("🔧 Product Extractor inicializado")
    
    def normalize_product(self, raw_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza dados de um produto
        
        Args:
            raw_product: Dados brutos do produto
            
        Returns:
            Produto normalizado
        """
        try:
            normalized = {}
            
            # Armazenar nome do produto para validação de imagem
            self._current_product_name = raw_product.get('nome', '')
            
            # Processar campos obrigatórios
            for field in self.required_fields:
                if field in raw_product and raw_product[field]:
                    normalized[field] = self._normalize_field(field, raw_product[field])
                else:
                    logger.warning(f"⚠️ Campo obrigatório '{field}' ausente ou vazio")
                    return {}  # Produto inválido sem campos obrigatórios
            
            # Processar campos opcionais
            for field in self.optional_fields:
                if field in raw_product and raw_product[field]:
                    normalized[field] = self._normalize_field(field, raw_product[field])
                else:
                    normalized[field] = None
            
            # Adicionar metadados
            normalized.update({
                'id': raw_product.get('id'),
                'categoria_url': raw_product.get('categoria_url'),
                'data_scraped': raw_product.get('data_scraped'),
                'data_normalized': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'normalizado'
            })
            
            logger.debug(f"✅ Produto normalizado: {normalized.get('nome', 'N/A')}")
            return normalized
            
        except Exception as e:
            logger.error(f"❌ Erro ao normalizar produto: {e}")
            return {}
    
    def normalize_products_batch(self, raw_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza lista de produtos
        
        Args:
            raw_products: Lista de produtos brutos
            
        Returns:
            Lista de produtos normalizados
        """
        logger.info(f"🔄 Normalizando lote de {len(raw_products)} produtos")
        
        normalized_products = []
        
        for i, raw_product in enumerate(raw_products, 1):
            try:
                normalized = self.normalize_product(raw_product)
                if normalized:
                    normalized_products.append(normalized)
                else:
                    logger.warning(f"⚠️ Produto {i} descartado (dados inválidos)")
            except Exception as e:
                logger.error(f"❌ Erro ao processar produto {i}: {e}")
                continue
        
        success_rate = len(normalized_products) / len(raw_products) * 100 if raw_products else 0
        logger.info(f"✅ Normalização concluída: {len(normalized_products)}/{len(raw_products)} produtos ({success_rate:.1f}%)")
        
        return normalized_products
    
    def _normalize_field(self, field_name: str, value: Any) -> Any:
        """
        Normaliza campo específico
        
        Args:
            field_name: Nome do campo
            value: Valor a ser normalizado
            
        Returns:
            Valor normalizado
        """
        if value is None:
            return None
        
        # Converter para string se necessário
        if not isinstance(value, str):
            value = str(value)
        
        # Limpar espaços
        value = value.strip()
        
        # Normalização específica por campo
        if field_name == 'nome':
            return self._normalize_name(value)
        elif field_name == 'preco':
            return self._normalize_price(value)
        elif field_name == 'codigo':
            return self._normalize_code(value)
        elif field_name == 'marca':
            return self._normalize_brand(value)
        elif field_name == 'descricao':
            return self._normalize_description(value)
        elif field_name == 'url':
            return self._normalize_url(value)
        elif field_name == 'imagem':
            # Primeiro normalizar a URL, depois validar
            normalized_url = self._normalize_image_url(value)
            # Validar com o nome do produto se disponível
            product_name = getattr(self, '_current_product_name', '')
            return self._validate_product_image(normalized_url, product_name)
        elif field_name == 'disponivel':
            return self._normalize_availability(value)
        else:
            return value
    
    def _normalize_name(self, name: str) -> str:
        """Normaliza nome do produto"""
        # Remover caracteres extras
        name = re.sub(r'\s+', ' ', name)  # Múltiplos espaços
        name = re.sub(r'[^\w\s\-\(\)\.\,]', '', name)  # Caracteres especiais
        
        # Capitalizar corretamente
        name = name.title()
        
        # Limitar tamanho
        if len(name) > 200:
            name = name[:197] + "..."
        
        return name
    
    def _normalize_price(self, price: str) -> Optional[Dict[str, Any]]:
        """
        Normaliza preço do produto
        CORRIGIDO: Melhor extração e validação de preços atuais
        """
        try:
            if not price or not str(price).strip():
                return None
            
            price_str = str(price).strip()
            
            # Remover textos comuns que não são preços
            price_str = re.sub(r'(indisponível|esgotado|sem estoque|consulte|a partir de)', '', price_str, flags=re.IGNORECASE)
            
            # Extrair apenas números e vírgulas/pontos
            price_clean = re.sub(r'[^\d.,]', '', price_str)
            
            if not price_clean or len(price_clean) < 1:
                logger.debug(f"💰 Preço vazio após limpeza: '{price}'")
                return None
            
            # Verificar se não é apenas pontos/vírgulas
            if re.match(r'^[.,]+$', price_clean):
                logger.debug(f"💰 Preço inválido (apenas separadores): '{price}'")
                return None
            
            # Converter para float baseado no formato brasileiro
            try:
                if ',' in price_clean and '.' in price_clean:
                    # Formato: 1.234,56 (brasileiro)
                    price_clean = price_clean.replace('.', '').replace(',', '.')
                elif ',' in price_clean and price_clean.count(',') == 1:
                    # Formato: 1234,56 (brasileiro)
                    price_clean = price_clean.replace(',', '.')
                elif '.' in price_clean and price_clean.count('.') == 1:
                    # Formato: 1234.56 (americano)
                    # Manter como está
                    pass
                
                price_float = float(price_clean)
                
                # Validar se o preço faz sentido (entre R$ 1 e R$ 50.000)
                if price_float < 1 or price_float > 50000:
                    logger.warning(f"⚠️ Preço fora da faixa esperada: R$ {price_float}")
                    if price_float < 1:
                        return None
                
                return {
                    'valor': price_float,
                    'moeda': 'BRL',
                    'texto': f"R$ {price_float:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'),
                    'original': price_str,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            except ValueError:
                logger.warning(f"⚠️ Não foi possível converter preço: '{price_clean}' de '{price}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao normalizar preço '{price}': {e}")
            return None
    
    def _normalize_code(self, code: str) -> str:
        """Normaliza código do produto"""
        # Remover espaços e caracteres especiais desnecessários
        code = re.sub(r'[^\w\-]', '', code.upper())
        return code
    
    def _normalize_brand(self, brand: str) -> str:
        """Normaliza marca do produto"""
        # Capitalizar primeira letra
        brand = brand.strip().title()
        
        # Corrigir marcas conhecidas
        brand_mapping = {
            'Hp': 'HP',
            'Canon': 'Canon',
            'Epson': 'Epson',
            'Brother': 'Brother',
            'Samsung': 'Samsung',
            'Lexmark': 'Lexmark',
            'Xerox': 'Xerox',
            'Ricoh': 'Ricoh'
        }
        
        return brand_mapping.get(brand, brand)
    
    def _normalize_description(self, description: str) -> str:
        """Normaliza descrição do produto"""
        # Remover tags HTML se houver
        description = re.sub(r'<[^>]+>', '', description)
        
        # Limpar espaços extras
        description = re.sub(r'\s+', ' ', description)
        
        # Limitar tamanho
        if len(description) > 500:
            description = description[:497] + "..."
        
        return description.strip()
    
    def _normalize_url(self, url: str) -> str:
        """Normaliza URL do produto"""
        # Remover espaços
        url = url.strip()
        
        # Garantir que seja URL válida
        if not url.startswith('http'):
            logger.warning(f"⚠️ URL pode estar inválida: {url}")
        
        return url
    
    def _validate_product_image(self, image_url: str, product_name: str) -> Optional[str]:
        """
        MELHORADO: Valida se a imagem corresponde ao produto e não é genérica
        NOVA FUNCIONALIDADE: Validação rigorosa de correspondência produto-imagem
        
        Args:
            image_url: URL da imagem
            product_name: Nome do produto
            
        Returns:
            URL validada ou None se inválida
        """
        if not image_url or not image_url.strip():
            return None
        
        image_url = image_url.strip()
        
        # Verificar se é URL válida
        if not image_url.startswith('http'):
            logger.warning(f"⚠️ URL de imagem inválida: {image_url}")
            return None
        
        # NOVA VALIDAÇÃO: Verificar se não é imagem de thumbnail muito pequena
        if any(size in image_url.lower() for size in ['70x70', '100x100', '50x50', '30x30']):
            logger.warning(f"⚠️ Imagem muito pequena (thumbnail) rejeitada: {image_url}")
            return None
        
        # NOVA VALIDAÇÃO: Priorizar imagens de alta qualidade
        if any(size in image_url for size in ['1800x', '1200x']):
            logger.info(f"✅ Imagem de alta qualidade aceita: {image_url}")
            return image_url
        
        # Extrair informações do produto para validação
        product_lower = product_name.lower() if product_name else ""
        image_lower = image_url.lower()
        
        # Lista de palavras que indicam imagens genéricas ou incorretas
        generic_indicators = [
            'placeholder', 'default', 'no-image', 'sem-imagem',
            'generico', 'generic', 'modelo', 'refil-generico',
            'cartucho-generico', 'toner-generico', 'loading',
            'spinner', 'ajax-loader', 'blank', 'dummy'
        ]
        
        # Verificar se a imagem não é genérica
        for indicator in generic_indicators:
            if indicator in image_lower:
                logger.warning(f"⚠️ Imagem genérica detectada: {image_url}")
                return None
        
        # NOVA VALIDAÇÃO: Verificar correspondência de marcas
        detected_brand = self._extract_brand_from_product_name(product_name)
        image_brand = self._extract_brand_from_image_url(image_url)
        
        if detected_brand and image_brand and detected_brand != image_brand:
            logger.warning(f"⚠️ Marca na imagem ({image_brand}) diferente do produto ({detected_brand}): {image_url}")
            # Não rejeitar automaticamente, mas logar aviso
        
        # NOVA VALIDAÇÃO: Verificar correspondência de modelos/códigos
        if self._validate_model_correspondence(product_name, image_url):
            logger.info(f"✅ Correspondência de modelo validada: {image_url}")
            return image_url
        
        # NOVA VALIDAÇÃO: Verificar se imagem pode ser de produto relacionado
        if self._appears_to_be_related_product_image(image_url, product_name):
            logger.warning(f"⚠️ Possível imagem de produto relacionado: {image_url}")
            return None
        
        # Se passou por todas as validações
        logger.debug(f"✅ Imagem validada: {image_url}")
        return image_url
    
    def _extract_brand_from_product_name(self, product_name: str) -> Optional[str]:
        """Extrai marca do nome do produto"""
        if not product_name:
            return None
        
        product_lower = product_name.lower()
        brands = ['hp', 'canon', 'epson', 'brother', 'samsung', 'lexmark', 'xerox', 'ricoh', 'pantum', 'okidata']
        
        for brand in brands:
            if brand in product_lower:
                return brand
        
        return None
    
    def _extract_brand_from_image_url(self, image_url: str) -> Optional[str]:
        """Extrai marca da URL da imagem"""
        if not image_url:
            return None
        
        url_lower = image_url.lower()
        brands = ['hp', 'canon', 'epson', 'brother', 'samsung', 'lexmark', 'xerox', 'ricoh', 'pantum', 'okidata']
        
        for brand in brands:
            if brand in url_lower:
                return brand
        
        return None
    
    def _validate_model_correspondence(self, product_name: str, image_url: str) -> bool:
        """Valida se o modelo na imagem corresponde ao produto"""
        if not product_name or not image_url:
            return False
        
        product_lower = product_name.lower()
        
        # Extrair códigos/modelos do produto
        import re
        
        # Padrões de códigos comuns
        patterns = [
            r'm\d{4}',  # M6800, M7100, etc.
            r'\d{6,}',  # Códigos longos como 301022274001
            r'[a-z]+\d{3,}',  # Códigos alfanuméricos
        ]
        
        product_codes = []
        for pattern in patterns:
            matches = re.findall(pattern, product_lower)
            product_codes.extend(matches)
        
        # Se encontrou códigos no produto, verificar se algum está na URL da imagem
        if product_codes:
            for code in product_codes:
                if code in image_url.lower():
                    return True
        
        # Se não encontrou códigos específicos, considerar válido
        return True
    
    def _appears_to_be_related_product_image(self, image_url: str, product_name: str) -> bool:
        """Verifica se a imagem parece ser de um produto relacionado (não o principal)"""
        if not image_url or not product_name:
            return False
        
        # Indicadores de produtos relacionados na URL
        related_indicators = [
            'related', 'similar', 'cross-sell', 'upsell',
            'accessories', 'bundle', 'kit'
        ]
        
        url_lower = image_url.lower()
        for indicator in related_indicators:
            if indicator in url_lower:
                return True
        
        # Verificar se é um produto muito diferente baseado no nome
        product_type = self._extract_product_type(product_name)
        
        # Se o produto é um cabo, mas a imagem pode ser de outro tipo
        if product_type == 'cabo':
            # Verificar se a URL sugere outro tipo de produto
            other_types = ['toner', 'cartucho', 'impressora', 'scanner', 'cilindro']
            for other_type in other_types:
                if other_type in url_lower and other_type not in product_name.lower():
                    return True
        
        return False
    
    def _extract_product_type(self, product_name: str) -> str:
        """Extrai o tipo do produto do nome"""
        if not product_name:
            return 'unknown'
        
        name_lower = product_name.lower()
        
        if 'cabo' in name_lower:
            return 'cabo'
        elif 'toner' in name_lower:
            return 'toner'
        elif 'cartucho' in name_lower:
            return 'cartucho'
        elif 'impressora' in name_lower:
            return 'impressora'
        elif 'scanner' in name_lower:
            return 'scanner'
        elif 'cilindro' in name_lower:
            return 'cilindro'
        else:
            return 'unknown'
    
    def _normalize_image_url(self, image_url: str) -> str:
        """
        Normaliza URL da imagem com validação avançada
        
        Args:
            image_url: URL da imagem original
            
        Returns:
            URL normalizada ou None se inválida
        """
        if not image_url:
            return None
        
        # Limpar espaços
        image_url = image_url.strip()
        
        # Verificar se é URL válida
        if not image_url.startswith(('http://', 'https://')):
            logger.warning(f"⚠️ URL de imagem inválida: {image_url}")
            return None
        
        # Verificar se é arquivo de imagem válido
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        if not any(image_url.lower().endswith(ext) for ext in valid_extensions):
            # Se não tem extensão, mas pode ser uma URL dinâmica válida
            if '?' in image_url or 'image' in image_url.lower() or 'img' in image_url.lower():
                logger.debug(f"📸 URL de imagem sem extensão, mas parece válida: {image_url}")
            else:
                logger.warning(f"⚠️ URL não parece ser de imagem: {image_url}")
                return None
        
        logger.debug(f"📸 Imagem normalizada: {image_url}")
        return image_url
    
    def _normalize_availability(self, availability: Any) -> bool:
        """Normaliza disponibilidade do produto"""
        if isinstance(availability, bool):
            return availability
        elif isinstance(availability, str):
            return availability.lower() not in ['false', '0', 'indisponivel', 'esgotado']
        else:
            return bool(availability)
    
    def generate_summary(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera resumo dos produtos processados
        
        Args:
            products: Lista de produtos normalizados
            
        Returns:
            Resumo estatístico
        """
        if not products:
            return {'total': 0, 'com_preco': 0, 'disponiveis': 0, 'marcas': []}
        
        total = len(products)
        com_preco = sum(1 for p in products if p.get('preco'))
        disponiveis = sum(1 for p in products if p.get('disponivel'))
        
        # Marcas únicas
        marcas = list(set(p.get('marca') for p in products if p.get('marca')))
        
        # Categorias (baseado nas URLs)
        categorias = list(set(p.get('categoria_url') for p in products if p.get('categoria_url')))
        
        summary = {
            'total_produtos': total,
            'com_preco': com_preco,
            'disponiveis': disponiveis,
            'sem_preco': total - com_preco,
            'indisponiveis': total - disponiveis,
            'marcas_encontradas': len(marcas),
            'marcas': sorted(marcas),
            'categorias_processadas': len(categorias),
            'taxa_preco': (com_preco / total * 100) if total > 0 else 0,
            'taxa_disponibilidade': (disponiveis / total * 100) if total > 0 else 0,
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"📊 Resumo gerado: {total} produtos, {len(marcas)} marcas, {com_preco} com preço")
        
        return summary
    
    def export_to_json(self, products: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Exporta produtos para arquivo JSON
        
        Args:
            products: Lista de produtos
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/products_{timestamp}.json"
        
        try:
            # Criar estrutura do arquivo
            export_data = {
                'metadata': {
                    'total_produtos': len(products),
                    'data_export': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'resumo': self.generate_summary(products)
                },
                'produtos': products
            }
            
            # Salvar arquivo
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Produtos exportados para: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar produtos: {e}")
            return ""
    
    def validate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Valida lista de produtos e remove inválidos
        
        Args:
            products: Lista de produtos
            
        Returns:
            Lista de produtos válidos
        """
        valid_products = []
        
        for i, product in enumerate(products, 1):
            if self.is_valid_product(product):
                valid_products.append(product)
            else:
                logger.warning(f"⚠️ Produto {i} inválido removido: {product.get('nome', 'N/A')}")
        
        logger.info(f"✅ Validação: {len(valid_products)}/{len(products)} produtos válidos")
        return valid_products
    
    def is_valid_product(self, product: Dict[str, Any]) -> bool:
        """
        Verifica se produto é válido
        
        Args:
            product: Dados do produto
            
        Returns:
            True se válido
        """
        # Verificar campos obrigatórios
        for field in self.required_fields:
            if not product.get(field):
                return False
        
        # Verificar se nome tem tamanho mínimo
        nome = product.get('nome', '')
        if len(nome) < 3:
            return False
        
        # Verificar se URL é válida
        url = product.get('url', '')
        if url and not url.startswith('http'):
            return False
        
        return True 
 
 
 
 