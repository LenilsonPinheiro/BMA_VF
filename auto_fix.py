# -*- coding: utf-8 -*-
"""
==============================================================================
Script de Automação e Reparo de Banco de Dados
==============================================================================

Este script (`auto_fix.py`) orquestra uma série de tarefas de manutenção para
garantir que o ambiente da aplicação Flask e o banco de dados estejam em um
estado consistente e atualizado, especialmente durante o desenvolvimento.

Ele é projetado para ser executado automaticamente no início da aplicação (por
exemplo, via `run.ps1`) para prevenir e corrigir problemas comuns relacionados
a migrações de banco de dados (Alembic/Flask-Migrate).

Principais Funcionalidades:
---------------------------
- **Configuração de Logging:** Centraliza todos os logs (incluindo `print`)
  em um arquivo `run_log.txt` para fácil depuração.
- **Gerenciamento de Ambiente:** Garante a criação de diretórios essenciais
  como a pasta `instance`.
- **Backup de Banco de Dados:** Cria backups automáticos do banco de dados
  antes de realizar operações críticas.
- **Gerenciamento de Migrações:**
    - Inicializa o `Flask-Migrate` se necessário (`flask db init`).
    - Estampa o banco de dados com a revisão mais recente (`flask db stamp head`)
      para criar uma linha de base em bancos de dados novos.
    - Gera novas migrações automaticamente (`flask db migrate`) se detectar
      mudanças nos modelos.
    - Aplica todas as migrações pendentes (`flask db upgrade`).
- **Reparo de Inconsistências:** Inclui lógica para detectar e tentar corrigir
  problemas na tabela `alembic_version` que podem impedir as migrações de
  funcionarem corretamente.

Como Usar:
-----------
- **Uso Automático:** Geralmente chamado por um script de inicialização como
  `run.ps1`.
- **Uso Manual:** `python auto_fix.py`
- **Reset Completo:** `python auto_fix.py clean` (cria um backup e remove o
  banco de dados e a pasta de migrações para um recomeço limpo).

==============================================================================
AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.)
==============================================================================
QUALQUER ALTERAÇÃO NESTE ARQUIVO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA
INTEIRO DO PROJETO FOR ATUALIZADO. Isso inclui documentação, comentários e
scripts de diagnóstico. NÃO FAÇA MUDANÇAS ISOLADAS.
==============================================================================

Autor: Lenilson Pinheiro
Data: Janeiro 2025
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
# 1. CONFIGURAÇÃO DE CAMINHOS
# Definição de caminhos absolutos para diretórios e arquivos críticos.
# Usar caminhos absolutos evita problemas de execução a partir de diferentes
# diretórios de trabalho.
# ===========================================================================
BASE = os.path.abspath(os.path.dirname(__file__))
LOG_PATH = os.path.join(BASE, 'run_log.txt')
DB_PATH = os.path.join(BASE, 'instance', 'site.db')
BACKUP_DIR = os.path.join(BASE, 'instance', 'backups')
VERSIONS_DIR = os.path.join(BASE, 'migrations', 'versions')
MIGRATIONS_DIR = os.path.join(BASE, 'migrations')

# ===========================================================================
# 2. CONFIGURAÇÃO DE LOGGING
# Configura um sistema de logging duplo:
#   1. Um logger padrão que grava em 'run_log.txt'.
#   2. A função `print` é sobrescrita (`monkey-patched`) para que todas as
#      chamadas a `print()` sejam exibidas no console e também enviadas
#      para o arquivo de log, garantindo a captura de todas as saídas.
# ===========================================================================
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

# Logger a nível de módulo para uso explícito, permitindo filtragem por ferramentas de CI.
logger = logging.getLogger('bma_vf')
logger.setLevel(logging.INFO)

# Preserva a função 'print' original e a substitui por uma que também loga.
_original_print = builtins.print
def _print_and_log(*args, **kwargs):
    """
    Wrapper para a função `print` que também envia a saída para o logger.
    
    Isso garante que todas as mensagens impressas via `print()` em qualquer
    parte do script sejam capturadas no arquivo de log `run_log.txt`.
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
    Executa um comando de subprocesso de forma segura e captura sua saída.

    Esta função é um wrapper para `subprocess.run` que lida com a captura
    de stdout/stderr, logging da execução e tratamento de erros comuns como
    `FileNotFoundError`.

    Args:
        cmd (list): O comando e seus argumentos como uma lista de strings.
        env (dict, optional): Variáveis de ambiente a serem usadas.
                              Usa o ambiente atual se for None.

    Returns:
        tuple[int, str, str]: Uma tupla contendo o código de retorno,
                              a saída padrão (stdout) e a saída de erro (stderr).
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
    Garante que a pasta 'instance' exista no diretório base do projeto.
    
    Esta pasta é crucial para armazenar arquivos específicos da instância da
    aplicação que não devem ser versionados, como o banco de dados SQLite.
    """
    instance_path = os.path.join(BASE, 'instance')
    if not os.path.isdir(instance_path):
        os.makedirs(instance_path, exist_ok=True)
        print(f"[INFO] Pasta 'instance' criada: {instance_path}")
    else:
        print(f"[INFO] Pasta 'instance' já existe: {instance_path}")

def backup_db(remove_db: bool = False, remove_migrations: bool = False):
    """
    Cria um backup do banco de dados e, opcionalmente, limpa o ambiente.

    Args:
        remove_db (bool, optional): Se True, apaga o arquivo `site.db` original
                                    após o backup bem-sucedido. Defaults to False.
        remove_migrations (bool, optional): Se True, apaga a pasta `migrations`
                                            inteira. Útil para um reset completo.
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
    Lista todas as revisões de migração disponíveis no sistema de arquivos.

    Varre o diretório `migrations/versions` e extrai os identificadores de
    revisão dos nomes dos arquivos, ordenando-os por data de modificação
    para garantir a ordem cronológica correta.

    Returns:
        list[str]: Uma lista ordenada de identificadores de revisão.
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
    Estabelece e retorna uma conexão direta com o banco de dados SQLite.
    
    Returns:
        sqlite3.Connection: Objeto de conexão com o banco de dados.
    """
    print(f"[INFO] Tentando conectar ao banco de dados em: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def get_current_db_revision(conn: sqlite3.Connection) -> str or None:
    """
    Obtém a revisão atual do banco de dados a partir da tabela 'alembic_version'.

    Tenta ler a coluna `version_num` e, como fallback, outras colunas para
    maior compatibilidade.

    Args:
        conn (sqlite3.Connection): Uma conexão ativa com o banco de dados.
        
    Returns:
        str or None: O identificador da revisão atual ou None se não for encontrado.
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
    Define ou redefine a revisão do Alembic no banco de dados.

    Esta função apaga a tabela `alembic_version` existente (se houver) e a
    recria com um único registro contendo a nova revisão. É uma operação
    destrutiva usada para forçar o estado de revisão do banco de dados.

    Args:
        conn (sqlite3.Connection): Uma conexão ativa com o banco de dados.
        new_rev (str): O novo identificador de revisão a ser definido.
        
    Returns:
        bool: True se a operação for bem-sucedida, False caso contrário.
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
    Remove a tabela `alembic_version` do banco de dados.

    Usado para limpar o estado de migração do banco de dados, por exemplo,
    quando nenhuma revisão de migração existe mais no sistema de arquivos.

    Args:
        conn (sqlite3.Connection): Uma conexão ativa com o banco de dados.
        
    Returns:
        bool: True se a tabela foi removida com sucesso ou se já não existia.
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
    Tenta reparar o estado do Alembic, alinhando a revisão no banco de dados
    com as migrações disponíveis no sistema de arquivos.

    Se a revisão do DB for inválida ou não existir, ele a define para a mais
    recente disponível. Se não houver revisões de migração, ele remove a
    tabela `alembic_version`.

    Returns:
        int: Código de saída (0 para sucesso, diferente de 0 para erro).
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
    Garante que o diretório de migrações do Flask-Migrate exista.

    Se a pasta `migrations` não for encontrada, executa o comando `flask db init`
    para criá-la.

    Args:
        env (dict): O ambiente a ser usado para executar o comando `flask`.

    Returns:
        int: O código de retorno do comando `flask db init` (ou 0 se nada
             precisou ser feito).
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
    Ponto de entrada principal do script.
    
    Orquestra a sequência de operações de backup, verificação e migração
    para garantir que o banco de dados esteja em um estado consistente e pronto
    para a aplicação.

    Args:
        argv (list): A lista de argumentos da linha de comando. Suporta
                     o argumento 'clean' para forçar um reset completo do
                     banco de dados e das migrações.
                     
    Returns:
        int: 0 em caso de sucesso, ou um código de erro diferente de zero
             em caso de falha.
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
