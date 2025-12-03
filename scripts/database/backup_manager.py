"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

backup_db.py: Script para backup e limpeza do banco de dados SQLite.

Este script realiza backup do banco de dados 'site.db' localizado na pasta 'instance',
criando uma cópia com timestamp no diretório 'backups'. Opcionalmente, remove o banco
original e/ou a pasta de migrações se especificado via argumento de linha de comando.

==============================================================================
COMO USAR ESTE SCRIPT
==============================================================================

PROPÓSITO:
  Criar backups seguros do banco de dados SQLite antes de operações destrutivas.
  Permite reset completo do ambiente removendo DB e migrações.
  SEMPRE execute este script ANTES de modificações críticas.

DEPENDÊNCIAS:
  - Python 3.11+
  - Permissão de leitura/escrita em instance/ e instance/backups/
  - Nenhuma dependência de bibliotecas externas (apenas stdlib)

USO:
  Backup apenas:                       python backup_db.py
  Backup + remover banco:              python backup_db.py --delete-db
  Backup + remover banco e migrações:  python backup_db.py --delete-db --remove-migrations

ARGUMENTOS:
  --delete-db: Após backup, remove o arquivo site.db original.
  --remove-migrations: Após backup, remove pasta migrations/ (para reset completo)

ARQUIVOS GERADOS:
  instance/backups/site.db.bak.YYYYMMDDHHMMSS (backup com timestamp)

FLUXOS DE AUTOMAÇÃO QUE USAM ESTE SCRIPT:
  1. Pre-Deploy: backup_db.py → run_all_tests.py → deploy  (Apenas backup)
  2. Recovery: backup_db.py → check_db.py → repair_alembic.py (Apenas backup)
  3. Reset Completo: backup_db.py --delete-db --remove-migrations → limpeza_total_venv.py
  4. Before Major Changes: backup_db.py → operation → verify (Apenas backup)

LOGS GERADOS:
  [INFO] Backup criado em instance/backups/site.db.bak.20251130_143022
  [INFO] Banco removido: instance/site.db
  [INFO] Pasta migrations removida.

SAÍDA ESPERADA (sucesso):
  [INFO] Backup criado em instance/backups/site.db.bak.YYYYMMDDHHMMSS
  Exit code: 0

SAÍDA ESPERADA (erro - arquivo protegido):
  [ERROR] Falha ao remover banco: Permission denied
  Exit code: 2

EXIT CODES:
  0 = Sucesso
  1 = Backup falhou (arquivo já não existe)
  2 = Falha ao remover banco de dados
  3 = Falha ao remover pasta migrations

SEGURANÇA:
  ✓ Sempre cria backup ANTES de remover qualquer coisa
  ✓ A remoção do banco de dados agora é OPCIONAL via flag --delete-db

DICAS:
  - Por padrão, o script agora APENAS cria o backup.
  - Use --delete-db com cautela, apenas quando um reset for necessário.
"""

import os
import shutil
import datetime
import sys

# Define caminhos base do projeto
BASE = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE, 'instance', 'site.db')
BACKUP_DIR = os.path.join(BASE, 'instance', 'backups')

def main():
    """
    Função principal do script backup_db.py.
    """
    # ========================================================================
    # PARSE DE ARGUMENTOS
    # ========================================================================
    args = sys.argv[1:]
    remove_migrations = '--remove-migrations' in args
    delete_db = '--delete-db' in args

    if delete_db:
        print('[INFO] Flag --delete-db detectada. O banco de dados original será removido após o backup.')
    if remove_migrations:
        print('[INFO] Flag --remove-migrations detectada. A pasta de migrações será removida.')

    # ========================================================================
    # EXECUTA BACKUP DO BANCO DE DADOS
    # ========================================================================
    if os.path.exists(DB_PATH):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            bak_name = 'site.db.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            bak_path = os.path.join(BACKUP_DIR, bak_name)
            
            shutil.copy2(DB_PATH, bak_path)
            print('[INFO] Backup criado em', bak_path)
        except Exception as e:
            print(f'[ERROR] Falha ao criar o arquivo de backup: {e}')
            sys.exit(1)
        
        if delete_db:
            try:
                os.remove(DB_PATH)
                print('[INFO] Banco de dados original removido:', DB_PATH)
            except Exception as e:
                print(f'[ERROR] Falha ao remover o banco de dados: {e}')
                sys.exit(2)
    else:
        print(f'[ERROR] Backup falhou: O arquivo de banco de dados não foi encontrado em "{DB_PATH}"')
        sys.exit(1)

    # ========================================================================
    # OPCIONALMENTE REMOVE MIGRAÇÕES (para reset completo)
    # ========================================================================
    if remove_migrations:
        mig_path = os.path.join(BASE, 'migrations')
        if os.path.isdir(mig_path):
            try:
                print(f'[INFO] Removendo a pasta de migrações em: {mig_path}')
                shutil.rmtree(mig_path)
                print('[INFO] Pasta de migrações removida.')
            except Exception as e:
                print(f'[ERROR] Falha ao remover a pasta de migrações: {e}')
                sys.exit(3)
        else:
            print(f'[INFO] Pasta de migrações não encontrada em: {mig_path}')

    # ========================================================================
    # SUCESSO
    # ========================================================================
    print('[INFO] backup_db.py completado com sucesso.')
    sys.exit(0)

if __name__ == '__main__':
    main()
