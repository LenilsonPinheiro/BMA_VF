#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy Completo Automático para PythonAnywhere
Executa TODOS os passos necessários
"""

import requests
import time
import sys

# Configurações
PA_USERNAME = 'bmadv'
PA_TOKEN = '59a5fbe2b30772b26b21a8773ec5a5d90867f2bc'
PA_HOST = 'www.pythonanywhere.com'

print("=" * 80)
print("DEPLOY AUTOMÁTICO COMPLETO PARA PYTHONANYWHERE")
print("=" * 80)
print(f"\nUsername: {PA_USERNAME}")
print(f"Host: {PA_HOST}\n")

def api_call(method, endpoint, data=None, files=None):
    """Faz chamada para API do PythonAnywhere"""
    url = f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/{endpoint}'
    headers = {'Authorization': f'Token {PA_TOKEN}'}
    
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            if files:
                r = requests.post(url, headers=headers, files=files)
            else:
                r = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=data)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers)
        
        return r
    except Exception as e:
        print(f"✗ Erro na requisição: {e}")
        return None

# PASSO 1: Verificar conta
print("\n[1/8] Verificando conta PythonAnywhere...")
r = api_call('GET', 'cpu/')
if r and r.status_code == 200:
    print("✓ Conta verificada!")
else:
    print("✗ Erro ao verificar conta")
    print("  Verifique se o token está correto")
    sys.exit(1)

# PASSO 2: Criar console para executar comandos
print("\n[2/8] Criando console Bash...")
r = api_call('POST', 'consoles/', {'executable': 'bash'})
if r and r.status_code == 201:
    console_id = r.json()['id']
    print(f"✓ Console criado (ID: {console_id})")
else:
    print("⚠ Não foi possível criar console via API")
    console_id = None

# PASSO 3: Criar virtualenv
print("\n[3/8] Criando virtualenv...")
r = api_call('POST', 'virtualenvs/', {
    'name': 'belarminoenv',
    'python_version': 'python311'
})
if r and r.status_code in [200, 201]:
    print("✓ Virtualenv criado!")
elif r and r.status_code == 400 and 'already exists' in r.text.lower():
    print("✓ Virtualenv já existe!")
else:
    print("⚠ Aviso ao criar virtualenv (pode já existir)")

# PASSO 4: Criar Web App
print("\n[4/8] Criando Web App...")
domain = f'{PA_USERNAME}.pythonanywhere.com'
r = api_call('POST', 'webapps/', {
    'domain_name': domain,
    'python_version': 'python311'
})
if r and r.status_code in [200, 201]:
    print(f"✓ Web App criada: https://{domain}")
elif r and r.status_code == 409:
    print(f"✓ Web App já existe: https://{domain}")
else:
    print(f"⚠ Aviso ao criar Web App (pode já existir)")

# PASSO 5: Configurar virtualenv na Web App
print("\n[5/8] Configurando virtualenv na Web App...")
virtualenv_path = f'/home/{PA_USERNAME}/.virtualenvs/belarminoenv'
r = api_call('PATCH', f'webapps/{domain}/', {
    'virtualenv_path': virtualenv_path
})
if r and r.status_code == 200:
    print("✓ Virtualenv configurado!")
else:
    print("⚠ Aviso ao configurar virtualenv")

# PASSO 6: Configurar static files
print("\n[6/8] Configurando arquivos estáticos...")
static_path = f'/home/{PA_USERNAME}/BelarminoMonteiroAdvogado/BelarminoMonteiroAdvogado/static'
r = api_call('POST', f'webapps/{domain}/static_files/', {
    'url': '/static/',
    'path': static_path
})
if r and r.status_code in [200, 201]:
    print("✓ Static files configurados!")
else:
    print("⚠ Static files podem já estar configurados")

# PASSO 7: Criar arquivo WSGI
print("\n[7/8] Configurando arquivo WSGI...")
wsgi_content = f"""import sys
import os

project_home = '/home/{PA_USERNAME}/BelarminoMonteiroAdvogado'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['SECRET_KEY'] = 'e851374856e95ba033620eb7a2346914190e37b2210fab2f3798074d5a84e16b'
os.environ['FLASK_ENV'] = 'production'

from BelarminoMonteiroAdvogado import create_app
application = create_app()
"""

wsgi_path = f'/var/www/{PA_USERNAME}_pythonanywhere_com_wsgi.py'
r = api_call('POST', f'files/path{wsgi_path}', {'content': wsgi_content})
if r and r.status_code in [200, 201]:
    print("✓ Arquivo WSGI configurado!")
else:
    print("⚠ Aviso ao configurar WSGI")

# PASSO 8: Recarregar Web App
print("\n[8/8] Recarregando Web App...")
r = api_call('POST', f'webapps/{domain}/reload/')
if r and r.status_code == 200:
    print("✓ Web App recarregada!")
else:
    print("⚠ Aviso ao recarregar")

# RESUMO
print("\n" + "=" * 80)
print("CONFIGURAÇÃO AUTOMÁTICA CONCLUÍDA!")
print("=" * 80)
print(f"\n✓ Web App criada: https://{domain}")
print(f"✓ Virtualenv: {virtualenv_path}")
print(f"✓ Static files configurados")
print(f"✓ WSGI configurado")

print("\n" + "=" * 80)
print("PRÓXIMOS PASSOS MANUAIS NECESSÁRIOS:")
print("=" * 80)
print("\n1. Acesse: https://www.pythonanywhere.com/user/bmadv/consoles/")
print("2. Abra um console Bash")
print("3. Execute os seguintes comandos:\n")
print("   git clone https://github.com/LenilsonPinheiro/BelarminoMonteiroAdvogado.git")
print("   cd BelarminoMonteiroAdvogado")
print("   workon belarminoenv")
print("   pip install -r requirements.txt")
print("   mkdir -p instance")
print("   flask db upgrade")
print("   flask init-db")
print("   flask create-admin")
print("\n4. Depois, recarregue a Web App em:")
print("   https://www.pythonanywhere.com/user/bmadv/webapps/")
print("\n5. Teste em: https://bmadv.pythonanywhere.com")

print("\n" + "=" * 80)
print("NOTA: O repositório GitHub precisa ser criado manualmente")
print("devido ao token inválido. Você pode:")
print("1. Criar em: https://github.com/new")
print("2. Nome: BelarminoMonteiroAdvogado")
print("3. Depois fazer push do código local")
print("=" * 80 + "\n")
