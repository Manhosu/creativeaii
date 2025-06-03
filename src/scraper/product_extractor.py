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
            return self._normalize_image_url(value)
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
        """Normaliza preço do produto"""
        try:
            # Extrair apenas números e vírgulas/pontos
            price_clean = re.sub(r'[^\d.,]', '', price)
            
            if not price_clean:
                return None
            
            # Converter para float
            if ',' in price_clean and '.' in price_clean:
                # Formato: 1.234,56
                price_clean = price_clean.replace('.', '').replace(',', '.')
            elif ',' in price_clean:
                # Formato: 1234,56
                price_clean = price_clean.replace(',', '.')
            
            try:
                price_float = float(price_clean)
                return {
                    'valor': price_float,
                    'moeda': 'BRL',
                    'texto': f"R$ {price_float:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
                }
            except ValueError:
                logger.warning(f"⚠️ Preço inválido: {price}")
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
    
    def _normalize_image_url(self, image_url: str) -> str:
        """Normaliza URL da imagem"""
        return self._normalize_url(image_url)
    
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
 
 
 
 