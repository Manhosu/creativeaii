#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Creative IA - Sistema de Geração Automática de Conteúdo SEO
==============================================================

Arquivo principal para deploy no Railway.
Este arquivo inicia o servidor web e todos os componentes do sistema.

Autor: Creative IA Team
Versão: 1.0.0
"""

import os
import sys
import uvicorn

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Importa e executa o main do src
    from src.main import app
    
    if __name__ == "__main__":
        # Configurações para Railway
        port = int(os.environ.get("PORT", 3025))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print("🚀 Creative IA iniciando...")
        print(f"Porta: {port}")
        print(f"Host: {host}")
        print(f"🔧 Ambiente: {'Production' if not os.environ.get('DEBUG') else 'Development'}")
        
        # Inicia o servidor uvicorn
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
        
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("🔍 Verificando estrutura de diretórios...")
    
    # Debug: mostra estrutura do projeto
    import os
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # Mostra apenas os primeiros 5 arquivos
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... e mais {len(files) - 5} arquivos")
    
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    sys.exit(1) 