# 📖 MANUAL DO USUÁRIO - SISTEMA CREATIVE API

> **📋 MANUAL ÚNICO E COMPLETO - TUDO O QUE VOCÊ PRECISA SABER**

## 🔗 **ACESSE O SISTEMA:**
**Link:** https://creativeaii.onrender.com/

## 🎯 **O QUE É ESTE SISTEMA?**

Este sistema **gera artigos automaticamente** para seu blog WordPress sobre produtos da sua loja online. 

**Em palavras simples:** Você tem produtos → O sistema cria textos sobre eles → Publica no seu blog automaticamente.

---

## 🚀 **COMO COMEÇAR (PASSO A PASSO)**

### **1️⃣ PRIMEIRO ACESSO**

1. Abra seu navegador (Chrome, Firefox, etc.)
2. Digite o endereço do sistema: **https://creativeaii.onrender.com/**
3. Você verá a tela inicial com os 2 botões principais

## 📦 **COMO USAR O SISTEMA**

> **🎯 PRODUTOS JÁ ESTÃO NO SISTEMA!** Você pode começar gerando artigos imediatamente.

### **PASSO 1: VER PRODUTOS E GERAR ARTIGOS**

1. **Clique em "Scraper"** 
2. **Veja a lista de produtos** já carregados no sistema
3. **Clique em "✨ Gerar Artigo"** ao lado do produto desejado
4. **Aguarde** (1-2 minutos) - a IA está escrevendo o artigo

### **PASSO 2: REVISAR O ARTIGO**

1. **Leia o artigo** gerado pela IA
2. **Edite apenas o título** se necessário
3. **Escolha uma das opções:**
   - **✅ "Aprovar e Publicar"** → Artigo vai para o seu blog
   - **❌ "Rejeitar"** → Explique o motivo da rejeição

### **PASSO 3: SISTEMA INTELIGENTE**

- **Se aprovar:** Artigo é publicado automaticamente no WordPress
- **Se rejeitar:** A IA aprende com sua explicação e evita o mesmo erro nos próximos artigos

---

## 🎛️ **PRINCIPAIS BOTÕES E O QUE FAZEM**

> **🎯 O SISTEMA TEM APENAS 2 BOTÕES PRINCIPAIS:**

### **🕷️ Scraper** 
- Mostra produtos já carregados no sistema
- Lista produtos disponíveis para gerar artigos
- Local onde você gera novos artigos

### **⚙️ Configurações**
- Configura conexão com WordPress
- Ajusta configurações do sistema
- Visualiza agenda automática

---

## ⏰ **SISTEMA AUTOMÁTICO**

### **O QUE ACONTECE SOZINHO:**

1. **Todo domingo às 10h:** Sistema atualiza produtos (busca novos e remove antigos)
2. **Todo domingo às 10h15:** Sistema gera artigos automaticamente dos produtos atualizados

> **📋 IMPORTANTE:** Os produtos já estão carregados! Domingo é só para manter tudo atualizado.


## 💡 **DICAS IMPORTANTES**

### **✅ FAÇA SEMPRE:**
- Explique claramente quando rejeitar um artigo

### **❌ NÃO FAÇA:**
- Não rejeite sem explicar o motivo
- Nas primeiras 2 semanas de uso, nao adicione ou remova categorias nas configurações, pois o sistema ainda esta fazendo a leitura total das categorias existentes

### **🧠 SISTEMA INTELIGENTE:**
- Quando você rejeita um artigo e explica o motivo, a IA aprende
- Nos próximos artigos, ela evitará cometer o mesmo erro
- Quanto mais você usar, melhor ela fica!

# CORREÇÃO FINALIZADA: Contagens de Produtos Corrigidas Completamente ✅

## 🎯 **PROBLEMA RESOLVIDO**
**Data:** 23/06/2025 17:30  
**Usuário reportou:** "preciso que mostre a quantidade real de produtos em todos os lugares"

### ❌ **SITUAÇÃO PROBLEMÁTICA ANTERIOR**
- **Dashboard:** 558 produtos (correto)
- **Lista de produtos:** 680 produtos (INCORRETO)
- **Categorias:** 680 produtos (INCORRETO)
- **Total de inconsistências:** 2 de 3 interfaces

## ✅ **SITUAÇÃO APÓS CORREÇÃO**
**TODAS AS INTERFACES MOSTRAM 558 PRODUTOS ÚNICOS**

### 🔧 **CORREÇÕES APLICADAS**

#### **1. Endpoint `/scraper/products` - src/main.py**
**Problema:** Contava TODOS os produtos de TODOS os arquivos, incluindo duplicatas

**Antes:**
```python
total_products = len(all_products)  # ❌ Incluía duplicatas
```

**Depois:**
```python
# Identificar arquivos únicos (preferir _CORRIGIDO)
unique_products = set()  # ✅ Contar produtos únicos
for product in all_products:
    if product.get('nome'):
        unique_products.add(product['nome'])

total_products_unique = len(unique_products)  # ✅ Usar contagem única
```

#### **2. ActiveCategoriesManager - src/config/active_categories_manager.py**
**Problema:** Sistema de atualização de contagens também incluía duplicatas

**Correção:**
```python
# 🚨 CORREÇÃO: Usar mesma lógica para evitar duplicatas
category_files = {}

# Primeiro, identificar arquivos únicos (preferir _CORRIGIDO)
for file_path in products_dir.glob("products_*.json"):
    if 'CORRIGIDO' in file_name:
        category_files[category_slug] = file_path  # ✅ Prioridade
    elif category_slug not in category_files:
        category_files[category_slug] = file_path  # ✅ Primeiro único

# Contar produtos únicos por nome em cada arquivo
unique_products = set()
for product in data['produtos']:
    if product.get('nome'):
        unique_products.add(product['nome'])  # ✅ Sem duplicatas
```

### 📊 **RESULTADOS FINAIS**

| Interface | Antes | Depois | Status |
|-----------|-------|--------|--------|
| Dashboard (`/scraper/stats`) | 558 | 558 | ✅ Sempre correto |
| Lista (`/scraper/products`) | 680 | 558 | ✅ **CORRIGIDO** |
| Categorias (`/scraper/categories`) | 680 | 558 | ✅ **CORRIGIDO** |

### 🎉 **CONFIRMAÇÃO FINAL**
- ✅ **100% das interfaces** mostram 558 produtos únicos
- ✅ **Eliminação completa** de duplicatas na contagem
- ✅ **Consistência total** entre todas as telas
- ✅ **Sistema robusto** que prioriza arquivos `_CORRIGIDO`

### 🔍 **CAUSA RAIZ DOS 680 PRODUTOS**
O sistema estava contando:
- Arquivo original: `products_cartuchos-de-tinta_20250616.json` (100 produtos)
- Arquivo corrigido: `products_cartuchos-de-tinta_20250616_CORRIGIDO.json` (100 produtos)
- Arquivo recente: `products_cartuchos-de-tinta_20250623.json` (100 produtos)
- **Total incorreto:** 300 produtos da mesma categoria!

### 🛡️ **SISTEMA ANTI-DUPLICAÇÃO IMPLEMENTADO**
1. **Priorização:** Arquivos `_CORRIGIDO` têm prioridade absoluta
2. **Unicidade:** Apenas um arquivo por categoria é considerado
3. **Contagem única:** Produtos são contados por nome único, não por linha
4. **Consistência:** Todos os endpoints usam a mesma lógica

---

**🎯 MISSÃO CUMPRIDA:** Sistema agora mostra a quantidade real de produtos (558) em **TODOS** os lugares!