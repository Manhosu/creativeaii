#!/usr/bin/env python3
"""
Investigar mudanças no WordPress que podem estar afetando a autenticação
"""

import requests
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

WP_SITE_URL = os.getenv('WP_SITE_URL', 'https://blog.creativecopias.com.br')
WP_USERNAME = os.getenv('WP_USERNAME', 'publicador_seo')
WP_PASSWORD = os.getenv('WP_PASSWORD')

print("🔍 INVESTIGAÇÃO DE MUDANÇAS NO WORDPRESS")
print("=" * 60)
print(f"🌐 Site: {WP_SITE_URL}")
print(f"👤 Usuário: {WP_USERNAME}")
print(f"🔑 Senha sendo usada: {WP_PASSWORD}")
print("=" * 60)

# Headers de autenticação
auth_string = f"{WP_USERNAME}:{WP_PASSWORD}"
auth_bytes = base64.b64encode(auth_string.encode()).decode()
headers = {
    'Authorization': f'Basic {auth_bytes}',
    'Content-Type': 'application/json',
    'User-Agent': 'Creative IA System'
}

def check_plugins_that_block_api():
    """Verificar plugins que podem estar bloqueando a API"""
    print("\n1️⃣ VERIFICANDO PLUGINS ATIVOS")
    
    try:
        # Tentar obter informações sobre plugins via API
        url = f"{WP_SITE_URL}/wp-json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            namespaces = data.get('namespaces', [])
            
            print("📦 Plugins detectados via API:")
            security_plugins = []
            
            if 'wordfence/v1' in namespaces:
                security_plugins.append('Wordfence')
                print("   🛡️ Wordfence - PODE ESTAR BLOQUEANDO!")
                
            if 'akismet/v1' in namespaces:
                print("   ✅ Akismet - Sem problemas conhecidos")
                
            if 'redirection/v1' in namespaces:
                print("   🔀 Redirection - Sem problemas conhecidos")
                
            # Verificar outros plugins de segurança comuns
            if any(plugin in ' '.join(namespaces) for plugin in ['security', 'limit', 'firewall']):
                print("   ⚠️ Plugin de segurança detectado!")
                
            if security_plugins:
                print(f"\n⚠️ PLUGINS DE SEGURANÇA ATIVOS: {', '.join(security_plugins)}")
                print("   Estes plugins podem estar bloqueando Application Passwords!")
            else:
                print("\n✅ Nenhum plugin de segurança problemático detectado")
                
    except Exception as e:
        print(f"❌ Erro ao verificar plugins: {e}")

def check_user_exists():
    """Verificar se o usuário existe e está ativo"""
    print("\n2️⃣ VERIFICANDO SE USUÁRIO EXISTE")
    
    try:
        # Buscar usuário sem autenticação (público)
        url = f"{WP_SITE_URL}/wp-json/wp/v2/users"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            users = response.json()
            user_found = False
            
            for user in users:
                if user.get('slug') == WP_USERNAME or user.get('name', '').lower() == WP_USERNAME.lower():
                    user_found = True
                    print(f"✅ Usuário encontrado:")
                    print(f"   ID: {user.get('id')}")
                    print(f"   Nome: {user.get('name')}")
                    print(f"   Slug: {user.get('slug')}")
                    break
            
            if not user_found:
                print(f"❌ Usuário '{WP_USERNAME}' NÃO encontrado!")
                print("   Possíveis causas:")
                print("   - Nome de usuário mudou")
                print("   - Usuário foi deletado")
                print("   - Usuário está inativo")
        else:
            print(f"❌ Erro ao listar usuários: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")

def test_different_endpoints():
    """Testar diferentes endpoints para ver onde funciona e onde não"""
    print("\n3️⃣ TESTANDO DIFERENTES ENDPOINTS")
    
    endpoints = [
        ("/wp-json", "GET", "Info geral da API"),
        ("/wp-json/wp/v2/posts", "GET", "Listar posts"),
        ("/wp-json/wp/v2/users/me", "GET", "Info do usuário atual"),
        ("/wp-json/wp/v2/categories", "GET", "Listar categorias"),
    ]
    
    for endpoint, method, description in endpoints:
        url = f"{WP_SITE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_icon} {description}: {response.status_code}")
            
            if response.status_code not in [200, 404]:
                try:
                    error = response.json()
                    print(f"      Erro: {error.get('message', 'Desconhecido')}")
                except:
                    print(f"      Erro: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ {description}: Erro de conexão - {e}")

def check_auth_header_format():
    """Verificar se o header de autenticação está correto"""
    print("\n4️⃣ VERIFICANDO FORMATO DA AUTENTICAÇÃO")
    
    print(f"Username: '{WP_USERNAME}'")
    print(f"Password: '{WP_PASSWORD}'")
    print(f"Auth string: '{WP_USERNAME}:{WP_PASSWORD}'")
    
    # Decodificar o que foi codificado para verificar
    auth_string = f"{WP_USERNAME}:{WP_PASSWORD}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    decoded = base64.b64decode(auth_bytes).decode()
    
    print(f"Encoded: {auth_bytes}")
    print(f"Decoded check: '{decoded}'")
    print(f"Match: {decoded == auth_string}")

def check_wp_json_health():
    """Verificar se a API está saudável"""
    print("\n5️⃣ VERIFICANDO SAÚDE DA API WORDPRESS")
    
    try:
        # Verificar endpoints básicos
        endpoints = [
            f"{WP_SITE_URL}/wp-json",
            f"{WP_SITE_URL}/wp-json/wp/v2",
        ]
        
        for url in endpoints:
            response = requests.get(url, timeout=10)
            print(f"   {url}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'name' in data:
                    print(f"      Site: {data.get('name')}")
                if 'namespaces' in data:
                    print(f"      Namespaces: {len(data.get('namespaces', []))}")
    except Exception as e:
        print(f"❌ Erro ao verificar saúde da API: {e}")

def suggest_immediate_fixes():
    """Sugerir correções imediatas"""
    print("\n🛠️ CORREÇÕES IMEDIATAS A TENTAR:")
    print("=" * 60)
    
    print("1️⃣ VERIFICAR NO WORDPRESS ADMIN:")
    print("   • wp-admin/users.php - verificar se usuário existe")
    print("   • wp-admin/profile.php - verificar Application Passwords")
    
    print("\n2️⃣ VERIFICAR WORDFENCE (se ativo):")
    print("   • wp-admin/admin.php?page=WordfenceSecOpt")
    print("   • Procurar por 'REST API' ou 'Application Password'")
    print("   • Desativar temporariamente para testar")
    
    print("\n3️⃣ VERIFICAR CLOUDFLARE:")
    print("   • Pode estar bloqueando requisições com Basic Auth")
    print("   • Adicionar regra para permitir /wp-json/*")
    
    print("\n4️⃣ LOGS DO SERVIDOR:")
    print("   • Verificar error_log do WordPress")
    print("   • Procurar por bloqueios de IP ou autenticação")

if __name__ == "__main__":
    if not WP_PASSWORD:
        print("❌ WP_PASSWORD não encontrada!")
        exit(1)
    
    check_plugins_that_block_api()
    check_user_exists()
    test_different_endpoints()
    check_auth_header_format()
    check_wp_json_health()
    suggest_immediate_fixes()
    
    print("\n" + "=" * 60)
    print("🔍 INVESTIGAÇÃO CONCLUÍDA")
    print("=" * 60) 