#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy Completo para Produção - Orquestrador Principal
Sistema automatizado de preparação, testes e deploy para Google App Engine.

Autor: Lenilson Pinheiro
Data: Janeiro 2025
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class Colors:
    """Cores para output no terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

class ProductionDeployment:
    """Sistema completo de deploy para produção"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report = {
            "timestamp": self.timestamp,
            "steps": [],
            "errors": [],
            "warnings": []
        }
        self.steps = [
            (self.step_1_backup_database, "BACKUP DO BANCO DE DADOS"),
            (self.step_2_optimize_images, "OTIMIZAÇÃO DE IMAGENS"),
            (self.step_3_run_tests, "EXECUÇÃO DA SUÍTE DE TESTES"),
            (self.step_4_gcloud_deploy, "DEPLOY NO GOOGLE APP ENGINE"),
            (self.step_5_validate_deployment, "VALIDAÇÃO PÓS-DEPLOY")
        ]
    
    def log(self, message, level="INFO"):
        """Log de mensagens"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        self.report["steps"].append({
            "time": timestamp,
            "level": level,
            "message": message
        })
    
    def run_command(self, command, description):
        """Executa comando e captura resultado"""
        self.log(f"Executando: {description}...")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log(f"SUCESSO - {description}", "OK")
                return True, result.stdout
            else:
                self.log(f"FALHA - {description}", "ERROR")
                self.report["errors"].append({
                    "command": command,
                    "error": result.stderr.strip()
                })
                return False, result.stderr
        except subprocess.TimeoutExpired:
            error_msg = "Comando excedeu o tempo limite de 5 minutos."
            self.log(f"FALHA - {description} - {error_msg}", "ERROR")
            self.report["errors"].append({
                "command": command,
                "error": error_msg
            })
            return False, error_msg
        except Exception as e:
            self.log(f"FALHA - {description} - Exceção: {str(e)}", "ERROR")
            self.report["errors"].append({
                "command": command,
                "error": str(e)
            })
            return False, str(e)
    
    def print_progress(self, step, total_steps, start_time):
        """Imprime a barra de progresso, percentual e ETA."""
        if step == 0:
            return 
        
        percentage = (step / total_steps) * 100
        bar_length = 40
        filled_length = int(bar_length * step // total_steps)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        elapsed_time = time.time() - start_time
        avg_time_per_step = elapsed_time / step
        eta = (total_steps - step) * avg_time_per_step
        
        elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed_time))
        eta_str = time.strftime("%M:%S", time.gmtime(eta))

        print(f"\n{Colors.BOLD}Progresso: |{bar}| {percentage:.1f}% completo{Colors.END}")
        print(f"{Colors.YELLOW}Tempo decorrido: {elapsed_str} | ETA: {eta_str}{Colors.END}")

    def execute_step(self, step_func, step_name, current_step, total_steps):
        """Executa um passo e lida com o resultado."""
        header_text = f"PASSO {current_step} de {total_steps}: {step_name}"
        print_header(header_text)
        self.log(header_text, "STEP")
        success = step_func()
        if not success:
            self.log(f"FALHA no passo: {step_name}", "CRITICAL")
            self.generate_report()
            sys.exit(1)
        return success

    def step_1_backup_database(self):
        """Passo 1: Backup do banco de dados"""
        return self.run_command(
            f'"{sys.executable}" backup_db.py',
            "Backup do Banco de Dados"
        )[0]

    def step_2_optimize_images(self):
        """Passo 2: Otimização de imagens"""
        return self.run_command(
            f'"{sys.executable}" otimizar_imagens.py',
            "Otimização de Imagens para WebP"
        )[0]

    def step_3_run_tests(self):
        """Passo 3: Executar suíte completa de testes"""
        return self.run_command(
            f'"{sys.executable}" run_all_tests.py',
            "Execução da Suíte Completa de Testes"
        )[0]

    def step_4_gcloud_deploy(self):
        """Passo 4: Deploy para Google App Engine"""
        gcloud_check = subprocess.run("where gcloud", shell=True, capture_output=True)
        if gcloud_check.returncode != 0:
            self.log("Google Cloud SDK (gcloud) não encontrado no PATH.", "CRITICAL")
            return False
        
        return self.run_command(
            "gcloud app deploy --quiet",
            "Deploy para Google App Engine"
        )[0]

    def step_5_validate_deployment(self):
        """Passo 5: Validar o deploy em produção"""
        return self.run_command(
            f'"{sys.executable}" validar_deploy.py',
            "Validação Pós-Deploy"
        )[0]

    def generate_report(self):
        """Gera um relatório final do processo de deploy."""
        print_header("GERANDO RELATÓRIO FINAL")
        
        report_content = f"""
# RELATÓRIO DE DEPLOY - PRODUÇÃO
**Data/Hora:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## ✅ RESUMO

- **Total de Passos:** {len(self.report['steps'])}
- **Erros:** {len(self.report['errors'])}
- **Avisos:** {len(self.report['warnings'])}

## 📊 PASSOS EXECUTADOS

"""
        for step in self.report['steps']:
            report_content += f"- [{step['time']}] [{step['level']}] {step['message']}\n"
        
        if self.report['errors']:
            report_content += "\n## ❌ ERROS\n\n"
            for error in self.report['errors']:
                report_content += f"- **Comando:** `{error['command']}`\n"
                report_content += f"  **Erro:** {error['error']}\n\n"
        
        if self.report['warnings']:
            report_content += "\n## AVISOS\n\n"
            for warning in self.report['warnings']:
                report_content += f"- {warning}\n"
        
        # Salvar relatório
        report_file = self.project_root / f"DEPLOY_REPORT_{self.timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.log(f"✓ Relatório salvo em: {report_file.name}")
        
        # Salvar JSON
        json_file = self.project_root / f"DEPLOY_REPORT_{self.timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        return True
    
    def run(self):
        """Executar deploy completo"""
        print_header("INICIANDO DEPLOY COMPLETO PARA PRODUÇÃO (GOOGLE APP ENGINE)")
        start_time = time.time()
        total_steps = len(self.steps)
        
        try:
            for i, (step_func, step_name) in enumerate(self.steps):
                self.execute_step(step_func, step_name, current_step=i + 1, total_steps=total_steps)
                self.print_progress(i + 1, total_steps, start_time)
            
        except Exception as e:
            self.log(f"Erro fatal durante o deploy: {str(e)}", "CRITICAL")
            self.report["errors"].append({
                "command": "deploy_complete",
                "error": str(e)
            })
            self.generate_report()
            return False
        
        self.generate_report()
        print_header("DEPLOY CONCLUÍDO COM SUCESSO!")
        return True

if __name__ == "__main__":
    print_header("SISTEMA DE DEPLOY PARA PRODUÇÃO - BMA_VF")
    
    deployer = ProductionDeployment()
    success = deployer.run()
    
    if success:
        print(f"\n{Colors.GREEN}✓ Deploy finalizado com sucesso!{Colors.END}")
        print("Verifique o relatório gerado para mais detalhes.")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}✗ Deploy falhou! Verifique o relatório e os logs de erro.{Colors.END}")
        sys.exit(1)
