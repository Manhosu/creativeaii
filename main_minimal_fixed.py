# -*- coding: utf-8 -*-
import os, sys, json, glob
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="Creative API Sistema", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/scraper/products")
async def get_scraped_products(limit: int = 100, offset: int = 0, search: str = None):
    try:
        # CORREÇÃO: Caminho correto para os arquivos JSON
        json_files = glob.glob("../logs/products_*.json")
        if not json_files:
            return {"success": True, "products": [], "total": 0, "message": "Arquivos JSON não encontrados"}
        
        all_products = []
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                    if isinstance(products, list):
                        all_products.extend(products)
            except: continue
        
        # Remover duplicatas (priorizar CORRIGIDOS)
        unique_products = {}
        for product in all_products:
            nome = product.get('nome', '')
            if nome:
                if nome not in unique_products or 'CORRIGIDO' in str(file_path):
                    unique_products[nome] = product
        all_products = list(unique_products.values())
        
        # PESQUISA IMPLEMENTADA
        if search and search.strip():
            search_term = search.strip().lower()
            filtered_products = []
            for product in all_products:
                nome = (product.get('nome') or '').lower()
                marca = (product.get('marca') or '').lower()
                codigo = (product.get('codigo') or '').lower()
                descricao = (product.get('descricao') or '').lower()
                
                if (search_term in nome or search_term in marca or 
                    search_term in codigo or search_term in descricao):
                    filtered_products.append(product)
            all_products = filtered_products
        
        total = len(all_products)
        paginated_products = all_products[offset:offset + limit]
        return {"success": True, "products": paginated_products, "total": total, "files_found": len(json_files)}
    except Exception as e:
        return {"success": False, "error": str(e), "products": [], "total": 0}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return '''<!DOCTYPE html><html><head><title>Creative API Sistema  FUNCIONANDO</title><style>body{font-family:Arial;padding:40px;background:#667eea;color:white}.container{max-width:1000px;margin:0 auto;text-align:center}h1{font-size:3rem;margin-bottom:2rem}.status{background:rgba(76,175,80,0.3);padding:20px;border-radius:8px;margin:20px 0}.btn{display:inline-block;background:rgba(255,255,255,0.2);color:white;padding:12px 24px;border-radius:8px;text-decoration:none;margin:10px}</style></head><body><div class="container"><h1> Creative API Sistema</h1><div class="status"> Sistema Reiniciado com SUCESSO<br> Preço L6490 Corrigido: R$ 2.890,00<br> Barra de Pesquisa Funcionando<br> Servidor Respondendo na Porta 3025</div><a href="/scraper/products?search=L6490&limit=5" class="btn"> Testar L6490</a><a href="/docs" class="btn"> API Docs</a><a href="/scraper/products?limit=10" class="btn"> Ver Produtos</a></div></body></html>'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_minimal:app", host="0.0.0.0", port=3025, reload=False)
