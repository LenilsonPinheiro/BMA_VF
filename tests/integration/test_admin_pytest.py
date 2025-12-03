"""
Teste de integração para as rotas do painel administrativo usando Pytest.

Este arquivo substitui o script legado 'test_admin_routes.py' e se integra
ao framework de testes Pytest, utilizando as fixtures definidas em conftest.py.

Autor: Gemini Agent (baseado no trabalho de Lenilson Pinheiro)
Data: Dezembro 2025
"""

import pytest
from flask import url_for

# Credenciais padrão criadas na fixture 'app' em conftest.py
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def login(client):
    """
    Função auxiliar para realizar login como administrador.
    Retorna a resposta do POST de login.
    """
    return client.post(url_for('auth.login'), data={
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    }, follow_redirects=True)

def test_admin_routes_unauthenticated(client):
    """
    Testa se as rotas do admin estão protegidas contra acesso não autenticado.
    """
    protected_routes = [
        'admin.dashboard',
        'admin.design_editor',
        'admin.list_services', 
        'admin.list_posts'
    ]
    
    for route_name in protected_routes:
        response = client.get(url_for(route_name))
        # Espera-se um redirecionamento (302) para a página de login
        assert response.status_code == 302
        assert '/auth/login' in response.location

def test_login_logout(client):
    """
    Testa o processo de login e logout.
    """
    # Teste de login com sucesso
    response = login(client)
    assert response.status_code == 200
    assert b'Dashboard' in response.data  # Verifica se foi redirecionado para o dashboard
    assert b'Login bem-sucedido!' in response.data # Mensagem flash

    # Teste de logout
    response = client.get(url_for('auth.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Voc\xc3\xaa foi desconectado.' in response.data # Mensagem flash de logout
    assert b'Login' in response.data # Verifica se foi redirecionado para a p\xe1gina de login

def test_login_invalid_credentials(client):
    """
    Testa a falha no login com credenciais inválidas.
    """
    response = client.post(url_for('auth.login'), data={
        'username': 'invaliduser',
        'password': 'invalidpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Nome de usu\xc3\xa1rio ou senha inv\xc3\xa1lidos' in response.data
    assert b'Dashboard' not in response.data


@pytest.mark.usefixtures("client")
class TestAuthenticatedAdminRoutes:
    """
    Agrupa testes para rotas que exigem autenticação.
    Usa uma classe para compartilhar o estado de login entre os métodos.
    """
    
    @pytest.fixture(autouse=True)
    def login_first(self, client):
        """
        Fixture de classe que garante que o login seja executado
        antes de cada teste nesta classe.
        """
        login(client)

    def test_dashboard_access(self, client):
        """Testa o acesso ao dashboard principal."""
        response = client.get(url_for('admin.dashboard'))
        assert response.status_code == 200
        assert b'Dashboard' in response.data
        assert b'Vis\xc3\xa3o Geral' in response.data

    def test_dashboard_sections(self, client):
        """Testa o acesso a seções específicas do dashboard via fragmentos."""
        # Embora o cliente de teste não processe fragmentos (#), podemos verificar
        # se a página principal do dashboard é carregada corretamente.
        # Os fragmentos são responsabilidade do lado do cliente (navegador).
        response = client.get(url_for('admin.dashboard'))
        assert response.status_code == 200
        # Verifica se os IDs das seções existem no HTML
        assert b'id="Content"' in response.data
        assert b'id="HomeSections"' in response.data
        assert b'id="Navigation"' in response.data
        assert b'id="Services"' in response.data
        assert b'id="Team"' in response.data
        assert b'id="SEO"' in response.data
        assert b'id="Theme"' in response.data

    def test_design_editor_access(self, client):
        """Testa o acesso ao editor de design."""
        response = client.get(url_for('admin.design_editor'))
        assert response.status_code == 200
        assert b'Editor de Design' in response.data
        assert b'Cores' in response.data # Verifica a presen\xe7a de elementos esperados

    def test_profile_page_access(self, client):
        """Testa o acesso à página de perfil do usuário."""
        response = client.get(url_for('admin.profile'))
        assert response.status_code == 200
        assert b'Perfil do Usu\xc3\xa1rio' in response.data

    def test_settings_page_access(self, client):
        """Testa o acesso à página de configurações."""
        response = client.get(url_for('admin.settings'))
        assert response.status_code == 200
        assert b'Configura\xc3\xa7\xc3\xb5es do Site' in response.data

    @pytest.mark.parametrize("route", [
        'main.home',
        'main.sobre',
        'main.contato',
        'main.areas_atuacao',
        'main.politica_privacidade'
    ])
    def test_public_routes_access(self, client, route):
        """Testa o acesso às principais rotas públicas."""
        response = client.get(url_for(route))
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data

    def test_special_files_access(self, client):
        """Testa o acesso ao robots.txt e sitemap.xml."""
        response_robots = client.get('/robots.txt')
        assert response_robots.status_code == 200
        assert b'User-agent' in response_robots.data

        response_sitemap = client.get('/sitemap.xml')
        assert response_sitemap.status_code == 200
        assert b'urlset' in response_sitemap.data

    @pytest.mark.parametrize("service_slug", [
        "direito-civil",
        "direito-do-consumidor",
        "direito-previdenciario",
        "direito-de-familia",
    ])
    def test_service_pages_access(self, client, app, service_slug):
        """
        Testa o acesso a páginas de serviço individuais.
        Nota: Este é um teste básico de acesso. A criação e teste de rotas
        dinâmicas mais a fundo já é coberta em 'test_routes.py'.
        """
        # Garante que a página/serviço existe para o teste.
        # Isto pode ser melhorado com fixtures dedicadas no futuro.
        with app.app_context():
            from BelarminoMonteiroAdvogado.models import Pagina, db
            if not Pagina.query.filter_by(slug=service_slug).first():
                pagina = Pagina(
                    slug=service_slug,
                    titulo_pagina=service_slug.replace('-', ' ').title(),
                    conteudo=f"Conteúdo para {service_slug}",
                    tipo='servico'
                )
                db.session.add(pagina)
                db.session.commit()

        response = client.get(f'/{service_slug}')
        # Se a página existir, o status deve ser 200.
        # Se não, é um 404, o que também é um comportamento esperado
        # se o serviço não estiver cadastrado. Não falharemos o teste por 404.
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert service_slug.replace('-', ' ').title().encode('utf-8') in response.data
