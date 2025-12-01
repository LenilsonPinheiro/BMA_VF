"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

auto_fix.py: Script de automação para gerenciamento de ambiente e banco de dados Flask.

Este script é responsável por uma série de tarefas de manutenção para uma aplicação Flask,
incluindo:
- Configuração de logging detalhado.
- Execução segura de comandos shell.
- Garantia da existência da pasta 'instance' (para dados da aplicação, como SQLite DB).
- Backup do banco de dados SQLite.
- Gerenciamento e reparo de migrações do banco de dados usando sistema de atualizacao do banco (Alembic).
- Detecção e correção de inconsistências na tabela 'alembic_version'.
- Criação de migrações iniciais (baseline) se necessário.

É projetado para ser executado como parte do processo de inicialização da aplicação
(por exemplo, via run.bat) para garantir que o ambiente e o banco de dados estejam
sempre em um estado consistente e atualizado.

==============================================================================
COMO USAR ESTE SCRIPT
==============================================================================

PROPÓSITO:
  Este script é chamado automaticamente por run.ps1 no startup da aplicação.
  Sua função é garantir consistência do BD e ambiente antes da app iniciar.

DEPENDÊNCIAS:
  - Python 3.11+ (com venv ativado)
  - Flask e extensões (instaladas via requirements.txt)
  - Alembic/Flask-Migrate (para migrações de DB)
  - Permissão de leitura/escrita em instance/ e migrations/ folders

USO:
  Uso automático:   python auto_fix.py (via run.ps1)
  Uso manual:       python auto_fix.py
  Reset completo:   python auto_fix.py clean

ARQUIVOS DE LOG:
  Todos os eventos são registrados em: run_log.txt (raiz do projeto)
  Também aparecem no console (stdout/stderr)

FLUXOS DE AUTOMAÇÃO QUE USA ESTE SCRIPT:
  - Startup (Dev Local): run.ps1 → auto_fix.py → flask init-db → dev server
  - Recovery (BD Corrompido): backup_db.py → auto_fix.py → verify
  - Reset (Limpo Completo): backup_db.py → auto_fix.py clean → run.ps1

LOGS ESPERADOS (sucesso):
  [INFO] auto_fix: starting maintenance run
  [INFO] auto_fix: backup created at instance/backups/...
  [INFO] auto_fix: flask db upgrade succeeded
  [INFO] auto_fix: completed successfully

LOGS ESPERADOS (erro):
  [ERROR] auto_fix: unrecoverable error: {msg}
  Ver run_log.txt para detalhes completos
  Exit code: 2 (erro não recuperável)

==============================================================================
"""
import os
import sys
import shutil
import datetime
import glob
import sqlite3
import subprocess
import textwrap
import logging
import builtins

# ===========================================================================
# Configurações de Caminho
# Define caminhos absolutos para diretórios e arquivos críticos do projeto.
# ===========================================================================
BASE = os.path.abspath(os.path.dirname(__file__))
LOG_PATH = os.path.join(BASE, 'run_log.txt')
DB_PATH = os.path.join(BASE, 'instance', 'site.db')
BACKUP_DIR = os.path.join(BASE, 'instance', 'backups')
VERSIONS_DIR = os.path.join(BASE, 'migrations', 'versions')
MIGRATIONS_DIR = os.path.join(BASE, 'migrations')

# ===========================================================================
# Configuração de Logging
# Configura o sistema de logging para gravar em 'run_log.txt' e também
# exibir no console. A função 'print' é sobrescrita para também logar.
# ===========================================================================
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

# Module-level logger to use alongside the existing print->log wrapper.
# Using a named logger lets CI and other tools filter or redirect logs if needed.
logger = logging.getLogger('bma_vf')
logger.setLevel(logging.INFO)

# Preserva a função 'print' original e a substitui por uma que também loga.
_original_print = builtins.print
def _print_and_log(*args, **kwargs):
    """
    Função wrapper para 'print' que também envia a saída para o logger.
    Garanti que todas as mensagens impressas via 'print' sejam capturadas no run_log.txt.
    """
    try:
        _original_print(*args, **kwargs)
    except Exception as e:
        # Em caso de falha ao imprimir no console (e.g., stdout fechado), loga a exceção.
        logging.error(f"Erro ao imprimir no console: {e}")
    try:
        # Converte todos os argumentos para string e os une para o log.
        logging.info(' '.join(str(a) for a in args))
    except Exception as e:
        # Em caso de falha ao logar, loga a exceção para evitar interrupção.
        logging.error(f"Erro ao logar mensagem: {e}")
builtins.print = _print_and_log

def run_cmd(cmd: list, env: dict = None) -> tuple:
    """
    Executa um comando shell e captura sua saída, imprimindo-a e retornando
    o código de retorno, stdout e stderr.
    
    Args:
        cmd (list): Uma lista de strings representando o comando e seus argumentos.
        env (dict, optional): Variáveis de ambiente a serem usadas para o comando.
                              Defaults to None, usando o ambiente atual.
    
    Returns:
        tuple: (returncode, stdout, stderr) do processo executado.
    """
    print(f"[CMD] Executando: {' '.join(cmd)}")
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, check=False)
        if p.stdout:
            print(f"[STDOUT] {p.stdout.strip()}")
        if p.stderr:
            print(f"[STDERR] {p.stderr.strip()}")
        print(f"[CMD] Comando concluído com código de retorno: {p.returncode}")
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        print(f"[ERROR] Comando não encontrado ou não executável: '{cmd[0]}'. Verifique se está no PATH.")
        return 1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao executar comando '{' '.join(cmd)}': {e}")
        return 1, "", str(e)


def ensure_instance():
    """
    Garante que a pasta 'instance' exista. Esta pasta é crucial para armazenar
    arquivos específicos da instância da aplicação, como o banco de dados SQLite.
    """
    instance_path = os.path.join(BASE, 'instance')
    if not os.path.isdir(instance_path):
        os.makedirs(instance_path, exist_ok=True)
        print(f"[INFO] Pasta 'instance' criada: {instance_path}")
    else:
        print(f"[INFO] Pasta 'instance' já existe: {instance_path}")

def backup_db(remove_db: bool = False, remove_migrations: bool = False):
    """
    Realiza um backup do banco de dados SQLite existente. Opcionalmente, pode
    remover o banco de dados original e/ou a pasta de migrações após o backup.
    
    Args:
        remove_db (bool, optional): Se True, remove o arquivo do banco de dados após o backup.
                                    Defaults to False.
        remove_migrations (bool, optional): Se True, remove a pasta de migrações após o backup.
                                            Defaults to False.
    """
    if os.path.exists(DB_PATH):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        bak_name = 'site.db.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        bak_path = os.path.join(BACKUP_DIR, bak_name)
        shutil.copy2(DB_PATH, bak_path)
        print(f"[INFO] Backup do banco de dados criado em: {bak_path}")
        if remove_db:
            os.remove(DB_PATH)
            print(f"[INFO] Banco de dados removido para recriação: {DB_PATH}")
    else:
        print("[INFO] Nenhum banco de dados encontrado para backup em: {DB_PATH}")
    
    if remove_migrations and os.path.isdir(MIGRATIONS_DIR):
        print(f"[INFO] Removendo pasta de migrações: {MIGRATIONS_DIR}")
        shutil.rmtree(MIGRATIONS_DIR)
        print("[INFO] Pasta de migrações removida (remove_migrations=True).")
    elif remove_migrations:
        print(f"[INFO] Solicitação para remover migrações, mas a pasta não existe: {MIGRATIONS_DIR}")


def list_available_revisions() -> list:
    """
    Lista todas as revisões de migração disponíveis na pasta 'migrations/versions',
    ordenadas por data de modificação.
    
    Returns:
        list: Uma lista de strings, onde cada string é o identificador da revisão.
    """
    revs = []
    if os.path.isdir(VERSIONS_DIR):
        for p in glob.glob(os.path.join(VERSIONS_DIR, '*.py')):
            fn = os.path.basename(p)
            # Revisa o formato do nome do arquivo para extrair a revisão
            # Ex: 'ab12c34_add_user_table.py' -> 'ab12c34'
            if '_' in fn:
                rev = fn.split('_', 1)[0]
                revs.append((rev, os.path.getmtime(p)))
        # Ordena as revisões pela data de modificação para garantir a sequência correta.
        revs.sort(key=lambda x: x[1])
    return [r for r,_ in revs]

def get_db_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados SQLite.
    
    Returns:
        sqlite3.Connection: Objeto de conexão com o banco de dados.
    """
    print(f"[INFO] Tentando conectar ao banco de dados em: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def get_current_db_revision(conn: sqlite3.Connection) -> str or None:
    """
    Obtém a revisão atual do banco de dados a partir da tabela 'alembic_version'.
    
    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados.
        
    Returns:
        str or None: O número da revisão atual ou None se a tabela ou revisão não existir.
    """
    cur = conn.cursor()
    print("[INFO] Verificando a existência da tabela 'alembic_version'.")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
    if not cur.fetchone():
        print("[INFO] Tabela 'alembic_version' não encontrada no banco de dados.")
        return None
    
    print("[INFO] Tentando ler a revisão da tabela 'alembic_version'.")
    # Tenta colunas 'version_num' ou 'version' para compatibilidade.
    for col in ('version_num','version'):
        try:
            cur.execute(f"SELECT {col} FROM alembic_version LIMIT 1")
            row = cur.fetchone()
            if row:
                print(f"[INFO] Revisão atual do banco de dados ('{col}'): {row[0]}")
                return row[0]
        except sqlite3.OperationalError:
            print(f"[WARN] Coluna '{col}' não encontrada ou erro operacional.")
            continue
    
    # Tentativa genérica se as colunas específicas falharem.
    try:
        cur.execute("SELECT * FROM alembic_version LIMIT 1")
        row = cur.fetchone()
        if row:
            print(f"[INFO] Revisão atual do banco de dados (genérico): {row[0]}")
            return row[0]
    except Exception as e:
        print(f"[ERROR] Erro ao tentar obter revisão de forma genérica: {e}")
    
    print("[WARN] Não foi possível determinar a revisão atual do banco de dados.")
    return None

def set_db_revision(conn: sqlite3.Connection, new_rev: str) -> bool:
    """
    Define a revisão do banco de dados na tabela 'alembic_version'.
    Remove a tabela existente e a recria para garantir um estado limpo.
    
    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados.
        new_rev (str): O novo número de revisão a ser definido.
        
    Returns:
        bool: True se a revisão foi definida com sucesso, False caso contrário.
    """
    cur = conn.cursor()
    try:
        print("[INFO] Removendo tabela 'alembic_version' existente (se houver).")
        cur.execute("DROP TABLE IF EXISTS alembic_version")
        print("[INFO] Criando nova tabela 'alembic_version'.")
        cur.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
        print(f"[INFO] Inserindo nova revisão '{new_rev}' em 'alembic_version'.")
        cur.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (new_rev,))
        conn.commit()
        print(f"[SUCESSO] alembic_version atualizado para: {new_rev}")
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao atualizar alembic_version para '{new_rev}': {e}")
        conn.rollback()
        return False

def remove_db_revision_table(conn: sqlite3.Connection) -> bool:
    """
    Remove a tabela 'alembic_version' do banco de dados.
    
    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados.
        
    Returns:
        bool: True se a tabela foi removida (ou não existia), False caso contrário.
    """
    cur = conn.cursor()
    try:
        print("[INFO] Tentando remover a tabela 'alembic_version'.")
        cur.execute("DROP TABLE IF EXISTS alembic_version")
        conn.commit()
        print("[SUCESSO] alembic_version removida (se existia).")
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao remover alembic_version: {e}")
        conn.rollback()
        return False

def repair_alembic() -> int:
    """
    Tenta reparar o estado do Alembic no banco de dados, alinhando-o com as
    migrações disponíveis no sistema de arquivos.
    
    Returns:
        int: Código de retorno (0 para sucesso, diferente de 0 para erro).
    """
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Banco de dados não encontrado em {DB_PATH}. Não é possível reparar o Alembic.")
        return 10
    
    available = list_available_revisions()
    if not available:
        print("[WARN] Nenhuma revisão de migração encontrada no sistema de arquivos. Não é possível reparar o Alembic de forma significativa.")
        # Se não há revisões, a tabela alembic_version pode estar lá de forma errada.
        try:
            conn_no_revs = get_db_connection()
            remove_db_revision_table(conn_no_revs)
            conn_no_revs.close()
            return 0
        except Exception as e:
            print(f"[ERROR] Falha ao tentar remover alembic_version sem revisões disponíveis: {e}")
            return 13
    
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"[ERROR] Não foi possível abrir o banco de dados para reparo do Alembic: {e}")
        return 11
    
    try:
        current = get_current_db_revision(conn)
        print(f"[INFO] Revisão atual registrada no DB: '{current}'")
        print(f"[INFO] Revisões disponíveis no sistema de arquivos: {available}")
        
        if current and current in available:
            print("[SUCESSO] A revisão atual do DB está alinhada com as migrações disponíveis. Nada a fazer.")
            conn.close()
            return 0
        
        if available:
            # Se a revisão atual não está presente ou é inválida, ajusta para a mais recente disponível.
            chosen = available[-1] # Pega a revisão mais recente.
            print(f"[WARN] Revisão do DB ('{current}') ausente ou inválida. Ajustando 'alembic_version' para a mais recente disponível: '{chosen}'")
            ok = set_db_revision(conn, chosen)
            conn.close()
            return 0 if ok else 12
        else:
            # Caso não haja revisões disponíveis, remove a tabela alembic_version se ela existir.
            print("[WARN] Nenhuma revisão encontrada em 'migrations/versions'. Removendo 'alembic_version' (se existir) para um estado limpo.")
            ok = remove_db_revision_table(conn)
            conn.close()
            return 0 if ok else 13
            
    except Exception as e:
        print(f"[ERROR] Erro inesperado durante o reparo do Alembic: {e}")
        try:
            conn.close()
        except Exception:
            pass # Ignora erro ao fechar conexão em caso de falha.
        return 14

def ensure_migrations_initialized(env: dict) -> int:
    """
    Garante que a pasta de migrações do Alembic esteja inicializada.
    Executa 'flask db init' se a pasta 'migrations' não existir.
    
    Args:
        env (dict): Variáveis de ambiente a serem passadas para o comando 'flask'.
        
    Returns:
        int: Código de retorno do comando 'flask db init' ou 0 se já inicializado.
    """
    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"[INFO] Pasta de migrações não encontrada em {MIGRATIONS_DIR}. Inicializando migrações ('flask db init').")
        rc, out, err = run_cmd(['python', '-m', 'flask', 'db', 'init'], env=env)
        if rc != 0:
            print(f"[ERROR] 'flask db init' falhou com código {rc}. Saída: {err.strip() or out.strip()}")
            return rc
        print("[SUCESSO] Migrações inicializadas com sucesso.")
    else:
        print(f"[INFO] Pasta de migrações já existe em {MIGRATIONS_DIR}. Não é necessário inicializar.")
    return 0


def main(argv: list) -> int:
    """
    Função principal do script auto_fix.py. Orquestra todas as operações
    de manutenção e gerenciamento de banco de dados.
    
    Args:
        argv (list): Argumentos da linha de comando passados para o script.
                     Suporta o argumento 'clean' para forçar a remoção do DB
                     e das migrações antes de iniciar o processo.
                     
    Returns:
        int: Código de saída do script (0 para sucesso, diferente de 0 para erro).
    """
    # Analisa os argumentos da linha de comando para determinar se o DB e as migrações devem ser removidos.
    remove_migrations = False
    remove_db = False
    if len(argv) > 1 and argv[1].lower() == 'clean':
        print("[INFO] Argumento 'clean' detectado. Forçando remoção do banco de dados e migrações.")
        remove_db = True
        remove_migrations = True

    # Log de início (adicional ao print que já grava em run_log.txt)
    try:
        logger.info("auto_fix: starting maintenance run. argv=%s", argv)
    except Exception:
        # Se logger falhar, continuamos com prints já existentes
        pass

    # Garante que a variável FLASK_APP esteja definida no ambiente, necessária para comandos 'flask'.
    env = os.environ.copy()
    if 'FLASK_APP' not in env:
        print("[ERROR] Variável de ambiente FLASK_APP não definida. Certifique-se de que FLASK_APP está configurada antes de executar auto_fix.py.")
        return 1 # Erro fatal se FLASK_APP não estiver definida.
    print(f"[INFO] FLASK_APP está definido no ambiente como: {env['FLASK_APP']}.")

    # Registro complementar
    try:
        logger.info("auto_fix: FLASK_APP=%s", env.get('FLASK_APP'))
    except Exception:
        pass

    ensure_instance() # Garante que a pasta 'instance' exista.
    logger.info("auto_fix: ensuring instance and running backup_db (remove_db=%s, remove_migrations=%s)", remove_db, remove_migrations)
    backup_db(remove_db=remove_db, remove_migrations=remove_migrations) # Realiza backup e opcionalmente limpa.

    # Garante que as migrações do Alembic estejam inicializadas.
    rc = ensure_migrations_initialized(env)
    if rc != 0:
        logger.error("auto_fix: ensure_migrations_initialized failed with rc=%s", rc)
        print("[ERROR] Falha ao inicializar migrações. Abortando auto_fix.py.")
        return rc

    # Após 'flask db init', se 'versions' está vazia, estampamos com 'head'.
    # Isso é crucial para indicar a Alembic que o estado atual do DB é o ponto de partida.
    if not list_available_revisions():
        print("[INFO] Nenhuma revisão de migração encontrada. Estampando o banco de dados com 'head'.")
        rc_stamp, _, _ = run_cmd(['python', '-m', 'flask', 'db', 'stamp', 'head'], env=env)
        if rc_stamp != 0:
            logger.error("auto_fix: flask db stamp head failed with rc=%s", rc_stamp)
            print(f"[ERROR] Falha ao executar 'flask db stamp head'. Código: {rc_stamp}.")
            return rc_stamp
        print("[SUCESSO] Banco de dados estampado com 'head'.")

    # Tenta gerar uma nova migração (detecta mudanças no modelo).
    print("[INFO] Tentando gerar nova migração com 'flask db migrate -m \"auto migration\"'.")
    rc_migrate, out_migrate, err_migrate = run_cmd(['python', '-m', 'flask', 'db', 'migrate', '-m', 'auto migration'], env=env)
    if rc_migrate != 0:
        logger.warning("auto_fix: flask db migrate returned rc=%s", rc_migrate)
        print(f"[WARN] 'flask db migrate' retornou um erro ({rc_migrate}). Saída: {err_migrate.strip() or out_migrate.strip()}")
        # Se migrate falhar aqui, pode ser um problema de contexto ou modelo,
        # mas não deve ser por "Can't locate revision" se o stamp head funcionou.
        # Não faremos mais tentativas de reparo complexas aqui, pois o 'clean'
        # já deveria ter garantido um estado limpo.
    else:
        print("[SUCESSO] Geração de migração bem-sucedida.")

    # Aplica todas as migrações pendentes ao banco de dados.
    print("[INFO] Aplicando todas as migrações pendentes com 'flask db upgrade'.")
    rc_up, out_up, err_up = run_cmd(['python', '-m', 'flask', 'db', 'upgrade'], env=env)
    if rc_up != 0:
        logger.error("auto_fix: flask db upgrade failed with rc=%s", rc_up)
        print(f"[ERROR] 'flask db upgrade' falhou. Código: {rc_up}. Saída: {err_up.strip() or out_up.strip()}")
        return 2 # Erro crítico se o upgrade não puder ser aplicado.
    else:
        logger.info("auto_fix: flask db upgrade succeeded")
        print("[SUCESSO] Migrações aplicadas com sucesso.")

    logger.info("auto_fix: completed successfully")
    print("[SUCESSO] auto_fix.py concluído. Banco de dados está atualizado.")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
