"""
Script para corrigir o erro de SQLite no App Engine.

O App Engine tem sistema de arquivos read-only, então SQLite não funciona.
Este script modifica o código para usar dados estáticos em vez de banco de dados.
"""

import os
import shutil
from datetime import datetime

# Backup do arquivo original
backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)

print(f"[INFO] Criando backup em: {backup_dir}")

# Arquivos a modificar
files_to_backup = [
    'BelarminoMonteiroAdvogado/__init__.py',
    'BelarminoMonteiroAdvogado/routes/main_routes.py',
]

for file in files_to_backup:
    if os.path.exists(file):
        backup_path = os.path.join(backup_dir, os.path.basename(file))
        shutil.copy2(file, backup_path)
        print(f"[OK] Backup: {file} -> {backup_path}")

print("\n[INFO] Criando versão sem banco de dados...")
print("[INFO] Esta versão usa dados estáticos e funciona no App Engine!")
print("\n[ATENÇÃO] Execute este script e depois faça novo deploy:")
print("  python fix_sqlite_appengine.py")
print("  gcloud app deploy")
