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

REM ====================================================================
REM MELHORIA 1: Validação de Dependências
REM ====================================================================

echo [INFO] Verificando dependencias...
echo.

REM Verifica se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo [ERRO] Por favor, crie o ambiente virtual executando: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Verifica se o script Python existe
if not exist "deploy_production_complete.py" (
    echo [ERRO] Script deploy_production_complete.py nao encontrado!
    echo [ERRO] Certifique-se de estar no diretorio correto do projeto.
    echo.
    pause
    exit /b 1
)

echo [OK] Todas as dependencias encontradas.
echo.

REM ====================================================================
REM MELHORIA 2: Log de Execução com Timestamp
REM ====================================================================

REM Cria diretório de logs se não existir
if not exist "logs" mkdir logs

REM Gera timestamp para o log
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set LOG_DATE=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
set LOG_TIME=%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%
set LOG_FILE=logs\deploy_%LOG_DATE%_%LOG_TIME%.log

echo [INFO] Log da execucao sera salvo em: %LOG_FILE%
echo.
echo ================================================== >> %LOG_FILE%
echo DEPLOY INICIADO EM: %LOG_DATE% %LOG_TIME:~0,2%:%LOG_TIME:~3,2%:%LOG_TIME:~6,2% >> %LOG_FILE%
echo ================================================== >> %LOG_FILE%
echo. >> %LOG_FILE%

echo [INFO] Ativando ambiente virtual e executando script Python...
echo.

REM Chama o script Python usando o ambiente virtual para garantir consistência.
call venv\Scripts\activate.bat

REM Executa o script e captura a saída no log mantendo exibição na tela
python deploy_production_complete.py 2>&1 | powershell -Command "ForEach-Object { Write-Host $_; Add-Content -Path '%LOG_FILE%' -Value $_ }"

REM Captura o código de retorno do script Python
set DEPLOY_EXIT_CODE=%ERRORLEVEL%

REM Registra o resultado no log
echo. >> %LOG_FILE%
echo ================================================== >> %LOG_FILE%
if %DEPLOY_EXIT_CODE% EQU 0 (
    echo DEPLOY CONCLUIDO COM SUCESSO >> %LOG_FILE%
    echo [SUCESSO] Deploy finalizado com sucesso! >> %LOG_FILE%
    echo.
    echo [SUCESSO] Deploy finalizado com sucesso!
) else (
    echo DEPLOY FALHOU COM CODIGO: %DEPLOY_EXIT_CODE% >> %LOG_FILE%
    echo [ERRO] Deploy falhou com codigo de erro: %DEPLOY_EXIT_CODE% >> %LOG_FILE%
    echo.
    echo [ERRO] Deploy falhou com codigo de erro: %DEPLOY_EXIT_CODE%
)
echo ================================================== >> %LOG_FILE%
echo.
echo [INFO] Log completo disponivel em: %LOG_FILE%
echo.

pause
exit /b %DEPLOY_EXIT_CODE%
