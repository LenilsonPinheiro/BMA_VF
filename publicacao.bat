@echo off
rem ============================================================================
rem SCRIPT DE PUBLICAÇÃO AUTOMATIZADO
rem Belarmino Monteiro Advocacia
rem
rem Este script realiza o deploy da aplicação para o Google App Engine.
rem
rem USO:
rem   publicacao.bat [PROJECT_ID]
rem
rem Onde [PROJECT_ID] é o ID do seu projeto no Google Cloud.
rem Se não for fornecido, o script usará o projeto configurado no gcloud.
rem ============================================================================

echo.
echo [BMA-DEPLOY] - INICIANDO SCRIPT DE PUBLICACAO
echo.

rem Verifica se o gcloud CLI está instalado
gcloud --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Google Cloud SDK (gcloud) nao encontrado.
    echo Instale-o e configure-o antes de continuar.
    goto:eof
)

rem Define o ID do projeto
set PROJECT_ID=%1
if not defined PROJECT_ID (
    echo [AVISO] ID do projeto nao fornecido. Usando o projeto atualmente configurado no gcloud.
) else (
    echo [INFO] Configurando o projeto para: %PROJECT_ID%
    gcloud config set project %PROJECT_ID%
)

echo.
echo [INFO] Iniciando o deploy para o App Engine...
echo.

rem Executa o deploy
gcloud app deploy BelarminoMonteiroAdvogado/app.yaml --promote --stop-previous-version

echo.
echo [INFO] Deploy finalizado.
echo Verifique o status no Console do Google Cloud.
echo.

pause
