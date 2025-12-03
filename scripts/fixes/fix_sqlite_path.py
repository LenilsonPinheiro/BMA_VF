#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CORREÇÃO ATÔMICA UNIFICADA (SINTAXE + DB + INICIALIZAÇÃO)
Autor: Senior Lead Architect
Data: 2025

Este script realiza três operações críticas em um único passo:
1.  **Reparo de Sintaxe:** Verifica e corrige o bloco 'app.config.from_mapping', 
    garantindo que o parêntese de fechamento ')' exista.
2.  **Configuração de Banco de Dados Híbrida:** - No GCP (App Engine): Força o uso de '/tmp/site.db' (único local com permissão de escrita).
    - Localmente: Usa 'instance/site.db'.
3.  **Inicialização Forçada:** Injeta código para executar 'db.create_all()' 
    na inicialização do servidor, prevenindo erros 502/Worker Timeout.
"""
import os
import re
import sys

# Define caminhos absolutos
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
INIT_FILE = os.path.join(ROOT_DIR, 'BelarminoMonteiroAdvogado', '__init__.py')

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def log(msg, type="INFO"):
    """Registra mensagens coloridas no console."""
    prefix = f"[{type}]"
    if type == "INFO":
        color = Colors.GREEN
    elif type == "WARN":
        color = Colors.YELLOW
    elif type == "ERROR":
        color = Colors.RED
    else:
        color = Colors.RESET
    
    print(f"{color}{prefix} {msg}{Colors.RESET}")

def fix_sqlite_and_syntax():
    """Função principal de correção."""
    log(f"Iniciando análise do arquivo: {INIT_FILE}")
    
    if not os.path.exists(INIT_FILE):
        log("ERRO FATAL: Arquivo __init__.py não encontrado.", "ERROR")
        return

    with open(INIT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)
    
    # --- PASSO 1: LIMPEZA DE LIXO DE INJEÇÕES ANTERIORES ---
    log("1. Limpando injeções de código antigas ou duplicadas...")
    
    # Remove blocos de configuração de DB antigos (identificados por comentários ou padrões)
    content = re.sub(r'# --- CONFIGURAÇÃO DE DB DINÂMICA.*?# --- FIM DA CONFIGURAÇÃO DB DINÂMICA ---', '', content, flags=re.DOTALL)
    content = re.sub(r'# --- INICIALIZAÇÃO CRÍTICA.*?return app', 'return app', content, flags=re.DOTALL)
    
    # Remove linhas soltas que podem ter sobrado de tentativas manuais
    content = re.sub(r"app\.config\['SQLALCHEMY_DATABASE_URI'\].*?\n", "", content)
    content = re.sub(r"app\.config\['SQLALCHEMY_TRACK_MODIFICATIONS'\].*?\n", "", content)

    # --- PASSO 2: CORREÇÃO DE SINTAXE (O PARÊNTESE PERDIDO) ---
    log("2. Verificando integridade sintática do 'app.config.from_mapping'...")
    
    # Regex para encontrar o bloco from_mapping. 
    # Procura por "from_mapping(" até "WTF_CSRF_ENABLED=True" (que é a última linha conhecida deste bloco).
    mapping_pattern = re.compile(r'(app\.config\.from_mapping\([\s\S]*?WTF_CSRF_ENABLED=True.*?)(\s*\n)', re.DOTALL)
    
    match = mapping_pattern.search(content)
    if match:
        block = match.group(1)
        # Verifica se o bloco termina com parêntese
        if not block.strip().endswith(')'):
            log("AVISO: Parêntese de fechamento não encontrado. Corrigindo...", "WARN")
            # Adiciona o parêntese faltante
            corrected_block = block.rstrip() + "\n    )"
            content = content.replace(block, corrected_block)
            log("Sintaxe corrigida com sucesso.")
    else:
        log("AVISO: Bloco 'from_mapping' não encontrado com o padrão esperado. Verifique manualmente se houver erros.", "WARN")

    # --- PASSO 3: INJEÇÃO DA NOVA LÓGICA DE BANCO DE DADOS ---
    log("3. Injetando lógica de Banco de Dados (Custo Zero / Híbrido)...")

    # Garante importação do os no topo do arquivo
    if 'import os' not in content:
        content = 'import os\n' + content

    # Bloco de Código: Configuração DB
    DB_CONFIG_BLOCK = """
    # --- CONFIGURAÇÃO DE DB DINÂMICA (SQLITE /TMP - CUSTO ZERO) ---
    # Lógica inteligente para alternar entre ambiente Local e GCP
    if test_config is None:
        if os.environ.get('GAE_ENV') == 'standard':
            # No GCP App Engine, apenas /tmp permite escrita
            DB_URI = 'sqlite:////tmp/site.db'
            app.logger.info("MODO GCP: Usando SQLite persistente em /tmp/site.db")
        else:
            # Localmente, usa a pasta instance padrão
            DB_URI = f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
            app.logger.info(f"MODO LOCAL: Usando SQLite em {app.instance_path}/site.db")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    else:
        app.config.update(test_config)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # --- FIM DA CONFIGURAÇÃO DB DINÂMICA ---
    """

    # Encontra onde injetar (logo após o from_mapping corrigido)
    # Procura pelo fechamento ')' do from_mapping
    inject_point_regex = re.compile(r'(app\.config\.from_mapping\([\s\S]*?\))', re.DOTALL)
    match = inject_point_regex.search(content)
    
    if match:
        # Injeta logo após o parêntese de fechamento
        content = content[:match.end()] + "\n" + DB_CONFIG_BLOCK + content[match.end():]
    else:
        # Fallback: tenta injetar antes de db.init_app se o regex acima falhar
        log("AVISO: Ponto de injeção padrão não encontrado. Tentando antes de db.init_app...", "WARN")
        content = content.replace("db.init_app(app)", DB_CONFIG_BLOCK + "\n    db.init_app(app)")

    # --- PASSO 4: INJEÇÃO DA INICIALIZAÇÃO FORÇADA (PREVINE 502) ---
    log("4. Injetando inicialização forçada do DB (db.create_all)...")

    INIT_DB_CODE = """
    # --- INICIALIZAÇÃO CRÍTICA DO BANCO DE DADOS (GCP SAFE) ---
    # Garante que as tabelas existam antes da primeira requisição
    with app.app_context():
        try:
            # Verifica se uma tabela essencial existe (ex: 'user')
            inspector = db.inspect(db.engine)
            if not inspector.has_table("user"): 
                app.logger.info("Inicialização: Tabela 'user' não encontrada. Criando DB...")
                db.create_all()
                # Tenta popular dados apenas se a função existir no escopo
                if 'ensure_essential_data' in locals() or 'ensure_essential_data' in globals():
                    ensure_essential_data()
                app.logger.info("Inicialização: DB criado e populado com sucesso.")
            else:
                app.logger.info("Inicialização: DB já existe. Pulando criação.")
        except Exception as e:
            app.logger.error(f"FALHA NA INICIALIZAÇÃO DO DB: {e}")
            # Não aborta para permitir tentativa de recuperação pelo Flask
            
    return app
    """

    # Remove qualquer 'return app' existente no final para evitar código inalcançável
    # Procura o último 'return app' (indentado)
    content = re.sub(r'\s*return app\s*$', '', content.strip())
    
    # Adiciona o novo bloco de retorno
    content += "\n" + INIT_DB_CODE

    # --- FINALIZAÇÃO ---
    with open(INIT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    log("="*50)
    log("SUCESSO: Arquivo __init__.py atualizado e corrigido.")
    log(f"Tamanho original: {original_len} bytes -> Novo tamanho: {len(content)} bytes")
    log("Ações realizadas:")
    log("  - Sintaxe de 'from_mapping' verificada/corrigida.")
    log("  - Configuração de SQLite '/tmp' injetada.")
    log("  - Inicialização 'db.create_all()' adicionada.")
    log("="*50)
    log("PRÓXIMO PASSO: Execute 'gcloud app deploy app.yaml'")

if __name__ == "__main__":
    try:
        fix_sqlite_and_syntax()
    except Exception as e:
        log(f"ERRO DE SCRIPT: {e}", "ERROR")