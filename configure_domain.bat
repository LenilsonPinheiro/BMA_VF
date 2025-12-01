@echo off
setlocal enabledelayedexpansion

echo =================================================
echo      CONFIGURADOR DE DOMINIO - GOOGLE CLOUD
echo =================================================
echo.

REM --- PASSO 1: Obter o nome do dominio ---
set /p DOMAIN_NAME="Digite o dominio que deseja configurar (ex: seudominio.com.br): "
if "%DOMAIN_NAME%"=="" (
    echo [ERRO] Nenhum dominio foi digitado.
    pause
    exit /b 1
)

echo.
echo [INFO] Iniciando configuracao para: %DOMAIN_NAME%
echo.

REM --- PASSO 2: Tentar criar o mapeamento de dominio ---
echo [INFO] Tentando criar o mapeamento no App Engine...
gcloud app domain-mappings create %DOMAIN_NAME% > domain_mapping_output.txt 2>&1

REM --- PASSO 3: Verificar se o dominio precisa de verificacao ---
findstr /C:"domain is not verified" domain_mapping_output.txt >nul
if %ERRORLEVEL% EQU 0 (
    echo [AVISO] O dominio precisa ser verificado.
    echo.
    echo [INFO] Buscando o registro de verificacao necessario...
    
    REM Comando para obter o registro TXT de verificacao
    for /f "tokens=*" %%a in ('gcloud domains verifications verify --domain-name=%DOMAIN_NAME% --format="value(resource.data)" 2^>nul') do set TXT_RECORD=%%a

    if "!TXT_RECORD!"=="" (
        echo [ERRO] Nao foi possivel obter o registro de verificacao automaticamente.
        echo Por favor, siga as instrucoes no Google Cloud Console:
        echo https://console.cloud.google.com/appengine/settings/custom-domains
        del domain_mapping_output.txt
        pause
        exit /b 1
    )

    echo.
    echo ====================================================================
    echo      ACAO NECESSARIA: Adicione este registro no seu DNS
    echo ====================================================================
    echo.
    echo Acesse o painel do seu provedor de dominio (Registro.br) e crie
    echo um novo registro DNS com os seguintes valores:
    echo.
    echo   - Tipo: TXT
    echo   - Nome/Host: @ (ou deixe em branco, dependendo do provedor)
    echo   - Valor/Conteudo: !TXT_RECORD!
    echo.
    echo ====================================================================
    echo.
    echo Apos adicionar o registro, aguarde alguns minutos para a propagacao.
    pause

    echo.
    echo [INFO] Tentando criar o mapeamento novamente apos a verificacao...
    gcloud app domain-mappings create %DOMAIN_NAME%
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar o mapeamento. Verifique se o registro TXT foi
        echo adicionado corretamente e tente executar este script novamente.
        del domain_mapping_output.txt
        pause
        exit /b 1
    )
)

del domain_mapping_output.txt

echo.
echo [SUCESSO] Mapeamento de dominio criado!
echo.

REM --- PASSO 4: Exibir os registros DNS finais ---
echo ====================================================================
echo      ACAO FINAL: Adicione os seguintes registros DNS
echo ====================================================================
echo.
echo No painel do seu provedor de dominio (Registro.br), adicione:
echo.
echo 1. Para o dominio principal (%DOMAIN_NAME%):
echo    Adicione os seguintes registros do tipo A e AAAA.
echo.
echo    Tipo | Nome | Valor
echo    -----|------|-----------------------
echo    A    | @    | 216.239.32.21
echo    A    | @    | 216.239.34.21
echo    A    | @    | 216.239.36.21
echo    A    | @    | 216.239.38.21
echo    AAAA | @    | 2001:4860:4802:32::15
echo    AAAA | @    | 2001:4860:4802:34::15
echo    AAAA | @    | 2001:4860:4802:36::15
echo    AAAA | @    | 2001:4860:4802:38::15
echo.
echo 2. Para o subdominio 'www' (www.%DOMAIN_NAME%):
echo.
echo    Tipo  | Nome | Valor
echo    ------|------|----------------------
echo    CNAME | www  | ghs.googlehosted.com
echo.
echo ====================================================================
echo.
echo Apos adicionar estes registros, pode levar algumas horas para que
echo seu site fique disponivel no novo dominio.
echo.
pause