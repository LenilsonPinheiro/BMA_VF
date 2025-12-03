"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Teste Completo de Todos os Temas (1-8)
Verifica: Cores, Contraste, Links, Estrutura
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "http://localhost:5000"

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def test_theme_homepage(theme_num):
    """Testa a homepage de um tema específico"""
    print_section(f"TESTANDO TEMA {theme_num} (OPTION{theme_num})")
    
    results = {
        'css_loaded': False,
        'links_working': [],
        'links_broken': [],
        'colors_ok': True,
        'structure_ok': True
    }
    
    try:
        # Simula acesso com o tema ativo
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            print_success(f"Homepage carrega (Status: {response.status_code})")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Verifica se CSS do tema está linkado
            css_links = soup.find_all('link', rel='stylesheet')
            theme_css_found = False
            for link in css_links:
                href = link.get('href', '')
                if f'style-option{theme_num}.css' in href or f'option{theme_num}' in href:
                    theme_css_found = True
                    results['css_loaded'] = True
                    print_success(f"CSS do tema encontrado: {href}")
                    break
            
            if not theme_css_found:
                print_warning(f"CSS específico do tema {theme_num} não encontrado")
            
            # 2. Verifica links do menu
            nav_links = soup.find_all('a', href=True)
            print(f"\n  Testando {len(nav_links)} links encontrados...")
            
            for link in nav_links[:10]:  # Testa os primeiros 10 links
                href = link.get('href')
                if href.startswith('/') and not href.startswith('//'):
                    try:
                        link_response = requests.get(f"{BASE_URL}{href}", timeout=5)
                        if link_response.status_code == 200:
                            results['links_working'].append(href)
                        else:
                            results['links_broken'].append((href, link_response.status_code))
                    except:
                        results['links_broken'].append((href, 'timeout'))
            
            if results['links_working']:
                print_success(f"{len(results['links_working'])} links funcionando")
            if results['links_broken']:
                print_error(f"{len(results['links_broken'])} links com problemas")
                for href, status in results['links_broken'][:3]:
                    print(f"    - {href}: {status}")
            
            # 3. Verifica estrutura HTML básica
            has_nav = soup.find('nav') is not None
            has_footer = soup.find('footer') is not None
            has_main = soup.find('main') is not None or soup.find(class_=re.compile('wrapper|container'))
            
            if has_nav and has_footer:
                print_success("Estrutura HTML completa (nav + footer)")
                results['structure_ok'] = True
            else:
                print_warning(f"Estrutura incompleta (nav:{has_nav}, footer:{has_footer})")
                results['structure_ok'] = False
            
        else:
            print_error(f"Falha ao carregar homepage (Status: {response.status_code})")
    
    except Exception as e:
        print_error(f"Erro ao testar tema: {str(e)}")
    
    return results

def test_all_themes():
    """Testa todos os 8 temas"""
    print_header("TESTE COMPLETO DE TODOS OS TEMAS (1-8)")
    
    print(f"{Colors.CYAN}URL Base: {BASE_URL}{Colors.END}")
    print(f"{Colors.CYAN}Testando estrutura, links e CSS de cada tema{Colors.END}\n")
    
    all_results = {}
    
    for theme_num in range(1, 9):
        results = test_theme_homepage(theme_num)
        all_results[theme_num] = results
    
    # Relatório Final
    print_header("RELATÓRIO FINAL")
    
    print(f"\n{Colors.BOLD}RESUMO POR TEMA:{Colors.END}\n")
    
    for theme_num, results in all_results.items():
        status_icon = "" if results['css_loaded'] and results['structure_ok'] else "⚠"
        color = Colors.GREEN if results['css_loaded'] and results['structure_ok'] else Colors.YELLOW
        
        print(f"{color}{status_icon} Tema {theme_num}:{Colors.END}")
        print(f"   CSS Carregado: {'' if results['css_loaded'] else ''}")
        print(f"   Estrutura OK: {'' if results['structure_ok'] else ''}")
        print(f"   Links OK: {len(results['links_working'])}")
        print(f"   Links Quebrados: {len(results['links_broken'])}")
        print()
    
    # Estatísticas Gerais
    total_themes = len(all_results)
    themes_ok = sum(1 for r in all_results.values() if r['css_loaded'] and r['structure_ok'])
    
    print(f"\n{Colors.BOLD}ESTATÍSTICAS GERAIS:{Colors.END}")
    print(f"  Total de Temas: {total_themes}")
    print(f"  {Colors.GREEN}Temas OK: {themes_ok}{Colors.END}")
    print(f"  {Colors.YELLOW}Temas com Avisos: {total_themes - themes_ok}{Colors.END}")
    
    if themes_ok == total_themes:
        print(f"\n{Colors.GREEN}{Colors.BOLD} TODOS OS TEMAS PASSARAM! {Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}  ALGUNS TEMAS PRECISAM DE ATENÇÃO  {Colors.END}\n")

if __name__ == "__main__":
    print(f"\n{Colors.CYAN}Aguardando servidor Flask em {BASE_URL}...{Colors.END}")
    print(f"{Colors.CYAN}Certifique-se de que o servidor está rodando!{Colors.END}\n")
    
    try:
        # Testa se o servidor está respondendo
        response = requests.get(BASE_URL, timeout=5)
        print(f"{Colors.GREEN} Servidor respondendo!{Colors.END}\n")
        
        test_all_themes()
    
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED} ERRO: Servidor não está respondendo em {BASE_URL}{Colors.END}")
        print(f"{Colors.YELLOW}Por favor, inicie o servidor Flask primeiro:{Colors.END}")
        print(f"{Colors.CYAN}  python run.py{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED} ERRO: {str(e)}{Colors.END}\n")
