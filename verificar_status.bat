@echo off
echo ========================================
echo      VERIFICANDO STATUS DO GIT
echo ========================================
cd /d "%~dp0"
echo.
echo [1] Status dos arquivos:
git status
echo.
echo [2] Ultimos commits:
git log --oneline -5
echo.
echo [3] Branch atual:
git branch
echo.
echo ========================================
echo Se aparecer "working tree clean" = SUCESSO!
echo ========================================
pause 