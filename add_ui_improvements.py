# -*- coding: utf-8 -*-
"""
==============================================================================
Script de Manutenção: Adicionar CSS de Melhorias de UI
==============================================================================

Este script foi projetado para uma tarefa de manutenção específica: garantir
que o arquivo de CSS `ui-improvements.css` esteja presente em todos os
templates base (`base_option*.html`) do projeto.

Funcionalidade:
---------------
1.  **Itera sobre Templates:** Percorre uma lista predefinida de arquivos de
    template base.
2.  **Verifica Existência:** Checa se o link para `ui-improvements.css` já
    existe no arquivo para evitar duplicatas.
3.  **Injeta o Link:** Caso o link não exista, ele o injeta no local correto,
    antes do bloco `{% block head %}{% endblock %}`.
4.  **Log de Ações:** Imprime no console o status de cada arquivo (adicionado,
    já existente, não encontrado), permitindo que o desenvolvedor acompanhe
    o que foi feito.

Este tipo de script é útil para aplicar alterações em múltiplos arquivos de
forma rápida e consistente após um refactoring ou adição de um novo recurso
global de estilo.

Autor: Lenilson Pinheiro
Data: Janeiro 2025
"""
import os
import re
import logging

# Configuração básica do logger para imprimir no console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Lista de templates base para atualizar
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

logger.info("Iniciando verificação e adição do 'ui-improvements.css' nos templates.")

for template_path in templates:
    if not os.path.exists(template_path):
        logger.warning(f"Arquivo não encontrado: {template_path}")
        continue
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica se o link já foi adicionado
    if 'ui-improvements.css' in content:
        logger.debug(f"Link já existe em: {template_path}")
        continue
    
    # Procura pelo padrão {% block head %}{% endblock %}
    pattern = r'(\s*{% block head %}{% endblock %})'
    
    if re.search(pattern, content):
        # Adiciona o link antes do bloco {% block head %}
        new_content = re.sub(
            pattern,
            f'\n{ui_improvements_line}\\1',
            content
        )
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Link adicionado com sucesso em: {template_path}")
    else:
        logger.warning(f"Padrão {{% block head %}} não encontrado em: {template_path}")

logger.info("Processo de adição de CSS concluído.")
