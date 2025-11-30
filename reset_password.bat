@echo off
REM Script para resetar a senha do administrador do site NetPalm.

echo.
echo =================================================
echo      RESET DE SENHA DO ADMINISTRADOR
echo =================================================
echo.

REM Muda para o diretorio onde o script esta localizado
cd /d "%~dp0"

echo Ativando ambiente virtual...
call .\venv\Scripts\activate

echo Configurando aplicacao Flask...
set FLASK_APP=BelarminoMonteiroAdvogado

echo.
echo Executando o comando de reset de senha...
echo Siga as instrucoes no terminal para definir a nova senha.
echo.

flask reset-password

echo.
echo =================================================
echo      PROCESSO CONCLUIDO
echo =================================================
echo.
pause