#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONFIGURAÇÃO WORDPRESS PRODUÇÃO
Script para configurar e testar WordPress real (sem modo demo)
"""

import requests
import os
import json
from datetime import datetime

def test_wordpress_credentials():
    """Testa credenciais WordPress reais"""
    
    print("🔧 CONFIGURAÇÃO WORDPRESS PRODUÇÃO")
    print("=" * 60)
    print("Testando credenciais reais (SEM modo demo)")
    print("=" * 60)
    
    # Credenciais WordPress
    WP_SITE_URL = "https://blog.creativecopias.com.br"
    WP_USERNAME = "publicador_seo"
    WP_PASSWORD = "f1cSXdACIapaxrKGlklf7yB4"  # App password
    
    print(f"🌐 Site WordPress: {WP_SITE_URL}")
    print(f"👤 Usuário: {WP_USERNAME}")
    print(f"🔐 Senha: {'*' * len(WP_PASSWORD)}")
    print()
    
    # 1. Testar acesso básico à API
    print("1. 🔍 TESTANDO ACESSO À API WORDPRESS...")
    try:
        api_url = f"{WP_SITE_URL}/wp-json/wp/v2/"
        response = requests.get(api_url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            api_data = response.json()
            print(f"   ✅ API WordPress acessível")
            print(f"   📋 Descrição: {api_data.get('description', 'N/A')}")
            print(f"   🔗 URL: {api_data.get('url', 'N/A')}")
        else:
            print(f"   ❌ API não acessível - Código {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao acessar API: {e}")
        return False
    
    # 2. Testar autenticação
    print("\n2. 🔐 TESTANDO AUTENTICAÇÃO...")
    try:
        auth_url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
        
        response = requests.get(
            auth_url,
            auth=(WP_USERNAME, WP_PASSWORD),
            params={'per_page': 1},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            posts = response.json()
            print(f"   ✅ Autenticação bem-sucedida")
            print(f"   📝 Posts encontrados: {len(posts)}")
            
            if posts:
                print(f"   📄 Último post: {posts[0].get('title', {}).get('rendered', 'N/A')}")
                
        elif response.status_code == 401:
            print(f"   ❌ Falha na autenticação - Credenciais inválidas")
            error_data = response.json()
            print(f"   📋 Erro: {error_data.get('message', 'N/A')}")
            return False
        else:
            print(f"   ⚠️ Resposta inesperada - Código {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro na autenticação: {e}")
        return False
    
    # 3. Testar criação de post
    print("\n3. 📝 TESTANDO CRIAÇÃO DE POST...")
    try:
        create_url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
        
        test_post_data = {
            'title': f'Teste Sistema SEO - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': '<p>Este é um post de teste criado pelo Sistema SEO. Pode ser removido.</p>',
            'status': 'draft',  # Criar como rascunho
            'excerpt': 'Post de teste do sistema automatizado de publicação SEO.'
        }
        
        response = requests.post(
            create_url,
            auth=(WP_USERNAME, WP_PASSWORD),
            json=test_post_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get('id')
            post_url = post_data.get('link')
            
            print(f"   ✅ Post criado com sucesso!")
            print(f"   📝 ID: {post_id}")
            print(f"   🔗 URL: {post_url}")
            print(f"   📊 Status: {post_data.get('status')}")
            
            # Tentar remover o post de teste
            print("\n4. 🗑️ REMOVENDO POST DE TESTE...")
            delete_response = requests.delete(
                f"{create_url}/{post_id}",
                auth=(WP_USERNAME, WP_PASSWORD),
                params={'force': True},
                timeout=10
            )
            
            if delete_response.status_code in [200, 410]:
                print(f"   ✅ Post de teste removido")
            else:
                print(f"   ⚠️ Post de teste não foi removido (ID: {post_id})")
            
            return True
            
        elif response.status_code == 401:
            print(f"   ❌ Não autorizado - Verifique permissões do usuário")
            return False
        elif response.status_code == 403:
            print(f"   ❌ Acesso proibido - Usuário sem permissão para criar posts")
            return False
        else:
            print(f"   ❌ Falha na criação - Código {response.status_code}")
            error_data = response.json()
            print(f"   📋 Erro: {error_data.get('message', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao criar post: {e}")
        return False

def update_railway_environment():
    """Mostra comandos para atualizar variáveis no Railway"""
    
    print("\n" + "=" * 60)
    print("🚀 CONFIGURAÇÃO NO RAILWAY")
    print("=" * 60)
    print("Execute os comandos abaixo no painel do Railway:")
    print()
    print("1. Acesse: https://railway.app/dashboard")
    print("2. Selecione seu projeto: creative-api")
    print("3. Vá em 'Variables'")
    print("4. Configure as variáveis:")
    print()
    print("   WP_SITE_URL=https://blog.creativecopias.com.br")
    print("   WP_USERNAME=publicador_seo")
    print("   WP_PASSWORD=f1cSXdACIapaxrKGlklf7yB4")
    print()
    print("5. Clique em 'Deploy' para aplicar as mudanças")
    print()

def test_system_integration():
    """Testa a integração com o sistema"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTE DE INTEGRAÇÃO")
    print("=" * 60)
    
    base_url = "https://creativeia-production.up.railway.app"
    
    print("Testando se o sistema reconhece as credenciais...")
    
    try:
        # Testar status do publisher
        response = requests.get(f"{base_url}/publisher", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Publisher Status: {data.get('status', 'N/A')}")
            
            wordpress_data = data.get('wordpress', {})
            if wordpress_data.get('success'):
                print(f"✅ WordPress Configurado: {wordpress_data.get('site_url', 'N/A')}")
                print(f"✅ Autenticação: {'OK' if wordpress_data.get('authenticated') else 'FALHA'}")
            else:
                print(f"❌ WordPress não configurado no sistema")
        else:
            print(f"❌ Sistema não acessível - Código {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar sistema: {e}")

def main():
    """Função principal"""
    
    print("🔧 INICIANDO CONFIGURAÇÃO WORDPRESS PRODUÇÃO")
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testar credenciais WordPress
    if test_wordpress_credentials():
        print("\n🎉 CREDENCIAIS WORDPRESS OK!")
        print("✅ Todas as credenciais estão funcionando corretamente")
        
        # Mostrar configuração Railway
        update_railway_environment()
        
        # Testar integração
        test_system_integration()
        
        print("\n" + "=" * 60)
        print("✅ WORDPRESS PRONTO PARA PRODUÇÃO!")
        print("=" * 60)
        print("O sistema está configurado para publicar posts reais.")
        print("Não haverá mais modo demo - apenas publicações reais.")
        print()
        print("🌐 Teste no navegador:")
        print("1. Acesse: https://creativeia-production.up.railway.app/interface/publisher")
        print("2. Clique em 'Testar WordPress'")
        print("3. Publique um artigo real")
        print()
        
    else:
        print("\n❌ FALHA NA CONFIGURAÇÃO")
        print("Verifique as credenciais ou permissões do usuário WordPress")

if __name__ == "__main__":
    main() 