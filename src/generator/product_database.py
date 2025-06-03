#!/usr/bin/env python3
"""
Product Database
Base de dados de produtos variados para geração de artigos
"""

import random
from typing import Dict, List, Any
from loguru import logger

class ProductDatabase:
    """Base de dados de produtos para geração variada de artigos"""
    
    def __init__(self):
        """Inicializa banco de produtos"""
        self.products = self._initialize_products()
        self.used_products = set()
        logger.info(f"📦 Product Database inicializado com {len(self.products)} produtos")
    
    def _initialize_products(self) -> List[Dict[str, Any]]:
        """Inicializa lista de produtos variados"""
        
        products = []
        
        # IMPRESSORAS HP
        hp_printers = [
            {
                'nome': 'HP LaserJet Pro M404n',
                'marca': 'HP',
                'preco': 'R$ 899,00',
                'descricao': 'Impressora laser monocromática profissional para escritórios',
                'tipo': 'impressora',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'HP LaserJet Pro M404dn',
                'marca': 'HP', 
                'preco': 'R$ 1.199,00',
                'descricao': 'Impressora laser monocromática com duplex automático',
                'tipo': 'impressora',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'HP LaserJet Pro M428fdw',
                'marca': 'HP',
                'preco': 'R$ 1.899,00',
                'descricao': 'Multifuncional laser monocromática com Wi-Fi e fax',
                'tipo': 'multifuncional',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'HP Color LaserJet Pro M454dn',
                'marca': 'HP',
                'preco': 'R$ 2.299,00',
                'descricao': 'Impressora laser colorida profissional com duplex',
                'tipo': 'impressora',
                'categoria': 'laser-color'
            },
            {
                'nome': 'HP DeskJet Ink Advantage 2774',
                'marca': 'HP',
                'preco': 'R$ 449,00',
                'descricao': 'Multifuncional jato de tinta com Wi-Fi para home office',
                'tipo': 'multifuncional',
                'categoria': 'jato-tinta'
            },
            {
                'nome': 'HP OfficeJet Pro 9012e',
                'marca': 'HP',
                'preco': 'R$ 1.349,00',
                'descricao': 'Multifuncional jato de tinta profissional com HP+',
                'tipo': 'multifuncional',
                'categoria': 'jato-tinta'
            }
        ]
        
        # IMPRESSORAS CANON
        canon_printers = [
            {
                'nome': 'Canon PIXMA G3111',
                'marca': 'Canon',
                'preco': 'R$ 699,00',
                'descricao': 'Multifuncional tanque de tinta com Wi-Fi',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Canon PIXMA G4111',
                'marca': 'Canon',
                'preco': 'R$ 849,00',
                'descricao': 'Multifuncional tanque de tinta com fax e ADF',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Canon imageCLASS LBP6030',
                'marca': 'Canon',
                'preco': 'R$ 579,00',
                'descricao': 'Impressora laser monocromática compacta',
                'tipo': 'impressora',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'Canon imageCLASS MF3010',
                'marca': 'Canon',
                'preco': 'R$ 899,00',
                'descricao': 'Multifuncional laser monocromática',
                'tipo': 'multifuncional',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'Canon PIXMA TS3150',
                'marca': 'Canon',
                'preco': 'R$ 329,00',
                'descricao': 'Multifuncional jato de tinta com Wi-Fi',
                'tipo': 'multifuncional',
                'categoria': 'jato-tinta'
            }
        ]
        
        # IMPRESSORAS EPSON
        epson_printers = [
            {
                'nome': 'Epson L3150',
                'marca': 'Epson',
                'preco': 'R$ 649,00',
                'descricao': 'Multifuncional EcoTank com Wi-Fi',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Epson L4150',
                'marca': 'Epson',
                'preco': 'R$ 799,00',
                'descricao': 'Multifuncional EcoTank com duplex automático',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Epson L6161',
                'marca': 'Epson',
                'preco': 'R$ 1.099,00',
                'descricao': 'Multifuncional EcoTank A3+ com ADF',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Epson EcoTank L14150',
                'marca': 'Epson',
                'preco': 'R$ 2.499,00',
                'descricao': 'Multifuncional A3+ profissional com fax',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Epson WorkForce WF-2830',
                'marca': 'Epson',
                'preco': 'R$ 499,00',
                'descricao': 'Multifuncional jato de tinta com Wi-Fi',
                'tipo': 'multifuncional',
                'categoria': 'jato-tinta'
            }
        ]
        
        # IMPRESSORAS BROTHER
        brother_printers = [
            {
                'nome': 'Brother HL-L2350DW',
                'marca': 'Brother',
                'preco': 'R$ 899,00',
                'descricao': 'Impressora laser monocromática com Wi-Fi e duplex',
                'tipo': 'impressora',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'Brother DCP-L2520DW',
                'marca': 'Brother',
                'preco': 'R$ 1.199,00',
                'descricao': 'Multifuncional laser monocromática com Wi-Fi',
                'tipo': 'multifuncional',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'Brother MFC-L2710DW',
                'marca': 'Brother',
                'preco': 'R$ 1.599,00',
                'descricao': 'Multifuncional laser monocromática com fax e ADF',
                'tipo': 'multifuncional',
                'categoria': 'laser-mono'
            },
            {
                'nome': 'Brother DCP-T520W',
                'marca': 'Brother',
                'preco': 'R$ 649,00',
                'descricao': 'Multifuncional tanque de tinta com Wi-Fi',
                'tipo': 'multifuncional',
                'categoria': 'tanque-tinta'
            },
            {
                'nome': 'Brother HL-L3230CDW',
                'marca': 'Brother',
                'preco': 'R$ 1.699,00',
                'descricao': 'Impressora laser colorida com Wi-Fi e duplex',
                'tipo': 'impressora',
                'categoria': 'laser-color'
            }
        ]
        
        # TONERS E CARTUCHOS
        supplies = [
            {
                'nome': 'Toner HP CF217A Original',
                'marca': 'HP',
                'preco': 'R$ 329,00',
                'descricao': 'Toner original HP 17A para LaserJet Pro M102/M130',
                'tipo': 'toner',
                'categoria': 'suprimento'
            },
            {
                'nome': 'Cartucho HP 664XL Preto',
                'marca': 'HP',
                'preco': 'R$ 89,00',
                'descricao': 'Cartucho de tinta original HP 664XL preto',
                'tipo': 'cartucho',
                'categoria': 'suprimento'
            },
            {
                'nome': 'Toner Brother TN-2370',
                'marca': 'Brother',
                'preco': 'R$ 299,00',
                'descricao': 'Toner original Brother para HL-L2320D/L2360DW',
                'tipo': 'toner',
                'categoria': 'suprimento'
            },
            {
                'nome': 'Kit 4 Tintas Epson L3150',
                'marca': 'Epson',
                'preco': 'R$ 199,00',
                'descricao': 'Kit completo de tintas originais para EcoTank L3150',
                'tipo': 'tinta',
                'categoria': 'suprimento'
            },
            {
                'nome': 'Toner Canon 137',
                'marca': 'Canon',
                'preco': 'R$ 279,00',
                'descricao': 'Toner original Canon 137 para imageCLASS MF212w/MF216n',
                'tipo': 'toner',
                'categoria': 'suprimento'
            }
        ]
        
        # COMBINAR TODOS OS PRODUTOS
        products.extend(hp_printers)
        products.extend(canon_printers)
        products.extend(epson_printers)
        products.extend(brother_printers)
        products.extend(supplies)
        
        # ADICIONAR IDS ÚNICOS
        for i, product in enumerate(products, 1):
            product['id'] = f"prod_{i:03d}"
            product['url'] = f"https://www.creativecopias.com.br/produto/{product['id']}"
        
        return products
    
    def get_random_product(self, exclude_used: bool = True) -> Dict[str, Any]:
        """
        Retorna produto aleatório
        
        Args:
            exclude_used: Se deve excluir produtos já usados
            
        Returns:
            Produto aleatório
        """
        available_products = []
        
        if exclude_used:
            # Filtrar produtos não usados
            available_products = [p for p in self.products if p['id'] not in self.used_products]
            
            # Se todos foram usados, resetar
            if not available_products:
                logger.info("🔄 Todos os produtos foram usados, resetando lista")
                self.used_products.clear()
                available_products = self.products.copy()
        else:
            available_products = self.products.copy()
        
        # Selecionar produto aleatório
        product = random.choice(available_products)
        
        # Marcar como usado
        if exclude_used:
            self.used_products.add(product['id'])
        
        logger.debug(f"📦 Produto selecionado: {product['nome']}")
        return product.copy()
    
    def get_products_by_type(self, product_type: str) -> List[Dict[str, Any]]:
        """
        Retorna produtos por tipo
        
        Args:
            product_type: Tipo do produto (impressora, multifuncional, toner, etc.)
            
        Returns:
            Lista de produtos do tipo especificado
        """
        return [p for p in self.products if p.get('tipo') == product_type]
    
    def get_products_by_brand(self, brand: str) -> List[Dict[str, Any]]:
        """
        Retorna produtos por marca
        
        Args:
            brand: Marca do produto
            
        Returns:
            Lista de produtos da marca especificada
        """
        return [p for p in self.products if p.get('marca', '').lower() == brand.lower()]
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Retorna produtos por categoria
        
        Args:
            category: Categoria do produto
            
        Returns:
            Lista de produtos da categoria especificada
        """
        return [p for p in self.products if p.get('categoria') == category]
    
    def get_product_variations(self, base_product: Dict[str, Any], count: int = 3) -> List[Dict[str, Any]]:
        """
        Retorna variações de um produto base
        
        Args:
            base_product: Produto base
            count: Número de variações desejadas
            
        Returns:
            Lista de produtos similares
        """
        # Buscar produtos da mesma marca ou categoria
        same_brand = self.get_products_by_brand(base_product.get('marca', ''))
        same_category = self.get_products_by_category(base_product.get('categoria', ''))
        
        # Combinar e remover o produto base
        candidates = list(set(same_brand + same_category))
        candidates = [p for p in candidates if p['id'] != base_product.get('id')]
        
        # Retornar quantidade solicitada
        return random.sample(candidates, min(count, len(candidates)))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da base de produtos
        
        Returns:
            Estatísticas da base
        """
        stats = {
            'total_produtos': len(self.products),
            'produtos_usados': len(self.used_products),
            'produtos_disponiveis': len(self.products) - len(self.used_products),
            'por_tipo': {},
            'por_marca': {},
            'por_categoria': {}
        }
        
        # Estatísticas por tipo
        for product in self.products:
            tipo = product.get('tipo', 'indefinido')
            marca = product.get('marca', 'indefinida')
            categoria = product.get('categoria', 'indefinida')
            
            stats['por_tipo'][tipo] = stats['por_tipo'].get(tipo, 0) + 1
            stats['por_marca'][marca] = stats['por_marca'].get(marca, 0) + 1
            stats['por_categoria'][categoria] = stats['por_categoria'].get(categoria, 0) + 1
        
        return stats
    
    def reset_used_products(self):
        """Reseta lista de produtos usados"""
        self.used_products.clear()
        logger.info("🔄 Lista de produtos usados resetada")
    
    def export_products(self) -> List[Dict[str, Any]]:
        """
        Exporta todos os produtos
        
        Returns:
            Lista completa de produtos
        """
        return self.products.copy() 