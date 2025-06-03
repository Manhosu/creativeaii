## 🎯 Objetivo do Projeto

Criar um sistema automatizado que:

1. Acesse URLs de categorias do site (ex: https://www.creativecopias.com.br/impressoras)
2. Identifique produtos listados e novos que ainda não foram processados
3. Gere artigos otimizados para SEO com base nas informações dos produtos
4. Permita revisão humana antes da publicação
5. Publique os textos automaticamente via API do WordPress
6. Possua painel para configurar URLs de categorias, preferências e ajustes de conteúdo

---

## ✅ Tarefas Iniciais

### 1. Estrutura do Projeto
- [ ] Criar estrutura básica do projeto com organização modular
  - `/src`
  - `/src/scraper` (scraping das páginas)
  - `/src/generator` (geração de conteúdo)
  - `/src/review` (painel ou repositório local dos posts)
  - `/src/publisher` (integração com WordPress via API)
  - `/src/config` (URLs, palavras-chave, instruções manuais)
  - `/src/scheduler` (agendador diário ou semanal)
  - `/src/logger` (logs de erros e eventos)
- [ ] Criar o arquivo `README.md` com a explicação do projeto e dependências
- [ ] Criar o arquivo `CHECKLIST.md` com tarefas detalhadas do projeto (veja modelo abaixo)

### 2. Ambiente
- [ ] Escolher e configurar ambiente em Python (FastAPI ou CLI)
- [ ] Adicionar arquivo `requirements.txt` ou `pyproject.toml`
- [ ] Criar `.env.example` com variáveis sensíveis (ex: URL do site, chave da API WordPress)

---

## 🧾 Checklist.md (modelo inicial)

```markdown
# ✅ Checklist do Projeto: Sistema de Geração Automática de Conteúdo SEO

## Etapas Iniciais
- [ ] Estrutura de pastas criada
- [ ] Dependências instaladas
- [ ] Ambiente de variáveis configurado
- [ ] README.md documentado

## Funcionalidades Principais
- [ ] Scraper funcionando para uma URL de categoria
- [ ] Identificação de novos produtos com hash ou ID
- [ ] Geração de texto com IA (simulada ou real)
- [ ] Exportação para painel de revisão ou pasta local
- [ ] Publicação via API WordPress (modo rascunho)
- [ ] Painel para gerenciar URLs e configurações
- [ ] Agendador de tarefas automáticas (cron)
- [ ] Logs de erros e sucesso

## Expansões Futuras
- [ ] Instruções manuais por categoria
- [ ] Painel web com login
- [ ] Pontuação de originalidade

> Atualize este checklist a cada entrega concluída.
