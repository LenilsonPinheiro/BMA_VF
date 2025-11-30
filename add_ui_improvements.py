"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script para adicionar o link do CSS ui-improvements.css em todos os modelo de paginas base
"""

import os
import re

# Lista de modelo de paginas base para atualizar
templates = [
    'BelarminoMonteiroAdvogado/templates/base_option2.html',
    'BelarminoMonteiroAdvogado/templates/base_option3.html',
    'BelarminoMonteiroAdvogado/templates/base_option4.html',
    'BelarminoMonteiroAdvogado/templates/base_option5.html',
    'BelarminoMonteiroAdvogado/templates/base_option6.html',
    'BelarminoMonteiroAdvogado/templates/base_option7.html',
    'BelarminoMonteiroAdvogado/templates/base_option8.html',
]

# Linha a ser adicionada
ui_improvements_line = '    <!-- UI/UX Improvements -->\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/ui-improvements.css\') }}">\n'

for template_path in templates:
    if not os.path.exists(template_path):
        print(f" Arquivo não encontrado: {template_path}")
        continue
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica se já foi adicionado
    if 'ui-improvements.css' in content:
        print(f" Já existe em: {template_path}")
        continue
    
    # Procura pelo padrão {% block head %}{% endblock %}
    pattern = r'(\s*{% block head %}{% endblock %})'
    
    if re.search(pattern, content):
        # Adiciona antes do {% block head %}
        new_content = re.sub(
            pattern,
            f'\n{ui_improvements_line}\\1',
            content
        )
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f" Adicionado em: {template_path}")
    else:
        print(f"  Padrão não encontrado em: {template_path}")

print("\n Processo concluído!")
