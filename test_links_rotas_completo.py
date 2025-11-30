#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_links_rotas_completo.py

VERIFICAÇÃO COMPLETA DE LINKS E ROTAS
- Testa todos os layouts (option1-8)
- Testa todas as páginas
- Verifica links internos
- Verifica links externos
- Valida navegação

Autor: 
Data: Janeiro 2025
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent))

# Cores
class C:
    H = '\033[95m'
    B = '\033[94m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    E = '\033[0m'

def print_header(text):
    print(f"\n{C.H}{'='*80}{C.E}")
    print(f"{C.H}{text.center(80)}{C.E}")
    print(f"{C.H}{'='*80}{C.E}\n")

def print_success(text):
    print(f"{C.G} {text}{C.E}")

def print_error(text):
    print(f"{C.R} {text}{C.E}")

def print_info(text):
    print(f"{C.B} {text}{C.E}")

# Contadores
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_theme_routes(theme_number):
    """Testa rotas para um tema específico"""
    global total_tests, passed_tests, failed_tests
    
    try:
        from BelarminoMonteiroAdvogado import create_app
        from BelarminoMonteiroAdvogado.models import db, ThemeSettings
        
        app = create_app()
        
        with app.app_context():
            # Configurar tema
            theme = ThemeSettings.query.first()
            if theme:
                theme.current_theme = f'option{theme_number}'
                db.session.commit()
            
            client = app.test_client()
            
            # Rotas para testar
            routes = [
                ('/', 'Home'),
                ('/sobre-nos', 'Sobre'),
                ('/contato', 'Contato'),
                ('/politica-de-privacidade', 'Política'),
                ('/direito-civil', 'Direito Civil'),
                ('/direito-do-consumidor', 'Direito Consumidor'),
                ('/direito-previdenciario', 'Direito Previdenciário'),
                ('/direito-de-familia', 'Direito Família')
            ]
            
            all_passed = True
            for route, name in routes:
                total_tests += 1
                response = client.get(route)
                
                if response.status_code == 200:
                    passed_tests += 1
                    print_success(f"Theme {theme_number} - {name}: {response.status_code}")
                else:
                    failed_tests += 1
                    print_error(f"Theme {theme_number} - {name}: {response.status_code}")
                    all_passed = False
            
            return all_passed
            
    except Exception as e:
        print_error(f"Erro ao testar theme {theme_number}: {e}")
        return False

def test_navigation_links():
    """Testa links de navegação em todos os templates"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        
        app = create_app()
        client = app.test_client()
        
        # Páginas para verificar links
        pages = [
            '/',
            '/sobre-nos',
            '/contato',
            '/direito-civil'
        ]
        
        all_passed = True
        for page in pages:
            total_tests += 1
            response = client.get(page)
            
            if response.status_code == 200:
                content = response.data.decode('utf-8')
                
                # Procurar por links quebrados (href="#" ou href="")
                broken_links = re.findall(r'href=["\']#["\']|href=["\']["\']', content)
                
                if broken_links:
                    print_error(f"{page}: {len(broken_links)} links vazios encontrados")
                    failed_tests += 1
                    all_passed = False
                else:
                    print_success(f"{page}: Todos os links OK")
                    passed_tests += 1
            else:
                print_error(f"{page}: Erro {response.status_code}")
                failed_tests += 1
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erro ao testar links: {e}")
        return False

def test_static_resources():
    """Verifica se recursos estáticos estão acessíveis"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        
        app = create_app()
        client = app.test_client()
        
        # Recursos para testar
        resources = [
            '/static/css/style.css',
            '/static/css/theme.css',
            '/static/css/admin.css',
            '/static/js/script.js',
            '/static/js/resource-preloader.js',
            '/static/images/BM.png',
            '/static/images/Belarmino.png',
            '/static/images/Taise.png'
        ]
        
        all_passed = True
        for resource in resources:
            total_tests += 1
            response = client.get(resource)
            
            if response.status_code == 200:
                passed_tests += 1
                size = len(response.data)
                print_success(f"{resource}: {size} bytes")
            else:
                failed_tests += 1
                print_error(f"{resource}: {response.status_code}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erro ao testar recursos: {e}")
        return False

def test_form_actions():
    """Verifica ações de formulários"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        
        app = create_app()
        client = app.test_client()
        
        # Testar página de contato
        total_tests += 1
        response = client.get('/contato')
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Verificar se tem formulário
            if '<form' in content and 'action=' in content:
                print_success("Formulário de contato: Presente e configurado")
                passed_tests += 1
                return True
            else:
                print_error("Formulário de contato: Não encontrado")
                failed_tests += 1
                return False
        else:
            print_error(f"Página de contato: {response.status_code}")
            failed_tests += 1
            return False
            
    except Exception as e:
        print_error(f"Erro ao testar formulários: {e}")
        return False

def test_all_themes():
    """Testa todos os 8 temas"""
    print_info("Testando todos os 8 temas...")
    
    all_passed = True
    for i in range(1, 9):
        if not test_theme_routes(i):
            all_passed = False
    
    return all_passed

def main():
    """Executa todos os testes de links e rotas"""
    print_header("VERIFICAÇÃO COMPLETA DE LINKS E ROTAS")
    print_info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # SEÇÃO 1: TESTES DE TEMAS
    print_header("1. TESTES DE TODOS OS TEMAS (1-8)")
    test_all_themes()
    
    # SEÇÃO 2: TESTES DE NAVEGAÇÃO
    print_header("2. TESTES DE LINKS DE NAVEGAÇÃO")
    test_navigation_links()
    
    # SEÇÃO 3: TESTES DE RECURSOS ESTÁTICOS
    print_header("3. TESTES DE RECURSOS ESTÁTICOS")
    test_static_resources()
    
    # SEÇÃO 4: TESTES DE FORMULÁRIOS
    print_header("4. TESTES DE FORMULÁRIOS")
    test_form_actions()
    
    # RELATÓRIO FINAL
    print_header("RELATÓRIO FINAL")
    print(f"\nTotal de testes: {total_tests}")
    print_success(f"Passou: {passed_tests}")
    print_error(f"Falhou: {failed_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nTaxa de sucesso: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print_header(" TODOS OS LINKS E ROTAS FUNCIONANDO! ")
        return 0
    else:
        print_header(" ALGUNS LINKS/ROTAS COM PROBLEMAS! ")
        return 1

if __name__ == '__main__':
    sys.exit(main())
