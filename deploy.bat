@echo off
REM ====================================================================
REM deploy.bat - Atalho para o Orquestrador de Deploy em Python
REM Este script simplesmente executa o `deploy_production_complete.py`,
REM que contém toda a lógica de deploy, testes e validação.
REM ====================================================================

echo ========================================
echo  INICIANDO ORQUESTRADOR DE DEPLOY
echo  Belarmino Monteiro Advogado
echo ========================================
echo.

echo [INFO] Ativando ambiente virtual e executando script Python...
echo.

REM Chama o script Python usando o ambiente virtual para garantir consistência.
call venv\Scripts\activate.bat
python deploy_production_complete.py

pause
