#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
from pathlib import Path

def test_review_endpoints():
    """Testa todos os endpoints de review"""
    base_url = "http://localhost:3025"
    
    print("🔍 TESTANDO ENDPOINTS DE REVIEW...")
    
    # 1. Testar status do módulo review
    print("\n1. Testando status do módulo review...")
    try:
        response = requests.get(f"{base_url}/review")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Review Status: {data.get('status', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 2. Testar listagem de artigos
    print("\n2. Testando listagem de artigos...")
    try:
        response = requests.get(f"{base_url}/review/articles")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                articles = data.get('articles', [])
                print(f"   ✅ {len(articles)} artigos encontrados")
                if articles:
                    # Mostrar primeiro artigo como exemplo
                    first = articles[0]
                    print(f"   📝 Primeiro artigo: '{first.get('titulo', 'N/A')}' (Status: {first.get('status', 'N/A')})")
            else:
                print(f"   ❌ Falha na API: {data}")
        else:
            print(f"   ❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 3. Testar endpoint API específico
    print("\n3. Testando endpoint API específico...")
    try:
        response = requests.get(f"{base_url}/review/api/list")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                count = data.get('count', 0)
                print(f"   ✅ API List: {count} artigos via API")
            else:
                print(f"   ❌ API Falhou: {data}")
        else:
            print(f"   ❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 4. Testar estatísticas
    print("\n4. Testando estatísticas...")
    try:
        response = requests.get(f"{base_url}/review/stats")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('statistics', {})
                print(f"   ✅ Estatísticas:")
                print(f"     - Total: {stats.get('total_artigos', 0)}")
                print(f"     - Pendentes: {stats.get('pendentes', 0)}")
                print(f"     - Aprovados: {stats.get('aprovados', 0)}")
                print(f"     - Rejeitados: {stats.get('rejeitados', 0)}")
            else:
                print(f"   ❌ Stats Falhou: {data}")
        else:
            print(f"   ❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")

def run_generator_test():
    """Executa geração de um artigo de teste"""
    base_url = "http://localhost:3025"
    
    print("\n🤖 TESTANDO GERADOR...")
    
    try:
        response = requests.post(f"{base_url}/generator/generate")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Artigo gerado com sucesso!")
                print(f"   📝 ID: {data.get('article_id', 'N/A')}")
            else:
                print(f"   ❌ Falha na geração: {data}")
        else:
            print(f"   ❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")

def main():
    print("🚀 CREATIVE API - TESTE DE DIAGNÓSTICO COMPLETO")
    print("=" * 60)
    
    # Verificar se servidor está rodando
    try:
        response = requests.get("http://localhost:3025/health")
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
        else:
            print("❌ Servidor não está respondendo corretamente")
            return
    except:
        print("❌ Servidor não está rodando! Execute 'python main.py' primeiro.")
        return
    
    # Executar testes
    test_review_endpoints()
    
    # Perguntar se quer gerar um artigo de teste
    resposta = input("\n🤖 Deseja gerar um artigo de teste? (s/n): ").lower()
    if resposta == 's':
        run_generator_test()
        print("\n🔄 Retestando após geração...")
        test_review_endpoints()
    
    print("\n✅ DIAGNÓSTICO CONCLUÍDO!")
    print("Se ainda houver problemas, verifique os logs do servidor.")

if __name__ == "__main__":
    main() 