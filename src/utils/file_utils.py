"""
Utilitários para manipulação de arquivos em ambiente de produção e desenvolvimento
"""
import json
import os
import glob
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def find_product_files() -> List[str]:
    """
    Encontra arquivos de produtos em diferentes localizações
    Funciona tanto em desenvolvimento quanto em produção
    """
    possible_paths = [
        "logs/products_*.json",
        "src/logs/products_*.json", 
        "./logs/products_*.json",
        "./src/logs/products_*.json",
        "/app/logs/products_*.json",
        "/app/src/logs/products_*.json"
    ]
    
    json_files = []
    for path_pattern in possible_paths:
        try:
            files = glob.glob(path_pattern)
            if files:
                json_files.extend(files)
                logger.info(f"✅ Encontrados {len(files)} arquivos em: {path_pattern}")
                break
        except Exception as e:
            logger.debug(f"Erro ao buscar em {path_pattern}: {e}")
            continue
    
    return json_files

def load_all_products() -> List[Dict[str, Any]]:
    """
    Carrega todos os produtos dos arquivos JSON disponíveis
    """
    json_files = find_product_files()
    
    if not json_files:
        logger.warning("⚠️ Nenhum arquivo de produtos encontrado")
        return []
    
    # Mapeamento de categorias conhecidas
    categorias_mapeamento = {
        'cartuchos-de-tinta': 'Cartuchos de Tinta',
        'cartuchos-de-toner': 'Cartuchos de Toner', 
        'refil-de-toner': 'Refil de Toner',
        'refil-de-tinta': 'Refil de Tinta',
        'impressoras': 'Impressoras',
        'multifuncional': 'Multifuncionais',
        'plotters': 'Plotters',
        'suprimentos': 'Suprimentos',
        'papel-fotografico': 'Papel Fotográfico',
        'scanner': 'Scanners',
        'impressora-com-defeito': 'Impressoras Usadas'
    }
    
    # Agrupar arquivos por categoria e pegar apenas o mais recente de cada uma
    categoria_files = {}
    for json_file in json_files:
        filename = os.path.basename(json_file)
        categoria_from_file = filename.replace('products_', '').split('_')[0]
        
        # Se não existe ou é mais recente, atualizar
        if categoria_from_file not in categoria_files:
            categoria_files[categoria_from_file] = json_file
        else:
            # Comparar timestamps nos nomes dos arquivos
            current_timestamp = filename.split('_')[-1].replace('.json', '')
            existing_filename = os.path.basename(categoria_files[categoria_from_file])
            existing_timestamp = existing_filename.split('_')[-1].replace('.json', '')
            
            if current_timestamp > existing_timestamp:
                categoria_files[categoria_from_file] = json_file
    
    all_products = []
    
    # Carregar produtos apenas dos arquivos mais recentes
    for categoria_key, json_file in categoria_files.items():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Usar categoria_key já extraída
                filename = os.path.basename(json_file)
                categoria_nome = categorias_mapeamento.get(categoria_key, categoria_key.title())
                
                # Adicionar produtos
                if isinstance(data, list):
                    for product in data:
                        product['categoria_key'] = categoria_key
                        product['categoria_nome'] = categoria_nome
                        product['source_file'] = filename
                        all_products.append(product)
                elif isinstance(data, dict) and 'produtos' in data:
                    for product in data['produtos']:
                        product['categoria_key'] = categoria_key
                        product['categoria_nome'] = categoria_nome
                        product['source_file'] = filename
                        all_products.append(product)
        except Exception as e:
            logger.warning(f"Erro ao carregar arquivo {json_file}: {e}")
            continue
    
    logger.info(f"📦 Total de {len(all_products)} produtos carregados de {len(categoria_files)} categorias")
    return all_products

def find_product_by_name(produto_nome: str) -> Optional[Dict[str, Any]]:
    """
    Busca produto específico por nome
    """
    try:
        all_products = load_all_products()
        
        # Procurar produto por nome exato
        for produto in all_products:
            if produto.get('nome', '').strip().lower() == produto_nome.strip().lower():
                logger.info(f"✅ Produto encontrado: {produto.get('categoria_nome', 'N/A')}")
                return produto
        
        logger.warning(f"⚠️ Produto não encontrado: {produto_nome}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar produto: {e}")
        return None

def get_minimal_product_data(produto_nome: str) -> Dict[str, Any]:
    """
    Retorna dados mínimos de produto para fallback
    """
    return {
        'nome': produto_nome,
        'categoria_nome': 'produtos',
        'preco': 'Consulte',
        'codigo': 'N/A',
        'marca': 'N/A',
        'descricao': f'Produto {produto_nome} de qualidade disponível em nossa loja.',
        'url': '#',
        'imagem': ''
    } 