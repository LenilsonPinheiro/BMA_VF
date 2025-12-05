#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executor de Deploy com Dashboard - Roda testes e atualiza dashboard em tempo real
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from deploy_monitor import DeployMonitor


def run_tests_with_dashboard():
    """Executa testes e atualiza dashboard em tempo real"""
    
    monitor = DeployMonitor()
    
    # Cria dashboard HTML
    html = monitor.generate_html_dashboard()
    with open("deploy_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    monitor.add_message("Dashboard gerado: deploy_dashboard.html", "success")
    monitor.save_dashboard()
    
    print("\n" + "="*60)
    print("MONITOR DE DEPLOY - BMA_VF")
    print("="*60)
    print(f"Dashboard: file://{Path('deploy_dashboard.html').absolute()}")
    print("="*60 + "\n")
    
    # Lista de testes com suas fases
    tests = [
        ("test_app.py", "Testes Unitários", 0),
        ("test_database_schema.py", "Testes Unitários", 0),
        ("test_all_routes_complete.py", "Testes de Rotas", 1),
        ("test_admin_routes.py", "Testes de Rotas", 1),
        ("test_all_themes_complete.py", "Testes de Temas", 2),
        ("test_all_themes.py", "Testes de Temas", 2),
        ("test_links_rotas_completo.py", "Testes de Rotas", 1),
        ("test_media_completo.py", "Testes de Pré-Deploy", 3),
        ("test_pre_deploy_completo.py", "Testes de Pré-Deploy", 3),
        ("test_pre_deploy_completo_v2.py", "Testes de Pré-Deploy", 3),
        ("test_completo_final.py", "Validação Final", 4),
        ("test_human_simulation.py", "Validação Final", 4),
        ("test_visual_humano_completo.py", "Validação Final", 4),
    ]
    
    monitor.state["tests_total"] = len(tests)
    
    passed = 0
    failed = 0
    
    print(f"Total de testes a executar: {len(tests)}\n")
    
    for idx, (test_file, phase_name, phase_idx) in enumerate(tests):
        
        monitor.state["current_step"] = phase_idx + 1
        monitor.state["phase"] = phase_name
        
        print(f"\n[{idx+1}/{len(tests)}] Executando {test_file} ({phase_name})...")
        monitor.add_message(f"Iniciando: {test_file}", "info")
        monitor.save_dashboard()
        
        try:
            # Executa teste com timeout
            result = subprocess.run(
                f"python {test_file}",
                capture_output=True,
                timeout=120,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                passed += 1
                print(f"  ✓ {test_file} PASSOU")
                monitor.add_message(f"✓ {test_file} PASSOU", "success")
            else:
                failed += 1
                print(f"  ✗ {test_file} FALHOU")
                monitor.add_message(f"✗ {test_file} FALHOU", "error")
                # Mostra primeiras linhas do erro
                if result.stderr:
                    err_lines = result.stderr.split('\n')[:3]
                    for line in err_lines:
                        if line.strip():
                            monitor.add_message(f"    {line}", "warning")
                
        except subprocess.TimeoutExpired:
            failed += 1
            print(f"  ✗ {test_file} TIMEOUT (>120s)")
            monitor.add_message(f"✗ {test_file} TIMEOUT", "error")
        except Exception as e:
            failed += 1
            print(f"  ✗ {test_file} ERRO: {str(e)}")
            monitor.add_message(f"✗ {test_file} ERRO: {str(e)}", "error")
        
        monitor.state["tests_passed"] = passed
        monitor.state["tests_failed"] = failed
        monitor.save_dashboard()
        
        # Calcula progresso
        elapsed = time.time() - monitor.state["start_time"]
        avg_per_test = elapsed / (idx + 1)
        remaining = len(tests) - (idx + 1)
        eta_seconds = int(avg_per_test * remaining)
        eta_time = datetime.now() + timedelta(seconds=eta_seconds)
        monitor.state["estimated_completion"] = eta_time.isoformat()
        
        print(f"  Progresso: {passed} passaram, {failed} falharam")
        print(f"  ETA: {eta_time.strftime('%H:%M:%S')}")
    
    # Resultado final
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"Total de testes: {len(tests)}")
    print(f"✓ Passaram: {passed} ({(passed/len(tests)*100):.1f}%)")
    print(f"✗ Falharam: {failed} ({(failed/len(tests)*100):.1f}%)")
    print(f"Tempo total: {(time.time() - monitor.state['start_time']):.1f}s")
    
    if failed == 0:
        print("\n✓ TODOS OS TESTES PASSARAM - DEPLOY APROVADO!")
        monitor.state["status"] = "aprovado"
    else:
        print(f"\n✗ {failed} TESTES FALHARAM - DEPLOY BLOQUEADO")
        monitor.state["status"] = "bloqueado"
    
    print("="*60)
    print(f"\nDashboard: file://{Path('deploy_dashboard.html').absolute()}")
    print("="*60 + "\n")
    
    monitor.add_message(f"Deploy finalizado: {passed}/{len(tests)} passaram", 
                        "success" if failed == 0 else "error")
    monitor.state["current_step"] = len(monitor.phases)
    monitor.save_dashboard()
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests_with_dashboard()
    exit(0 if success else 1)
