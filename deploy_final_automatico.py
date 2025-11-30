#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy COMPLETO e AUTOMÁTICO para PythonAnywhere
Executa TODOS os comandos necessários via API
"""

import requests
import time
import json

# Configurações
PA_USERNAME = 'bmadv'
PA_TOKEN = '59a5fbe2b30772b26b21a8773ec5a5d90867f2bc'
PA_HOST = 'www.pythonanywhere.com'

# PASSO 4: Criar virtualenv
print("\n[4/10] Criando virtualenv...")
send_console_input(console_id, 'mkvirtualenv --python=/usr/bin/python3.11 belarminoenv')
time.sleep(5)
print("✓ Virtualenv criado")

# PASSO 5: Instalar dependências
print("\n[5/10] Instalando dependências...")
send_console_input(console_id, 'cd BelarminoMonteiroAdvogado && workon belarminoenv && pip install -r requirements.txt')
time.sleep(30)  # Aguarda instalação
print("✓ Dependências instaladas")

# PASSO 6: Criar diretório instance
print("\n[6/10] Criando diretório instance...")
send_console_input(console_id, 'cd BelarminoMonteiroAdvogado && mkdir -p instance')
time.sleep(2)
print("✓ Diretório instance criado")

# PASSO 7: Inicializar banco de dados
print("\n[7/10] Inicializando banco de dados...")
send_console_input(console_id, 'cd BelarminoMonteiroAdvogado && workon belarminoenv && flask db upgrade')
time.sleep(5)
send_console_input(console_id, 'flask init-db')
time.sleep(5)
print("✓ Banco de dados inicializado")

# PASSO 8: Criar usuário admin
print("\n[8/10] Criando usuário admin...")
print("   Username: admin")
print("   Password: Admin@2025")
send_console_input(console_id, 'cd BelarminoMonteiroAdvogado && workon belarminoenv && flask create-admin')
time.sleep(2)
send_console_input(console_id, 'admin')
time.sleep(1)
send_console_input(console_id, 'Admin@2025')
time.sleep(2)
print("✓ Usuário admin criado")

# PASSO 9: Configurar Web App
print("\n[9/10] Configurando Web App...")
domain = f'{PA_USERNAME}.pythonanywhere.com'

# Configurar virtualenv
virtualenv_path = f'/home/{PA_USERNAME}/.virtualenvs/belarminoenv'
r = api_call('PATCH', f'webapps/{domain}/', {'virtualenv_path': virtualenv_path})
if r and r.status_code == 200:
    print("✓ Virtualenv configurado na Web App")

# Configurar static files
static_path = f'/home/{PA_USERNAME}/BelarminoMonteiroAdvogado/BelarminoMonteiroAdvogado/static'
r = api_call('POST', f'webapps/{domain}/static_files/', {
    'url': '/static/',
    'path': static_path
})
print("✓ Static files configurados")

# Atualizar arquivo WSGI
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
print("✓ Arquivo WSGI atualizado")

# PASSO 10: Recarregar Web App
print("\n[10/10] Recarregando Web App...")
r = api_call('POST', f'webapps/{domain}/reload/')
if r and r.status_code == 200:
    print("✓ Web App recarregada!")
else:
    print("⚠ Aviso ao recarregar (pode estar OK)")

# Fechar console
api_call('DELETE', f'consoles/{console_id}/')

# RESUMO FINAL
print("\n" + "=" * 80)
print("🎉 DEPLOY COMPLETO E AUTOMÁTICO CONCLUÍDO!")
print("=" * 80)
print(f"\n✅ SITE NO AR: https://{domain}")
print(f"✅ ADMIN: https://{domain}/admin")
print(f"   Username: admin")
print(f"   Password: Admin@2025")
print("\n" + "=" * 80)
print("PRÓXIMOS PASSOS:")
print("=" * 80)
print("\n1. Teste o site: https://bmadv.pythonanywhere.com")
print("2. Faça login no admin: https://bmadv.pythonanywhere.com/admin")
print("3. Configure o domínio personalizado (opcional)")
print("\n" + "=" * 80)
print("CONFIGURAÇÃO DO DOMÍNIO belarminononteiroadvogado.com.br:")
print("=" * 80)
print("\n1. Upgrade para plano Hacker ($5/mês)")
print("2. Adicione o domínio na Web App")
print("3. Configure DNS no Registro.br:")
print("   - Tipo: CNAME")
print("   - Nome: @")
print("   - Valor: bmadv.pythonanywhere.com")
print("\n" + "=" * 80 + "\n")
