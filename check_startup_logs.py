#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import sys
from pathlib import Path

def check_server_status():
    """Verifica se o servidor está rodando e os logs aparecem"""
    base_url = "http://localhost:3025"
    
    print("🔍 VERIFICANDO STATUS GERAL DO SISTEMA...")
    
    # 1. Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Sistema Online")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Uptime: {data.get('uptime', 'N/A')}")
        else:
            print("❌ Health check falhou")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return False
    
    # 2. Verificar módulos individuais
    modules = {
        'scraper': 'Scraper (Extração de produtos)',
        'generator': 'Generator (Geração de artigos)',
        'review': 'Review (Revisão de conteúdo)',
        'publisher': 'Publisher (Publicação WordPress)',
        'scheduler': 'Scheduler (Automação)',
        'config': 'Config (Configurações)'
    }
    
    print("\n📋 STATUS DOS MÓDULOS:")
    for module_key, module_name in modules.items():
        try:
            response = requests.get(f"{base_url}/{module_key}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'N/A')
                status_icon = "✅" if status in ['ready', 'active', 'ativo'] else "⚠️"
                print(f"   {status_icon} {module_name}: {status}")
            else:
                print(f"   ❌ {module_name}: ERRO HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
    
    # 3. Verificar estatísticas de review
    print("\n📊 ESTATÍSTICAS DE REVISÃO:")
    try:
        response = requests.get(f"{base_url}/review/stats", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('statistics', {})
                print(f"   📄 Total de Artigos: {stats.get('total_artigos', 0)}")
                print(f"   ⏳ Pendentes: {stats.get('pendentes', 0)}")
                print(f"   ✅ Aprovados: {stats.get('aprovados', 0)}")
                print(f"   ❌ Rejeitados: {stats.get('rejeitados', 0)}")
            else:
                print("   ❌ Falha ao obter estatísticas")
        else:
            print("   ❌ Endpoint de estatísticas não responde")
    except Exception as e:
        print(f"   ❌ Erro ao obter estatísticas: {e}")
    
    # 4. Testar endpoint de listagem
    print("\n📝 TESTE DE LISTAGEM DE ARTIGOS:")
    try:
        response = requests.get(f"{base_url}/review/articles?limit=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('articles'):
                articles = data.get('articles', [])
                print(f"   ✅ {len(articles)} artigos carregados com sucesso")
                for i, article in enumerate(articles[:3], 1):
                    titulo = article.get('titulo', 'Sem título')[:50]
                    status = article.get('status', 'N/A')
                    print(f"   {i}. {titulo}... (Status: {status})")
            else:
                print("   ⚠️ API responde mas sem artigos")
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return True

def check_log_files():
    """Verifica se os arquivos de log existem e têm conteúdo recente"""
    print("\n📋 VERIFICANDO ARQUIVOS DE LOG...")
    
    log_files = [
        "logs/main.log",
        "logs/scheduler.log"
    ]
    
    for log_file in log_files:
        if Path(log_file).exists():
            size = Path(log_file).stat().st_size
            print(f"   ✅ {log_file}: {size} bytes")
        else:
            print(f"   ❌ {log_file}: Não encontrado")

def main():
    print("🚀 CREATIVE API - VERIFICAÇÃO COMPLETA DO SISTEMA")
    print("=" * 65)
    
    # Verificar status geral
    if not check_server_status():
        print("\n❌ Sistema não está funcionando corretamente!")
        return
    
    # Verificar logs
    check_log_files()
    
    print("\n" + "=" * 65)
    print("✅ VERIFICAÇÃO CONCLUÍDA!")
    print("\nPara acessar a interface web:")
    print("🌐 Dashboard: http://localhost:3025")
    print("📝 Review: http://localhost:3025/interface/review")
    print("📚 API Docs: http://localhost:3025/docs")

if __name__ == "__main__":
    main() 