# run.ps1
# Script para iniciar a aplicação Flask, gerenciar ambiente e banco de dados.

# Configurações iniciais
$ErrorActionPreference = "Stop" # Interrompe o script em caso de erro
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# --- Initial Setup and Logging ---
# All logging to run_log.txt will now be handled by auto_fix.py.
# Console output for high-level steps.

Write-Host "[INFO] run.ps1 iniciado. Checando o ambiente..."

# --- Ensure and Activate Virtual Environment ---
Write-Host "[INFO] Verificando e ativando ambiente virtual..."
$venvDir = Join-Path $scriptDir "venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $venvDir)) {
    Write-Host "[WARN] Pasta 'venv' não encontrada. Criando novo ambiente virtual..."
    try {
        python -m venv $venvDir
        Write-Host "[SUCESSO] Ambiente virtual 'venv' criado com sucesso."
    } catch {
        Write-Host "[ERROR] Falha ao criar o ambiente virtual. Verifique se o Python está no PATH."
        exit 1
    }
}

# --- Ativa o ambiente virtual para a sessão atual do PowerShell ---
. (Join-Path $venvDir "Scripts\Activate.ps1")
Write-Host "[INFO] Ambiente virtual ativado. Usando Python de: $($venvPython)"

# Define o ponto de entrada da aplicação Flask.
$env:FLASK_APP = "BelarminoMonteiroAdvogado"

# --- Install Dependencies ---
Write-Host "[INFO] Instalando/Atualizando dependencias Python..."

$requirementsPath = Join-Path $scriptDir "requirements.txt"
if (Test-Path $requirementsPath) {
    try {
        # Primeiro, atualiza as ferramentas de build dentro do venv para evitar erros de compilação
        Write-Host "[INFO] Atualizando pip, setuptools e wheel..."
        & $venvPython -m pip install --upgrade pip
        Write-Host "[SUCESSO] Ferramentas de build atualizadas."

        # Agora, instala as dependências do projeto
        Write-Host "[INFO] Instalando pacotes de requirements.txt..."
        & $venvPython -m pip install -r $requirementsPath
        Write-Host "[SUCESSO] Dependencias instaladas/atualizadas."
    } catch {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host "[ERRO CRÍTICO] Falha ao instalar as dependências do projeto." -ForegroundColor Red
        Write-Host "Verifique a mensagem de erro acima e o arquivo 'requirements.txt'." -ForegroundColor Red
        Write-Host "================================================================================" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[WARN] requirements.txt nao encontrado. Pulando instalacao de dependencias."
}

# --- Ensure 'instance' folder exists ---
Write-Host "[INFO] Verificando pasta 'instance'..."
$instancePath = Join-Path $scriptDir "instance"
if (-not (Test-Path $instancePath)) {
    New-Item -ItemType Directory -Path $instancePath | Out-Null
    Write-Host "[INFO] Pasta 'instance' criada."
} else {
    Write-Host "[INFO] Pasta 'instance' ja existe."
}

# --- Run auto_fix.py for DB setup/migrations ---
# auto_fix.py will handle all logging to run_log.txt internally.
Write-Host "[INFO] Executando auto_fix.py para setup do banco de dados..."
try {
    & $venvPython (Join-Path $scriptDir "auto_fix.py") $args
    Write-Host "[SUCESSO] auto_fix.py executado com sucesso."
} catch {
    Write-Host "[ERROR] auto_fix.py falhou. Verifique run_log.txt (gerado por auto_fix.py) para detalhes."
    exit 1
}

# --- Run flask init-db to populate essential data and create admin user ---
Write-Host "[INFO] Executando 'flask init-db' para popular dados essenciais e criar usuário admin..."
try {
    & $venvPython -m flask init-db
    Write-Host "[SUCESSO] 'flask init-db' executado com sucesso."
} catch {
    Write-Host "[ERROR] 'flask init-db' falhou. Verifique a saída acima ou logs."
    exit 1
}

# --- Start Flask Development Server ---
Write-Host "[INFO] Preparando e iniciando servidor Flask..."
Write-Host "[INFO] Iniciando servidor Flask em http://127.0.0.1:5000"
Write-Host "[INFO] Pressione CTRL+C para parar o servidor."

# Start Flask server (this is a blocking command, will stay open)
try {
    # O modo debug do Flask é ideal para desenvolvimento, recarregando automaticamente em mudanças.
    # Para um ambiente mais próximo da produção, use 'waitress-serve' ou 'gunicorn'.
    $env:FLASK_DEBUG = "1"
    & $venvPython -m flask run --host=127.0.0.1 --port=5000
} catch {
    Write-Host "[ERROR] Servidor Flask falhou ao iniciar. Detalhes: $($_.Exception.Message)"
    exit 1
}

Write-Host "[INFO] Servidor Flask encerrado."
Write-Host "[INFO] Execucao de run.ps1 concluida."
