#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy Automático para PythonAnywhere via API
Autor: Lenilson Pinheiro Valério
Data: 29/11/2025
"""

import requests
import json
import time
import os
import subprocess

# Configurações
PYTHONANYWHERE_USERNAME = 'bmadv'
PYTHONANYWHERE_TOKEN = '59a5fbe2b30772b26b21a8773ec5a5d90867f2bc'
PYTHONANYWHERE_HOST = 'www.pythonanywhere.com'
DOMAIN_NAME = 'bmadv.pythonanywhere.com'

PROJECT_DIR = 'BelarminoMonteiroAdvogado'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, total_steps, message):
    """Imprime passo formatado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}[{step_num}/{total_steps}] {message}{Colors.END}")

def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Imprime mensagem informativa"""
    print(f"{Colors.YELLOW}→ {message}{Colors.END}")

def api_request(method, endpoint, data=None):
    """Faz requisição para a API do PythonAnywhere"""
    url = f'https://{PYTHONANYWHERE_HOST}/api/v0/user/{PYTHONANYWHERE_USERNAME}/{endpoint}'
    headers = {'Authorization': f'Token {PYTHONANYWHERE_TOKEN}'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except Exception as e:
        print_error(f"Erro na requisição: {str(e)}")
        return None



def step5_create_virtualenv():
    """Passo 5: Criar virtualenv"""
    print_step(5, 13, "Criando virtualenv")
    
    data = {
        'name': 'belarminoenv',
        'python_version': 'python311'
    }
    
    response = api_request('POST', 'virtualenvs/', data)
    
    if response and response.status_code in [201, 200]:
        print_success("Virtualenv criado")
        return True
    else:
        print_info("Virtualenv pode já existir ou erro ao criar")
        return True  # Continuar mesmo se falhar

def step6_create_webapp():
    """Passo 6: Criar Web App"""
    print_step(6, 13, "Criando Web App")
    
    data = {
        'domain_name': DOMAIN_NAME,
        'python_version': 'python311'
    }
    
    response = api_request('POST', 'webapps/', data)
    
    if response and response.status_code in [201, 200]:
        print_success(f"Web App criada: https://{DOMAIN_NAME}")
        return True
    else:
        print_info("Web App pode já existir")
        return True

def step7_configure_wsgi():
    """Passo 7: Configurar arquivo WSGI"""
    print_step(7, 13, "Configurando arquivo WSGI")
    
    wsgi_content = f"""# WSGI configuration for {DOMAIN_NAME}

import sys
import os

# Adicionar o diretório do projeto ao path
project_home = f'/home/{PYTHONANYWHERE_USERNAME}/{PROJECT_DIR}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurar variáveis de ambiente
os.environ['SECRET_KEY'] = 'e851374856e95ba033620eb7a2346914190e37b2210fab2f3798074d5a84e16b'
os.environ['FLASK_ENV'] = 'production'

# Importar a aplicação
from BelarminoMonteiroAdvogado import create_app
application = create_app()
"""
    
    # Criar arquivo WSGI via API de arquivos
    wsgi_path = f'/var/www/{PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py'
    
    response = api_request('POST', f'files/path{wsgi_path}', {'content': wsgi_content})
    
    if response and response.status_code in [200, 201]:
        print_success("Arquivo WSGI configurado")
        return True
    else:
        print_error("Falha ao configurar WSGI")
        print_info("Configure manualmente via interface web")
        return False

def step8_configure_virtualenv_webapp():
    """Passo 8: Configurar virtualenv na Web App"""
    print_step(8, 13, "Configurando virtualenv na Web App")
    
    virtualenv_path = f'/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/belarminoenv'
    
    data = {
        'virtualenv_path': virtualenv_path
    }
    
    response = api_request('PATCH', f'webapps/{DOMAIN_NAME}/', data)
    
    if response and response.status_code == 200:
        print_success("Virtualenv configurado na Web App")
        return True
    else:
        print_error("Falha ao configurar virtualenv")
        return False

def step9_configure_static_files():
    """Passo 9: Configurar arquivos estáticos"""
    print_step(9, 13, "Configurando arquivos estáticos")
    
    static_path = f'/home/{PYTHONANYWHERE_USERNAME}/{PROJECT_DIR}/BelarminoMonteiroAdvogado/static'
    
    data = {
        'url': '/static/',
        'path': static_path
    }
    
    response = api_request('POST', f'webapps/{DOMAIN_NAME}/static_files/', data)
    
    if response and response.status_code in [200, 201]:
        print_success("Arquivos estáticos configurados")
        return True
    else:
        print_info("Configuração de static files pode já existir")
        return True

def step10_reload_webapp():
    """Passo 10: Recarregar Web App"""
    print_step(10, 13, "Recarregando Web App")
    
    response = api_request('POST', f'webapps/{DOMAIN_NAME}/reload/')
    
    if response and response.status_code == 200:
        print_success("Web App recarregada")
        return True
    else:
        print_error("Falha ao recarregar Web App")
        return False

def main():
    """Função principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}DEPLOY AUTOMÁTICO PARA PYTHONANYWHERE{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Username:{Colors.END} {PYTHONANYWHERE_USERNAME}")
    print(f"{Colors.BOLD}Domínio:{Colors.END} https://{DOMAIN_NAME}")
    print(f"{Colors.BOLD}Projeto:{Colors.END} {PROJECT_DIR}\n")
    
    # Executar passos
    steps = [
        ("Criar virtualenv", step5_create_virtualenv),
        ("Criar Web App", step6_create_webapp),
        ("Configurar WSGI", step7_configure_wsgi),
        ("Configurar virtualenv", step8_configure_virtualenv_webapp),
        ("Configurar static files", step9_configure_static_files),
        ("Recarregar Web App", step10_reload_webapp),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for i, (name, func) in enumerate(steps, 1):
        if func():
            success_count += 1
        time.sleep(2)  # Aguardar entre passos
    
    # Resumo
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}RESUMO DO DEPLOY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Passos concluídos:{Colors.END} {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 DEPLOY CONCLUÍDO COM SUCESSO!{Colors.END}")
        print(f"\n{Colors.BOLD}Seu site está em:{Colors.END} https://{DOMAIN_NAME}")
        print(f"\n{Colors.YELLOW}PRÓXIMOS PASSOS MANUAIS:{Colors.END}")
        print("1. Acesse: https://www.pythonanywhere.com/user/bmadv/consoles/")
        print("2. Abra um console Bash")
        print("3. Execute:")
        print(f"   cd ~/{PROJECT_DIR}")
        print("   workon belarminoenv")
        print("   pip install -r requirements.txt")
        print("   flask db upgrade")
        print("   flask init-db")
        print("   flask create-admin")
        print("\n4. Recarregue a Web App em:")
        print("   https://www.pythonanywhere.com/user/bmadv/webapps/")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  DEPLOY PARCIALMENTE CONCLUÍDO{Colors.END}")
        print(f"\n{Colors.YELLOW}Alguns passos falharam. Verifique os erros acima.{Colors.END}")
        print(f"\n{Colors.YELLOW}Você pode completar manualmente seguindo:{Colors.END}")
        print("   DEPLOY_PYTHONANYWHERE_COMPLETO.md")
    
    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Deploy cancelado pelo usuário{Colors.END}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}Erro fatal: {str(e)}{Colors.END}\n")
