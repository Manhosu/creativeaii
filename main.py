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
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Importa e executa o main do src
    from src.main import app
    
    if __name__ == "__main__":
        # Configurações para Railway
        port = int(os.environ.get("PORT", 3025))
        host = os.environ.get("HOST", "0.0.0.0")
        debug = os.environ.get("DEBUG", "false").lower() == "true"
        
        logger.info("🚀 Creative IA iniciando...")
        logger.info(f"Porta: {port}")
        logger.info(f"Host: {host}")
        logger.info(f"🔧 Ambiente: {'Development' if debug else 'Production'}")
        
        # Verificar variáveis essenciais
        required_vars = ["OPENAI_API_KEY", "WP_SITE_URL", "WP_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"⚠️ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
            logger.warning("Sistema funcionará em modo limitado")
        
        # Criar diretórios necessários
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        
        # Inicia o servidor uvicorn
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=debug,  # Só reload em development
            log_level="info" if not debug else "debug",
            access_log=not debug  # Menos logs em production
        )
        
except ImportError as e:
    logger.error(f"❌ Erro ao importar módulos: {e}")
    logger.info("🔍 Verificando estrutura de diretórios...")
    
    # Debug: mostra estrutura do projeto
    import os
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        if level > 3:  # Limitar profundidade
            continue
        indent = ' ' * 2 * level
        logger.info(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:3]:  # Mostra apenas os primeiros 3 arquivos
            logger.info(f"{subindent}{file}")
        if len(files) > 3:
            logger.info(f"{subindent}... e mais {len(files) - 3} arquivos")
    
    sys.exit(1)
    
except Exception as e:
    logger.error(f"❌ Erro inesperado: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1) 