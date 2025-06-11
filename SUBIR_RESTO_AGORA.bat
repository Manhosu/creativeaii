@echo off
echo SUBINDO O RESTO DOS ARQUIVOS PARA GITHUB!
echo =========================================
cd /d "%~dp0"
echo Verificando status...
git status
echo.
echo Adicionando TODOS os arquivos restantes...
git add .
git add -A
echo.
echo Fazendo commit completo...
git commit -m "COMMIT FINAL - TODOS os arquivos M e U incluidos - Sistema Creative API 100% completo"
echo.
echo Fazendo push para MASTER (nao main)...
git push origin master
echo.
echo ========================================
echo     ✅ TUDO COMMITADO E NO GITHUB!
echo ========================================
pause 