# -*- coding: utf-8 -*-
"""
==============================================================================
Arquivo de Configuração de Testes (Pytest Fixtures)
==============================================================================

Este arquivo (`conftest.py`) é utilizado pelo Pytest para definir "fixtures",
que são funções auxiliares e objetos de dados compartilhados entre os testes.
As fixtures definidas aqui ajudam a criar um ambiente de teste consistente e
reprodutível para a aplicação.

Fixtures Principais:
--------------------
- **app:** Cria e configura uma instância da aplicação Flask em modo de teste
  (`TESTING=True`). Utiliza um banco de dados SQLite em memória para garantir
  isolamento e velocidade. A fixture tem escopo de sessão, significando que
  é criada apenas uma vez por sessão de teste.
- **client:** Fornece um cliente de teste do Flask (`test_client`) para
  simular requisições HTTP às rotas da aplicação sem a necessidade de um
  servidor web real. Tem escopo de função, então um novo cliente é criado
  para cada função de teste.
- **runner:** Fornece um executor de comandos de CLI (`test_cli_runner`) para
  testar os comandos de linha de comando personalizados do Flask.
- **Fixtures de Tema:** Um conjunto de fixtures parametrizadas (`theme_number`,
  `theme_name`, `theme_option`) para facilitar a execução de testes em
  diferentes temas visuais do site.

O uso de fixtures promove a reutilização de código e torna os testes mais
limpos e fáceis de manter.
"""
import os
import pytest
from sqlalchemy import text
from BelarminoMonteiroAdvogado import create_app, db
from BelarminoMonteiroAdvogado.models import ThemeSettings

@pytest.fixture(params=[1, 2, 3, 4, 5, 6, 7, 8])
def theme_number(request):
    """Fixture parametrizada que fornece o número de cada tema (1 a 8)."""
    return request.param

@pytest.fixture
def theme_num(theme_number):
    """Fixture de compatibilidade que simplesmente retorna o `theme_number`."""
    return theme_number

@pytest.fixture
def theme_name(theme_number):
    """
    Retorna um nome descritivo para um tema com base em seu número.
    Ex: 1 -> "Tema Clássico"
    """
    themes = {
        1: "Tema Clássico",
        2: "Tema Escuro",
        3: "Tema Azul",
        4: "Tema Verde",
        5: "Tema Vermelho",
        6: "Tema Roxo",
        7: "Tema Laranja",
        8: "Tema Minimalista"
    }
    return themes.get(theme_number, f"Tema {theme_number}")

@pytest.fixture
def theme_option(theme_number):
    """
    Retorna o nome da opção do tema no formato 'optionX'.
    Ex: 1 -> "option1"
    """
    return f"option{theme_number}"

@pytest.fixture(scope='session')
def app():
    """
    Cria e configura uma instância da aplicação Flask para a sessão de testes.

    - Configura a aplicação para o modo de teste.
    - Usa um banco de dados SQLite em memória para isolamento.
    - Desabilita CSRF para simplificar os testes de formulário.
    - Cria todas as tabelas do banco de dados e um usuário admin padrão.
    - Ao final da sessão, derruba todas as tabelas do banco de dados.
    """
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    }
    
    app = create_app(test_config=config)
    
    with app.app_context():
        db.create_all()
        
        # Cria um usuário administrador para testes de rotas protegidas
        from BelarminoMonteiroAdvogado.models import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('admin'))
            db.session.add(admin)
            db.session.commit()

        # Garante que a tabela de configurações de tema tenha um registro inicial
        theme = ThemeSettings.query.first()
        if not theme:
            theme = ThemeSettings(theme='option1')
            db.session.add(theme)
            db.session.commit()
        
        yield app
    
    # Limpeza após o término de todos os testes da sessão
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """
    Fornece um cliente de teste do Flask para simular requisições HTTP.
    
    Esta fixture tem escopo de função, garantindo que cada teste receba um
    cliente "limpo" e um contexto de requisição isolado.
    """
    with app.test_client() as client:
        yield client

@pytest.fixture
def runner(app):
    """
    Fornece um `test_cli_runner` para testar os comandos de CLI do Flask.
    """
    return app.test_cli_runner()
