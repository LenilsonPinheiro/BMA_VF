@echo off
echo ========================================
echo  Deploy para Google Cloud Platform
echo  Belarmino Monteiro Advogado
echo ========================================
echo.

REM Verificar se gcloud está instalado
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Google Cloud SDK nao encontrado!
    echo.
    echo Por favor, instale o Google Cloud SDK:
    echo https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)

echo [INFO] Google Cloud SDK encontrado!
echo.

REM Verificar se está logado
echo [INFO] Verificando autenticacao...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Nao esta autenticado no Google Cloud
    echo [INFO] Fazendo login...
    gcloud auth login
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao fazer login
        pause
        exit /b 1
    )
)

echo [OK] Autenticado com sucesso!
echo.

REM Verificar projeto configurado
echo [INFO] Verificando projeto...
for /f "delims=" %%i in ('gcloud config get-value project 2^>nul') do set PROJECT_ID=%%i

if "%PROJECT_ID%"=="" (
    echo [AVISO] Nenhum projeto configurado
    echo.
    set /p PROJECT_ID="Digite o ID do projeto (ex: belarmino-monteiro-advogado): "
    gcloud config set project %PROJECT_ID%
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao configurar projeto
        pause
        exit /b 1
    )
)

echo [OK] Projeto: %PROJECT_ID%
echo.

REM Verificar SECRET_KEY
echo [INFO] Verificando SECRET_KEY no app.yaml...
findstr /C:"MUDE-ESTA-CHAVE" BelarminoMonteiroAdvogado\app.yaml >nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  [AVISO] SECRET_KEY NAO CONFIGURADA!
    echo ========================================
    echo.
    echo A SECRET_KEY ainda esta com o valor padrao.
    echo Por seguranca, voce deve gerar uma nova chave.
    echo.
    echo Execute no Python:
    echo   import secrets
    echo   print(secrets.token_hex(32))
    echo.
    echo E cole o resultado no arquivo:
    echo   BelarminoMonteiroAdvogado\app.yaml
    echo.
    set /p CONTINUAR="Deseja continuar mesmo assim? (S/N): "
    if /i not "%CONTINUAR%"=="S" (
        echo Deploy cancelado.
        pause
        exit /b 0
    )
)

echo.
echo ========================================
echo  Iniciando Deploy
echo ========================================
echo.
echo [INFO] Fazendo deploy da aplicacao...
echo [INFO] Isso pode levar alguns minutos...
echo.

gcloud app deploy --quiet

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  [SUCESSO] Deploy Concluido!
    echo ========================================
    echo.
    echo Sua aplicacao esta disponivel em:
    for /f "delims=" %%i in ('gcloud app describe --format="value(defaultHostname)" 2^>nul') do set APP_URL=%%i
    echo https://%APP_URL%
    echo.
    set /p ABRIR="Deseja abrir o site no navegador? (S/N): "
    if /i "%ABRIR%"=="S" (
        gcloud app browse
    )
    echo.
    echo Proximos passos:
    echo 1. Configure o dominio personalizado
    echo 2. Verifique os logs: gcloud app logs tail -s default
    echo 3. Monitore em: https://console.cloud.google.com/appengine
    echo.
) else (
    echo.
    echo ========================================
    echo  [ERRO] Deploy Falhou!
    echo ========================================
    echo.
    echo Verifique os logs para mais detalhes:
    echo   gcloud app logs tail -s default
    echo.
    echo Ou acesse o console:
    echo   https://console.cloud.google.com/appengine
    echo.
)

pause
