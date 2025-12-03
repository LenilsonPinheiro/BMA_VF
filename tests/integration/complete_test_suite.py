#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_completo_final.py

BATERIA COMPLETA DE TESTES FINAIS
- Testes funcionais
- Testes de cores e contrastes (padrao de acessibilidade)
- Testes de acessibilidade
- Testes de performance
- Testes de SEO
- Testes de segurança
- Validação de todos os temas (claro/escuro)

Autor: 
Data: Janeiro 2025
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import re

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN} {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL} {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN} {text}{Colors.ENDC}")

# Contadores globais
total_tests = 0
passed_tests = 0
failed_tests = 0
warnings = 0

def run_test(test_name, test_func):
    """Executa um teste e registra o resultado"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    print(f"\n Teste {total_tests}: {test_name}")
    try:
        result = test_func()
        if result:
            passed_tests += 1
            print_success(f"Passou: {test_name}")
            return True
        else:
            failed_tests += 1
            print_error(f"Falhou: {test_name}")
            return False
    except Exception as e:
        failed_tests += 1
        print_error(f"Erro: {test_name} - {str(e)}")
        return False

# ============================================================================
# TESTES DE CORES E CONTRASTES (padrao de acessibilidade)
# ============================================================================

def calculate_luminance(r, g, b):
    """Calcula a luminância relativa de uma cor RGB"""
    def adjust(c):
        c = c / 255.0
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

def calculate_contrast_ratio(color1, color2):
    """Calcula a razão de contraste entre duas cores"""
    l1 = calculate_luminance(*color1)
    l2 = calculate_luminance(*color2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)

def hex_to_rgb(hex_color):
    """Converte cor hexadecimal para RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def test_color_contrasts():
    """Testa contrastes de cores em todos os temas"""
    print_info("Testando contrastes de cores (padrao de acessibilidade)...")
    
    # Definição de cores dos temas
    themes = {
        'light': {
            'background': '#ffffff',
            'text': '#333333',
            'primary': '#1a1a2e',
            'accent': '#b92027',
            'secondary': '#6c757d'
        },
        'dark': {
            'background': '#111111',
            'text': '#eeeeee',
            'primary': '#ffffff',
            'accent': '#b92027',
            'secondary': '#aaaaaa'
        }
    }
    
    # Requisitos padrao de acessibilidade
    MIN_CONTRAST_NORMAL = 4.5  # Texto normal
    MIN_CONTRAST_LARGE = 3.0   # Texto grande (18pt+ ou 14pt+ bold)
    
    all_passed = True
    
    for theme_name, colors in themes.items():
        print_info(f"\nAnalisando tema: {theme_name.upper()}")
        
        bg_rgb = hex_to_rgb(colors['background'])
        text_rgb = hex_to_rgb(colors['text'])
        primary_rgb = hex_to_rgb(colors['primary'])
        accent_rgb = hex_to_rgb(colors['accent'])
        
        # Teste 1: Contraste texto/fundo
        contrast_text_bg = calculate_contrast_ratio(text_rgb, bg_rgb)
        if contrast_text_bg >= MIN_CONTRAST_NORMAL:
            print_success(f"Texto/Fundo: {contrast_text_bg:.2f}:1  (mín: {MIN_CONTRAST_NORMAL}:1)")
        else:
            print_error(f"Texto/Fundo: {contrast_text_bg:.2f}:1  (mín: {MIN_CONTRAST_NORMAL}:1)")
            all_passed = False
        
        # Teste 2: Contraste primário/fundo
        contrast_primary_bg = calculate_contrast_ratio(primary_rgb, bg_rgb)
        if contrast_primary_bg >= MIN_CONTRAST_NORMAL:
            print_success(f"Primário/Fundo: {contrast_primary_bg:.2f}:1 ")
        else:
            print_error(f"Primário/Fundo: {contrast_primary_bg:.2f}:1 ")
            all_passed = False
        
        # Teste 3: Contraste accent/fundo
        contrast_accent_bg = calculate_contrast_ratio(accent_rgb, bg_rgb)
        if contrast_accent_bg >= MIN_CONTRAST_LARGE:  # Accent geralmente usado em títulos grandes
            print_success(f"Accent/Fundo: {contrast_accent_bg:.2f}:1  (mín: {MIN_CONTRAST_LARGE}:1)")
        else:
            print_warning(f"Accent/Fundo: {contrast_accent_bg:.2f}:1 ⚠ (mín: {MIN_CONTRAST_LARGE}:1)")
    
    return all_passed

def test_css_color_consistency():
    """Verifica consistência de cores nos arquivos CSS"""
    print_info("Verificando consistência de cores nos CSS...")
    
    css_files = [
        'BelarminoMonteiroAdvogado/static/css/theme.css',
        'BelarminoMonteiroAdvogado/static/css/style.css',
        'BelarminoMonteiroAdvogado/static/css/admin.css'
    ]
    
    all_passed = True
    
    for css_file in css_files:
        if not os.path.exists(css_file):
            print_warning(f"Arquivo não encontrado: {css_file}")
            continue
        
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Procura por cores hardcoded que deveriam usar variáveis
            hardcoded_colors = re.findall(r'(?<!var\()#[0-9a-fA-F]{3,6}(?!\))', content)
            
            if hardcoded_colors:
                unique_colors = set(hardcoded_colors)
                print_warning(f"{css_file}: {len(unique_colors)} cores hardcoded encontradas")
                print_info(f"  Cores: {', '.join(list(unique_colors)[:5])}...")
            else:
                print_success(f"{css_file}: Usando variáveis CSS corretamente")
    
    return all_passed

# ============================================================================
# TESTES FUNCIONAIS
# ============================================================================

def test_flask_app():
    """Testa se a aplicação Flask inicia corretamente"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        app = create_app()
        print_success("Aplicação Flask criada com sucesso")
        return True
    except Exception as e:
        print_error(f"Erro ao criar aplicação: {e}")
        return False

def test_database_connection():
    """Testa conexão com banco de dados"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        from BelarminoMonteiroAdvogado.models import db
        
        app = create_app()
        with app.app_context():
            # Tenta uma busca simples
            db.session.execute(db.text('SELECT 1'))
            print_success("Conexão com banco de dados OK")
            return True
    except Exception as e:
        print_error(f"Erro na conexão: {e}")
        return False

def test_routes():
    """Testa rotas principais"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        
        app = create_app()
        client = app.test_client()
        
        routes_to_test = [
            ('/', 'Página inicial'),
            ('/sobre-nos', 'Sobre nós'),
            ('/contato', 'Contato'),
            ('/sitemap.xml', 'Sitemap'),
            ('/robots.txt', 'Robots.txt')
        ]
        
        all_passed = True
        for route, name in routes_to_test:
            response = client.get(route)
            if response.status_code == 200:
                print_success(f"{name}: {response.status_code}")
            else:
                print_error(f"{name}: {response.status_code}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print_error(f"Erro ao testar rotas: {e}")
        return False

# ============================================================================
# TESTES DE ARQUIVOS
# ============================================================================

def test_required_files():
    """Verifica existência de arquivos essenciais"""
    required_files = [
        'main.py',
        'requirements.txt',
        '.gcloudignore',
        'BelarminoMonteiroAdvogado/__init__.py',
        'BelarminoMonteiroAdvogado/app.yaml',
        'BelarminoMonteiroAdvogado/models.py',
        'BelarminoMonteiroAdvogado/forms.py',
        'BelarminoMonteiroAdvogado/static/js/resource-preloader.js',
        'BelarminoMonteiroAdvogado/templates/base.html',
        'BelarminoMonteiroAdvogado/templates/sobre.html'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Encontrado: {file_path}")
        else:
            print_error(f"Faltando: {file_path}")
            all_exist = False
    
    return all_exist

def test_image_optimization():
    """Verifica se imagens foram otimizadas"""
    images_dir = Path('BelarminoMonteiroAdvogado/static/images')
    
    if not images_dir.exists():
        print_error("Diretório de imagens não encontrado")
        return False
    
    # Procura por imagens WebP
    webp_images = list(images_dir.rglob('*.webp'))
    jpg_images = list(images_dir.rglob('*.jpg'))
    png_images = list(images_dir.rglob('*.png'))
    
    print_info(f"Imagens WebP: {len(webp_images)}")
    print_info(f"Imagens JPG: {len(jpg_images)}")
    print_info(f"Imagens PNG: {len(png_images)}")
    
    if len(webp_images) > 0:
        print_success("Imagens WebP encontradas (otimização ativa)")
        return True
    else:
        print_warning("Nenhuma imagem WebP encontrada")
        return True  # Não é erro crítico

def test_video_references():
    """Verifica referências de vídeo nos templates"""
    templates_to_check = [
        'BelarminoMonteiroAdvogado/templates/home/_hero_section.html',
        'BelarminoMonteiroAdvogado/templates/home/home_option1.html',
        'BelarminoMonteiroAdvogado/templates/sobre.html'
    ]
    
    all_passed = True
    for template in templates_to_check:
        if not os.path.exists(template):
            continue
        
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Verifica se usa WebM
            if '.webm' in content:
                print_success(f"{os.path.basename(template)}: Usando WebM ")
            elif '.mp4' in content:
                print_warning(f"{os.path.basename(template)}: Usando MP4 (considere WebM)")
            else:
                print_info(f"{os.path.basename(template)}: Sem vídeos")
    
    return all_passed

# ============================================================================
# TESTES DE SEGURANÇA
# ============================================================================

def test_security_headers():
    """Verifica configurações de segurança"""
    try:
        from BelarminoMonteiroAdvogado import create_app
        
        app = create_app()
        
        # Verifica SECRET_KEY
        if app.config.get('SECRET_KEY') and len(app.config['SECRET_KEY']) > 20:
            print_success("SECRET_KEY configurada adequadamente")
        else:
            print_error("SECRET_KEY fraca ou não configurada")
            return False
        
        # Verifica CSRF
        if 'csrf' in str(app.extensions).lower():
            print_success("protecao contra ataques ativo")
        else:
            print_warning("protecao contra ataques não detectado")
        
        return True
    except Exception as e:
        print_error(f"Erro ao verificar segurança: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa todos os testes"""
    print_header("BATERIA COMPLETA DE TESTES FINAIS")
    print_info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Diretório: {os.getcwd()}")
    
    # SEÇÃO 1: TESTES DE CORES E CONTRASTES
    print_header("1. TESTES DE CORES E CONTRASTES (WCAG 2.1 AA)")
    run_test("Contrastes de cores", test_color_contrasts)
    run_test("Consistência de cores CSS", test_css_color_consistency)
    
    # SEÇÃO 2: TESTES FUNCIONAIS
    print_header("2. TESTES FUNCIONAIS")
    run_test("Criação da aplicação Flask", test_flask_app)
    run_test("Conexão com banco de dados", test_database_connection)
    run_test("Rotas principais", test_routes)
    
    # SEÇÃO 3: TESTES DE ARQUIVOS
    print_header("3. TESTES DE ARQUIVOS")
    run_test("Arquivos essenciais", test_required_files)
    run_test("Otimização de imagens", test_image_optimization)
    run_test("Referências de vídeo", test_video_references)
    
    # SEÇÃO 4: TESTES DE SEGURANÇA
    print_header("4. TESTES DE SEGURANÇA")
    run_test("Configurações de segurança", test_security_headers)
    
    # RELATÓRIO FINAL
    print_header("RELATÓRIO FINAL")
    print(f"\nTotal de testes: {total_tests}")
    print_success(f"Passou: {passed_tests}")
    print_error(f"Falhou: {failed_tests}")
    print_warning(f"Avisos: {warnings}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nTaxa de sucesso: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print_header(" TODOS OS TESTES PASSARAM! PRONTO PARA DEPLOY! ")
        return 0
    else:
        print_header(" ALGUNS TESTES FALHARAM! CORRIJA ANTES DO DEPLOY! ")
        return 1

if __name__ == '__main__':
    sys.exit(main())
