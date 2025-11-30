"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script de Diagnóstico Completo para Temas 5, 6, 7 e 8
Identifica: páginas faltando, links quebrados, problemas de contraste
"""

import os
import re
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED} {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN} {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE} {text}{Colors.END}")

# Estrutura esperada de arquivos
EXPECTED_FILES = {
    'modelo de paginas': [
        'base_option5.html',
        'base_option6.html',
        'base_option7.html',
        'base_option8.html',
    ],
    'home': [
        'home_option5.html',
        'home_option6.html',
        'home_option7.html',
        'home_option8.html',
    ],
    'css': [
        'style-option5.css',
        'style-option6.css',
        'style-option7.css',
        'style-option8.css',
    ]
}

def check_file_exists(filepath):
    """Verifica se um arquivo existe"""
    return os.path.exists(filepath)

def check_missing_files():
    """Verifica arquivos faltando"""
    print_section("1. VERIFICANDO ARQUIVOS FALTANDO")
    
    base_path = Path("BelarminoMonteiroAdvogado")
    missing_files = []
    
    # Verifica modelo de paginas base
    for file in EXPECTED_FILES['modelo de paginas']:
        filepath = base_path / "modelo de paginas" / file
        if not filepath.exists():
            missing_files.append(str(filepath))
            print_error(f"Arquivo faltando: {filepath}")
        else:
            print_success(f"Encontrado: {filepath}")
    
    # Verifica modelo de paginas home
    for file in EXPECTED_FILES['home']:
        filepath = base_path / "modelo de paginas" / "home" / file
        if not filepath.exists():
            missing_files.append(str(filepath))
            print_error(f"Arquivo faltando: {filepath}")
        else:
            print_success(f"Encontrado: {filepath}")
    
    # Verifica CSS
    for file in EXPECTED_FILES['css']:
        filepath = base_path / "static" / "css" / file
        if not filepath.exists():
            missing_files.append(str(filepath))
            print_error(f"Arquivo faltando: {filepath}")
        else:
            print_success(f"Encontrado: {filepath}")
    
    return missing_files

def extract_links_from_modelo de pagina(filepath):
    """Extrai todos os links de um modelo de pagina"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrões para encontrar links
        patterns = [
            r'href=["\']([^"\']+)["\']',  # href="..."
            r'url_for\(["\']([^"\']+)["\']',  # url_for('...')
            r'src=["\']([^"\']+)["\']',  # src="..."
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            links.extend(matches)
        
        return links
    except Exception as e:
        print_error(f"Erro ao ler {filepath}: {e}")
        return []

def check_broken_links():
    """Verifica links quebrados nos modelo de paginas"""
    print_section("2. VERIFICANDO LINKS QUEBRADOS")
    
    base_path = Path("BelarminoMonteiroAdvogado")
    broken_links = []
    
    # Templates para verificar
    modelo de paginas_to_check = [
        base_path / "modelo de paginas" / f"base_option{i}.html" for i in range(5, 9)
    ] + [
        base_path / "modelo de paginas" / "home" / f"home_option{i}.html" for i in range(5, 9)
    ]
    
    for modelo de pagina in modelo de paginas_to_check:
        if not modelo de pagina.exists():
            continue
        
        print_info(f"\nVerificando: {modelo de pagina.name}")
        links = extract_links_from_modelo de pagina(modelo de pagina)
        
        for link in links:
            # Ignora links externos e âncoras
            if link.startswith(('http://', 'https://', '#', 'javascript:', '{{')):
                continue
            
            # Verifica se é um arquivo estático
            if link.startswith('/static/'):
                file_path = base_path / link.replace('/static/', 'static/')
                if not file_path.exists():
                    broken_links.append((modelo de pagina.name, link))
                    print_error(f"  Link quebrado: {link}")
            
            # Verifica rotas Flask
            elif link.startswith('/'):
                # Rotas conhecidas
                known_routes = [
                    '/', '/sobre-nos', '/contato', '/areas-de-atuacao',
                    '/politica-de-privacidade', '/admin', '/auth/login'
                ]
                if link not in known_routes and not any(link.startswith(r) for r in known_routes):
                    print_warning(f"  Rota desconhecida: {link}")
    
    if not broken_links:
        print_success("\nNenhum link quebrado encontrado!")
    
    return broken_links

def extract_colors_from_css(filepath):
    """Extrai cores de um arquivo CSS"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrões para cores
        color_patterns = [
            r'color:\s*([#\w().,\s]+);',
            r'background-color:\s*([#\w().,\s]+);',
            r'background:\s*([#\w().,\s]+);',
            r'border-color:\s*([#\w().,\s]+);',
        ]
        
        colors = {}
        for pattern in color_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                color = match.strip()
                if color not in colors:
                    colors[color] = 0
                colors[color] += 1
        
        return colors
    except Exception as e:
        print_error(f"Erro ao ler {filepath}: {e}")
        return {}

def check_contrast_issues():
    """Verifica problemas de contraste"""
    print_section("3. VERIFICANDO PROBLEMAS DE CONTRASTE")
    
    base_path = Path("BelarminoMonteiroAdvogado/static/css")
    contrast_issues = []
    
    for i in range(5, 9):
        css_file = base_path / f"style-option{i}.css"
        if not css_file.exists():
            continue
        
        print_info(f"\nAnalisando: {css_file.name}")
        
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Procura por problemas comuns
            issues = []
            
            # 1. Cor branca em fundo branco
            if re.search(r'color:\s*#fff', content, re.IGNORECASE) and \
               re.search(r'background:\s*#fff', content, re.IGNORECASE):
                issues.append("Possível texto branco em fundo branco")
            
            # 2. Cor preta em fundo preto
            if re.search(r'color:\s*#000', content, re.IGNORECASE) and \
               re.search(r'background:\s*#000', content, re.IGNORECASE):
                issues.append("Possível texto preto em fundo preto")
            
            # 3. Cores muito claras
            light_colors = re.findall(r'color:\s*(#[fF]{6}|#[fF]{3}|white|rgba?\(255,\s*255,\s*255)', content)
            if len(light_colors) > 5:
                issues.append(f"Muitas cores claras detectadas ({len(light_colors)})")
            
            # 4. Verifica se há definição de contraste para dark mode
            if 'dark-mode' not in content:
                issues.append("Sem suporte para dark mode")
            
            if issues:
                for issue in issues:
                    print_warning(f"  {issue}")
                contrast_issues.append((css_file.name, issues))
            else:
                print_success("  Nenhum problema óbvio de contraste")
        
        except Exception as e:
            print_error(f"  Erro ao analisar: {e}")
    
    return contrast_issues

def check_modelo de pagina_structure():
    """Verifica estrutura dos modelo de paginas"""
    print_section("4. VERIFICANDO ESTRUTURA DOS TEMPLATES")
    
    base_path = Path("BelarminoMonteiroAdvogado/modelo de paginas")
    structure_issues = []
    
    for i in range(5, 9):
        # Verifica base modelo de pagina
        base_modelo de pagina = base_path / f"base_option{i}.html"
        home_modelo de pagina = base_path / "home" / f"home_option{i}.html"
        
        if base_modelo de pagina.exists():
            print_info(f"\nVerificando: {base_modelo de pagina.name}")
            
            try:
                with open(base_modelo de pagina, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica elementos essenciais
                checks = {
                    'DOCTYPE': '<!DOCTYPE html>' in content,
                    'HTML tag': '<html' in content,
                    'HEAD tag': '<head>' in content,
                    'BODY tag': '<body' in content,
                    'Navigation': 'nav' in content.lower(),
                    'Footer': 'footer' in content.lower(),
                    'CSS link': 'stylesheet' in content,
                }
                
                for check, passed in checks.items():
                    if passed:
                        print_success(f"  {check}: OK")
                    else:
                        print_error(f"  {check}: FALTANDO")
                        structure_issues.append((base_modelo de pagina.name, check))
            
            except Exception as e:
                print_error(f"  Erro ao verificar: {e}")
        
        # Verifica home modelo de pagina
        if home_modelo de pagina.exists():
            print_info(f"\nVerificando: {home_modelo de pagina.name}")
            
            try:
                with open(home_modelo de pagina, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica se estende o base correto
                if f"base_option{i}.html" in content:
                    print_success(f"  Estende base_option{i}.html corretamente")
                else:
                    print_error(f"  NÃO estende base_option{i}.html")
                    structure_issues.append((home_modelo de pagina.name, "extends incorreto"))
                
                # Verifica blocos essenciais
                blocks = ['content', 'title']
                for block in blocks:
                    if f"block {block}" in content:
                        print_success(f"  Bloco '{block}': OK")
                    else:
                        print_warning(f"  Bloco '{block}': FALTANDO")
            
            except Exception as e:
                print_error(f"  Erro ao verificar: {e}")
    
    return structure_issues

def generate_report(missing_files, broken_links, contrast_issues, structure_issues):
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL DE DIAGNÓSTICO")
    
    total_issues = len(missing_files) + len(broken_links) + len(contrast_issues) + len(structure_issues)
    
    print(f"\n{Colors.BOLD}RESUMO:{Colors.END}")
    print(f"  Arquivos faltando: {Colors.RED if missing_files else Colors.GREEN}{len(missing_files)}{Colors.END}")
    print(f"  Links quebrados: {Colors.RED if broken_links else Colors.GREEN}{len(broken_links)}{Colors.END}")
    print(f"  Problemas de contraste: {Colors.YELLOW if contrast_issues else Colors.GREEN}{len(contrast_issues)}{Colors.END}")
    print(f"  Problemas de estrutura: {Colors.YELLOW if structure_issues else Colors.GREEN}{len(structure_issues)}{Colors.END}")
    print(f"\n  {Colors.BOLD}TOTAL DE PROBLEMAS: {Colors.RED if total_issues > 0 else Colors.GREEN}{total_issues}{Colors.END}")
    
    if total_issues == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD} NENHUM PROBLEMA ENCONTRADO! {Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}  AÇÃO NECESSÁRIA  {Colors.END}\n")
        
        if missing_files:
            print(f"\n{Colors.RED}{Colors.BOLD}ARQUIVOS FALTANDO:{Colors.END}")
            for file in missing_files:
                print(f"  - {file}")
        
        if broken_links:
            print(f"\n{Colors.RED}{Colors.BOLD}LINKS QUEBRADOS:{Colors.END}")
            for template, link in broken_links:
                print(f"  - {template}: {link}")
        
        if contrast_issues:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}PROBLEMAS DE CONTRASTE:{Colors.END}")
            for css_file, issues in contrast_issues:
                print(f"  - {css_file}:")
                for issue in issues:
                    print(f"    • {issue}")
        
        if structure_issues:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}PROBLEMAS DE ESTRUTURA:{Colors.END}")
            for template, issue in structure_issues:
                print(f"  - {template}: {issue}")

def main():
    print_header("DIAGNÓSTICO COMPLETO - TEMAS 5, 6, 7 e 8")
    
    print(f"{Colors.CYAN}Iniciando análise detalhada...{Colors.END}\n")
    
    # Executa verificações
    missing_files = check_missing_files()
    broken_links = check_broken_links()
    contrast_issues = check_contrast_issues()
    structure_issues = check_template_structure()
    
    # Gera relatório
    generate_report(missing_files, broken_links, contrast_issues, structure_issues)
    
    print(f"\n{Colors.CYAN}Diagnóstico concluído!{Colors.END}\n")

if __name__ == "__main__":
    main()
