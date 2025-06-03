#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
INSTRUÇÕES PARA CONFIGURAÇÃO WORDPRESS
Guia passo-a-passo para configurar WordPress em produção
"""

def show_wordpress_setup_instructions():
    """Mostra instruções detalhadas para configurar WordPress"""
    
    print("🔧 CONFIGURAÇÃO WORDPRESS PRODUÇÃO")
    print("=" * 70)
    print("INSTRUÇÕES PASSO-A-PASSO PARA FUNCIONAMENTO REAL")
    print("=" * 70)
    print()
    
    print("📋 SITUAÇÃO ATUAL:")
    print("   ✅ Sistema funcionando em modo demonstração")
    print("   ⚠️ WordPress precisa de credenciais corretas")
    print("   🎯 Objetivo: Publicação real no blog")
    print()
    
    print("🔐 PASSO 1: ACESSAR WORDPRESS ADMIN")
    print("-" * 40)
    print("1. Acesse: https://blog.creativecopias.com.br/wp-admin")
    print("2. Faça login com conta de administrador")
    print("3. Anote o nome de usuário usado para login")
    print()
    
    print("🔑 PASSO 2: CRIAR SENHA DE APLICAÇÃO")
    print("-" * 40)
    print("1. No painel WordPress, vá em: 'Usuários' > 'Perfil'")
    print("2. Role até encontrar a seção 'Senhas de Aplicação'")
    print("3. No campo 'Nome da Nova Senha de Aplicação', digite:")
    print("   'Sistema SEO Automatizado'")
    print("4. Clique em 'Adicionar Nova Senha de Aplicação'")
    print("5. COPIE a senha gerada (formato: abcd efgh ijkl mnop)")
    print("6. GUARDE essa senha - ela só aparece uma vez!")
    print()
    
    print("🚀 PASSO 3: CONFIGURAR NO RAILWAY")
    print("-" * 40)
    print("1. Acesse: https://railway.app/dashboard")
    print("2. Selecione o projeto: creative-api")
    print("3. Vá na aba 'Variables'")
    print("4. Configure estas 3 variáveis:")
    print()
    print("   WP_SITE_URL=https://blog.creativecopias.com.br")
    print("   WP_USERNAME=seu_usuario_admin_aqui")
    print("   WP_PASSWORD=senha_aplicacao_gerada_aqui")
    print()
    print("5. Clique em 'Deploy' para aplicar")
    print("6. Aguarde o redeploy (2-3 minutos)")
    print()
    
    print("✅ PASSO 4: TESTAR FUNCIONAMENTO")
    print("-" * 40)
    print("1. Acesse: https://creativeia-production.up.railway.app/review")
    print("2. Clique em 'Publicar' em um artigo")
    print("3. Deve aparecer: 'Artigo publicado no WordPress com sucesso!'")
    print("4. Verifique no blog se o post apareceu")
    print()
    
    print("🔍 COMO VERIFICAR SE DEU CERTO:")
    print("-" * 40)
    print("• Na interface deve aparecer: 'tipo: wordpress_real'")
    print("• No log deve aparecer: 'Publicação REAL concluída'")
    print("• O post deve aparecer em: https://blog.creativecopias.com.br")
    print()
    
    print("⚠️ SE DER ERRO:")
    print("-" * 40)
    print("• Verifique se o usuário é administrador ou editor")
    print("• Confirme se a senha de aplicação está correta")
    print("• Teste novamente após 5 minutos do redeploy")
    print()
    
    print("💡 EXEMPLO DE CONFIGURAÇÃO:")
    print("-" * 40)
    print("WP_SITE_URL=https://blog.creativecopias.com.br")
    print("WP_USERNAME=admin")
    print("WP_PASSWORD=abcd efgh ijkl mnop")
    print()
    
    print("🎉 APÓS CONFIGURAÇÃO:")
    print("-" * 40)
    print("• Sistema publicará posts reais automaticamente")
    print("• Posts aparecerão no blog imediatamente")
    print("• Não haverá mais modo demonstração")
    print("• Todas as funcionalidades serão reais")
    print()

def show_current_status():
    """Mostra status atual do sistema"""
    
    print("📊 STATUS ATUAL DO SISTEMA")
    print("=" * 50)
    print("✅ Interface web funcionando")
    print("✅ Geração de artigos funcionando")
    print("✅ Sistema de revisão funcionando")
    print("✅ Banco de dados funcionando")
    print("🔄 WordPress em modo fallback (demonstração)")
    print()
    print("🎯 PRÓXIMO PASSO: Configurar credenciais WordPress")
    print()

def main():
    """Função principal"""
    show_current_status()
    show_wordpress_setup_instructions()
    
    print("=" * 70)
    print("📞 PRECISA DE AJUDA?")
    print("=" * 70)
    print("Se tiver dúvidas na configuração:")
    print("1. Verifique se tem acesso admin ao WordPress")
    print("2. Confirme se as senhas de aplicação estão habilitadas")
    print("3. Teste uma variável por vez no Railway")
    print()
    print("O sistema continuará funcionando em modo demonstração")
    print("até que o WordPress seja configurado corretamente.")
    print()

if __name__ == "__main__":
    main() 