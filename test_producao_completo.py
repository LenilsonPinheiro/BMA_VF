#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Suite Completo para Produção - Google App Engine
Testa todas as funcionalidades do site em produção

Autor: Lenilson Pinheiro Valério
Data: Janeiro 2025
"""

import requests
import time
from urllib.parse import urljoin

# URL base do site em produção
BASE_URL = "https://belarmino-advogado.rj.r.appspot.com"

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

def print_test(test_name, passed, details=""):
    """Imprime resultado de um teste"""
    status = f"{Colors.GREEN}✓ PASSOU{Colors.END}" if passed else f"{Colors.RED}✗ FALHOU{Colors.END}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {Colors.YELLOW}→ {details}{Colors.END}")

def test_url(url, expected_status=200, check_content=None, test_name=""):
    """Testa uma URL específica"""
    try:
        response = requests.get(url, timeout=30, allow_redirects=True)
        
        # Verifica status code
        status_ok = response.status_code == expected_status
        
        # Verifica conteúdo se especificado
        content_ok = True
        if check_content:
            content_ok = check_content in response.text
        
        passed = status_ok and content_ok
        
        details = f"Status: {response.status_code}"
        if check_content and not content_ok:
            details += f" | Conteúdo '{check_content}' não encontrado"
        
        print_test(test_name or url, passed, details)
        return passed
        
    except Exception as e:
        print_test(test_name or url, False, f"Erro: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print_header("TESTE COMPLETO DE PRODUÇÃO - GOOGLE APP ENGINE")
    print(f"{Colors.BOLD}URL Base:{Colors.END} {BASE_URL}")
    print(f"{Colors.BOLD}Data/Hora:{Colors.END} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_tests = 0
    passed_tests = 0
    
    # ========================================
    # 1. TESTE DE PÁGINAS PRINCIPAIS
    # ========================================
    print_header("1. PÁGINAS PRINCIPAIS")
    
    tests = [
        (f"{BASE_URL}/", "Página Inicial", "Belarmino"),
        (f"{BASE_URL}/sobre", "Página Sobre", "Sobre"),
        (f"{BASE_URL}/contato", "Página Contato", "Contato"),
        (f"{BASE_URL}/areas-atuacao", "Áreas de Atuação", "Áreas"),
    ]
    
    for url, name, content in tests:
        total_tests += 1
        if test_url(url, check_content=content, test_name=name):
            passed_tests += 1
    
    # ========================================
    # 2. TESTE DE ÁREAS DE ATUAÇÃO ESPECÍFICAS
    # ========================================
    print_header("2. ÁREAS DE ATUAÇÃO ESPECÍFICAS")
    
    areas = [
        "direito-civil",
        "direito-trabalhista",
        "direito-previdenciario",
        "direito-consumidor"
    ]
    
    for area in areas:
        total_tests += 1
        url = f"{BASE_URL}/areas-atuacao/{area}"
        if test_url(url, test_name=f"Área: {area.replace('-', ' ').title()}"):
            passed_tests += 1
    
    # ========================================
    # 3. TESTE DE SSL/HTTPS
    # ========================================
    print_header("3. SEGURANÇA SSL/HTTPS")
    
    total_tests += 1
    try:
        response = requests.get(BASE_URL, timeout=30)
        is_https = response.url.startswith('https://')
        print_test("Redirecionamento HTTPS", is_https, 
                  f"URL final: {response.url}")
        if is_https:
            passed_tests += 1
    except Exception as e:
        print_test("Redirecionamento HTTPS", False, f"Erro: {str(e)}")
    
    # ========================================
    # 4. TESTE DE RECURSOS ESTÁTICOS
    # ========================================
    print_header("4. RECURSOS ESTÁTICOS")
    
    static_resources = [
        ("/static/css/style.css", "CSS Principal"),
        ("/static/css/theme.css", "CSS Tema"),
        ("/static/js/script.js", "JavaScript Principal"),
        ("/static/images/BM.png", "Logo"),
    ]
    
    for resource, name in static_resources:
        total_tests += 1
        url = urljoin(BASE_URL, resource)
        if test_url(url, test_name=f"Recurso: {name}"):
            passed_tests += 1
    
    # ========================================
    # 5. TESTE DE PERFORMANCE
    # ========================================
    print_header("5. PERFORMANCE")
    
    total_tests += 1
    try:
        start_time = time.time()
        response = requests.get(BASE_URL, timeout=30)
        load_time = time.time() - start_time
        
        # Considera bom se carregar em menos de 3 segundos
        is_fast = load_time < 3.0
        print_test("Tempo de Carregamento", is_fast,
                  f"Tempo: {load_time:.2f}s (meta: < 3.0s)")
        if is_fast:
            passed_tests += 1
    except Exception as e:
        print_test("Tempo de Carregamento", False, f"Erro: {str(e)}")
    
    # ========================================
    # 6. TESTE DE HEADERS HTTP
    # ========================================
    print_header("6. HEADERS HTTP")
    
    total_tests += 1
    try:
        response = requests.get(BASE_URL, timeout=30)
        headers = response.headers
        
        # Verifica headers importantes
        has_content_type = 'content-type' in headers
        has_server = 'server' in headers
        
        passed = has_content_type
        details = f"Content-Type: {headers.get('content-type', 'N/A')}"
        
        print_test("Headers HTTP", passed, details)
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test("Headers HTTP", False, f"Erro: {str(e)}")
    
    # ========================================
    # 7. TESTE DE FORMULÁRIO DE CONTATO
    # ========================================
    print_header("7. FORMULÁRIO DE CONTATO")
    
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/contato", timeout=30)
        has_form = '<form' in response.text
        has_name_field = 'name' in response.text.lower()
        has_email_field = 'email' in response.text.lower()
        has_message_field = 'message' in response.text.lower()
        
        passed = has_form and has_name_field and has_email_field and has_message_field
        details = f"Form: {has_form}, Name: {has_name_field}, Email: {has_email_field}, Message: {has_message_field}"
        
        print_test("Formulário Presente", passed, details)
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test("Formulário Presente", False, f"Erro: {str(e)}")
    
    # ========================================
    # 8. TESTE DE RESPONSIVIDADE (META TAGS)
    # ========================================
    print_header("8. RESPONSIVIDADE")
    
    total_tests += 1
    try:
        response = requests.get(BASE_URL, timeout=30)
        has_viewport = 'viewport' in response.text
        has_mobile_meta = 'width=device-width' in response.text
        
        passed = has_viewport and has_mobile_meta
        details = f"Viewport: {has_viewport}, Mobile-friendly: {has_mobile_meta}"
        
        print_test("Meta Tags Responsivas", passed, details)
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test("Meta Tags Responsivas", False, f"Erro: {str(e)}")
    
    # ========================================
    # 9. TESTE DE SEO (META TAGS)
    # ========================================
    print_header("9. SEO - META TAGS")
    
    total_tests += 1
    try:
        response = requests.get(BASE_URL, timeout=30)
        has_title = '<title>' in response.text
        has_description = 'description' in response.text
        has_og_tags = 'og:' in response.text
        
        passed = has_title and has_description
        details = f"Title: {has_title}, Description: {has_description}, Open Graph: {has_og_tags}"
        
        print_test("Meta Tags SEO", passed, details)
        if passed:
            passed_tests += 1
    except Exception as e:
        print_test("Meta Tags SEO", False, f"Erro: {str(e)}")
    
    # ========================================
    # 10. TESTE DE ÁREA ADMINISTRATIVA
    # ========================================
    print_header("10. ÁREA ADMINISTRATIVA")
    
    total_tests += 1
    # Deve redirecionar para login ou mostrar página de login
    if test_url(f"{BASE_URL}/admin", expected_status=200, 
                check_content="login", test_name="Acesso Admin (deve pedir login)"):
        passed_tests += 1
    
    # ========================================
    # RESUMO FINAL
    # ========================================
    print_header("RESUMO DOS TESTES")
    
    percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{Colors.BOLD}Total de Testes:{Colors.END} {total_tests}")
    print(f"{Colors.GREEN}{Colors.BOLD}Testes Passados:{Colors.END} {passed_tests}")
    print(f"{Colors.RED}{Colors.BOLD}Testes Falhados:{Colors.END} {total_tests - passed_tests}")
    print(f"{Colors.BOLD}Taxa de Sucesso:{Colors.END} {percentage:.1f}%")
    
    if percentage == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TODOS OS TESTES PASSARAM! SITE 100% FUNCIONAL!{Colors.END}")
    elif percentage >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  SITE FUNCIONAL COM PEQUENOS PROBLEMAS{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SITE COM PROBLEMAS CRÍTICOS{Colors.END}")
    
    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}\n")
    
    return percentage == 100

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
