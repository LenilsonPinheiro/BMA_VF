#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner com barra de progresso, percentual e ETA em tempo real.
Integra todos os testes e mostra andamento detalhado.
"""

import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import json

class ProgressTracker:
    """Sistema de rastreamento de progresso com barra visual e ETA"""
    
    def __init__(self, total_tests=13):
        self.total_tests = total_tests
        self.current_test = 0
        self.start_time = time.time()
        self.test_times = {}
        self.test_results = {}
        
    def update(self, test_name, status="running"):
        """Atualiza progresso do teste atual"""
        self.current_test += 1 if status == "completed" else 0
        elapsed = time.time() - self.start_time
        
        if test_name in self.test_times and status == "completed":
            self.test_times[test_name] = time.time() - self.test_times.get(test_name, self.start_time)
        elif status == "running":
            self.test_times[test_name] = time.time()
        
        self.test_results[test_name] = status
        self.display_progress()
        
    def get_eta(self):
        """Calcula ETA baseado no tempo médio dos testes"""
        if not self.test_times:
            return None
            
        completed_times = [t for t in self.test_times.values() if isinstance(t, float)]
        if not completed_times:
            return None
            
        avg_time = sum(completed_times) / len(completed_times)
        remaining_tests = self.total_tests - self.current_test
        remaining_seconds = int(avg_time * remaining_tests)
        
        return datetime.now() + timedelta(seconds=remaining_seconds)
    
    def display_progress(self):
        """Exibe barra de progresso com percentual e ETA"""
        percentage = (self.current_test / self.total_tests) * 100
        bar_length = 40
        filled = int(bar_length * self.current_test / self.total_tests)
        bar = "#" * filled + "-" * (bar_length - filled)
        
        elapsed = int(time.time() - self.start_time)
        eta = self.get_eta()
        eta_str = eta.strftime("%H:%M:%S") if eta else "calculando..."
        
        # Limpa linha anterior e exibe nova
        sys.stdout.write("\r")
        sys.stdout.write(
            f"[{bar}] {percentage:6.1f}% | "
            f"Testes: {self.current_test}/{self.total_tests} | "
            f"Tempo: {elapsed}s | "
            f"ETA: {eta_str}     "
        )
        sys.stdout.flush()
    
    def get_summary(self):
        """Retorna sumário completo dos testes"""
        elapsed = int(time.time() - self.start_time)
        passed = sum(1 for s in self.test_results.values() if s == "passed")
        failed = sum(1 for s in self.test_results.values() if s == "failed")
        
        return {
            "total_tests": self.total_tests,
            "passed": passed,
            "failed": failed,
            "elapsed_seconds": elapsed,
            "success_rate": (passed / self.total_tests * 100) if self.total_tests > 0 else 0
        }


def run_test_with_progress(test_file, tracker):
    """Executa um teste individual e rastreia progresso"""
    test_name = Path(test_file).stem
    tracker.update(test_name, "running")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        status = "passed" if result.returncode == 0 else "failed"
        tracker.test_results[test_name] = status
        tracker.update(test_name, "completed")
        
        return status == "passed", result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        tracker.test_results[test_name] = "timeout"
        tracker.update(test_name, "completed")
        return False, "", f"TIMEOUT: {test_name} levou mais de 120 segundos"
    
    except Exception as e:
        tracker.test_results[test_name] = "error"
        tracker.update(test_name, "completed")
        return False, "", str(e)


def main():
    print("\n")
    print("=" * 80)
    print("  TESTE COMPLETO DO PROJETO - BMA_VF")
    print("=" * 80)
    print(f"  Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Lista de testes críticos para deploy
    test_files = [
        "test_app.py",
        "test_database_schema.py",
        "test_all_routes_complete.py",
        "test_admin_routes.py",
        "test_all_themes_complete.py",
        "test_all_themes.py",
        "test_links_rotas_completo.py",
        "test_media_completo.py",
        "test_pre_deploy_completo.py",
        "test_pre_deploy_completo_v2.py",
        "test_completo_final.py",
        "test_human_simulation.py",
        "test_visual_humano_completo.py",
    ]
    
    tracker = ProgressTracker(len(test_files))
    
    results = {}
    failed_tests = []
    
    print("\nExecutando testes...\n")
    
    for test_file in test_files:
        if not Path(test_file).exists():
            tracker.update(Path(test_file).stem, "skipped")
            continue
        
        passed, stdout, stderr = run_test_with_progress(test_file, tracker)
        results[test_file] = {
            "passed": passed,
            "stdout": stdout[:500],  # Primeiros 500 chars
            "stderr": stderr[:500]
        }
        
        if not passed:
            failed_tests.append(test_file)
    
    # Exibe sumário final
    print("\n" * 2)
    print("=" * 80)
    print("  RESUMO FINAL DOS TESTES")
    print("=" * 80)
    
    summary = tracker.get_summary()
    print(f"\n  Total de testes: {summary['total_tests']}")
    print(f"  [PASS] Passaram: {summary['passed']} ({summary['success_rate']:.1f}%)")
    print(f"  [FAIL] Falharam: {summary['failed']}")
    print(f"  [TIMER] Tempo total: {summary['elapsed_seconds']}s")
    
    if failed_tests:
        print(f"\n  [ERRO] TESTES FALHADOS:")
        for test in failed_tests:
            print(f"     - {test}")
        print("\n" + "=" * 80)
        print("  STATUS: [BLOQUEADO] NAO APROVADO PARA DEPLOY")
        print("=" * 80 + "\n")
        return 1
    else:
        print("\n" + "=" * 80)
        print("  STATUS: [OK] PRONTO PARA DEPLOY")
        print("=" * 80 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
