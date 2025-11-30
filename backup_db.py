"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

backup_db.py: Script para backup e limpeza do banco de dados SQLite.

Este script realiza backup do banco de dados 'site.db' localizado na pasta 'instance',
criando uma cópia com timestamp no diretório 'backups'. Opcionalmente, remove o banco
original e/ou a pasta de migrações se especificado via argumento de linha de comando.

Uso:
    python backup_db.py [--remove-migrations]

Argumentos:
    --remove-migrations: Remove a pasta 'migrations' após o backup.
"""

import os
import shutil
import datetime
import sys

# Define caminhos base do projeto
BASE = os.path.abspath(os.path.dirname(__file__))  # Caminho absoluto do diretório do script
DB_PATH = os.path.join(BASE, 'instance', 'site.db')  # Caminho para o banco de dados SQLite
BACKUP_DIR = os.path.join(BASE, 'instance', 'backups')  # Diretório para armazenar backups

def main():
    """
    Função principal do script backup_db.py.

    Processa argumentos da linha de comando, realiza backup do banco de dados,
    remove o banco original se existir, e opcionalmente remove a pasta de migrações.
    """
    remove_migrations = False  # Flag para indicar se deve remover a pasta de migrações
    # Verifica se o argumento opcional '--remove-migrations' foi passado
    if len(sys.argv) > 1 and sys.argv[1] == '--remove-migrations':
        remove_migrations = True

    # Verifica se o banco de dados existe para backup
    if os.path.exists(DB_PATH):
        # Cria o diretório de backups se não existir
        os.makedirs(BACKUP_DIR, exist_ok=True)
        # Gera nome do arquivo de backup com timestamp
        bak_name = 'site.db.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        bak_path = os.path.join(BACKUP_DIR, bak_name)
        # Copia o banco de dados para o arquivo de backup
        shutil.copy2(DB_PATH, bak_path)
        print('[INFO] Backup criado em', bak_path)
        try:
            # Remove o banco de dados original após backup
            os.remove(DB_PATH)
            print('[INFO] Banco removido:', DB_PATH)
        except Exception as e:
            print('[ERROR] Falha ao remover banco:', e)
            sys.exit(2)  # Sai com código de erro se falhar ao remover
    else:
        print('[INFO] Nenhum banco encontrado para backup/remover.')

    # Se solicitado, remove a pasta de migrações
    if remove_migrations:
        mig = os.path.join(BASE, 'migrations')  # Caminho para a pasta de migrações
        if os.path.isdir(mig):
            try:
                # Remove a pasta de migrações recursivamente
                shutil.rmtree(mig)
                print('[INFO] Pasta migrations removida.')
            except Exception as e:
                print('[ERROR] Falha ao remover migrations:', e)
                sys.exit(3)  # Sai com código de erro se falhar

    sys.exit(0)  # Sai com sucesso

# Executa a função main se o script for chamado diretamente
if __name__ == '__main__':
    main()
