@echo off
REM Script generico para executar migracoes do Flask-Migrate.
REM Uso: migrate.bat "Sua mensagem de migracao aqui" (ASPAS SAO OBRIGATORIAS se a mensagem tiver espacos)

if [%1]==[] (
    echo ERRO: Por favor, forneca uma mensagem para a migracao entre aspas.
    echo Exemplo: migrate.bat "Adiciona campo de biografia para equipe"
    pause
    exit /b
)

echo.
echo =================================================
echo      EXECUTANDO MIGRACAO DO BANCO DE DADOS
echo =================================================
echo.

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
echo.
echo --- PASSO 1: Aplicando migracoes pendentes (se houver)... ---
flask db upgrade
if %errorlevel% neq 0 (
    echo ERRO: Falha ao atualizar o banco de dados para a ultima versao.
    pause
    exit /b
)

REM Gera o arquivo de migracao
echo.
echo --- PASSO 2: Gerando novo arquivo de migracao... ---
flask db migrate -m "%~1"
if %errorlevel% neq 0 (
    echo AVISO: Nenhuma alteracao detectada nos modelos. Nenhuma nova migracao foi criada.
)

REM Aplica a migracao ao banco de dados
echo.
echo --- PASSO 3: Aplicando a nova migracao (se foi criada)... ---
flask db upgrade
if %errorlevel% neq 0 (
    echo ERRO: Falha ao aplicar a migracao.
    pause
    exit /b
)

echo.
echo =================================================
echo      MIGRACAO CONCLUIDA COM SUCESSO!
echo =================================================
echo.
pause
