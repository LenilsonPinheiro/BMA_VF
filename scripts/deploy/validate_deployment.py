#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script de Validação para Deploy no Google Cloud Platform
Verifica se todos os arquivos e configurações estão corretos antes do publicacao.
"""

import os
import sys
import yaml
import re
from pathlib import Path

# Cores para output
class Colors:
    """
    Definição de Colors.
    Componente essencial para a arquitetura do sistema.
    """
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """
    Definição de print_header.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    """
    Definição de print_success.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"{Colors.GREEN} {text}{Colors.END}")

def print_warning(text):
    """
    Definição de print_warning.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    """
    Definição de print_error.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"{Colors.RED} {text}{Colors.END}")

def print_info(text):
    """
    Definição de print_info.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"{Colors.BLUE} {text}{Colors.END}")

# Contadores
errors = 0
warnings = 0
successes = 0

def check_file_exists(filepath, description):
    """Verifica se um arquivo existe"""
    global errors, successes
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        successes += 1
        return True
    else:
        print_error(f"{description} não encontrado: {filepath}")
        errors += 1
        return False

def check_requirements():
    """Verifica o arquivo requirements.txt"""
    global errors, warnings, successes
    print_header("Verificando requirements.txt")
    
    if not check_file_exists('requirements.txt', 'Arquivo requirements.txt'):
        return
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = {
        'Flask': r'Flask[>=<]=',
        'gunicorn': r'gunicorn[>=<]=',
        'Flask-SQLAlchemy': r'Flask-SQLAlchemy[>=<]=',
        'Flask-Login': r'Flask-Login[>=<]=',
        'Flask-WTF': r'Flask-WTF[>=<]=',
        'python-dotenv': r'python-dotenv[>=<]='
    }
    
    for package, pattern in required_packages.items():
        if re.search(pattern, content):
            print_success(f"Pacote encontrado: {package}")
            successes += 1
        else:
            print_error(f"Pacote ausente ou sem versão: {package}")
            errors += 1

def check_main_py():
    """Verifica o arquivo main.py"""
    global errors, warnings, successes
    print_header("Verificando main.py")
    
    if not check_file_exists('main.py', 'Arquivo main.py'):
        return
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Importação do create_app': 'from BelarminoMonteiroAdvogado import create_app',
        'Criação da app': 'app = create_app()',
        'Bloco __main__': "if __name__ == '__main__':"
    }
    
    for check_name, check_string in checks.items():
        if check_string in content:
            print_success(f"{check_name} encontrado")
            successes += 1
        else:
            print_error(f"{check_name} não encontrado")
            errors += 1

def check_app_yaml():
    """Verifica o arquivo app.yaml"""
    global errors, warnings, successes
    print_header("Verificando app.yaml")
    
    yaml_path = 'BelarminoMonteiroAdvogado/app.yaml'
    if not check_file_exists(yaml_path, 'Arquivo app.yaml'):
        return
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Verificar campos obrigatórios
        required_fields = ['runtime', 'entrypoint']
        for field in required_fields:
            if field in config:
                print_success(f"Campo '{field}' encontrado: {config[field]}")
                successes += 1
            else:
                print_error(f"Campo obrigatório '{field}' ausente")
                errors += 1
        
        # Verificar SECRET_KEY
        if 'env_variables' in config and 'SECRET_KEY' in config['env_variables']:
            secret_key = config['env_variables']['SECRET_KEY']
            if 'MUDE' in secret_key or 'default' in secret_key.lower():
                print_error("SECRET_KEY ainda está com valor padrão! GERE UMA NOVA!")
                print_info("Execute: python -c \"import secrets; print(secrets.token_hex(32))\"")
                errors += 1
            elif len(secret_key) < 32:
                print_warning("SECRET_KEY parece muito curta (< 32 caracteres)")
                warnings += 1
            else:
                print_success("SECRET_KEY configurada (parece segura)")
                successes += 1
        else:
            print_error("SECRET_KEY não encontrada em env_variables")
            errors += 1
        
        # Verificar runtime
        if config.get('runtime') == 'python311':
            print_success("Runtime Python 3.11 configurado")
            successes += 1
        else:
            print_warning(f"Runtime não é python311: {config.get('runtime')}")
            warnings += 1
        
        # Verificar handlers para arquivos estáticos
        if 'handlers' in config:
            static_handler = any('/static' in str(h.get('url', '')) for h in config['handlers'])
            if static_handler:
                print_success("Handler para arquivos estáticos configurado")
                successes += 1
            else:
                print_warning("Handler para /static não encontrado")
                warnings += 1
        
    except yaml.YAMLError as e:
        print_error(f"Erro ao parsear app.yaml: {e}")
        errors += 1
    except Exception as e:
        print_error(f"Erro ao verificar app.yaml: {e}")
        errors += 1

def check_gcloudignore():
    """Verifica o arquivo .gcloudignore"""
    global errors, warnings, successes
    print_header("Verificando .gcloudignore")
    
    if not check_file_exists('.gcloudignore', 'Arquivo .gcloudignore'):
        return
    
    with open('.gcloudignore', 'r', encoding='utf-8') as f:
        content = f.read()
    
    important_ignores = [
        ('*.pyc', 'Arquivos Python compilados'),
        ('__pymemoria temporaria__', 'Cache do Python'),
        ('instance/', 'Pasta instance (banco de dados local)'),
        ('*.db', 'Arquivos de banco de dados'),
        ('.env', 'Arquivos de ambiente'),
        ('*.bat', 'Scripts batch de desenvolvimento'),
        ('test_*.py', 'Scripts de teste')
    ]
    
    for pattern, description in important_ignores:
        if pattern in content:
            print_success(f"Ignorando {description}: {pattern}")
            successes += 1
        else:
            print_warning(f"Padrão não encontrado (recomendado): {pattern} ({description})")
            warnings += 1

def check_project_structure():
    """Verifica a estrutura do projeto"""
    global errors, warnings, successes
    print_header("Verificando Estrutura do Projeto")
    
    required_dirs = [
        ('BelarminoMonteiroAdvogado', 'Diretório principal da aplicação'),
        ('BelarminoMonteiroAdvogado/modelo de paginas', 'Diretório de modelo de paginas'),
        ('BelarminoMonteiroAdvogado/static', 'Diretório de arquivos estáticos'),
        ('BelarminoMonteiroAdvogado/routes', 'Diretório de rotas')
    ]
    
    for dir_path, description in required_dirs:
        if os.path.isdir(dir_path):
            print_success(f"{description}: {dir_path}")
            successes += 1
        else:
            print_error(f"{description} não encontrado: {dir_path}")
            errors += 1
    
    required_files = [
        ('BelarminoMonteiroAdvogado/__init__.py', 'Inicializador da aplicação'),
        ('BelarminoMonteiroAdvogado/models.py', 'Modelos do banco de dados'),
        ('BelarminoMonteiroAdvogado/forms.py', 'Formulários'),
    ]
    
    for file_path, description in required_files:
        check_file_exists(file_path, description)

def check_python_syntax():
    """Verifica sintaxe dos arquivos Python principais"""
    global errors, warnings, successes
    print_header("Verificando Sintaxe Python")
    
    python_files = [
        'main.py',
        'BelarminoMonteiroAdvogado/__init__.py',
        'BelarminoMonteiroAdvogado/models.py',
        'BelarminoMonteiroAdvogado/forms.py'
    ]
    
    for filepath in python_files:
        if not os.path.exists(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), filepath, 'exec')
            print_success(f"Sintaxe OK: {filepath}")
            successes += 1
        except SyntaxError as e:
            print_error(f"Erro de sintaxe em {filepath}: {e}")
            errors += 1
        except Exception as e:
            print_warning(f"Não foi possível verificar {filepath}: {e}")
            warnings += 1

def check_documentation():
    """Verifica se a documentação existe"""
    global successes, warnings
    print_header("Verificando Documentação")
    
    docs = [
        ('DEPLOY_RAPIDO.md', 'Guia rápido de publicacao'),
        ('GUIA_HOSPEDAGEM_GOOGLE_CLOUD.md', 'Guia completo de hospedagem'),
        ('RESUMO_HOSPEDAGEM.md', 'Resumo executivo'),
        ('publicacao.bat', 'Script de publicacao automatizado')
    ]
    
    for doc_file, description in docs:
        if os.path.exists(doc_file):
            print_success(f"{description}: {doc_file}")
            successes += 1
        else:
            print_warning(f"{description} não encontrado: {doc_file}")
            warnings += 1

def print_summary():
    """Imprime o resumo final"""
    print_header("RESUMO DA VALIDAÇÃO")
    
    print(f"{Colors.GREEN} Sucessos: {successes}{Colors.END}")
    print(f"{Colors.YELLOW}⚠ Avisos: {warnings}{Colors.END}")
    print(f"{Colors.RED} Erros: {errors}{Colors.END}")
    
    print("\n" + "="*60 + "\n")
    
    if errors == 0 and warnings == 0:
        print(f"{Colors.GREEN}{Colors.BOLD} TUDO PRONTO PARA DEPLOY!{Colors.END}")
        print(f"{Colors.GREEN}Você pode prosseguir com o publicacao usando:{Colors.END}")
        print(f"{Colors.BLUE}  publicacao.bat{Colors.END}")
        print(f"{Colors.BLUE}  ou{Colors.END}")
        print(f"{Colors.BLUE}  gcloud app publicacao{Colors.END}")
        return 0
    elif errors == 0:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ PRONTO COM AVISOS{Colors.END}")
        print(f"{Colors.YELLOW}Existem alguns avisos, mas você pode prosseguir.{Colors.END}")
        print(f"{Colors.YELLOW}Revise os avisos acima antes do publicacao.{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD} CORRIJA OS ERROS ANTES DO DEPLOY!{Colors.END}")
        print(f"{Colors.RED}Existem {errors} erro(s) que devem ser corrigidos.{Colors.END}")
        print(f"{Colors.RED}Revise os erros acima e corrija-os antes de fazer o publicacao.{Colors.END}")
        return 1

def main():
    """Função principal"""
    print_header("VALIDAÇÃO DE DEPLOY - GOOGLE CLOUD PLATFORM")
    print_info("Verificando configurações para deploy no Google App Engine...")
    
    # Executar todas as verificações
    check_requirements()
    check_main_py()
    check_app_yaml()
    check_gcloudignore()
    check_project_structure()
    check_python_syntax()
    check_documentation()
    
    # Imprimir resumo
    return print_summary()

if __name__ == '__main__':
    sys.exit(main())
