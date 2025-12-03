# -*- coding: utf-8 -*-
"""
Arquivo: test_theme_utils.py
Descrição: Módulo do sistema Belarmino Monteiro Advogado.
Autor: Equipe de Engenharia (Automated)
Data: 2025
"""

import pytest
from flask import url_for

def test_theme_change_in_db(app, theme_option):
    """Testa se a mudança de tema é persistida corretamente no banco de dados."""
    with app.app_context():
        from BelarminoMonteiroAdvogado.models import ThemeSettings, db
        
        theme_setting = ThemeSettings.query.first()
        if not theme_setting:
            theme_setting = ThemeSettings(theme=theme_option)
            db.session.add(theme_setting)
        else:
            theme_setting.theme = theme_option
        
        db.session.commit()
        
        updated_theme = ThemeSettings.query.first()
        assert updated_theme.theme == theme_option, f"Falha ao definir o tema para {theme_option} no banco de dados."

@pytest.mark.parametrize("theme_num", range(1, 9))
def test_theme_css_loading_on_homepage(client, app, theme_num):
    """
    Testa se a página inicial carrega e se a estrutura de CSS correta é carregada para cada tema.
    Verifica a presença de:
    1. base.css (estrutura)
    2. theme-light.css (variáveis light)
    3. theme-dark.css (variáveis dark)
    4. theme-optionX.css (variáveis do layout)
    """
    theme_to_set = f"option{theme_num}"

    # Define o tema no banco de dados para a sessão do teste
    with app.app_context():
        from BelarminoMonteiroAdvogado.models import ThemeSettings, db
        theme = ThemeSettings.query.first()
        theme.theme = theme_to_set
        db.session.commit()

    # Faz a requisição para a homepage
    response = client.get("/")
    assert response.status_code == 200, f"Página inicial falhou ao carregar para o tema {theme_to_set}"
    
    response_data = response.data.decode('utf-8')

    # 1. Verifica se o CSS base está sempre presente
    base_css_url = url_for('static', filename='css/base.css')
    assert base_css_url in response_data, "O arquivo base.css não foi encontrado no HTML."

    # 2. Verifica se os temas globais light e dark estão presentes
    light_theme_url = url_for('static', filename='css/theme-light.css')
    dark_theme_url = url_for('static', filename='css/theme-dark.css')
    assert light_theme_url in response_data, "O arquivo theme-light.css não foi encontrado."
    assert dark_theme_url in response_data, "O arquivo theme-dark.css não foi encontrado."

    # 3. Verifica se o CSS específico do layout (option) está presente
    option_css_url = url_for('static', filename=f'css/theme-{theme_to_set}.css')
    assert option_css_url in response_data, f"O arquivo theme-{theme_to_set}.css não foi encontrado."

