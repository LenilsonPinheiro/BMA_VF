# -*- coding: utf-8 -*-
"""
Arquivo: create_admin_user.py
Descrição: Módulo do sistema Belarmino Monteiro Advogado.
Autor: Equipe de Engenharia (Automated)
Data: 2025
"""

import sys
import getpass
import importlib
from pathlib import Path

BASE = Path(__file__).resolve().parent

def try_import(path):
    """
    Definição de try_import.
    Componente essencial para a arquitetura do sistema.
    """
    try:
        return importlib.import_module(path)
    except Exception:
        return None

# tenta localizar a factory create_app em run.py ou pacote
app_module = try_import('run') or try_import('BelarminoMonteiroAdvogado')
create_app = None
if app_module:
    create_app = getattr(app_module, 'create_app', None) or getattr(app_module, 'app', None)
if create_app is None:
    print("Nao encontrei create_app automaticamente. Abra o arquivo run.py e ajuste este script conforme o factory do seu projeto.")
    sys.exit(2)

# pede credenciais
username = input("Admin username: ").strip()
email = input("Admin email (opcional): ").strip()
password = getpass.getpass("Admin password: ").strip()

app = create_app() if callable(create_app) else create_app

with app.app_context():
    # tente importar db e User em caminhos comuns; ajuste se necessario
    db = None
    User = None
    candidates = [
        ('BelarminoMonteiroAdvogado.extensions', 'db'),
        ('BelarminoMonteiroAdvogado.extensions', 'User'),
        ('BelarminoMonteiroAdvogado.models', 'User'),
        ('models', 'User'),
        ('extensions', 'db'),
    ]
    for modpath, attr in candidates:
        mod = try_import(modpath)
        if not mod:
            continue
        if hasattr(mod, attr):
            if attr.lower() == 'db':
                db = getattr(mod, attr)
            else:
                User = getattr(mod, attr)
        if db and User:
            break

    # fallback: tentar encontrar 'db' e 'User' no pacote principal
    pkg = try_import('BelarminoMonteiroAdvogado') or try_import('run')
    if not db and pkg and hasattr(pkg, 'db'):
        db = getattr(pkg, 'db')
    if not User and pkg:
        for n in ('User','user','Usuario'):
            if hasattr(pkg, n):
                User = getattr(pkg, n)
                break

    if User is None or db is None:
        print("Nao foi possivel localizar automaticamente o modelo User ou a extensao db.")
        print("Abra create_admin.py e edite as importacoes para apontar para o seu modelo User e a instancia db.")
        sys.exit(3)

    # criar usuario conforme convenções comuns: adjust se necessario
    try:
        # cria objeto user conforme campos comunes
        u = User()
        # tenta set de atributos se existirem
        for k,v in (('username', username), ('email', email), ('password', password), ('is_admin', True), ('admin', True)):
            try:
                setattr(u, k, v)
            except Exception:
                pass
        # se tiver metodo set_password, use-o
        if hasattr(u, 'set_password'):
            u.set_password(password)
        elif hasattr(User, 'set_password'):
            User.set_password(u, password)
        elif hasattr(u, 'password_hash'):
            try:
                from werkzeug.security import generate_password_hash
                u.password_hash = generate_password_hash(password)
            except Exception:
                pass

        db.session.add(u)
        db.session.commit()
        print(f"[SUCESSO] Usuario admin '{username}' criado.")
    except Exception as e:
        print("Erro ao criar usuario admin:", e)
        try:
            db.session.rollback()
        except:
            pass
        sys.exit(4)
