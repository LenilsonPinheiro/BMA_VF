@echo off
REM =================================================================
REM      SCRIPT PRINCIPAL PARA AMBIENTE DE DESENVOLVIMENTO
REM =================================================================
REM Este script prepara o ambiente e inicia o servidor em modo DEBUG.
REM Nao apaga o banco de dados existente.
REM =================================================================

cd /d "%~dp0"

echo Verificando ambiente virtual...
IF NOT EXIST ".\venv\" (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call .\venv\Scripts\activate

echo Instalando/Atualizando dependencias do requirements.txt...
pip install -r requirements.txt

echo Configurando aplicacao Flask...
set FLASK_APP=BelarminoMonteiroAdvogado
set FLASK_DEBUG=1

echo Iniciando o servidor de desenvolvimento em modo DEBUG...
echo As alteracoes em arquivos .py e .html serao recarregadas automaticamente.
echo Acesse o site em http://127.0.0.1:5000

python -m flask run