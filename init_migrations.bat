@echo off
echo.
echo =================================================
echo      INICIALIZANDO O AMBIENTE DE MIGRACOES
echo =================================================
echo.

REM Muda para o diretorio onde o script esta localizado
cd /d "%~dp0"

REM Remove a pasta de migracoes antiga, se existir, para garantir um inicio limpo
IF EXIST "migrations" (
    echo Removendo pasta de migracoes antiga...
    rmdir /s /q migrations
)

echo Ativando ambiente virtual...
call .\\venv\\Scripts\\activate

echo Configurando aplicacao Flask...
set FLASK_APP=BelarminoMonteiroAdvogado

echo.
echo --- Executando 'flask db init' para criar a pasta de migracoes ---
flask db init

echo.
echo =================================================
echo      AMBIENTE DE MIGRACOES INICIALIZADO!
echo =================================================
echo Agora voce pode criar sua primeira migracao com: migrate.bat "Sua mensagem"
echo.
pause