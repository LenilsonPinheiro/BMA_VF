import os
import pytest
from sqlalchemy import text
from BelarminoMonteiroAdvogado import create_app, db
from BelarminoMonteiroAdvogado.models import ThemeSettings

# Fixture para o número do tema
@pytest.fixture(params=[1, 2, 3, 4, 5, 6, 7, 8])
def theme_number(request):
    return request.param

# Fixture de compatibilidade para testes que usam theme_num
@pytest.fixture
def theme_num(theme_number):
    return theme_number

# Fixture para o nome do tema
@pytest.fixture
def theme_name(theme_number):
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

# Fixture para a opção do tema (usada nas classes CSS)
@pytest.fixture
def theme_option(theme_number):
    return f"option{theme_number}"

# Fixture para o aplicativo Flask
@pytest.fixture(scope='session')
def app():
    # Configuração para testes
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    }
    
    # Cria o app com a configuração de teste
    app = create_app(test_config=config)
    
    with app.app_context():
        db.create_all()
        
        # Cria usuário admin para testes de login
        from BelarminoMonteiroAdvogado.models import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('admin'))
            db.session.add(admin)
            db.session.commit()

        # Garante que existe uma configuração de tema
        theme = ThemeSettings.query.first()
        if not theme:
            theme = ThemeSettings(theme='option1')
            db.session.add(theme)
            db.session.commit()
        
        yield app
    
    # Limpeza após os testes
    with app.app_context():
        db.drop_all()

# Fixture para o cliente de teste
@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client

# Fixture para o runner de linha de comando
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

