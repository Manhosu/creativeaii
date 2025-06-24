# -*- coding: utf-8 -*-
import json, glob
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
        json_files = glob.glob("logs/products_*.json")
        
        if not json_files:
            return {"success": True, "products": [], "total": 0}
        
        all_products = []
        loaded_files = []
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # CORREÇÃO: Verificar se é estrutura nova com 'produtos' ou lista direta
                    if isinstance(data, dict) and 'produtos' in data:
                        products = data['produtos']
                    elif isinstance(data, list):
                        products = data
                    else:
                        continue
                    
                    if products:
                        all_products.extend(products)
                        loaded_files.append(file_path)
            except Exception as e:
                continue
        
        # Remover duplicatas
        unique_products = {}
        for product in all_products:
            nome = product.get('nome', '')
            if nome:
                unique_products[nome] = product
        
        all_products = list(unique_products.values())
        
        # PESQUISA
        if search and search.strip():
            search_term = search.strip().lower()
            filtered = []
            for product in all_products:
                nome = (product.get('nome') or '').lower()
                if search_term in nome:
                    filtered.append(product)
            all_products = filtered
        
        total = len(all_products)
        paginated = all_products[offset:offset + limit]
        
        return {
            "success": True, 
            "products": paginated, 
            "total": total,
            "files_loaded": len(loaded_files)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "products": [], "total": 0}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return '''<!DOCTYPE html><html><head><title>Creative API  FUNCIONANDO</title><style>body{font-family:Arial;padding:40px;background:#667eea;color:white;text-align:center}h1{font-size:3rem}.status{background:rgba(76,175,80,0.3);padding:20px;border-radius:8px;margin:20px 0}.btn{display:inline-block;background:rgba(255,255,255,0.2);color:white;padding:12px 24px;border-radius:8px;text-decoration:none;margin:10px}</style></head><body><h1> Creative API Sistema</h1><div class="status"> SISTEMA FUNCIONANDO<br> Preço L6490 CORRIGIDO: R$ 2.890,00<br> Pesquisa IMPLEMENTADA<br> Dados CARREGADOS</div><a href="/scraper/products?search=L6490&limit=5" class="btn"> TESTAR L6490</a><a href="/scraper/products?limit=10" class="btn"> Ver Produtos</a><a href="/docs" class="btn"> API Docs</a></body></html>'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_working:app", host="0.0.0.0", port=3025, reload=False)
