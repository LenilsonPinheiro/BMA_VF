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

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[AVISO] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[ERRO] {text}{Colors.END}")

# Contadores
errors = 0
warnings = 0
successes = 0

def check_file_exists(filepath, description):
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
    global errors, successes
    print_header("Verificando requirements.txt")
    if check_file_exists('requirements.txt', 'Arquivo requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
        for pkg in ['Flask', 'gunicorn', 'Flask-SQLAlchemy']:
            if pkg in content:
                print_success(f"Pacote encontrado: {pkg}")
            else:
                print_warning(f"Pacote {pkg} não explícito (pode estar em dependências)")

def check_project_structure():
    global errors, successes
    print_header("Verificando Estrutura do Projeto")
    
    # CORREÇÃO AQUI: Mudado de 'modelo de paginas' para 'templates'
    required_dirs = [
        ('BelarminoMonteiroAdvogado', 'Diretório principal'),
        ('BelarminoMonteiroAdvogado/templates', 'Diretório de templates'),
        ('BelarminoMonteiroAdvogado/static', 'Diretório de estáticos'),
        ('BelarminoMonteiroAdvogado/routes', 'Diretório de rotas')
    ]
    
    for dir_path, description in required_dirs:
        if os.path.isdir(dir_path):
            print_success(f"{description}: {dir_path}")
            successes += 1
        else:
            print_error(f"{description} não encontrado: {dir_path}")
            errors += 1

def check_app_yaml():
    global errors, warnings, successes
    print_header("Verificando app.yaml")
    
    # Verifica locais possíveis para o app.yaml
    possible_paths = ['BelarminoMonteiroAdvogado/app.yaml', 'app.yaml', 'deployment/gcp/app.yaml']
    yaml_path = next((p for p in possible_paths if os.path.exists(p)), None)
    
    if yaml_path:
        print_success(f"app.yaml encontrado em: {yaml_path}")
        successes += 1
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            if config.get('runtime', '').startswith('python'):
                print_success(f"Runtime configurado: {config.get('runtime')}")
            else:
                print_error("Runtime python não encontrado no app.yaml")
                errors += 1
        except Exception as e:
            print_warning(f"Não foi possível ler app.yaml: {e}")
    else:
        print_error("app.yaml não encontrado em locais padrão")
        errors += 1

def print_summary():
    print_header("RESUMO DA VALIDAÇÃO")
    print(f"Sucessos: {successes} | Avisos: {warnings} | Erros: {errors}")
    
    if errors == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCESSO] TUDO PRONTO PARA DEPLOY!{Colors.END}")
        print(f"Comando: gcloud app deploy")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[ERRO] CORRIJA OS ERROS ACIMA!{Colors.END}")
        return 1

def main():
    check_requirements()
    check_project_structure()
    check_app_yaml()
    return print_summary()

if __name__ == '__main__':
    sys.exit(main())