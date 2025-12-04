"""
Teste de integração para as rotas da aplicação.

Autor: Lenilson Pinheiro
Data: Dezembro 2025
"""

import pytest
from BelarminoMonteiroAdvogado.models import AreaAtuacao, db

def test_homepage(client):
    """Testa a rota da página inicial."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data

def test_sobre_nos(client):
    """Testa a rota Sobre Nós."""
    response = client.get('/sobre-nos')
    assert response.status_code == 200
    # Verifica se algum dos textos possíveis está na resposta
    assert any(text in response.data.decode('utf-8', errors='ignore') 
              for text in ['Sobre Nós', 'Sobre', 'Sobre o Escritório'])

def test_contato(client):
    """Testa a rota de Contato."""
    response = client.get('/contato')
    assert response.status_code == 200
    # Verifica se algum dos textos de contato possíveis está na resposta
    assert any(text in response.data.decode('utf-8', errors='ignore')
              for text in ['Contato', 'Entre em Contato', 'Fale Conosco'])

def test_areas_atuacao(client):
    """Testa a rota de Áreas de Atuação."""
    response = client.get('/areas-de-atuacao')
    assert response.status_code == 200
    assert 'Áreas de Atuação'.encode('utf-8') in response.data

def test_politica_privacidade(client):
    """Testa a rota de Política de Privacidade."""
    response = client.get('/politica-de-privacidade')
    assert response.status_code == 200
    assert 'Política de Privacidade'.encode('utf-8') in response.data

def test_login_page(client):
    """Testa a rota de Login."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    # Verifica se algum dos textos de login possíveis está na resposta
    assert any(text in response.data.decode('utf-8', errors='ignore')
              for text in ['Login', 'Entrar', 'Autenticação', 'Acesso'])

def test_dynamic_service_routes(client, app):
    """Testa as rotas dinâmicas de serviços."""
    with app.app_context():
        from BelarminoMonteiroAdvogado.models import Pagina
        
        # Limpa áreas de atuação e páginas existentes para evitar conflitos
        AreaAtuacao.query.delete()
        Pagina.query.filter(Pagina.slug.in_(['direito-civil', 'direito-consumidor'])).delete()
        db.session.commit()
        
        # Cria algumas áreas de atuação de teste
        areas = [
            AreaAtuacao(
                titulo="Direito Civil",
                slug="direito-civil",
                descricao="Área de atuação em Direito Civil",
                icone="balance-scale.svg",
                categoria="Direito",
                ordem=1,
                ativo=True
            ),
            AreaAtuacao(
                titulo="Direito do Consumidor",
                slug="direito-consumidor",
                descricao="Área de atuação em Direito do Consumidor",
                icone="shopping-cart.svg",
                categoria="Direito",
                ordem=2,
                ativo=True
            )
        ]
        
        # Cria as páginas correspondentes
        paginas = [
            Pagina(
                slug=area.slug,
                titulo_menu=area.titulo,
                titulo_pagina=area.titulo,
                conteudo=f"<h1>{area.titulo}</h1><p>{area.descricao}</p>",
                tipo='servico',
                template_path='servico.html',
                ativo=True,
                mostrar_no_menu=True,
                ordem_menu=area.ordem
            ) for area in areas
        ]
        
        db.session.add_all(areas + paginas)
        db.session.commit()
        
        # Testa cada rota dinâmica
        for area in areas:
            response = client.get(f'/{area.slug}')
            assert response.status_code == 200, f"Falha ao acessar a rota /{area.slug}"
            assert area.titulo.encode('utf-8') in response.data, f"Título '{area.titulo}' não encontrado na resposta"

def test_404_page(client):
    """Testa a página 404 para rotas inexistentes."""
    response = client.get('/rota-que-nao-existe')
    assert response.status_code == 404
    assert 'Página não encontrada'.encode('utf-8') in response.data or b'404' in response.data

def test_health_check(client):
    """Testa a rota de health check."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}
