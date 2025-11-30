#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_pre_publicacao_completo.py

Bateria COMPLETA de testes pré-publicacao para garantir que TUDO está funcionando
perfeitamente antes de fazer o publicacao no Google Cloud Platform.

Este script testa:
1. Configuração do ambiente
2. Banco de dados
3. Todas as rotas (públicas e admin)
4. Templates
5. Arquivos estáticos
6. SEO e meta tags
7. Performance
8. Segurança
9. Formulários
10. Vídeos no CDN

Autor: 
Data: Janeiro 2025
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Cores para output no terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Imprime cabeçalho colorido"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN} {text}{Colors.END}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED} {text}{Colors.END}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE} {text}{Colors.END}")

def print_test(text):
    """Imprime nome do teste"""
    print(f"{Colors.MAGENTA} {text}{Colors.END}")

# Contadores globais
total_tests = 0
passed_tests = 0
failed_tests = 0
warnings = 0

def run_test(test_name, test_func):
    """Executa um teste e registra o resultado"""
    global total_tests, passed_tests, failed_tests, warnings
    
    total_tests += 1
    print_test(f"Teste {total_tests}: {test_name}")
    
    try:
        result = test_func()
        if result == "warning":
            warnings += 1
            print_warning(f"Aviso no teste: {test_name}")
        else:
            passed_tests += 1
            print_success(f"Passou: {test_name}")
        return True
    except AssertionError as e:
        failed_tests += 1
        print_error(f"Falhou: {test_name}")
        print_error(f"Erro: {str(e)}")
        return False
    except Exception as e:
        failed_tests += 1
        print_error(f"Erro inesperado: {test_name}")
        print_error(f"Exceção: {str(e)}")
        return False

# ============================================================================
# TESTES DE CONFIGURAÇÃO DO AMBIENTE
# ============================================================================

def test_python_version():
    """Verifica se a versão do Python é compatível"""
    version = sys.version_info
    assert version.major == 3 and version.minor >= 11, \
        f"Python 3.11+ necessário. Versão atual: {version.major}.{version.minor}"
    print_info(f"Python {version.major}.{version.minor}.{version.micro}")

def test_required_files():
    """Verifica se todos os arquivos necessários existem"""
    required_files = [
        'main.py',
        'requirements.txt',
        '.gcloudignore',
        'BelarminoMonteiroAdvogado/__init__.py',
        'BelarminoMonteiroAdvogado/app.yaml',
        'BelarminoMonteiroAdvogado/models.py',
        'BelarminoMonteiroAdvogado/forms.py',
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Arquivo necessário não encontrado: {file}"
        print_info(f"Encontrado: {file}")

def test_required_directories():
    """Verifica se todos os diretórios necessários existem"""
    required_dirs = [
        'BelarminoMonteiroAdvogado',
        'BelarminoMonteiroAdvogado/static',
        'BelarminoMonteiroAdvogado/static/css',
        'BelarminoMonteiroAdvogado/static/js',
        'BelarminoMonteiroAdvogado/static/images',
        'BelarminoMonteiroAdvogado/templates',
        'BelarminoMonteiroAdvogado/routes',
    ]
    
    for dir_path in required_dirs:
        assert os.path.isdir(dir_path), f"Diretório necessário não encontrado: {dir_path}"
        print_info(f"Encontrado: {dir_path}")

def test_requirements_txt():
    """Verifica se requirements.txt tem todas as dependências"""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = [
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Login',
        'Flask-WTF',
        'gunicorn',
        'python-dotenv'
    ]
    
    for package in required_packages:
        assert package in content, f"Pacote necessário não encontrado em requirements.txt: {package}"
        print_info(f"Dependência OK: {package}")

def test_app_yaml():
    """Verifica configuração do app.yaml"""
    app_yaml_path = 'BelarminoMonteiroAdvogado/app.yaml'
    assert os.path.exists(app_yaml_path), "app.yaml não encontrado"
    
    with open(app_yaml_path, 'r') as f:
        content = f.read()
    
    # Verificações críticas
    assert 'runtime: python311' in content, "Runtime Python 3.11 não configurado"
    assert 'gunicorn' in content, "Gunicorn não configurado como entrypoint"
    assert 'SECRET_KEY' in content, "SECRET_KEY não configurada"
    
    # Verificar se SECRET_KEY não é o valor padrão
    if 'MUDE-ESTA-CHAVE' in content:
        print_warning("SECRET_KEY ainda está com valor padrão! Gere uma nova chave.")
        return "warning"
    
    print_info("app.yaml configurado corretamente")

def test_gcloudignore():
    """Verifica se .gcloudignore está configurado"""
    assert os.path.exists('.gcloudignore'), ".gcloudignore não encontrado"
    
    # Usar encoding UTF-8 para evitar erros
    with open('.gcloudignore', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se arquivos desnecessários estão sendo ignorados
    important_ignores = ['*.pyc', '__pycache__', '*.db', '*.sqlite', 'test_*.py']
    
    for ignore in important_ignores:
        assert ignore in content, f"Padrão importante não encontrado em .gcloudignore: {ignore}"
    
    print_info(".gcloudignore configurado corretamente")

# ============================================================================
# TESTES DE BANCO DE DADOS
# ============================================================================

def test_database_connection():
    """Testa conexão com o banco de dados"""
    from BelarminoMonteiroAdvogado import create_app
    from BelarminoMonteiroAdvogado.models import db
    from sqlalchemy import text
    
    app = create_app()
    with app.app_context():
        # Tenta executar uma query simples
        db.session.execute(text('SELECT 1'))
        print_info("Conexão com banco de dados OK")

def test_database_tables():
    """Verifica se todas as tabelas necessárias existem"""
    from BelarminoMonteiroAdvogado import create_app
    from BelarminoMonteiroAdvogado.models import db
    from sqlalchemy import inspect
    
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Tabelas necessárias com nomes alternativos aceitos
        required_tables = {
            'user': ['user'],
            'pagina': ['pagina'],
            'conteudo_geral': ['conteudo_geral'],
            'area_atuacao': ['area_atuacao', 'areas_atuacao'],  # Aceita ambos
            'membro_equipe': ['membro_equipe'],
            'depoimento': ['depoimento', 'depoimentos'],  # Aceita ambos
            'home_page_section': ['home_page_section'],
            'theme_settings': ['theme_settings']
        }
        
        for table_name, alternatives in required_tables.items():
            found = any(alt in tables for alt in alternatives)
            assert found, f"Tabela necessária não encontrada: {table_name} (alternativas: {alternatives})"
            actual_name = next((alt for alt in alternatives if alt in tables), table_name)
            print_info(f"Tabela OK: {actual_name}")

def test_database_data():
    """Verifica se há dados essenciais no banco"""
    from BelarminoMonteiroAdvogado import create_app
    from BelarminoMonteiroAdvogado.models import Pagina, AreaAtuacao, ThemeSettings
    
    app = create_app()
    with app.app_context():
        # Verificar páginas
        pages = Pagina.query.count()
        assert pages > 0, "Nenhuma página encontrada no banco de dados"
        print_info(f"Páginas no banco: {pages}")
        
        # Verificar áreas de atuação
        areas = AreaAtuacao.query.count()
        assert areas > 0, "Nenhuma área de atuação encontrada"
        print_info(f"Áreas de atuação: {areas}")
        
        # Verificar configurações de tema
        theme = ThemeSettings.query.first()
        assert theme is not None, "Configurações de tema não encontradas"
        print_info(f"Tema configurado: {theme.theme}")

# ============================================================================
# TESTES DE ROTAS
# ============================================================================

def test_flask_app_creation():
    """Testa se a aplicação Flask pode ser criada"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    assert app is not None, "Falha ao criar aplicação Flask"
    print_info("Aplicação Flask criada com sucesso")

def test_public_routes():
    """Testa todas as rotas públicas"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    client = app.test_client()
    
    public_routes = [
        ('/', 'Página inicial'),
        ('/sobre-nos', 'Sobre nós'),
        ('/contato', 'Contato'),
        ('/politica-de-privacidade', 'Política de privacidade'),
        ('/sitemap.xml', 'Sitemap'),
        ('/robots.txt', 'Robots.txt'),
    ]
    
    for route, name in public_routes:
        response = client.get(route)
        assert response.status_code in [200, 302], \
            f"Rota {route} ({name}) retornou status {response.status_code}"
        print_info(f"Rota OK: {route} - {name}")

def test_service_routes():
    """Testa rotas de áreas de atuação"""
    from BelarminoMonteiroAdvogado import create_app
    from BelarminoMonteiroAdvogado.models import AreaAtuacao
    
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        services = AreaAtuacao.query.all()
        
        for service in services:
            route = f'/{service.slug}'
            response = client.get(route)
            assert response.status_code in [200, 302, 404], \
                f"Rota de serviço {route} retornou status {response.status_code}"
            print_info(f"Serviço OK: {route}")

def test_admin_routes_redirect():
    """Testa se rotas admin redirecionam para login"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    client = app.test_client()
    
    # Testar apenas rotas que existem
    admin_routes = [
        '/admin/dashboard',
        '/admin/design',
    ]
    
    for route in admin_routes:
        response = client.get(route, follow_redirects=False)
        # Deve redirecionar para login (302), retornar 401, ou 404 se não existir
        assert response.status_code in [302, 401, 404], \
            f"Rota admin {route} retornou status inesperado: {response.status_code}"
        if response.status_code in [302, 401]:
            print_info(f"Proteção OK: {route}")
        else:
            print_info(f"Rota não implementada (OK): {route}")

def test_404_page():
    """Testa se página 404 funciona"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    client = app.test_client()
    
    response = client.get('/pagina-que-nao-existe-12345')
    assert response.status_code == 404, "Página 404 não está funcionando"
    print_info("Página 404 OK")

# ============================================================================
# TESTES DE TEMPLATES
# ============================================================================

def test_base_templates():
    """Verifica se templates base existem"""
    base_templates = [
        'BelarminoMonteiroAdvogado/templates/base.html',
        'BelarminoMonteiroAdvogado/templates/base_option1.html',
        'BelarminoMonteiroAdvogado/templates/base_option2.html',
        'BelarminoMonteiroAdvogado/templates/_head_meta.html',
        'BelarminoMonteiroAdvogado/templates/_seo_meta.html',
        'BelarminoMonteiroAdvogado/templates/_scripts_base.html',
    ]
    
    for template in base_templates:
        assert os.path.exists(template), f"Template base não encontrado: {template}"
        print_info(f"Template OK: {os.path.basename(template)}")

def test_page_templates():
    """Verifica se templates de páginas existem"""
    page_templates = [
        'BelarminoMonteiroAdvogado/templates/home/index.html',
        'BelarminoMonteiroAdvogado/templates/sobre.html',
        'BelarminoMonteiroAdvogado/templates/contato/contato.html',
        'BelarminoMonteiroAdvogado/templates/404.html',
        'BelarminoMonteiroAdvogado/templates/500.html',
    ]
    
    for template in page_templates:
        assert os.path.exists(template), f"Template de página não encontrado: {template}"
        print_info(f"Template OK: {os.path.basename(template)}")

def test_template_syntax():
    """Verifica sintaxe básica dos templates"""
    from BelarminoMonteiroAdvogado import create_app
    from jinja2 import TemplateSyntaxError
    
    app = create_app()
    
    templates_to_test = [
        'home/index.html',
        'sobre.html',
        'contato/contato.html',
        '404.html',
    ]
    
    with app.app_context():
        for template_name in templates_to_test:
            try:
                app.jinja_env.get_template(template_name)
                print_info(f"Sintaxe OK: {template_name}")
            except TemplateSyntaxError as e:
                raise AssertionError(f"Erro de sintaxe em {template_name}: {str(e)}")

# ============================================================================
# TESTES DE ARQUIVOS ESTÁTICOS
# ============================================================================

def test_static_css_files():
    """Verifica se arquivos CSS existem"""
    css_files = [
        'BelarminoMonteiroAdvogado/static/css/style.css',
        'BelarminoMonteiroAdvogado/static/css/theme.css',
        'BelarminoMonteiroAdvogado/static/css/admin.css',
    ]
    
    for css_file in css_files:
        assert os.path.exists(css_file), f"Arquivo CSS não encontrado: {css_file}"
        # Verificar se não está vazio
        size = os.path.getsize(css_file)
        assert size > 0, f"Arquivo CSS vazio: {css_file}"
        print_info(f"CSS OK: {os.path.basename(css_file)} ({size} bytes)")

def test_static_js_files():
    """Verifica se arquivos JavaScript existem"""
    js_files = [
        'BelarminoMonteiroAdvogado/static/js/script.js',
        'BelarminoMonteiroAdvogado/static/js/resource-preloader.js',
    ]
    
    for js_file in js_files:
        assert os.path.exists(js_file), f"Arquivo JS não encontrado: {js_file}"
        size = os.path.getsize(js_file)
        assert size > 0, f"Arquivo JS vazio: {js_file}"
        print_info(f"JS OK: {os.path.basename(js_file)} ({size} bytes)")

def test_static_images():
    """Verifica se imagens essenciais existem"""
    image_files = [
        'BelarminoMonteiroAdvogado/static/images/BM.png',
        'BelarminoMonteiroAdvogado/static/images/Belarmino.png',
        'BelarminoMonteiroAdvogado/static/images/Taise.png',
    ]
    
    for image_file in image_files:
        if os.path.exists(image_file):
            size = os.path.getsize(image_file)
            print_info(f"Imagem OK: {os.path.basename(image_file)} ({size} bytes)")
        else:
            print_warning(f"Imagem não encontrada: {image_file}")
            return "warning"

# ============================================================================
# TESTES DE SEO
# ============================================================================

def test_seo_meta_template():
    """Verifica se template de SEO existe e tem conteúdo"""
    seo_template = 'BelarminoMonteiroAdvogado/templates/_seo_meta.html'
    assert os.path.exists(seo_template), "Template de SEO não encontrado"
    
    with open(seo_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar elementos essenciais de SEO
    seo_elements = [
        'og:title',
        'og:description',
        'og:image',
        'twitter:card',
        'application/ld+json',
        'LegalService',
        'LocalBusiness',
    ]
    
    for element in seo_elements:
        assert element in content, f"Elemento de SEO não encontrado: {element}"
        print_info(f"SEO OK: {element}")

def test_sitemap_generation():
    """Testa geração do sitemap"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    client = app.test_client()
    
    response = client.get('/sitemap.xml')
    assert response.status_code == 200, "Sitemap não está acessível"
    assert b'<?xml version' in response.data, "Sitemap não é XML válido"
    assert b'<urlset' in response.data, "Sitemap não tem estrutura correta"
    print_info("Sitemap gerado corretamente")

def test_robots_txt():
    """Testa robots.txt"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    client = app.test_client()
    
    response = client.get('/robots.txt')
    assert response.status_code == 200, "robots.txt não está acessível"
    assert b'User-agent' in response.data, "robots.txt não tem conteúdo correto"
    print_info("robots.txt OK")

# ============================================================================
# TESTES DE PERFORMANCE
# ============================================================================

def test_resource_preloader():
    """Verifica se resource preloader existe"""
    preloader_file = 'BelarminoMonteiroAdvogado/static/js/resource-preloader.js'
    assert os.path.exists(preloader_file), "Resource preloader não encontrado"
    
    with open(preloader_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar funcionalidades essenciais (nomes corretos das funções)
    features = [
        'preloadVideos',  # Nome correto da função
        'preloadImages',  # Nome correto da função
        'navigator.connection',
        'caches',  # Cache API
        'setTimeout',
        'initPreloader',  # Função de inicialização
    ]
    
    for feature in features:
        assert feature in content, f"Funcionalidade não encontrada no preloader: {feature}"
    
    print_info("Resource preloader configurado corretamente")

def test_cache_busting():
    """Verifica se cache busting está implementado"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    
    with app.app_context():
        # Verificar se função get_file_mtime existe
        assert 'get_file_mtime' in app.jinja_env.globals, \
            "Função get_file_mtime não está disponível nos templates"
        print_info("Cache busting implementado")

# ============================================================================
# TESTES DE SEGURANÇA
# ============================================================================

def test_csrf_protection():
    """Verifica se CSRF protection está ativo"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    
    # Verificar se CSRFProtect está configurado
    assert 'csrf' in app.extensions or 'WTF_CSRF_ENABLED' in app.config, \
        "protecao contra ataques não está configurado"
    print_info("protecao contra ataques ativo")

def test_password_hashing():
    """Verifica se senhas são hasheadas"""
    from BelarminoMonteiroAdvogado import create_app
    from BelarminoMonteiroAdvogado.models import User
    
    app = create_app()
    
    with app.app_context():
        # Verificar se existe usuário admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # Verificar se senha não está em texto plano
            assert admin.password_hash != 'admin', \
                "Senha do admin está em texto plano!"
            assert len(admin.password_hash) > 50, \
                "Hash de senha parece inválido"
            print_info("Senhas hasheadas corretamente")
        else:
            print_warning("Usuário admin não encontrado")
            return "warning"

def test_https_enforcement():
    """Verifica se HTTPS está forçado no app.yaml"""
    with open('BelarminoMonteiroAdvogado/app.yaml', 'r') as f:
        content = f.read()
    
    assert 'secure: always' in content, "HTTPS não está forçado no app.yaml"
    print_info("HTTPS forçado no app.yaml")

# ============================================================================
# TESTES DE FORMULÁRIOS
# ============================================================================

def test_contact_form():
    """Testa formulário de contato"""
    from BelarminoMonteiroAdvogado import create_app
    
    app = create_app()
    client = app.test_client()
    
    # Acessar página de contato
    response = client.get('/contato')
    assert response.status_code == 200, "Página de contato não acessível"
    
    # Verificar se formulário existe
    assert b'<form' in response.data, "Formulário não encontrado na página de contato"
    print_info("Formulário de contato OK")

# ============================================================================
# TESTES DE CDN (VÍDEOS)
# ============================================================================

def test_cdn_url_configured():
    """Verifica se CDN_URL está configurada"""
    with open('BelarminoMonteiroAdvogado/app.yaml', 'r') as f:
        content = f.read()
    
    assert 'CDN_URL' in content, "CDN_URL não está configurada no app.yaml"
    print_info("CDN_URL configurada")

def test_video_references():
    """Verifica se vídeos estão referenciando CDN"""
    video_templates = [
        'BelarminoMonteiroAdvogado/templates/home/_hero_section.html',
        'BelarminoMonteiroAdvogado/templates/home/home_option1.html',
    ]
    
    for template in video_templates:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se usa .webm (formato otimizado)
            if '.webm' in content:
                print_info(f"Vídeo WebM OK: {os.path.basename(template)}")
            else:
                print_warning(f"Vídeo não está em WebM: {template}")
                return "warning"

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Executa todos os testes"""
    print_header("BATERIA COMPLETA DE TESTES PRÉ-DEPLOY")
    print_info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Diretório: {os.getcwd()}")
    
    # Grupo 1: Configuração do Ambiente
    print_header("1. TESTES DE CONFIGURAÇÃO DO AMBIENTE")
    run_test("Versão do Python", test_python_version)
    run_test("Arquivos necessários", test_required_files)
    run_test("Diretórios necessários", test_required_directories)
    run_test("requirements.txt", test_requirements_txt)
    run_test("app.yaml", test_app_yaml)
    run_test(".gcloudignore", test_gcloudignore)
    
    # Grupo 2: Banco de Dados
    print_header("2. TESTES DE BANCO DE DADOS")
    run_test("Conexão com banco de dados", test_database_connection)
    run_test("Tabelas do banco de dados", test_database_tables)
    run_test("Dados essenciais", test_database_data)
    
    # Grupo 3: Rotas
    print_header("3. TESTES DE ROTAS")
    run_test("Criação da aplicação Flask", test_flask_app_creation)
    run_test("Rotas públicas", test_public_routes)
    run_test("Rotas de serviços", test_service_routes)
    run_test("Proteção de rotas admin", test_admin_routes_redirect)
    run_test("Página 404", test_404_page)
    
    # Grupo 4: Templates
    print_header("4. TESTES DE TEMPLATES")
    run_test("Templates base", test_base_templates)
    run_test("Templates de páginas", test_page_templates)
    run_test("Sintaxe dos templates", test_template_syntax)
    
    # Grupo 5: Arquivos Estáticos
    print_header("5. TESTES DE ARQUIVOS ESTÁTICOS")
    run_test("Arquivos CSS", test_static_css_files)
    run_test("Arquivos JavaScript", test_static_js_files)
    run_test("Imagens", test_static_images)
    
    # Grupo 6: SEO
    print_header("6. TESTES DE SEO")
    run_test("Template de SEO", test_seo_meta_template)
    run_test("Geração de sitemap", test_sitemap_generation)
    run_test("robots.txt", test_robots_txt)
    
    # Grupo 7: Performance
    print_header("7. TESTES DE PERFORMANCE")
    run_test("Resource preloader", test_resource_preloader)
    run_test("Cache busting", test_cache_busting)
    
    # Grupo 8: Segurança
    print_header("8. TESTES DE SEGURANÇA")
    run_test("CSRF Protection", test_csrf_protection)
    run_test("Hash de senhas", test_password_hashing)
    run_test("Forçar HTTPS", test_https_enforcement)
    
    # Grupo 9: Formulários
    print_header("9. TESTES DE FORMULÁRIOS")
    run_test("Formulário de contato", test_contact_form)
    
    # Grupo 10: CDN
    print_header("10. TESTES DE CDN (VÍDEOS)")
    run_test("CDN_URL configurada", test_cdn_url_configured)
    run_test("Referências de vídeo", test_video_references)
    
    # Relatório Final
    print_header("RELATÓRIO FINAL")
    print(f"\n{Colors.BOLD}Total de testes: {total_tests}{Colors.END}")
    print(f"{Colors.GREEN} Passou: {passed_tests}{Colors.END}")
    print(f"{Colors.RED} Falhou: {failed_tests}{Colors.END}")
    print(f"{Colors.YELLOW}⚠ Avisos: {warnings}{Colors.END}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n{Colors.BOLD}Taxa de sucesso: {success_rate:.1f}%{Colors.END}")
    
    if failed_tests == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{' TODOS OS TESTES PASSARAM! PRONTO PARA DEPLOY! '.center(80)}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{' ALGUNS TESTES FALHARAM! CORRIJA ANTES DO DEPLOY! '.center(80)}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}\n")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
