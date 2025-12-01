import pytest
from BelarminoMonteiroAdvogado import create_app, db
from BelarminoMonteiroAdvogado.models import User, AreaAtuacao
from werkzeug.security import generate_password_hash
@pytest.fixture
def app():
    """
    Cria uma instância da aplicação configurada para testes.
    Autor: Lenilson Pinheiro
    Data: Janeiro 2025
    """

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "UPLOAD_FOLDER": "./test_uploads"
    })
    
    with app.app_context():
        db.drop_all() # Limpa tudo
        db.create_all() # Recria
        
        # Cria admin
        admin = User(username='admin', password_hash=generate_password_hash('admin'))
        db.session.add(admin)
        db.session.commit()
            
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app): return app.test_client()

def test_login_page_loads(client):
    assert client.get('/auth/login').status_code == 200

def test_login_success(client):
    response = client.post('/auth/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    # Verifica sucesso (status 200 E presença de texto do dashboard)
    assert response.status_code == 200
    assert b"dashboard" in response.data.lower() or b"painel" in response.data.lower()

def test_create_service(client):
    client.post('/auth/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    response = client.post('/admin/add-area-atuacao', data={
        'titulo': 'Direito Digital Teste',
        'slug': 'direito-digital-teste',
        'descricao': 'Teste',
        'icone': 'bi-cpu'
    }, follow_redirects=True)
    assert response.status_code == 200