@echo off
echo.
echo =================================================
echo      INICIANDO LIMPEZA E REORGANIZACAO DO PROJETO
echo =================================================
echo.
cd /d "%~dp0"

echo --- FASE 1: Limpeza de Arquivos ---

echo [1.1] Removendo arquivos obsoletos da raiz...
IF EXIST "BelarminoMonteiroAdvogado.py" ( del "BelarminoMonteiroAdvogado.py" & echo  - Removido: BelarminoMonteiroAdvogado.py )

echo [1.2] Removendo diretorios duplicados...
IF EXIST "static" ( rmdir /s /q "static" & echo  - Removido: pasta 'static' da raiz )

echo [1.3] Removendo arquivos mal posicionados...
IF EXIST "BelarminoMonteiroAdvogado\app.py" ( del "BelarminoMonteiroAdvogado\app.py" & echo  - Removido: BelarminoMonteiroAdvogado\app.py )

echo.
echo --- FASE 2: Consolidacao ---
echo [2.1] Removendo .gitignore duplicado...
IF EXIST "BelarminoMonteiroAdvogado\.gitignore" ( del "BelarminoMonteiroAdvogado\.gitignore" & echo  - Removido: BelarminoMonteiroAdvogado\.gitignore )

echo.
echo =================================================
echo      LIMPEZA CONCLUIDA!
echo =================================================
echo.
