# -*- coding: utf-8 -*-
"""
Arquivo: health_check.py
Descrição: Módulo do sistema Belarmino Monteiro Advogado.
Autor: Equipe de Engenharia (Automated)
Data: 2025
"""

import os
import sys
import traceback
from BelarminoMonteiroAdvogado import create_app, db, ensure_essential_data

print("="*60)
print("INICIANDO DIAGNOSTICO DETALHADO - MODO SEM BLINDAGEM")
print("="*60)

try:
    print("\n[1] Criando a aplicacao Flask...")
    app = create_app()
    
    print(f"[INFO] Caminho da Instancia (app.instance_path): {app.instance_path}")
    
    # Informa a origem da configuração do DB
    if os.environ.get('DATABASE_URL'):
        print(f"[INFO] URI do Banco de Dados (via DATABASE_URL): {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    else:
        print(f"[INFO] URI do Banco de Dados (padrão local): {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Verifica onde o SQLite vai tentar escrever
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'sqlite' in uri:
        path_part = uri.replace('sqlite:///', '')
        # Corrige caminho se for relativo
        if not os.path.isabs(path_part):
            if 'instance' in app.instance_path and 'instance' not in path_part:
                 # Se o path não tem instance, mas o app tem, o flask joga na instance se instance_relative_config=True
                 estimated_path = os.path.join(app.instance_path, path_part)
            else:
                 estimated_path = os.path.join(app.root_path, path_part)
        else:
            estimated_path = path_part
            
        print(f"[INFO] Caminho estimado do arquivo DB: {estimated_path}")
        
        folder = os.path.dirname(estimated_path)
        if folder and not os.path.exists(folder):
            print(f"[ALERTA CRITICO] A pasta '{folder}' NAO existe. O Flask vai falhar ao tentar criar o banco aqui.")
            print(f"[ACAO] Tentando criar a pasta '{folder}' agora...")
            try:
                os.makedirs(folder)
                print("[SUCESSO] Pasta criada.")
            except Exception as e:
                print(f"[ERRO] Nao foi possivel criar a pasta: {e}")
        else:
            print(f"[OK] A pasta '{folder}' existe.")

    print("\n[2] Tentando criar tabelas (db.create_all)...")
    with app.app_context():
        try:
            db.create_all()
            print("[SUCESSO] Tabelas criadas no banco de dados.")
        except Exception as e:
            print("\n[ERRO FATAL] Falha ao criar tabelas. Detalhes:")
            traceback.print_exc()
            sys.exit(1)

        print("\n[3] Tentando popular dados iniciais (ensure_essential_data)...")
        try:
            ensure_essential_data()
            print("[SUCESSO] Dados essenciais inseridos/atualizados.")
        except Exception as e:
            print("\n[ERRO FATAL] Falha na insercao de dados. Provavel erro de Schema (models.py vs forms.py).")
            print("Detalhes do erro:")
            traceback.print_exc()
            sys.exit(1)

    print("\n" + "="*60)
    print("DIAGNOSTICO FINALIZADO: O sistema parece saudavel via Python puro.")
    print("Se este script rodou sem erros, o problema esta APENAS no seu run.bat.")
    print("="*60)

except Exception as e:
    print("\n[ERRO GERAL] Ocorreu um erro nao tratado:")
    traceback.print_exc()

input("\nPressione ENTER para sair...")