#!/usr/bin/env python3
"""
Listar todos os usuários do WordPress para identificar qual usar
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

WP_SITE_URL = os.getenv('WP_SITE_URL', 'https://blog.creativecopias.com.br')

print("👥 LISTA DE USUÁRIOS DO WORDPRESS")
print("=" * 50)
print(f"Site: {WP_SITE_URL}")
print("=" * 50)

def list_all_users():
    """Listar todos os usuários disponíveis"""
    try:
        # Tentar diferentes endpoints para obter usuários
        endpoints = [
            f"{WP_SITE_URL}/wp-json/wp/v2/users",
            f"{WP_SITE_URL}/wp-json/wp/v2/users?per_page=100"
        ]
        
        for i, url in enumerate(endpoints, 1):
            print(f"\n{i}️⃣ Tentativa {i}: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                print(f"   ✅ {len(users)} usuários encontrados:")
                
                for user in users:
                    print(f"\n   👤 USUÁRIO:")
                    print(f"      ID: {user.get('id')}")
                    print(f"      Nome: {user.get('name')}")
                    print(f"      Username/Slug: {user.get('slug')}")
                    print(f"      Email: {user.get('email', 'Não disponível')}")
                    print(f"      Roles: {user.get('roles', [])}")
                    print(f"      Capabilities: {user.get('capabilities', {})}")
                    
                    # Verificar se é admin
                    roles = user.get('roles', [])
                    is_admin = 'administrator' in roles
                    admin_icon = "👑" if is_admin else "👤"
                    print(f"      Admin: {admin_icon} {'SIM' if is_admin else 'NÃO'}")
                    
                if users:
                    print(f"\n📋 RESUMO DE USUÁRIOS:")
                    for user in users:
                        roles = user.get('roles', [])
                        is_admin = 'administrator' in roles
                        admin_status = "👑 ADMIN" if is_admin else "👤 Normal"
                        print(f"   • {user.get('slug')} ({user.get('name')}) - {admin_status}")
                    
                    print(f"\n🔧 SUGESTÃO DE CONFIGURAÇÃO:")
                    
                    # Encontrar admins
                    admins = [u for u in users if 'administrator' in u.get('roles', [])]
                    if admins:
                        admin = admins[0]  # Primeiro admin
                        print(f"   Usar este usuário admin: {admin.get('slug')}")
                        print(f"   Atualize o .env:")
                        print(f"   WP_USERNAME={admin.get('slug')}")
                        print(f"   WP_PASSWORD=nova_application_password")
                    else:
                        print("   ❌ Nenhum administrador encontrado!")
                        
                break
            else:
                error_text = response.text[:200] if response.text else "Sem resposta"
                print(f"   ❌ Erro: {error_text}")
                
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")

def suggest_next_steps():
    """Sugerir próximos passos"""
    print(f"\n📝 PRÓXIMOS PASSOS:")
    print("=" * 50)
    
    print("1️⃣ ESCOLHER O USUÁRIO CORRETO:")
    print("   • Use um usuário com role 'administrator'")
    print("   • Anote o 'slug' do usuário (não o nome)")
    
    print("\n2️⃣ GERAR APPLICATION PASSWORD:")
    print("   • Faça login no WordPress com esse usuário")
    print("   • Vá para: wp-admin/profile.php")
    print("   • Seção: 'Application Passwords'")
    print("   • Nome: 'Creative IA System'")
    print("   • Gere e copie a senha")
    
    print("\n3️⃣ ATUALIZAR CONFIGURAÇÕES:")
    print("   • Edite o arquivo .env")
    print("   • WP_USERNAME=slug_do_usuario_escolhido")
    print("   • WP_PASSWORD=nova_application_password")
    
    print("\n4️⃣ TESTAR NOVAMENTE:")
    print("   • Execute: python test_wordpress_permissions.py")

if __name__ == "__main__":
    list_all_users()
    suggest_next_steps()
    
    print("\n" + "=" * 50)
    print("👥 LISTAGEM CONCLUÍDA")
    print("=" * 50) 