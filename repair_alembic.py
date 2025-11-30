import os
import sqlite3
import sys
import glob

BASE = os.path.abspath(os.path.dirname(__file__))
DB = os.path.join(BASE, 'instance', 'site.db')
VERSIONS_DIR = os.path.join(BASE, 'migrations', 'versions')

def list_available_revisions():
    revs = []
    if os.path.isdir(VERSIONS_DIR):
        for p in glob.glob(os.path.join(VERSIONS_DIR, '*.py')):
            fn = os.path.basename(p)
            if '_' in fn:
                rev = fn.split('_', 1)[0]
                revs.append((rev, os.path.getmtime(p)))
    # sort by mtime (oldest -> newest)
    revs.sort(key=lambda x: x[1])
    return [r for r,_ in revs]

def get_current_db_revision(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
    if not cur.fetchone():
        return None
    # tenta colunas comuns
    for col in ('version_num','version'):
        try:
            cur.execute(f"SELECT {col} FROM alembic_version LIMIT 1")
            row = cur.fetchone()
            if row:
                return row[0]
        except sqlite3.OperationalError:
            continue
    # fallback: pega primeira coluna retornada
    try:
        cur.execute("SELECT * FROM alembic_version LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
    except Exception:
        return None
    return None

def set_db_revision(conn, new_rev):
    cur = conn.cursor()
    # drop/create canonical table with column version_num to be consistent
    try:
        cur.execute("DROP TABLE IF EXISTS alembic_version")
        cur.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
        cur.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (new_rev,))
        conn.commit()
        print(f"[INFO] alembic_version atualizado para: {new_rev}")
        return True
    except Exception as e:
        print("[ERROR] Falha ao atualizar alembic_version:", e)
        conn.rollback()
        return False

def remove_db_revision_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS alembic_version")
        conn.commit()
        print("[INFO] alembic_version removida (se existia).")
        return True
    except Exception as e:
        print("[ERROR] Falha ao remover alembic_version:", e)
        conn.rollback()
        return False

def main():
    if not os.path.exists(DB):
        print(f"[ERROR] Banco nao encontrado em {DB}")
        sys.exit(10)

    available = list_available_revisions()
    try:
        conn = sqlite3.connect(DB)
    except Exception as e:
        print("[ERROR] Nao foi possivel abrir o DB:", e)
        sys.exit(11)

    try:
        current = get_current_db_revision(conn)
        print("[INFO] Revisao atual no DB:", current)
        print("[INFO] Revisions disponiveis:", available)
        if current and current in available:
            print("[INFO] Revisao atual existe nos arquivos de migration. Nada a fazer.")
            conn.close()
            sys.exit(0)
        if available:
            # escolher a mais recente disponível (ultima da lista ordenada por mtime)
            chosen = available[-1]
            print(f"[WARN] Revisao ausente. Ajustando alembic_version para a mais recente disponivel: {chosen}")
            ok = set_db_revision(conn, chosen)
            conn.close()
            sys.exit(0 if ok else 12)
        else:
            # nao ha migrations/versions -> remover alembic_version para que stamp/head funcione
            print("[WARN] Nenhuma revision encontrada em migrations/versions. Removendo alembic_version (se existir).")
            ok = remove_db_revision_table(conn)
            conn.close()
            sys.exit(0 if ok else 13)
    except Exception as e:
        print("[ERROR] Erro inesperado:", e)
        try:
            conn.close()
        except:
            pass
        sys.exit(14)

if __name__ == '__main__':
    main()
