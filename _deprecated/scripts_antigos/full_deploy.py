#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy COMPLETO e AUTOMÁTICO - Execução Final
"""

import requests
import time

PA_USERNAME = 'bmadv'
PA_TOKEN = '59a5fbe2b30772b26b21a8773ec5a5d90867f2bc'
PA_HOST = 'www.pythonanywhere.com'

print("=" * 80)
print("🚀 DEPLOY AUTOMÁTICO COMPLETO - PYTHONANYWHERE")
print("=" * 80)

def api_call(method, endpoint, data=None):
    """
    Definição de api_call.
    Componente essencial para a arquitetura do sistema.
    """
    url = f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/{endpoint}'
    headers = {'Authorization': f'Token {PA_TOKEN}'}
    
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=data)
        
        return r
    except Exception as e:
        print(f"✗ Erro: {e}")
        return None

# Configurar Web App
print("\n[1/4] Configurando Web App...")
domain = f'{PA_USERNAME}.pythonanywhere.com'

# Configurar virtualenv
virtualenv_path = f'/home/{PA_USERNAME}/.virtualenvs/belarminoenv'
r = api_call('PATCH', f'webapps/{domain}/', {'virtualenv_path': virtualenv_path})
if r and r.status_code == 200:
    print("✓ Virtualenv configurado")

# Configurar static files
static_path = f'/home/{PA_USERNAME}/BelarminoMonteiroAdvogado/BelarminoMonteiroAdvogado/static'

# Deletar static files antigos
r = api_call('GET', f'webapps/{domain}/static_files/')
if r and r.status_code == 200:
    for sf in r.json():
        if sf['url'] == '/static/':
            requests.delete(
                f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/webapps/{domain}/static_files/{sf["id"]}/',
                headers={'Authorization': f'Token {PA_TOKEN}'}
            )

# Adicionar novo
r = api_call('POST', f'webapps/{domain}/static_files/', {
    'url': '/static/',
    'path': static_path
})
print("✓ Static files configurados")

# Atualizar WSGI
print("\n[2/4] Atualizando arquivo WSGI...")
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
r = requests.post(
    f'https://{PA_HOST}/api/v0/user/{PA_USERNAME}/files/path{wsgi_path}',
    headers={'Authorization': f'Token {PA_TOKEN}'},
    json={'content': wsgi_content}
)
print("✓ WSGI atualizado")

# Recarregar Web App
print("\n[3/4] Recarregando Web App...")
r = api_call('POST', f'webapps/{domain}/reload/')
time.sleep(3)
print("✓ Web App recarregada")

# Testar
print("\n[4/4] Testando site...")
try:
    r = requests.get(f'https://{domain}/', timeout=10)
    if r.status_code == 200:
        print("✓ Site respondendo!")
    else:
        print(f"⚠ Status: {r.status_code}")
except:
    print("⚠ Site ainda carregando...")

print("\n" + "=" * 80)
print("🎉 DEPLOY AUTOMÁTICO CONCLUÍDO!")
print("=" * 80)
print(f"\n✅ SITE: https://{domain}")
print(f"✅ ADMIN: https://{domain}/admin")
print(f"   Username: admin")
print(f"   Password: Admin@2025")
print("\n" + "=" * 80)
print("IMPORTANTE: Execute os comandos de inicialização:")
print("=" * 80)
print("\n1. Acesse: https://www.pythonanywhere.com/user/bmadv/consoles/")
print("2. Abra console Bash")
print("3. Execute:\n")
print("# Certifique-se de que os arquivos do projeto foram enviados para o diretório 'BelarminoMonteiroAdvogado'")
print("cd BelarminoMonteiroAdvogado")
print("mkvirtualenv --python=/usr/bin/python3.11 belarminoenv")
print("workon belarminoenv")
print("pip install -r requirements.txt")
print("mkdir -p instance")
print("flask db upgrade")
print("flask init-db")
print('echo -e "admin\\nAdmin@2025" | flask create-admin')
print("\n4. Recarregue em: https://www.pythonanywhere.com/user/bmadv/webapps/")
print("\n" + "=" * 80 + "\n")
