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

# --- Activate Virtual Environment ---
Write-Host "[INFO] Ativando ambiente virtual..."
$venvPath = Join-Path $scriptDir "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    . $venvPath # Source the activation script
    Write-Host "[INFO] Virtualenv ativado."
} else {
    Write-Host "[WARN] Virtualenv nao encontrado. Prosseguindo com o Python do PATH."
}

# Define o ponto de entrada da aplicação Flask.
$env:FLASK_APP = "BelarminoMonteiroAdvogado"

# --- Install Dependencies ---
Write-Host "[INFO] Instalando/Atualizando dependencias Python..."
$requirementsPath = Join-Path $scriptDir "requirements.txt"
if (Test-Path $requirementsPath) {
    # Upgrade pip first
    try {
        python -m pip install --upgrade pip
        Write-Host "[INFO] Pip atualizado."
    } catch {
        Write-Host "[ERROR] Falha ao atualizar o pip. Detalhes: $($_.Exception.Message)"
        exit 1
    }
    # Install/upgrade requirements
    try {
        python -m pip install -r $requirementsPath
        Write-Host "[INFO] Dependencias instaladas/atualizadas."
    } catch {
        Write-Host "[ERROR] Falha ao instalar dependencias. Verifique a saída acima."
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
    # Call Python script directly; its internal logging handles run_log.txt
    python (Join-Path $scriptDir "auto_fix.py") $args
    Write-Host "[INFO] auto_fix.py executado com sucesso."
} catch {
    Write-Host "[ERROR] auto_fix.py falhou. Verifique run_log.txt (gerado por auto_fix.py) para detalhes."
    exit 1
}

# --- Run flask init-db to populate essential data and create admin user ---
Write-Host "[INFO] Executando 'flask init-db' para popular dados essenciais e criar usuário admin..."
try {
    python -m flask init-db
    Write-Host "[INFO] 'flask init-db' executado com sucesso."
} catch {
    Write-Host "[ERROR] 'flask init-db' falhou. Verifique a saída acima ou logs."
    exit 1
}

# --- Start Flask Development Server ---
Write-Host "[INFO] Preparando e iniciando servidor Flask..."
Write-Host "[INFO] Iniciando servidor Flask em http://127.0.0.1:5000"
Write-Host "[INFO] Pressione CTRL+C para parar o servidor."

# Define o ponto de entrada da aplicação Flask.
$env:FLASK_APP = "BelarminoMonteiroAdvogado"

# Verifica se o comando 'flask' está disponível.
# Using Get-Command to check for executables in PATH
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Comando 'python' nao encontrado. Certifique-se de que o Python esta instalado e acessivel."
    exit 1
}

# Start Flask server (this is a blocking command, will stay open)
try {
    python -m flask run --host=127.0.0.1 --port=5000
} catch {
    Write-Host "[ERROR] Servidor Flask falhou ao iniciar. Detalhes: $($_.Exception.Message)"
    exit 1
}

Write-Host "[INFO] Servidor Flask encerrado."
Write-Host "[INFO] Execucao de run.ps1 concluida."
