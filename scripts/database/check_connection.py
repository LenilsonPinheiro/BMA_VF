"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

check_db.py: Script para verificar a integridade e conteúdo do banco de dados SQLite.

Este script conecta ao banco de dados 'site.db' localizado na pasta 'instance',
verifica a existência de tabelas e tenta acessar a tabela 'user' para confirmar
a acessibilidade e presença de dados. Útil para diagnóstico rápido do estado
do banco de dados durante desenvolvimento ou troubleshooting.

Uso:
    python check_db.py

Saída:
    Imprime mensagens de debug sobre o status da conexão, tabelas encontradas
    e acesso à tabela de usuários.
"""

import sqlite3
import os

# Define o caminho para o banco de dados SQLite
db_path = os.path.join(os.getcwd(), 'instance', 'site.db')

print(f"DEBUG: Checking database at: {db_path}")

try:
    # Tenta conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consulta todas as tabelas no banco de dados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"DEBUG: Tables found in DB: {tables}")

    # Tenta consultar a tabela 'user' para verificar acessibilidade
    try:
        cursor.execute("SELECT id, username FROM user LIMIT 1;")
        user_data = cursor.fetchone()
        if user_data:
            print(f"DEBUG: User table accessible. Found user: {user_data[1]}")
        else:
            print("DEBUG: User table accessible, but no users found.")
    except sqlite3.OperationalError as e:
        print(f"DEBUG: Error accessing 'user' table: {e}")

    # Fecha a conexão com o banco de dados
    conn.close()
    print("DEBUG: Database check complete.")

except sqlite3.Error as e:
    print(f"DEBUG: Error connecting or accessing database: {e}")
