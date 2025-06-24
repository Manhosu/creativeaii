#!/usr/bin/env python3
"""
Simula exatamente a lógica do endpoint /scraper/products para debuggar
"""

import json
import glob
import os

def simulate_endpoint():
    print('🔍 SIMULANDO ENDPOINT /scraper/products')
    print('='*60)
    
    # Buscar arquivos JSON de produtos
    json_files = glob.glob("logs/products_*.json")
    
    if not json_files:
        print("❌ Nenhum arquivo encontrado!")
        return
    
    print(f"📁 Arquivos encontrados: {len(json_files)}")
    for f in sorted(json_files):
        print(f"  - {os.path.basename(f)}")
    
    print()
    
    all_products = []
    
    # Mapeamento de categorias conhecidas
    categorias_mapeamento = {
        'cartuchos-de-tinta': 'Cartuchos de Tinta',
        'cartuchos-de-toner': 'Cartuchos de Toner', 
        'refil-de-toner': 'Refil de Toner',
        'impressoras': 'Impressoras',
        'multifuncional': 'Multifuncionais',
        'plotters': 'Plotters',
        'suprimentos': 'Suprimentos'
    }
    
    # Agrupar arquivos por categoria e priorizar CORRIGIDOS
    categoria_files = {}
    for json_file in json_files:
        filename = os.path.basename(json_file)
        categoria_from_file = filename.replace('products_', '').split('_')[0]
        
        # PRIORIDADE 1: Se é arquivo CORRIGIDO, sempre usar
        if 'CORRIGIDO' in filename:
            categoria_files[categoria_from_file] = json_file
            print(f"✅ Priorizando arquivo corrigido: {filename}")
        
        # PRIORIDADE 2: Se não existe arquivo para categoria, usar qualquer um
        elif categoria_from_file not in categoria_files:
            categoria_files[categoria_from_file] = json_file
            print(f"📄 Usando arquivo original: {filename}")
        
        # PRIORIDADE 3: Se já existe mas não é CORRIGIDO, comparar timestamps
        else:
            existing_filename = os.path.basename(categoria_files[categoria_from_file])
            
            # Se o existente não é CORRIGIDO e o atual é mais recente
            if 'CORRIGIDO' not in existing_filename:
                current_timestamp = filename.split('_')[-1].replace('.json', '')
                existing_timestamp = existing_filename.split('_')[-1].replace('.json', '')
                
                if current_timestamp > existing_timestamp:
                    categoria_files[categoria_from_file] = json_file
                    print(f"🔄 Atualizando para mais recente: {filename}")
            # Se existente é CORRIGIDO, manter (não sobrescrever)
    
    print(f"\n🔍 Usando apenas arquivos mais recentes: {len(categoria_files)} categorias de {len(json_files)} arquivos totais")
    
    # DEBUG: Listar arquivos selecionados
    for cat, file in categoria_files.items():
        filename = os.path.basename(file)
        print(f"📁 {cat}: {filename}")
    
    print()
    
    # Carregar produtos apenas dos arquivos mais recentes (FORÇAR ORDEM)
    for categoria_key in sorted(categoria_files.keys()):
        json_file = categoria_files[categoria_key]
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Usar categoria_key já extraída
                filename = os.path.basename(json_file)
                categoria_nome = categorias_mapeamento.get(categoria_key, categoria_key.title())
                
                # Adicionar produtos
                produtos_carregados = 0
                if isinstance(data, list):
                    for product in data:
                        product['categoria_key'] = categoria_key
                        product['categoria_nome'] = categoria_nome
                        product['source_file'] = filename
                        all_products.append(product)
                        produtos_carregados += 1
                elif isinstance(data, dict) and 'produtos' in data:
                    for product in data['produtos']:
                        product['categoria_key'] = categoria_key
                        product['categoria_nome'] = categoria_nome
                        product['source_file'] = filename
                        all_products.append(product)
                        produtos_carregados += 1
                
                print(f"✅ {categoria_key}: {produtos_carregados} produtos carregados de {filename}")
                
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo {json_file}: {e}")
            continue
    
    print(f"\n📊 TOTAL ANTES DA DEDUPLIFICAÇÃO: {len(all_products)} produtos")
    
    # DEDUPLIFICAÇÃO INTELIGENTE
    unique_products = {}
    for product in all_products:
        nome = product.get('nome', '').strip()
        categoria = product.get('categoria_key', '').strip()
        url = product.get('url', '').strip()
        
        # Criar chave única baseada no nome + categoria
        key = f"{nome.lower().replace('  ', ' ').strip()}|{categoria.lower()}"
        
        # Se não existe ou se tem URL melhor
        if key not in unique_products or (url and not unique_products[key].get('url')):
            unique_products[key] = product
    
    # Converter de volta para lista
    all_products = list(unique_products.values())
    
    print(f"📊 TOTAL APÓS DEDUPLIFICAÇÃO: {len(all_products)} produtos")
    
    # Contar por categoria
    categoria_counts = {}
    for product in all_products:
        cat = product.get('categoria_key', 'unknown')
        categoria_counts[cat] = categoria_counts.get(cat, 0) + 1
    
    print(f"\n📋 PRODUTOS POR CATEGORIA:")
    for cat, count in sorted(categoria_counts.items()):
        print(f"  {cat:20} -> {count:3d} produtos")
    
    print(f"\n🎯 TOTAL FINAL: {len(all_products)} produtos")

if __name__ == "__main__":
    simulate_endpoint() 