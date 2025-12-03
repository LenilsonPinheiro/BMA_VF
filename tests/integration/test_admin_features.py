# -*- coding: utf-8 -*-
"""
==============================================================================
Testes de Integração para Funcionalidades do Admin
==============================================================================

Este módulo contém testes de integração que verificam as funcionalidades
principais do painel de administração, focando em operações de
Criação, Leitura, Atualização e Exclusão (CRUD).

Esses testes simulam um administrador logado interagindo com os formulários
e rotas do painel para modificar o estado da aplicação e, em seguida,
verificam se as mudanças foram corretamente persistidas no banco de dados.
"""
import pytest
from flask import url_for
from BelarminoMonteiroAdvogado.models import db, AreaAtuacao, Pagina

# --- Fixtures ---

@pytest.fixture
def logged_in_client(client):
    """
    Fixture que fornece um cliente de teste já logado como 'admin'.
    Isso evita a repetição do código de login em cada teste que requer autenticação.
    """
    client.post(url_for('auth.login'), data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    yield client
    # O logout é feito implicitamente no final da sessão do cliente de teste.

# --- Testes para Gerenciamento de Áreas de Atuação (Serviços) ---

def test_create_new_service(logged_in_client, app):
    """
    Testa a criação de uma nova Área de Atuação (serviço) através do painel de admin.
    Verifica se o serviço e sua página associada são criados no banco de dados.
    """
    # Dados do novo serviço a ser criado
    service_data = {
        'titulo': 'Direito de Teste',
        'slug': 'direito-de-teste',
        'descricao': 'Descrição para a área de Direito de Teste.',
        'icone': 'bi-check'
    }

    # Simula o POST para a rota de adicionar serviço
    response = logged_in_client.post(
        url_for('admin.add_area_atuacao'),
        data=service_data,
        follow_redirects=True
    )

    # Verificações da Resposta HTTP
    assert response.status_code == 200, "A página de redirecionamento após criar o serviço não carregou."
    assert b'rea de Atuao &quot;Direito de Teste&quot; criada com sucesso!' in response.data, \
        "A mensagem flash de sucesso para criação de serviço não foi encontrada."

    # Verificações no Banco de Dados
    with app.app_context():
        # Verifica se a Área de Atuação foi criada
        new_service = AreaAtuacao.query.filter_by(slug='direito-de-teste').first()
        assert new_service is not None, "A nova área de atuação não foi encontrada no banco de dados."
        assert new_service.titulo == 'Direito de Teste'
        assert new_service.descricao == 'Descrição para a área de Direito de Teste.'

        # Verifica se a Página associada foi criada
        new_page = Pagina.query.filter_by(slug='direito-de-teste').first()
        assert new_page is not None, "A página associada à nova área de atuação não foi criada."
        assert new_page.tipo == 'servico'

def test_edit_service(logged_in_client, app):
    """
    Testa a edição de uma Área de Atuação existente.
    Cria um serviço, depois o edita e verifica se as alterações foram salvas.
    """
    # 1. Setup: Criar um serviço para editar
    with app.app_context():
        service_to_edit = AreaAtuacao(titulo='Serviço Original', slug='servico-original', descricao='Original')
        db.session.add(service_to_edit)
        db.session.commit()

    # 2. Ação: Enviar dados de edição para a rota
    edited_data = {
        'titulo': 'Serviço Editado',
        'descricao': 'Descrição Editada',
        'icone': 'bi-pencil'
    }
    response = logged_in_client.post(
        url_for('admin.edit_service', slug='servico-original'),
        data=edited_data,
        follow_redirects=True
    )
    
    # 3. Verificação: Checar a resposta e o banco de dados
    assert response.status_code == 200
    assert b'rea de Atuao &quot;Servio Editado&quot; atualizada com sucesso!' in response.data, \
        "A mensagem flash de sucesso para edição de serviço não foi encontrada."
    
    with app.app_context():
        edited_service = AreaAtuacao.query.filter_by(slug='servico-original').first()
        assert edited_service is not None
        assert edited_service.titulo == 'Serviço Editado'
        assert edited_service.descricao == 'Descrição Editada'
        assert edited_service.icone == 'bi-pencil'



# --- Testes para Gerenciamento de Membros da Equipe ---

def test_create_team_member(logged_in_client, app):
    """
    Testa a criação de um novo Membro da Equipe através do painel de admin.
    """
    from BelarminoMonteiroAdvogado.models import MembroEquipe
    
    member_data = {
        'nome': 'Advogado de Teste',
        'cargo': 'Sócio de Teste',
        'biografia': 'Uma biografia de teste.'
    }

    response = logged_in_client.post(
        url_for('admin.add_membro_equipe'),
        data=member_data,
        follow_redirects=True,
        content_type='multipart/form-data' # Necessário para uploads de arquivo
    )

    assert response.status_code == 200
    assert b'Membro da equipe &quot;Advogado de Teste&quot; adicionado com sucesso!' in response.data

    with app.app_context():
        new_member = MembroEquipe.query.filter_by(nome='Advogado de Teste').first()
        assert new_member is not None
        assert new_member.cargo == 'Sócio de Teste'

def test_edit_team_member(logged_in_client, app):
    """
    Testa a edição de um Membro da Equipe existente.
    """
    from BelarminoMonteiroAdvogado.models import MembroEquipe
    
    # 1. Setup: Criar um membro para editar
    with app.app_context():
        member_to_edit = MembroEquipe(nome='Membro Original', cargo='Cargo Original')
        db.session.add(member_to_edit)
        db.session.commit()
        member_id = member_to_edit.id

    # 2. Ação: Enviar dados de edição
    edited_data = {
        'nome': 'Membro Editado',
        'cargo': 'Cargo Editado',
        'biografia': 'Bio Editada'
    }
    response = logged_in_client.post(
        url_for('admin.edit_membro', id=member_id),
        data=edited_data,
        follow_redirects=True
    )

    # 3. Verificação
    assert response.status_code == 200
    assert b'Membro &quot;Membro Editado&quot; atualizado com sucesso!' in response.data

    with app.app_context():
        edited_member = MembroEquipe.query.get(member_id)
        assert edited_member.nome == 'Membro Editado'
        assert edited_member.cargo == 'Cargo Editado'


# --- Testes para Gerenciamento de Aparência (Tema e Design) ---

def test_change_theme(logged_in_client, app):
    """
    Testa a funcionalidade de mudança de tema do site.
    """
    from BelarminoMonteiroAdvogado.models import ThemeSettings

    # 1. Ação: Mudar o tema para 'option4'
    response = logged_in_client.post(
        url_for('admin.select_theme'),
        data={'theme': 'option4'},
        follow_redirects=True
    )

    # 2. Verificação
    assert response.status_code == 200
    assert b'Tema do site atualizado para &quot;option4&quot;!' in response.data

    with app.app_context():
        theme_settings = ThemeSettings.query.first()
        assert theme_settings is not None
        assert theme_settings.theme == 'option4'

def test_edit_design_colors(logged_in_client, app):
    """
    Testa a funcionalidade de edição das cores do design.
    """
    from BelarminoMonteiroAdvogado.models import ThemeSettings

    # 1. Dados das novas cores
    new_colors_data = {
        'cor_primaria_tema1': '#ff0000',
        'cor_texto_dark': '#eeeeee',
        'cor_fundo_dark': '#111111'
    }

    # 2. Ação: Enviar as novas cores para o editor de design
    # A rota é /admin/design-editor, mas ela processa o POST e redireciona.
    # O formulário é submetido para a própria rota.
    response = logged_in_client.post(
        url_for('admin.design_editor'),
        data=new_colors_data,
        follow_redirects=True
    )

    # 3. Verificação
    assert response.status_code == 200
    assert b'Configuraes de design salvas com sucesso!' in response.data

    with app.app_context():
        theme_settings = ThemeSettings.query.first()
        assert theme_settings is not None
        assert theme_settings.cor_primaria_tema1 == '#ff0000'
        assert theme_settings.cor_texto_dark == '#eeeeee'
        assert theme_settings.cor_fundo_dark == '#111111'
