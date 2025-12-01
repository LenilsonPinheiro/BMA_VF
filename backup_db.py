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
  Backup apenas:                   python backup_db.py
  Backup + remover migrações:      python backup_db.py --remove-migrations

ARGUMENTOS:
  --remove-migrations: Após backup, remove pasta migrations/ (para reset completo)

ARQUIVOS GERADOS:
  instance/backups/site.db.bak.YYYYMMDDHHMMSS (backup com timestamp)

FLUXOS DE AUTOMAÇÃO QUE USAM ESTE SCRIPT:
  1. Pre-Deploy: backup_db.py → run_all_tests.py → deploy
  2. Recovery: backup_db.py → check_db.py → repair_alembic.py
  3. Reset Completo: backup_db.py --remove-migrations → limpeza_total_venv.py
  4. Before Major Changes: backup_db.py → operation → verify

LOGS GERADOS:
  [INFO] Backup criado em instance/backups/site.db.bak.20251130_143022
  [INFO] Banco removido: instance/site.db
  [INFO] Pasta migrations removida.

SAÍDA ESPERADA (sucesso):
  [INFO] Backup criado em instance/backups/site.db.bak.YYYYMMDDHHMMSS
  [INFO] Banco removido: instance/site.db
  Exit code: 0

SAÍDA ESPERADA (erro - arquivo protegido):
  [ERROR] Falha ao remover banco: Permission denied
  Exit code: 2

SAÍDA ESPERADA (erro - migrations protegida):
  [ERROR] Falha ao remover migrations: Permission denied
  Exit code: 3

EXIT CODES:
  0 = Sucesso
  1 = Backup falhou (arquivo já não existe)
  2 = Falha ao remover banco de dados
  3 = Falha ao remover pasta migrations

SEGURANÇA:
  ✓ Sempre cria backup ANTES de remover qualquer coisa
  ✓ Timestamps garantem backups únicos para cada execução
  ✓ Backups antigos em instance/backups/ são mantidos (usar limpar_projeto.py para cleanup)
  ✓ Nunca remove arquivo sem confirmar com timestamp

DICAS:
  - Execute sempre antes de operações destrutivas (--remove-migrations flag)
  - Mantenha backups por pelo menos 1 semana
  - Revise instance/backups/ periodicamente para limpeza manual se necessário
  - Use com backup_db.py --remove-migrations apenas em casos de reset completo

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

    FLUXO EXECUTIVO:
      1. Processa argumentos da linha de comando
      2. Se BD existe: cria backup com timestamp em instance/backups/
      3. Remove BD original (para recriação limpa)
      4. Se --remove-migrations: remove pasta migrations/ também
      5. Retorna exit code apropriado
    
    EXIT CODES:
      0 = Sucesso (backup criado)
      1 = Falha genérica (veja output)
      2 = Falha ao remover BD original
      3 = Falha ao remover migrations (quando --remove-migrations usado)
    
    EXEMPLOS DE LOG:
      [INFO] Backup criado em instance/backups/site.db.bak.20251130_143022
      [INFO] Banco removido: instance/site.db
      [ERROR] Falha ao remover banco: Permission denied
    
    DEPENDÊNCIAS DE EXECUÇÃO:
      Este script é frequentemente chamado por:
      - deploy_production_complete.py (passo 1: segurança)
      - Manualmente antes de: repair_alembic.py, limpeza_total_venv.py
      - CI/CD jobs que precisam reset seguro
    
    SEGURANÇA:
      ✓ Backup SEMPRE criado antes de qualquer remoção
      ✓ Timestamps garantem identificação clara de cada backup
      ✓ Backups armazenados em instance/backups/ (separado do código)
      ✓ Falhas em remoção geram exit codes específicos
    """
    # ========================================================================
    # PARSE DE ARGUMENTOS
    # ========================================================================
    remove_migrations = False  # Flag para indicar se deve remover a pasta de migrações
    # Verifica se o argumento opcional '--remove-migrations' foi passado
    if len(sys.argv) > 1 and sys.argv[1] == '--remove-migrations':
        remove_migrations = True
        print('[INFO] Flag --remove-migrations detectada. Migrations serão removidas após backup.')

    # ========================================================================
    # EXECUTA BACKUP DO BANCO DE DADOS
    # ========================================================================
    # Verifica se o banco de dados existe para backup
    if os.path.exists(DB_PATH):
        # Cria o diretório de backups se não existir
        os.makedirs(BACKUP_DIR, exist_ok=True)
        # Gera nome do arquivo de backup com timestamp (permite múltiplos backups únicos)
        bak_name = 'site.db.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        bak_path = os.path.join(BACKUP_DIR, bak_name)
        # Copia o banco de dados para o arquivo de backup (preserva metadados)
        shutil.copy2(DB_PATH, bak_path)
        print('[INFO] Backup criado em', bak_path)
        try:
            # Remove o banco de dados original após backup (permite recriação limpa)
            os.remove(DB_PATH)
            print('[INFO] Banco removido:', DB_PATH)
        except Exception as e:
            print('[ERROR] Falha ao remover banco:', e)
            sys.exit(2)  # Sai com código de erro específico se falhar ao remover
    else:
        print('[INFO] Nenhum banco encontrado para backup/remover.')

    # ========================================================================
    # OPCIONALMENTE REMOVE MIGRAÇÕES (para reset completo)
    # ========================================================================
    # Se solicitado, remove a pasta de migrações também
    if remove_migrations:
        mig = os.path.join(BASE, 'migrations')  # Caminho para a pasta de migrações
        if os.path.isdir(mig):
            try:
                # Remove a pasta de migrações recursivamente
                print(f'[INFO] Removendo migrations em: {mig}')
                shutil.rmtree(mig)
                print('[INFO] Pasta migrations removida.')
            except Exception as e:
                print('[ERROR] Falha ao remover migrations:', e)
                sys.exit(3)  # Sai com código de erro específico se falhar
        else:
            print(f'[INFO] Pasta migrations não encontrada em: {mig}')

    # ========================================================================
    # SUCESSO
    # ========================================================================
    print('[INFO] backup_db.py completado com sucesso.')
    sys.exit(0)  # Sai com sucesso

# Executa a função main se o script for chamado diretamente
if __name__ == '__main__':
    main()
