import sqlite3
import os

def check_database():
    db_path = 'data/review_articles.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não existe!")
        return
    
    print(f"✅ Banco encontrado: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tabelas: {[t[0] for t in tables]}")
        
        # Verificar artigos (tabela correta é 'articles')
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        print(f"📄 Total de artigos: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, titulo, status FROM articles LIMIT 5")
            articles = cursor.fetchall()
            print("📝 Últimos artigos:")
            for article in articles:
                print(f"  - ID {article[0]}: {article[1]} (Status: {article[2]})")
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(articles)")
        columns = cursor.fetchall()
        print(f"🏗️ Estrutura da tabela 'articles':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_database() 