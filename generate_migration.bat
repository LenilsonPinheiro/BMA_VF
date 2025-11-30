@echo off
echo.
echo =================================================
echo      GERADOR DE MIGRACAO DE BANCO DE DADOS
echo =================================================
echo.

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call .\venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel ativar o ambiente virtual.
    pause
    exit /b
)

REM Configura a aplicacao Flask
echo Configurando aplicacao Flask...
set FLASK_APP=BelarminoMonteiroAdvogado

REM Gera o arquivo de migracao
echo.
echo --- Gerando arquivo de migracao ---
flask db migrate -m "%~1"
if %errorlevel% neq 0 (
    echo ERRO: Falha ao gerar nova migracao.
    pause
    exit /b
)

echo.
echo =================================================
echo      MIGRACAO GERADA COM SUCESSO!
echo =================================================
echo.
pause
