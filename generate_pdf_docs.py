#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar PDFs profissionais da documentação do Sistema Creative API
"""

import os
import markdown
from weasyprint import HTML, CSS
from datetime import datetime

def read_markdown_file(filename):
    """Lê arquivo markdown e retorna o conteúdo"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado")
        return ""

def convert_markdown_to_html(md_content, title=""):
    """Converte markdown para HTML com formatação profissional"""
    
    # Configurar extensões do markdown
    md = markdown.Markdown(extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.toc',
        'markdown.extensions.attr_list'
    ])
    
    # Converter markdown para HTML
    html_content = md.convert(md_content)
    
    # CSS profissional para PDF
    css_styles = """
    <style>
        @page {
            size: A4;
            margin: 2.5cm 2cm;
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 10px;
                color: #666;
            }
            @bottom-left {
                content: "Sistema Creative API - """ + title + """";
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            margin: 0;
            padding: 0;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            font-size: 28px;
            page-break-before: auto;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 25px;
            font-size: 22px;
        }
        
        h3 {
            color: #2980b9;
            margin-top: 20px;
            font-size: 18px;
        }
        
        h4 {
            color: #8e44ad;
            margin-top: 15px;
            font-size: 16px;
        }
        
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 15px;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }
        
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 90%;
        }
        
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            margin: 15px 0;
        }
        
        pre code {
            background: none;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }
        
        .success {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        
        .info {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        
        .cover-page {
            text-align: center;
            padding: 100px 0;
            page-break-after: always;
        }
        
        .cover-title {
            font-size: 36px;
            color: #2c3e50;
            margin-bottom: 20px;
            font-weight: bold;
        }
        
        .cover-subtitle {
            font-size: 24px;
            color: #7f8c8d;
            margin-bottom: 40px;
        }
        
        .cover-info {
            font-size: 16px;
            color: #95a5a6;
            margin-top: 50px;
        }
        
        .toc {
            page-break-after: always;
            margin: 30px 0;
        }
        
        .toc h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
        }
        
        .emoji {
            font-size: 1.2em;
        }
    </style>
    """
    
    # HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html

def create_cover_page(title, subtitle=""):
    """Cria página de capa profissional"""
    today = datetime.now().strftime("%d de %B de %Y")
    
    cover_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Capa - {title}</title>
        <style>
            @page {{
                size: A4;
                margin: 0;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }}
            .cover-container {{
                max-width: 80%;
                padding: 50px;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 30px;
            }}
            .title {{
                font-size: 42px;
                font-weight: bold;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .subtitle {{
                font-size: 24px;
                margin-bottom: 40px;
                opacity: 0.9;
            }}
            .date {{
                font-size: 18px;
                opacity: 0.8;
                margin-top: 50px;
            }}
            .version {{
                font-size: 16px;
                opacity: 0.7;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="cover-container">
            <div class="logo">🚀</div>
            <h1 class="title">{title}</h1>
            <p class="subtitle">{subtitle}</p>
            <div class="date">{today}</div>
            <div class="version">Versão 1.0.0</div>
        </div>
    </body>
    </html>
    """
    
    return cover_html

def generate_pdf(html_content, output_filename):
    """Gera PDF a partir do HTML"""
    try:
        # Criar diretório se não existir
        os.makedirs('docs_pdf', exist_ok=True)
        
        # Caminho completo do arquivo
        output_path = os.path.join('docs_pdf', output_filename)
        
        # Converter HTML para PDF
        HTML(string=html_content).write_pdf(output_path)
        
        print(f"✅ PDF gerado: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF {output_filename}: {str(e)}")
        return None

def generate_combined_pdf():
    """Gera um PDF único com toda a documentação"""
    
    print("📚 Gerando documentação completa em PDF...")
    
    # Ler todos os documentos
    readme_content = read_markdown_file('README_CLIENTE.md')
    exec_content = read_markdown_file('APRESENTACAO_EXECUTIVA.md')
    doc_content = read_markdown_file('DOCUMENTACAO_SISTEMA.md')
    tech_content = read_markdown_file('ESPECIFICACOES_TECNICAS.md')
    
    # Criar capa
    cover_html = create_cover_page(
        "Sistema Creative API",
        "Documentação Completa e Especificações Técnicas"
    )
    
    # Combinar todos os conteúdos
    combined_md = f"""
# 📚 Índice da Documentação

## Documentos Incluídos:
1. **Resumo Executivo** - Visão geral e benefícios
2. **Apresentação Comercial** - ROI e justificativa de investimento  
3. **Documentação Completa** - Funcionamento detalhado do sistema
4. **Especificações Técnicas** - Arquitetura e implementação

---

{readme_content}

---

{exec_content}

---

{doc_content}

---

{tech_content}
    """
    
    # Converter para HTML
    html_content = convert_markdown_to_html(combined_md, "Documentação Completa")
    
    # Adicionar capa ao HTML
    final_html = cover_html + html_content
    
    # Gerar PDF
    pdf_path = generate_pdf(final_html, 'Sistema_Creative_API_Documentacao_Completa.pdf')
    
    return pdf_path

def generate_individual_pdfs():
    """Gera PDFs individuais para cada documento"""
    
    print("📋 Gerando PDFs individuais...")
    
    documents = [
        ('README_CLIENTE.md', 'Sistema_Creative_API_Resumo.pdf', 'Resumo Executivo'),
        ('APRESENTACAO_EXECUTIVA.md', 'Sistema_Creative_API_Apresentacao.pdf', 'Apresentação Comercial'),
        ('DOCUMENTACAO_SISTEMA.md', 'Sistema_Creative_API_Documentacao.pdf', 'Documentação Completa'),
        ('ESPECIFICACOES_TECNICAS.md', 'Sistema_Creative_API_Especificacoes.pdf', 'Especificações Técnicas')
    ]
    
    generated_files = []
    
    for md_file, pdf_file, title in documents:
        print(f"📄 Processando {md_file}...")
        
        # Ler conteúdo
        content = read_markdown_file(md_file)
        
        if content:
            # Criar capa individual
            cover_html = create_cover_page("Sistema Creative API", title)
            
            # Converter para HTML
            html_content = convert_markdown_to_html(content, title)
            
            # Combinar capa + conteúdo
            final_html = cover_html + html_content
            
            # Gerar PDF
            pdf_path = generate_pdf(final_html, pdf_file)
            
            if pdf_path:
                generated_files.append(pdf_path)
    
    return generated_files

def main():
    """Função principal"""
    print("🚀 Sistema Creative API - Gerador de PDFs")
    print("=" * 50)
    
    try:
        # Verificar se weasyprint está instalado
        import weasyprint
        print("✅ WeasyPrint encontrado")
        
    except ImportError:
        print("❌ WeasyPrint não encontrado. Instalando...")
        os.system("pip install weasyprint")
        print("✅ WeasyPrint instalado")
    
    # Gerar PDF completo
    print("\n📚 Gerando documentação completa...")
    complete_pdf = generate_combined_pdf()
    
    # Gerar PDFs individuais
    print("\n📋 Gerando documentos individuais...")
    individual_pdfs = generate_individual_pdfs()
    
    # Resumo
    print("\n" + "=" * 50)
    print("✅ GERAÇÃO CONCLUÍDA!")
    print("=" * 50)
    
    if complete_pdf:
        print(f"📚 Documentação Completa: {complete_pdf}")
    
    if individual_pdfs:
        print("📋 Documentos Individuais:")
        for pdf in individual_pdfs:
            print(f"   📄 {pdf}")
    
    print(f"\n📁 Todos os PDFs estão na pasta: docs_pdf/")
    print("🎉 Pronto para enviar ao cliente!")

if __name__ == "__main__":
    main() 