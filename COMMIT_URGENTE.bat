@echo off
echo 🚨 COMMIT URGENTE - CORREÇÕES CRÍTICAS
echo =====================================
cd /d "%~dp0"

echo [1] Adicionando arquivos...
git add .
git add -A

echo [2] Fazendo commit urgente...
git commit -m "🚨 CORREÇÕES URGENTES - Problemas críticos resolvidos

✅ PROBLEMAS CORRIGIDOS:
- ✅ Removido botões Limpar e Gerador da interface scraper
- ✅ Corrigido imports do ActiveCategoriesManager (parcial)
- ✅ Sistema preparado para funcionamento completo

🔧 EM ANDAMENTO:
- Correção completa dos imports restantes
- Remoção de seções desnecessárias das configurações

📊 STATUS: Sistema parcialmente corrigido, continuando correções..."

echo [3] Fazendo push...
git push origin master

echo ✅ COMMIT URGENTE CONCLUÍDO!
echo Continuando com as correções restantes...
pause 