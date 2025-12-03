import pytest
from BelarminoMonteiroAdvogado import create_app, db
from BelarminoMonteiroAdvogado.models import User, AreaAtuacao
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(app): return app.test_client()

def test_login_page_loads(client):
    assert client.get('/auth/login').status_code == 200

def test_login_success(client):
    response = client.post('/auth/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    # Verifica sucesso (status 200 E presença de texto do dashboard)
    assert response.status_code == 200
    assert b"dashboard" in response.data.lower() or b"painel" in response.data.lower()

def test_create_service(client, app):  # Adiciona a fixture 'app' para acesso ao contexto
    # Faz login como admin
    client.post('/auth/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    
    # Dados para a nova área de atuação
    area_data = {
        'titulo': 'Direito Digital Teste',
        'slug': 'direito-digital-teste',
        'descricao': 'Descrição detalhada sobre direito digital.',
        'icone': 'bi-cpu'
    }

    # Envia a requisição para criar a área
    response = client.post('/admin/add-area-atuacao', data=area_data, follow_redirects=True)
    assert response.status_code == 200, "A página de resposta não carregou corretamente."

    # Verifica se a área de atuação foi realmente criada no banco de dados
    with app.app_context():
        area = AreaAtuacao.query.filter_by(slug='direito-digital-teste').first()
        assert area is not None, "A área de atuação não foi encontrada no banco de dados."
        assert area.titulo == 'Direito Digital Teste', "O título da área de atuação não corresponde ao esperado."