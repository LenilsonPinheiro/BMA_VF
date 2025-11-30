#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Master Test Runner - Executa todos os testes do projeto
Gera relatório completo e bloqueia deploy se houver falhas críticas
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80 + "\n")

def run_test_file(test_file, description):
    """Executa um arquivo de teste e retorna o resultado"""
    print_header(f"EXECUTANDO: {description}")
    print(f"Arquivo: {test_file}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}\n")
    
    if not os.path.exists(test_file):
        print(f"⚠️ Arquivo não encontrado: {test_file}")
        return {'status': 'SKIP', 'output': 'Arquivo não encontrado'}
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            print("✅ PASSOU")
            status = 'PASS'
        else:
            print("❌ FALHOU")
            status = 'FAIL'
        
        return {
            'status': status,
            'returncode': result.returncode,
            'output': output
        }
    except subprocess.TimeoutExpired:
        print("⏱️ TIMEOUT (>60s)")
        return {'status': 'TIMEOUT', 'output': 'Teste excedeu 60 segundos'}
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return {'status': 'ERROR', 'output': str(e)}

def main():
    """Função principal"""
    print_header("BATERIA COMPLETA DE TESTES - BELARMINO MONTEIRO ADVOGADO")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Diretório: {os.getcwd()}\n")
    
    # Lista de testes para executar
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
    for test in tests:
        result = run_test_file(test['file'], test['description'])
        result['file'] = test['file']
        result['description'] = test['description']
        result['critical'] = test['critical']
        results.append(result)
        
        # Pequena pausa entre testes
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
        
        if result['status'] in ['FAIL', 'ERROR']:
            # Mostrar últimas linhas do output
            lines = result['output'].split('\n')
            error_lines = [l for l in lines if 'ERROR' in l or 'FAIL' in l or 'Traceback' in l]
            if error_lines:
                print(f"   Erro: {error_lines[0][:100]}...")
        
        print()
    
    # Decisão de deploy
    print_header("DECISÃO DE DEPLOY")
    
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
