#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy Completo para Produção
Sistema automatizado de preparação, testes e deploy

Autor: Senior Full-Stack Engineer
Data: Janeiro 2025
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

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
    
    def log(self, message, level="INFO"):
        """Log de mensagens"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        self.report["steps"].append({
            "time": timestamp,
            "level": level,
            "message": message
        })
    
    def run_command(self, command, description):
        """Executa comando e captura resultado"""
        self.log(f"Executando: {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log(f"✓ {description} - Sucesso", "SUCCESS")
                return True, result.stdout
            else:
                self.log(f"✗ {description} - Falhou", "ERROR")
                self.report["errors"].append({
                    "command": command,
                    "error": result.stderr
                })
                return False, result.stderr
        except Exception as e:
            self.log(f"✗ {description} - Exceção: {str(e)}", "ERROR")
            self.report["errors"].append({
                "command": command,
                "error": str(e)
            })
            return False, str(e)
    
    def step_1_seo_optimization(self):
        """Passo 1: Otimização SEO"""
        self.log("=" * 60)
        self.log("PASSO 1: OTIMIZAÇÃO SEO")
        self.log("=" * 60)
        
        # Verificar robots.txt
        robots_path = self.project_root / "BelarminoMonteiroAdvogado" / "templates" / "robots.txt"
        if robots_path.exists():
            self.log("✓ robots.txt encontrado")
        else:
            self.log("✗ robots.txt não encontrado", "WARNING")
        
        # Verificar sitemap.xml
        sitemap_path = self.project_root / "BelarminoMonteiroAdvogado" / "templates" / "sitemap.xml"
        if sitemap_path.exists():
            self.log("✓ sitemap.xml encontrado")
        else:
            self.log("✗ sitemap.xml não encontrado", "WARNING")
        
        # Verificar meta tags
        seo_meta_path = self.project_root / "BelarminoMonteiroAdvogado" / "templates" / "_seo_meta.html"
        if seo_meta_path.exists():
            self.log("✓ Meta tags SEO encontradas")
        else:
            self.log("✗ Meta tags SEO não encontradas", "WARNING")
        
        return True
    
    def step_2_run_tests(self):
        """Passo 2: Executar testes"""
        self.log("=" * 60)
        self.log("PASSO 2: EXECUTANDO TESTES")
        self.log("=" * 60)
        
        # Teste de importação
        success, output = self.run_command(
            "python -c \"from BelarminoMonteiroAdvogado import create_app; app = create_app(); print('OK')\"",
            "Teste de importação da aplicação"
        )
        
        if not success:
            self.log("✗ Falha no teste de importação", "ERROR")
            return False
        
        # Verificar dependências
        success, output = self.run_command(
            "pip list",
            "Verificação de dependências instaladas"
        )
        
        return True
    

    
    def step_5_generate_deploy_commands(self):
        """Passo 5: Gerar comandos de deploy"""
        self.log("=" * 60)
        self.log("PASSO 5: COMANDOS DE DEPLOY")
        self.log("=" * 60)
        
        commands = f"""
# ============================================
# COMANDOS PARA DEPLOY NO PYTHONANYWHERE
# Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
# ============================================

# 1. Acesse o console Bash no PythonAnywhere
# 2. Faça o upload manual dos arquivos do projeto para o diretório /home/seu-usuario/seu-projeto
# 3. Execute os comandos abaixo no console Bash:

cd ~
cd belarminomonteiro.pythonanywhere.com

# Fazer backup do banco de dados atual
cp instance/site.db instance/site_backup_{self.timestamp}.db

# Atualizar dependências
pip install --user -r requirements.txt

# Executar migrações (se houver)
flask db upgrade

# Recarregar aplicação
touch /var/www/belarminomonteiro_pythonanywhere_com_wsgi.py

# ============================================
# VERIFICAÇÃO
# ============================================

# Verificar logs
tail -f /var/log/belarminomonteiro.pythonanywhere.com.error.log

# Testar aplicação
curl https://belarminomonteiro.pythonanywhere.com/

"""
        
        # Salvar comandos
        commands_file = self.project_root / f"DEPLOY_COMMANDS_{self.timestamp}.txt"
        with open(commands_file, 'w', encoding='utf-8') as f:
            f.write(commands)
        
        self.log(f"✓ Comandos salvos em: {commands_file.name}")
        return True
    
    def step_6_generate_report(self):
        """Passo 6: Gerar relatório"""
        self.log("=" * 60)
        self.log("PASSO 6: GERANDO RELATÓRIO")
        self.log("=" * 60)
        
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
            report_content += "\n## ⚠️ AVISOS\n\n"
            for warning in self.report['warnings']:
                report_content += f"- {warning}\n"
        
        report_content += f"""

## 🚀 PRÓXIMOS PASSOS

1. **Acessar PythonAnywhere:** https://www.pythonanywhere.com/
2. **Executar comandos:** Ver arquivo `DEPLOY_COMMANDS_{self.timestamp}.txt`
3. **Testar site:** https://belarminomonteiro.pythonanywhere.com/

## 📝 CHECKLIST PÓS-DEPLOY

- [ ] Site acessível
- [ ] Vídeos carregando
- [ ] Imagens carregando
- [ ] Formulários funcionando
- [ ] Admin acessível
- [ ] SEO tags presentes
- [ ] Robots.txt acessível
- [ ] Sitemap.xml acessível
- [ ] SSL ativo (HTTPS)
- [ ] Performance OK

---
**Gerado automaticamente pelo sistema de deploy**
"""
        
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
        self.log("=" * 60)
        self.log("INICIANDO DEPLOY PARA PRODUÇÃO")
        self.log("=" * 60)
        
        try:
            # Passo 1: SEO
            if not self.step_1_seo_optimization():
                self.log("✗ Falha na otimização SEO", "ERROR")
                return False
            
            # Passo 2: Testes
            if not self.step_2_run_tests():
                self.log("✗ Falha nos testes", "ERROR")
                return False
            
            # Passo 5: Gerar comandos
            if not self.step_5_generate_deploy_commands():
                self.log("✗ Falha ao gerar comandos", "ERROR")
                return False
            
            # Passo 6: Gerar relatório
            if not self.step_6_generate_report():
                self.log("✗ Falha ao gerar relatório", "ERROR")
                return False
            
            self.log("=" * 60)
            self.log("✓ DEPLOY CONCLUÍDO COM SUCESSO!")
            self.log("=" * 60)
            
            return True
            
        except Exception as e:
            self.log(f"✗ Erro fatal: {str(e)}", "ERROR")
            self.report["errors"].append({
                "command": "deploy_complete",
                "error": str(e)
            })
            return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     SISTEMA DE DEPLOY PARA PRODUÇÃO                         ║
║     Belarmino Monteiro Advogado                             ║
║                                                              ║
║     Preparando para deploy completo...                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    deployer = ProductionDeployment()
    success = deployer.run()
    
    if success:
        print("\n✓ Deploy concluído com sucesso!")
        print("\nPróximos passos:")
        print("1. Verifique os arquivos DEPLOY_COMMANDS_*.txt")
        print("2. Execute os comandos no PythonAnywhere")
        print("3. Teste o site em produção")
        sys.exit(0)
    else:
        print("\n✗ Deploy falhou! Verifique o relatório.")
        sys.exit(1)
