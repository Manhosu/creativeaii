@echo off
echo SUBINDO TUDO PARA GITHUB AGORA!!!
echo ================================
cd /d "%~dp0"
git add .
git add -A
git commit -m "COMMIT COMPLETO - Todos arquivos M e U incluidos - Sistema 100% funcional"
git push origin main
echo CONCLUIDO! Tudo no GitHub!
pause 