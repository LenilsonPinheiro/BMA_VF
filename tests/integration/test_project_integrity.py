# -*- coding: utf-8 -*-
"""
==============================================================================
Testes de Integridade do Projeto
==============================================================================

Este módulo contém uma suíte de testes Pytest que verifica a integridade
geral da estrutura do projeto, configuração e arquivos estáticos.

O objetivo é garantir que o projeto esteja em um estado são e consistente,
prevenindo erros comuns de configuração e estrutura antes de estágios mais
avançados de teste ou deploy.

Os testes aqui são, em sua maioria, verificações estáticas e não
necessitam de um servidor em execução ou de interações complexas com a aplicação.
"""
import os
import sys
import pytest
from jinja2 import TemplateSyntaxError

# Lista de arquivos essenciais para o funcionamento do projeto.
ESSENTIAL_FILES = [
    'main.py',
    'requirements.txt',
    '.gcloudignore',
    'run.bat',
    'BelarminoMonteiroAdvogado/__init__.py',
    'BelarminoMonteiroAdvogado/models.py',
    'BelarminoMonteiroAdvogado/forms.py',
    'deployment/gcp/app.yaml'
]

# Lista de diretórios que compõem a arquitetura do projeto.
ESSENTIAL_DIRS = [
    'BelarminoMonteiroAdvogado',
    'BelarminoMonteiroAdvogado/routes',
    'BelarminoMonteiroAdvogado/static',
    'BelarminoMonteiroAdvogado/static/css',
    'BelarminoMonteiroAdvogado/static/js',
    'BelarminoMonteiroAdvogado/static/images',
    'BelarminoMonteiroAdvogado/templates',
    'BelarminoMonteiroAdvogado/templates/admin',
    'BelarminoMonteiroAdvogado/templates/home',
    'tests',
    'tests/integration',
    'tests/unit',
]

# Pacotes mínimos que devem estar listados no requirements.txt.
REQUIRED_PACKAGES = [
    'Flask',
    'Flask-SQLAlchemy',
    'Flask-Login',
    'Flask-WTF',
    'gunicorn',
    'python-dotenv',
    'Pillow'
]

# Conteúdo esperado no .gcloudignore para evitar o upload de arquivos indesejados.
GCLOUDIGNORE_PATTERNS = [
    '*.pyc',
    '__pycache__',
    '*.db',
    '*.sqlite',
    'test_*.py',
    '/venv/',
    '.gitignore',
    '*.bat',
    '*.sh'
]

# Templates Jinja2 cuja sintaxe deve ser validada.
TEMPLATES_TO_VALIDATE = [
    'base.html',
    'home/home_option1.html',
    'admin/dashboard.html',
    'auth/login.html',
    '404.html',
    '500.html'
]

# --- Testes de Estrutura de Arquivos e Diretórios ---

@pytest.mark.parametrize("filepath", ESSENTIAL_FILES)
def test_essential_files_exist(filepath):
    """Verifica se arquivos essenciais existem no projeto."""
    assert os.path.exists(filepath), f"Arquivo essencial não encontrado: {filepath}"

@pytest.mark.parametrize("dirpath", ESSENTIAL_DIRS)
def test_essential_directories_exist(dirpath):
    """Verifica se diretórios essenciais existem no projeto."""
    assert os.path.isdir(dirpath), f"Diretório essencial não encontrado: {dirpath}"

# --- Testes de Arquivos de Configuração ---

def test_requirements_txt_contains_necessary_packages():
    """Verifica se o requirements.txt contém os pacotes mínimos necessários."""
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    for package in REQUIRED_PACKAGES:
        assert package in content, f"Pacote '{package}' não encontrado em requirements.txt"

def test_gcloudignore_is_correctly_configured():
    """Verifica se o .gcloudignore contém regras importantes."""
    # O .gcloudignore pode estar em um de dois locais
    gcloudignore_path = '.gcloudignore'
    if not os.path.exists(gcloudignore_path):
        gcloudignore_path = 'deployment/gcp/.gcloudignore'
    
    assert os.path.exists(gcloudignore_path), "Arquivo .gcloudignore não encontrado."

    with open(gcloudignore_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for pattern in GCLOUDIGNORE_PATTERNS:
        assert pattern in content, f"Padrão '{pattern}' não encontrado em .gcloudignore"

def test_app_yaml_for_gcp_is_correctly_configured():
    """Verifica a configuração do app.yaml para o Google Cloud Platform."""
    app_yaml_path = 'deployment/gcp/app.yaml'
    assert os.path.exists(app_yaml_path), "deployment/gcp/app.yaml não encontrado"

    with open(app_yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'runtime: python311' in content, "Runtime do Python não está configurado para python311"
    assert 'entrypoint: gunicorn' in content, "Entrypoint do Gunicorn não está configurado"
    assert 'SECRET_KEY' in content, "A variável de ambiente SECRET_KEY não está definida no app.yaml"
    assert 'MUDE-ESTA-CHAVE' not in content, "A SECRET_KEY ainda está com o valor padrão. Altere-a!"

# --- Testes de Sanidade do Código e Templates ---

def test_python_version_is_supported():
    """Verifica se a versão do Python em execução é compatível (>= 3.11)."""
    version = sys.version_info
    assert version.major == 3 and version.minor >= 11, \
        f"Versão do Python 3.11+ é necessária. Versão atual: {version.major}.{version.minor}"

@pytest.mark.parametrize("template_name", TEMPLATES_TO_VALIDATE)
def test_jinja_template_syntax(app, template_name):
    """Valida a sintaxe de templates Jinja2 essenciais para evitar erros de renderização."""
    try:
        app.jinja_env.get_template(template_name)
    except TemplateSyntaxError as e:
        pytest.fail(f"Erro de sintaxe no template '{template_name}': {e}", pytrace=False)
    except Exception as e:
        pytest.fail(f"Erro inesperado ao carregar o template '{template_name}': {e}", pytrace=False)

def test_password_is_hashed(app):
    """Verifica se a senha do usuário 'admin' está devidamente hasheada no banco de dados."""
    from BelarminoMonteiroAdvogado.models import User
    
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        assert admin_user is not None, "Usuário 'admin' não encontrado no banco de dados de teste."
        
        # A senha padrão é 'admin'. O hash nunca deve ser igual à senha em texto plano.
        assert admin_user.password_hash != 'admin', "A senha do usuário 'admin' parece estar em texto plano!"
        
        # Hashes modernos (scrypt, argon2, bcrypt) são longos.
        assert len(admin_user.password_hash) > 50, "O hash da senha parece curto ou inválido."

def test_app_creates_without_error(app):
    """Verifica se a factory create_app executa sem erros."""
    assert app is not None

def test_all_models_are_creatable(app):
    """
    Verifica se o SQLAlchemy consegue criar todas as tabelas a partir dos modelos.
    Este é um teste crucial para detectar erros de sintaxe ou de relacionamento nos models.py.
    """
    from sqlalchemy import inspect
    from BelarminoMonteiroAdvogado.models import db

    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'user',
            'pagina',
            'conteudo_geral',
            'area_atuacao',
            'membro_equipe',
            'depoimento',
            'cliente_parceiro',
            'setor_atendido',
            'home_page_section',
            'theme_settings'
        ]
        
        for table_name in required_tables:
            assert table_name in tables, f"A tabela '{table_name}' não foi criada. Verifique o modelo correspondente."
