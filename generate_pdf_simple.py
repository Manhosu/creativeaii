#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para gerar HTMLs profissionais da documentação
que podem ser facilmente convertidos para PDF pelo browser
"""

import os
import re
from datetime import datetime

def read_markdown_file(filename):
    """Lê arquivo markdown e retorna o conteúdo"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado")
        return ""

def markdown_to_html_simple(md_content):
    """Converte markdown básico para HTML"""
    html = md_content
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Bold e Italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Lists - básico
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]  # Remove "- " ou "* "
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            # Paragraphs
            if line.strip() and not line.startswith('<'):
                result_lines.append(f'<p>{line}</p>')
            else:
                result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)

def create_professional_html(content, title, doc_type=""):
    """Cria HTML profissional para PDF"""
    today = datetime.now().strftime("%d/%m/%Y")
    
    html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background: white;
        }}
        
        /* Capa */
        .cover-page {{
            text-align: center;
            padding: 150px 0;
            margin-bottom: 100px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            page-break-after: always;
        }}
        
        .cover-logo {{
            font-size: 72px;
            margin-bottom: 30px;
        }}
        
        .cover-title {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .cover-subtitle {{
            font-size: 28px;
            margin-bottom: 40px;
            opacity: 0.9;
        }}
        
        .cover-date {{
            font-size: 18px;
            opacity: 0.8;
            margin-top: 60px;
        }}
        
        .cover-version {{
            font-size: 16px;
            opacity: 0.7;
            margin-top: 10px;
        }}
        
        /* Headers */
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-top: 40px;
            margin-bottom: 25px;
            font-size: 32px;
            page-break-before: auto;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
            margin-top: 35px;
            margin-bottom: 20px;
            font-size: 26px;
        }}
        
        h3 {{
            color: #2980b9;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 22px;
        }}
        
        h4 {{
            color: #8e44ad;
            margin-top: 20px;
            margin-bottom: 12px;
            font-size: 18px;
        }}
        
        /* Text */
        p {{
            margin-bottom: 16px;
            text-align: justify;
            font-size: 14px;
        }}
        
        /* Lists */
        ul, ol {{
            margin-bottom: 20px;
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        /* Code */
        code {{
            background-color: #f8f9fa;
            padding: 3px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            border: 1px solid #e9ecef;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
            overflow-x: auto;
            margin: 20px 0;
            font-size: 13px;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            border: none;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 14px;
            border: 1px solid #dee2e6;
        }}
        
        th, td {{
            border: 1px solid #dee2e6;
            padding: 12px 15px;
            text-align: left;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #495057;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        /* Links */
        a {{
            color: #007bff;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* Strong/Bold */
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        /* Separators */
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 40px 0;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #6c757d;
            font-size: 12px;
        }}
        
        /* Highlights */
        .highlight {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        
        .success {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        
        .info {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        
        /* Page breaks */
        .page-break {{
            page-break-before: always;
        }}
        
        @media print {{
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <!-- Capa -->
    <div class="cover-page">
        <div class="cover-logo">🚀</div>
        <h1 class="cover-title">Sistema Creative API</h1>
        <p class="cover-subtitle">{doc_type}</p>
        <div class="cover-date">{today}</div>
        <div class="cover-version">Versão 1.0.0</div>
    </div>
    
    <!-- Conteúdo -->
    <div class="content">
        {content}
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <p>Sistema Creative API - Automação de Conteúdo SEO</p>
        <p>Gerado em {today}</p>
    </div>
</body>
</html>
"""
    
    return html_template

def process_document(md_file, output_file, doc_title, doc_type):
    """Processa um documento markdown para HTML"""
    print(f"📄 Processando {md_file}...")
    
    # Ler conteúdo
    md_content = read_markdown_file(md_file)
    
    if not md_content:
        print(f"❌ Erro ao ler {md_file}")
        return None
    
    # Converter para HTML
    html_content = markdown_to_html_simple(md_content)
    
    # Criar HTML completo
    full_html = create_professional_html(html_content, doc_title, doc_type)
    
    # Criar diretório se não existir
    os.makedirs('docs_html', exist_ok=True)
    
    # Salvar arquivo
    output_path = os.path.join('docs_html', output_file)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ HTML gerado: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erro ao salvar {output_file}: {str(e)}")
        return None

def create_combined_document():
    """Cria documento único com toda documentação"""
    print("📚 Gerando documentação completa...")
    
    # Ler todos os documentos
    readme_content = read_markdown_file('README_CLIENTE.md')
    exec_content = read_markdown_file('APRESENTACAO_EXECUTIVA.md')
    doc_content = read_markdown_file('DOCUMENTACAO_SISTEMA.md')
    tech_content = read_markdown_file('ESPECIFICACOES_TECNICAS.md')
    
    # Combinar conteúdos
    combined_content = f"""
# 📚 Documentação Completa do Sistema

## Índice
1. [Resumo Executivo](#resumo)
2. [Apresentação Comercial](#apresentacao)  
3. [Documentação Técnica](#documentacao)
4. [Especificações](#especificacoes)

---

<div id="resumo" class="page-break">

{readme_content}

</div>

---

<div id="apresentacao" class="page-break">

{exec_content}

</div>

---

<div id="documentacao" class="page-break">

{doc_content}

</div>

---

<div id="especificacoes" class="page-break">

{tech_content}

</div>
"""
    
    # Converter para HTML
    html_content = markdown_to_html_simple(combined_content)
    
    # Criar HTML completo
    full_html = create_professional_html(
        html_content, 
        "Sistema Creative API - Documentação Completa",
        "Documentação Completa e Especificações Técnicas"
    )
    
    # Salvar arquivo
    os.makedirs('docs_html', exist_ok=True)
    output_path = os.path.join('docs_html', 'Sistema_Creative_API_Documentacao_Completa.html')
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ Documentação completa gerada: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erro ao gerar documentação completa: {str(e)}")
        return None

def main():
    """Função principal"""
    print("🚀 Sistema Creative API - Gerador de Documentos HTML")
    print("=" * 60)
    
    documents = [
        ('README_CLIENTE.md', 'Sistema_Creative_API_Resumo.html', 'Resumo Executivo', 'Resumo Executivo'),
        ('APRESENTACAO_EXECUTIVA.md', 'Sistema_Creative_API_Apresentacao.html', 'Apresentação Comercial', 'Apresentação Comercial'),
        ('DOCUMENTACAO_SISTEMA.md', 'Sistema_Creative_API_Documentacao.html', 'Documentação Completa', 'Documentação Técnica'),
        ('ESPECIFICACOES_TECNICAS.md', 'Sistema_Creative_API_Especificacoes.html', 'Especificações Técnicas', 'Especificações Técnicas')
    ]
    
    generated_files = []
    
    # Gerar documentos individuais
    print("\n📋 Gerando documentos individuais...")
    for md_file, html_file, doc_title, doc_type in documents:
        result = process_document(md_file, html_file, doc_title, doc_type)
        if result:
            generated_files.append(result)
    
    # Gerar documento combinado
    print("\n📚 Gerando documento completo...")
    combined_doc = create_combined_document()
    if combined_doc:
        generated_files.append(combined_doc)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("✅ GERAÇÃO CONCLUÍDA!")
    print("=" * 60)
    
    if generated_files:
        print("📄 Arquivos HTML gerados:")
        for file_path in generated_files:
            print(f"   📄 {file_path}")
    
    print("\n💡 COMO CONVERTER PARA PDF:")
    print("1. Abra os arquivos HTML no navegador")
    print("2. Pressione Ctrl+P (Imprimir)")
    print("3. Selecione 'Salvar como PDF'")
    print("4. Configure margens e layout se necessário")
    print("5. Clique em 'Salvar'")
    
    print(f"\n📁 Todos os arquivos estão na pasta: docs_html/")
    print("🎉 Pronto para converter para PDF e enviar ao cliente!")

if __name__ == "__main__":
    main() 