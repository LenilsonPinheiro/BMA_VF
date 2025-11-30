@echo off
echo.
echo =================================================
echo      SCRIPT DE MIGRACAO DO BANCO DE DADOS
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

REM Sincroniza o banco de dados com o historico de migracoes
echo.
echo --- PASSO 1: Sincronizando historico do banco de dados ---
flask db stamp head
if %errorlevel% neq 0 (
    echo ERRO: Falha ao sincronizar o banco de dados.
    pause
    exit /b
)

REM Gera o arquivo de migracao
echo.
echo --- PASSO 2: Gerando arquivo de migracao (se necessario) ---
flask db migrate -m "Add color fields to ThemeSettings"
if %errorlevel% neq 0 (
    echo AVISO: Falha ao gerar nova migracao. Isso pode ser normal se nenhuma alteracao for detectada.
)

REM Aplica a migracao ao banco de dados
echo.
echo --- PASSO 3: Aplicando migracoes pendentes (se houver) ---
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