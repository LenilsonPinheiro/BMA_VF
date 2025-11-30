#!/bin/bash

# Script de setup automático para deploy no PythonAnywhere
# Execute este script no console Bash do PythonAnywhere

set -e # Encerra o script se qualquer comando falhar

PROJECT_DIR="netpalm"
PYTHON_VERSION="/usr/bin/python3.11"
VENV_NAME="venv"

echo "--- Iniciando setup do NetPalm no PythonAnywhere ---"

# 1. Acessa o diretório do projeto
echo ">>> Acessando o diretório do projeto..."
cd ~/$PROJECT_DIR

# 2. Cria o ambiente virtual
echo ">>> Criando ambiente virtual com Python 3.11..."
mkvirtualenv --python=$PYTHON_VERSION $VENV_NAME

# 3. Instala as dependências
echo ">>> Instalando dependências do requirements.txt..."
pip install -r requirements.txt

# 4. Cria o banco de dados
echo ">>> Criando o banco de dados SQLite..."
flask init-db

echo "--- Setup concluído com sucesso! ---"
echo "Próximos passos: Configure a aba 'Web' no painel do PythonAnywhere."