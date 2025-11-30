@echo off
echo.
echo =================================================
echo      RESETANDO E POPULANDO O BANCO DE DADOS
echo =================================================
echo.

REM Apaga o banco de dados antigo, se existir
IF EXIST .\\instance\\site.db (
    echo Removendo banco de dados antigo...
    del .\\instance\\site.db
)

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call .\\venv\\Scripts\\activate
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel ativar o ambiente virtual.
    pause
    exit /b
)

REM Configura a aplicacao Flask
echo Configurando aplicacao Flask...
set FLASK_APP=BelarminoMonteiroAdvogado

REM Executa o comando para inicializar e popular o banco de dados
echo.
echo --- Populando o banco de dados com dados padrao ---
flask init-db
if %errorlevel% neq 0 (
    echo ERRO: Falha ao popular o banco de dados.
    pause
    exit /b
)

echo.
echo =================================================
echo      BANCO DE DADOS RESETADO COM SUCESSO!
echo =================================================
echo.
echo Voce pode iniciar o site com o comando: dev.bat
pause
