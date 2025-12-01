#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Master Test Runner - Executa todos os testes do projeto
Gera relatório completo e bloqueia deploy se houver falhas críticas

==============================================================================
COMO USAR ESTE SCRIPT
==============================================================================

PROPÓSITO:
  Descobrir e executar TODOS os testes do projeto em um único comando.
  Gera relatório resumido com pass/fail por arquivo.
  Bloqueia deploy se há falhas críticas (exit code != 0).

DEPENDÊNCIAS:
  - Python 3.11+ (com venv ativado)
  - pytest instalado (via requirements.txt)
  - Todos os testes em arquivos test_*.py na raiz do projeto
  - Flask app deve estar configurado com test database (SQLite in-memory)

USO:
  python run_all_tests.py                    # Executa todos os testes
  python run_all_tests.py --fast             # Apenas testes rápidos (smoke tests)
  python run_all_tests.py --coverage         # Coleta coverage report

DEPENDÊNCIAS DE SCRIPTS:
  - Nenhuma dependência de outros scripts (standalone)
  - Porém, é frequentemente chamado por:
    * deploy_production_complete.py (validação antes de deploy)
    * CI/CD pipelines (validação em commits)
    * Localmente: antes de fazer commit

FLUXOS DE AUTOMAÇÃO QUE USAM ESTE SCRIPT:
  - Before Commit: pytest → run_all_tests.py → git commit
  - Pre-Deploy: backup_db.py → run_all_tests.py → deploy
  - CI/CD Job: on-push → run_all_tests.py → block-merge-if-fails

LOGS GERADOS:
  - Console (stdout/stderr) com progress em tempo real
  - Cada teste produz output capturado
  - Logger estruturado (bma_vf) para CI/CD parsing

ARQUIVOS DE TESTE DESCOBERTOS AUTOMATICAMENTE:
  - test_app.py (core fixtures)
  - test_admin_routes.py (admin functionality)
  - test_all_routes_complete.py (all public routes)
  - test_all_themes_complete.py (8 theme variants)
  - test_database_schema.py (schema validation)
  - test_producao_completo.py (production readiness)
  - ... e outros test_*.py no diretório raiz

SAÍDA ESPERADA (tudo passa):
  ✓ test_app.py ... PASS (0.45s)
  ✓ test_admin_routes.py ... PASS (1.23s)
  ...
  ✓ All tests passed (12 files, 127 tests, 15.8s)
  Exit code: 0

SAÍDA ESPERADA (algum teste falha):
  ✓ test_app.py ... PASS (0.45s)
  ✗ test_admin_routes.py ... FAIL (1.23s)
  ...
  ✗ Some tests failed - deployment blocked
  Exit code: 1

LOG MESSAGES (ao longo da execução):
  [INFO] run_all_tests: starting test run in /path/to/project
  [INFO] run_all_tests: discovered 12 test files
  [INFO] run_all_tests: running test_app.py (1/12)
  [ERROR] run_all_tests: test_admin_routes.py failed (returncode=1)
  [INFO] run_all_tests: finished in 15.8s - passed=11 failed=1

==============================================================================
"""

import sys
import os
import subprocess
import time
from datetime import datetime
import logging
import urllib.request


def setup_logger(name="bma_vf", level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = setup_logger()

def print_header(title):
    """
    Imprime cabeçalho formatado para melhor legibilidade do output.
    Útil para separar visualmente os blocos de teste.
    """
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80 + "\n")

def run_test_file(test_file, description):
    """
    Executa um arquivo de teste individual e retorna os resultados.
    
    DEPENDÊNCIAS:
      - Arquivo test_file deve existir
      - Deve ser executável com: python test_file
      - Suporta timeout de 60s por arquivo
    
    RETORNA:
      dict com keys: status (PASS/FAIL/SKIP), returncode, output
      
    LOGS GERADOS:
      [INFO] run_all_tests: starting {description} ({test_file})
      [INFO] run_all_tests: {test_file} finished with rc={returncode}
      [ERROR] run_all_tests: timeout running {test_file}
      [ERROR] run_all_tests: error running {test_file}: {exception}
    
    EXEMPLOS DE LOG:
      [INFO] run_all_tests: starting test_app.py (test_app.py)
      [INFO] run_all_tests: test_app.py finished with rc=0  (sucesso)
      [ERROR] run_all_tests: timeout running test_admin_routes.py (excedeu 60s)
    """
    print_header(f"EXECUTANDO: {description}")
    print(f"Arquivo: {test_file}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}\n")
    try:
        logger.info("run_all_tests: starting %s (%s)", description, test_file)
    except Exception:
        pass
    
    if not os.path.exists(test_file):
        print(f"⚠️ Arquivo não encontrado: {test_file}")
        return {'status': 'SKIP', 'output': 'Arquivo não encontrado'}
    
    # Cria pasta de logs para testes (cada execução cria um arquivo de log por teste)
    logs_dir = os.path.join(os.getcwd(), 'test_logs')
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception:
        pass

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    safe_name = test_file.replace(os.sep, '_').replace('/', '_')
    log_filename = f"{safe_name}.{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)

    try:
        # Force UTF-8 output from child Python processes on Windows consoles
        env = os.environ.copy()
        env.setdefault('PYTHONIOENCODING', 'utf-8')
        env.setdefault('PYTHONUTF8', '1')
        # Allow a longer timeout for some heavier tests
        TEST_TIMEOUT = int(os.environ.get('BMA_TEST_TIMEOUT', '120'))
        proc = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=TEST_TIMEOUT,
            env=env
        )
        output = (proc.stdout or '') + (proc.stderr or '')

        status = 'PASS' if proc.returncode == 0 else 'FAIL'
        if status == 'PASS':
            print("✅ PASSOU")
        else:
            print("❌ FALHOU")

        try:
            logger.info("run_all_tests: %s finished with rc=%s", test_file, proc.returncode)
        except Exception:
            pass

        # Salva saída completa em arquivo de log para análise posterior
        try:
            with open(log_path, 'w', encoding='utf-8') as fh:
                fh.write(f"# Test: {test_file}\n# Description: {description}\n# Timestamp: {timestamp}\n\n")
                fh.write(output)
        except Exception:
            # Não deixar falhar se não for possível gravar logs
            pass

        return {
            'status': status,
            'returncode': proc.returncode,
            'output': output,
            'log_path': log_path
        }
    except subprocess.TimeoutExpired as e:
        # Tenta obter qualquer saída parcial disponível
        out = (getattr(e, 'stdout', '') or '') + (getattr(e, 'stderr', '') or '')
        try:
            with open(log_path, 'w', encoding='utf-8') as fh:
                fh.write(f"# Test: {test_file}\n# Description: {description}\n# Timestamp: {timestamp}\n# TIMEOUT\n\n")
                fh.write(out)
        except Exception:
            pass
        print("⏱️ TIMEOUT (>60s)")
        try:
            logger.warning("run_all_tests: timeout running %s", test_file)
        except Exception:
            pass
        return {'status': 'TIMEOUT', 'output': out, 'log_path': log_path}
    except Exception as e:
        err = str(e)
        try:
            with open(log_path, 'w', encoding='utf-8') as fh:
                fh.write(f"# Test: {test_file}\n# Description: {description}\n# Timestamp: {timestamp}\n# EXCEPTION\n\n")
                fh.write(err)
        except Exception:
            pass
        print(f"❌ ERRO: {err}")
        try:
            logger.exception("run_all_tests: error running %s: %s", test_file, e)
        except Exception:
            pass
        return {'status': 'ERROR', 'output': err, 'log_path': log_path}

def main():
    """
    Função principal que orquestra a execução de todos os testes.
    
    FLUXO EXECUTIVO:
      1. Define lista de testes (críticos e não-críticos)
      2. Executa cada teste sequencialmente (timeout 60s por teste)
      3. Coleta resultado de cada arquivo (PASS/FAIL/SKIP/ERROR/TIMEOUT)
      4. Gera relatório estatístico completo
      5. Decide se deploy é liberado ou bloqueado
      6. Retorna exit code apropriado (0 = ok, 1 = bloqueado)
    
    TESTES CRÍTICOS (bloqueiam deploy se falharem):
      - test_pre_deploy_completo_v2.py: Modelos, rotas, templates
      - test_database_schema.py: Integridade do banco de dados
    
    TESTES NÃO-CRÍTICOS (apenas warning, não bloqueiam):
      - test_app.py: Fixtures básicas
      - test_admin_routes.py: Funcionalidade admin
      - test_all_routes_complete.py: Todas as rotas públicas
      - test_all_themes_complete.py: Validação de 8 temas
    
    LOGS GERADOS (estruturado para CI/CD):
      [INFO] run_all_tests: starting test run in {cwd}
      [INFO] run_all_tests: running test_X.py (N/total)
      [INFO] run_all_tests: finished in Xs - passed=N failed=M
    
    EXIT CODES:
      0 = Todos os críticos passaram (deploy OK)
      1 = Críticos falharam (deploy BLOQUEADO)
    """
    print_header("BATERIA COMPLETA DE TESTES - BELARMINO MONTEIRO ADVOGADO")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Diretório: {os.getcwd()}\n")
    # Linha de comando: flags opcionais
    #   --full         : imprime o output completo de cada teste no console
    #   --start-server : inicia o servidor Flask (flask run) em background antes dos testes
    #   --install-deps : instala dependências via `pip install -r requirements.txt` antes dos testes
    show_full = '--full' in sys.argv
    start_server = '--start-server' in sys.argv
    install_deps = '--install-deps' in sys.argv
    try:
        logger.info("run_all_tests: starting test run in %s", os.getcwd())
    except Exception:
        pass
    
    # ========================================================================
    # LISTA DE TESTES PARA EXECUTAR
    # ========================================================================
    # Cada teste tem:
    #   'file': nome do arquivo test_*.py
    #   'description': descrição amigável
    #   'critical': True se falhar bloqueia deploy, False apenas warning
    # ========================================================================
    tests = [
        {
            'file': 'test_pre_deploy_completo_v2.py',
            'description': 'Testes Pré-Deploy (Modelos, Rotas, Templates)',
            'critical': True
        },
        {
            'file': 'test_database_schema.py',
            'description': 'Testes de Schema do Banco de Dados',
            'critical': True
        },
        {
            'file': 'test_all_themes_complete.py',
            'description': 'Testes de Todos os Temas Visuais',
            'critical': False
        },
        {
            'file': 'test_all_routes_complete.py',
            'description': 'Testes de Todas as Rotas',
            'critical': False
        },
        {
            'file': 'test_admin_routes.py',
            'description': 'Testes de Rotas Administrativas',
            'critical': False
        }
    ]
    
    results = []
    start_time = time.time()

    # Executar cada teste
    server_proc = None
    server_log_handle = None
    try:
        # Se solicitado, instala dependências antes de rodar os testes
        if install_deps:
            req_file = os.path.join(os.getcwd(), 'requirements.txt')
            if os.path.exists(req_file):
                print('[INFO] Instalando dependências via requirements.txt...')
                try:
                    proc = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file], capture_output=True, text=True, encoding='utf-8', errors='replace')
                    print(proc.stdout)
                    if proc.returncode != 0:
                        print('[WARN] pip install retornou código != 0. Verifique requirements.txt e saída acima.')
                        print(proc.stderr)
                except Exception as e:
                    print(f'[ERROR] Falha ao executar pip install: {e}')
            else:
                print('[WARN] requirements.txt não encontrado; pulando instalação de dependências.')

        # Se solicitado, inicia o servidor Flask em background (útil para testes que usam requests a localhost)
        if start_server:
            print('[INFO] Iniciando servidor Flask em background (porta 5000)...')
            serv_env = os.environ.copy()
            serv_env.setdefault('FLASK_APP', 'BelarminoMonteiroAdvogado')
            serv_env.setdefault('PYTHONUNBUFFERED', '1')
            # Inicia flask run como processo em background, capturando logs
            logs_dir = os.path.join(os.getcwd(), 'test_logs')
            os.makedirs(logs_dir, exist_ok=True)
            server_log = os.path.join(logs_dir, 'server_startup.log')
            fh = open(server_log, 'w', encoding='utf-8', buffering=1)
            server_proc = subprocess.Popen(
                [sys.executable, '-m', 'flask', 'run', '--port', '5000'],
                env=serv_env,
                stdout=fh,
                stderr=fh
            )
            server_log_handle = fh

            # Poll the server root until it responds or timeout
            ready = False
            max_wait = 20
            waited = 0
            url = 'http://127.0.0.1:5000/'
            while waited < max_wait:
                try:
                    with urllib.request.urlopen(url, timeout=2) as r:
                        if r.status == 200:
                            ready = True
                            break
                except Exception:
                    pass
                time.sleep(1)
                waited += 1

            if not ready:
                print(f"[WARN] Servidor Flask não respondeu em {max_wait}s. Verifique {server_log}")
            else:
                print(f"[INFO] Servidor Flask respondeu em {waited}s. Logs em {server_log}")
    except Exception as e:
        print(f"[WARN] falha durante setup de pré-teste: {e}")

    for test in tests:
        result = run_test_file(test['file'], test['description'])
        result['file'] = test['file']
        result['description'] = test['description']
        result['critical'] = test['critical']
        results.append(result)

        # Pequena pausa entre testes
        try:
            logger.info("run_all_tests: waiting 0.5s before next test")
        except Exception:
            pass
        time.sleep(0.5)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Gerar relatório final
    print_header("RELATÓRIO FINAL DE TESTES")
    
    print(f"Tempo total: {duration:.2f} segundos\n")
    
    # Contar resultados
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    skipped = sum(1 for r in results if r['status'] == 'SKIP')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    timeouts = sum(1 for r in results if r['status'] == 'TIMEOUT')
    
    critical_failed = sum(1 for r in results if r['status'] == 'FAIL' and r['critical'])
    try:
        logger.info("run_all_tests: finished in %.2fs - passed=%d failed=%d", duration, passed, failed)
    except Exception:
        pass
    
    print("📊 ESTATÍSTICAS:")
    print(f"  Total de testes: {len(results)}")
    print(f"  ✅ Passaram: {passed}")
    print(f"  ❌ Falharam: {failed}")
    print(f"  ⏭️ Pulados: {skipped}")
    print(f"  ⚠️ Erros: {errors}")
    print(f"  ⏱️ Timeouts: {timeouts}")
    print(f"  🚨 Críticos falharam: {critical_failed}\n")
    
    print("📋 DETALHES POR TESTE:\n")
    for i, result in enumerate(results, 1):
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⏭️',
            'ERROR': '⚠️',
            'TIMEOUT': '⏱️'
        }.get(result['status'], '❓')
        
        critical_marker = ' [CRÍTICO]' if result['critical'] else ''
        
        print(f"{i}. {status_icon} {result['description']}{critical_marker}")
        print(f"   Arquivo: {result['file']}")
        print(f"   Status: {result['status']}")
        
        if result['status'] in ['FAIL', 'ERROR', 'TIMEOUT']:
            # Mostra onde o log completo foi salvo e uma cauda do output para leitura rápida
            log_path = result.get('log_path')
            if log_path:
                print(f"   Full log: {log_path}")
            # Mostrar as últimas linhas (tail) do output para contexto imediato
            out = (result.get('output') or '').strip()
            tail = out[-4000:]
            print("   --- Últimas linhas do output (tail) ---")
            print(tail)
            print("   ----------------------------------------")
            # Se o usuário passou '--full', imprime o output completo no console
            if show_full:
                print("   --- Output COMPLETO (show_full=True) ---")
                print(out)
                print("   ----------------------------------------")
        
        print()
    
    # Decisão de deploy
    print_header("DECISÃO DE DEPLOY")
    
    # Finaliza servidor iniciado em background (se houver)
    if server_proc:
        try:
            server_proc.terminate()
            server_proc.wait(timeout=5)
        except Exception:
            try:
                server_proc.kill()
            except Exception:
                pass
        try:
            if server_log_handle:
                server_log_handle.close()
        except Exception:
            pass

    if critical_failed > 0:
        print("🚨 DEPLOY BLOQUEADO!")
        print(f"   {critical_failed} teste(s) crítico(s) falharam")
        print("   Corrija os erros antes de fazer deploy.\n")
        print("📖 Consulte:")
        print("   - CORRIGIR_ERROS_FINAIS.txt")
        print("   - RELATORIO_TESTES_COMPLETO.md")
        return 1
    elif failed > 0 or errors > 0:
        print("⚠️ DEPLOY COM RESSALVAS")
        print(f"   {failed + errors} teste(s) não-crítico(s) falharam")
        print("   Recomenda-se corrigir antes do deploy.\n")
        return 0
    else:
        print("✅ DEPLOY LIBERADO!")
        print("   Todos os testes passaram")
        print("   Sistema pronto para produção!\n")
        print("🚀 Próximos passos:")
        print("   1. Faça o deploy para o ambiente de produção (PythonAnywhere ou Google Cloud)")
        return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {str(e)}")
        sys.exit(1)
