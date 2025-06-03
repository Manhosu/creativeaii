#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime

def check_railway_status():
    """Verifica se o Railway terminou o redeploy"""
    base_url = "https://creativeia-production.up.railway.app"
    
    print(f"🔄 Monitorando redeploy do Railway...")
    print(f"🌐 URL: {base_url}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)
    
    attempt = 1
    max_attempts = 30  # 5 minutos com intervalos de 10s
    
    while attempt <= max_attempts:
        try:
            print(f"🔍 Tentativa {attempt}/{max_attempts}...", end=" ")
            
            # Teste básico de conectividade
            response = requests.get(f"{base_url}/health", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    print("✅ Sistema online!")
                    
                    # Testar endpoints específicos do review
                    print("📝 Testando review...")
                    review_response = requests.get(f"{base_url}/review/stats", timeout=10)
                    
                    if review_response.status_code == 200:
                        review_data = review_response.json()
                        if review_data.get('success'):
                            stats = review_data.get('statistics', {})
                            print(f"✅ Review funcionando! {stats.get('total_artigos', 0)} artigos")
                            return True
                        else:
                            print(f"⚠️ Review responde mas com erro: {review_data}")
                    else:
                        print(f"❌ Review ainda com erro: {review_response.status_code}")
                else:
                    print(f"⚠️ Sistema respondendo mas status: {data.get('status')}")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            print("⏳ Timeout (ainda implantando...)")
        except requests.exceptions.ConnectionError:
            print("🚫 Conexão recusada (redeploy em andamento...)")
        except Exception as e:
            print(f"❌ Erro: {str(e)[:50]}")
        
        if attempt < max_attempts:
            print("   ⏳ Aguardando 10 segundos...")
            time.sleep(10)
        
        attempt += 1
    
    print("\n❌ Timeout atingido. O redeploy pode estar demorando mais que esperado.")
    return False

def run_full_test():
    """Executa teste completo após redeploy"""
    base_url = "https://creativeia-production.up.railway.app"
    
    print("\n🧪 EXECUTANDO TESTE COMPLETO PÓS-REDEPLOY")
    print("=" * 60)
    
    # Testar módulos
    modules = ['scraper', 'generator', 'review', 'publisher', 'scheduler']
    
    print("📋 Status dos módulos:")
    for module in modules:
        try:
            response = requests.get(f"{base_url}/{module}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'N/A')
                icon = "✅" if status in ['ready', 'operational'] else "⚠️"
                print(f"   {icon} {module.capitalize()}: {status}")
            else:
                print(f"   ❌ {module.capitalize()}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {module.capitalize()}: {e}")
    
    # Testar review especificamente  
    print("\n📝 Teste detalhado do Review:")
    
    # Stats
    try:
        response = requests.get(f"{base_url}/review/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('statistics', {})
                print(f"   ✅ Stats: {stats.get('total_artigos', 0)} artigos total")
                print(f"   📊 Pendentes: {stats.get('pendentes', 0)}")
                print(f"   📊 Aprovados: {stats.get('aprovados', 0)}")
            else:
                print(f"   ❌ Stats erro: {data}")
        else:
            print(f"   ❌ Stats HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats erro: {e}")
    
    # Articles
    try:
        response = requests.get(f"{base_url}/review/articles?limit=2", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('articles'):
                articles = data.get('articles', [])
                print(f"   ✅ Articles: {len(articles)} artigos carregados")
                if articles:
                    primeiro = articles[0]
                    print(f"   📝 Exemplo: {primeiro.get('titulo', 'N/A')[:40]}...")
            else:
                print(f"   ❌ Articles erro: {data}")
        else:
            print(f"   ❌ Articles HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Articles erro: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE COMPLETO FINALIZADO!")
    print(f"🌐 Acesse: {base_url}")
    print(f"📝 Review: {base_url}/interface/review")

def main():
    print("🚀 MONITOR DE REDEPLOY DO RAILWAY")
    print("=" * 50)
    
    # Aguardar o redeploy
    if check_railway_status():
        print("\n🎉 Redeploy concluído com sucesso!")
        time.sleep(2)  # Aguardar estabilizar
        run_full_test()
    else:
        print("\n⚠️ Redeploy ainda em andamento ou com problemas.")
        print("Tente executar novamente em alguns minutos.")

if __name__ == "__main__":
    main() 