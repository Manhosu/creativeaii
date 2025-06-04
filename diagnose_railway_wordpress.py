#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
from datetime import datetime
import base64

def test_railway_wordpress_connection():
    """
    DIAGNÓSTICO COMPLETO: Railway vs WordPress
    Identifica diferenças entre ambiente local e produção
    """
    
    print("🔍 DIAGNÓSTICO COMPLETO: Railway vs WordPress")
    print("=" * 70)
    
    # 1. VERIFICAR VARIÁVEIS DE AMBIENTE RAILWAY
    print("\n📋 1. VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("-" * 50)
    
    env_vars = {
        'WP_SITE_URL': os.getenv('WP_SITE_URL'),
        'WP_USERNAME': os.getenv('WP_USERNAME'), 
        'WP_PASSWORD': os.getenv('WP_PASSWORD'),
        'WORDPRESS_URL': os.getenv('WORDPRESS_URL'),
        'WORDPRESS_USERNAME': os.getenv('WORDPRESS_USERNAME'),
        'WORDPRESS_PASSWORD': os.getenv('WORDPRESS_PASSWORD')
    }
    
    missing_vars = []
    for var, value in env_vars.items():
        if value:
            if 'PASSWORD' in var:
                print(f"   ✅ {var}: ****{value[-4:]} (len: {len(value)})")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NÃO CONFIGURADA")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ VARIÁVEIS FALTANDO: {', '.join(missing_vars)}")
        return False
    
    # 2. TESTAR CONECTIVIDADE COM WORDPRESS
    print("\n🌐 2. TESTANDO CONECTIVIDADE")
    print("-" * 50)
    
    wp_base_url = env_vars['WP_SITE_URL'] or "https://blog.creativecopias.com.br"
    wp_api_url = f"{wp_base_url}/wp-json/wp/v2"
    
    try:
        # Teste básico da API
        print(f"   🔗 Testando: {wp_api_url}")
        response = requests.get(wp_api_url, timeout=10)
        
        if response.status_code == 200:
            api_info = response.json()
            print(f"   ✅ API WordPress: {api_info.get('description', 'OK')}")
            print(f"   📦 Namespaces: {len(api_info.get('namespaces', []))}")
        else:
            print(f"   ❌ API inacessível: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conectividade: {e}")
        return False
    
    # 3. TESTAR AUTENTICAÇÃO
    print("\n🔐 3. TESTANDO AUTENTICAÇÃO")
    print("-" * 50)
    
    # Credenciais do Railway
    username = env_vars['WP_USERNAME']
    password = env_vars['WP_PASSWORD']
    
    print(f"   👤 Usuário: {username}")
    print(f"   🔑 Senha: ****{password[-4:] if password else 'N/A'}")
    
    # Teste de autenticação básica
    auth = (username, password)
    
    try:
        # Teste 1: /users/me (verifica autenticação)
        me_response = requests.get(f"{wp_api_url}/users/me", auth=auth, timeout=10)
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"   ✅ Usuário autenticado: {user_data.get('name')}")
            print(f"   🎭 Roles: {user_data.get('roles', [])}")
            print(f"   🆔 ID: {user_data.get('id')}")
            
            # Verificar se tem permissão para criar posts
            capabilities = user_data.get('capabilities', {})
            can_publish = capabilities.get('publish_posts', False)
            can_edit = capabilities.get('edit_posts', False)
            
            print(f"   📝 Pode editar posts: {can_edit}")
            print(f"   🚀 Pode publicar posts: {can_publish}")
            
            if not can_publish:
                print("   ⚠️ ATENÇÃO: Usuário sem permissão para publicar!")
            
        elif me_response.status_code == 401:
            print("   ❌ FALHA DE AUTENTICAÇÃO!")
            print("   🔍 Credenciais inválidas ou usuário inexistente")
            return False
        else:
            print(f"   ❌ Erro na autenticação: HTTP {me_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no teste de autenticação: {e}")
        return False
    
    # 4. TESTAR CRIAÇÃO DE POST
    print("\n📝 4. TESTANDO CRIAÇÃO DE POST")
    print("-" * 50)
    
    test_post = {
        "title": f"Teste Railway {datetime.now().strftime('%d/%m %H:%M:%S')}",
        "content": "<p>Post de teste criado pelo diagnóstico Railway.</p>",
        "status": "draft"
    }
    
    try:
        create_response = requests.post(
            f"{wp_api_url}/posts",
            json=test_post,
            auth=auth,
            headers={'Content-Type': 'application/json'},
            timeout=20
        )
        
        if create_response.status_code == 201:
            post_data = create_response.json()
            print(f"   ✅ Post criado: ID {post_data.get('id')}")
            print(f"   🔗 URL: {post_data.get('link')}")
            
            # Limpar - deletar o post de teste
            delete_response = requests.delete(
                f"{wp_api_url}/posts/{post_data['id']}?force=true",
                auth=auth,
                timeout=10
            )
            if delete_response.status_code in [200, 410]:
                print("   🗑️ Post de teste removido")
            
            return True
            
        elif create_response.status_code == 401:
            error_data = create_response.json()
            print(f"   ❌ ERRO 401: {error_data.get('message', 'Sem permissão')}")
            print(f"   🔍 Código: {error_data.get('code', 'N/A')}")
            return False
        else:
            error_data = create_response.json() if create_response.content else {}
            print(f"   ❌ Falha na criação: HTTP {create_response.status_code}")
            print(f"   📄 Resposta: {error_data.get('message', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no teste de criação: {e}")
        return False

def compare_local_vs_railway():
    """Compara diferenças entre ambiente local e Railway"""
    
    print("\n🔄 5. COMPARAÇÃO LOCAL vs RAILWAY")
    print("-" * 50)
    
    print("   📍 Ambiente atual: RAILWAY")
    print("   🌐 IP externo: Diferente do localhost")
    print("   🔒 Headers: User-Agent diferente")
    print("   ⏰ Timeout: Pode ser diferente")
    
    # Verificar User-Agent atual
    try:
        response = requests.get("https://httpbin.org/user-agent", timeout=5)
        if response.status_code == 200:
            ua_data = response.json()
            print(f"   🤖 User-Agent: {ua_data.get('user-agent', 'N/A')}")
    except:
        print("   ⚠️ Não foi possível verificar User-Agent")

def generate_fix_recommendations():
    """Gera recomendações específicas para correção"""
    
    print("\n💡 6. RECOMENDAÇÕES DE CORREÇÃO")
    print("-" * 50)
    
    recommendations = [
        "✅ 1. Verificar App Password no WordPress:",
        "     - Acessar: wp-admin/profile.php",
        "     - Gerar nova senha específica para Railway",
        "     - Usar formato: abcd1234efgh5678 (sem espaços)",
        "",
        "✅ 2. Configurar variáveis no Railway:",
        "     WP_SITE_URL=https://blog.creativecopias.com.br",
        "     WP_USERNAME=publicador_seo",
        "     WP_PASSWORD=nova_app_password_aqui",
        "",
        "✅ 3. Verificar permissões do usuário:",
        "     - Role: Editor ou Administrator",
        "     - Capabilities: publish_posts = true",
        "",
        "✅ 4. Simplificar publicação inicial:",
        "     - Status: draft (não publish)",
        "     - Remover metadados complexos",
        "     - Testar com post básico primeiro",
        "",
        "✅ 5. Verificar WordPress Security:",
        "     - Plugins de segurança bloqueando API",
        "     - Firewall configurado incorretamente",
        "     - IP do Railway na whitelist"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")

def create_railway_test_config():
    """Cria configuração otimizada para Railway"""
    
    print("\n📋 7. CONFIGURAÇÃO OTIMIZADA RAILWAY")
    print("-" * 50)
    
    railway_config = """# CONFIGURAÇÃO OTIMIZADA PARA RAILWAY
# Variáveis que DEVEM estar configuradas

# === WORDPRESS (CRÍTICO) ===
WP_SITE_URL=https://blog.creativecopias.com.br
WP_USERNAME=publicador_seo
WP_PASSWORD=f1cSXdACIapaxrKGlklf7yB4

# === OPENAI (CRÍTICO) ===
OPENAI_API_KEY=sk-proj-sua_chave_aqui

# === SISTEMA ===
PORT=3025
DEBUG=false

# === CONFIGURAÇÕES SIMPLIFICADAS ===
WP_AUTO_PUBLISH=false
WP_DEFAULT_STATUS=draft
WP_DEFAULT_CATEGORY=1

# === TIMEOUT OTIMIZADO ===
SCRAPING_TIMEOUT=45
TIMEOUT_SECONDS=45
"""
    
    with open('railway_optimized_config.env', 'w', encoding='utf-8') as f:
        f.write(railway_config)
    
    print("   ✅ Configuração salva: railway_optimized_config.env")
    print("   📋 Copie essas variáveis para o Railway")

def main():
    """Executa diagnóstico completo"""
    
    print("🚀 DIAGNÓSTICO RAILWAY-WORDPRESS")
    print(f"⏰ Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executar testes
    wordpress_working = test_railway_wordpress_connection()
    
    # Comparar ambientes
    compare_local_vs_railway()
    
    # Gerar recomendações
    generate_fix_recommendations()
    
    # Criar configuração otimizada
    create_railway_test_config()
    
    # Resultado final
    print("\n" + "=" * 70)
    print("📊 RESULTADO FINAL")
    print("-" * 70)
    
    if wordpress_working:
        print("✅ WORDPRESS FUNCIONANDO!")
        print("💡 O problema pode estar na configuração específica do sistema")
        print("📝 Teste publicação manual via endpoint /debug/wordpress-auth")
    else:
        print("❌ PROBLEMA IDENTIFICADO!")
        print("🔧 Siga as recomendações acima para corrigir")
        print("📞 Verifique principalmente App Password e permissões")
    
    print(f"\n📁 Arquivos gerados:")
    print(f"   - railway_optimized_config.env")
    print(f"   - Log deste diagnóstico")

if __name__ == "__main__":
    main() 