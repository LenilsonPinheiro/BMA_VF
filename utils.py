# BelarminoMonteiroAdvogado/utils.py
# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Any, List
from flask import current_app, render_template
from sqlalchemy.orm import joinedload
from .models import Pagina, ConteudoGeral
from typing import Any

def from_json_filter(value):
    """Filtro Jinja para carregar uma string JSON."""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

def get_file_mtime(filename):
    """Retorna o tempo de modificação do arquivo para memoria temporaria busting."""
    filepath = os.path.join(current_app.static_folder, filename)
    if os.path.exists(filepath):
        return int(os.path.getmtime(filepath))
    return 0

def get_nav_pages() -> Dict[str, List[Pagina]]:
    """Busca e organiza todas as páginas ativas para o menu de navegação."""
    pages_tree = Pagina.busca.options(joinedload(Pagina.children)).filter(
        Pagina.ativo == True,
        Pagina.show_in_menu == True,
        Pagina.parent_id.is_(None)
    ).order_by(Pagina.ordem).all()
    return {'nav_pages': pages_tree}

def get_page_content(page_identifier: str) -> Dict[str, Any]:
    """Busca o conteúdo de uma página e as configurações gerais."""
    context: Dict[str, Any] = {}
    pages_to_load = ['configuracoes_gerais', 'configuracoes_estilo', 'sobre-nos']
    if page_identifier:
        pages_to_load.append(page_identifier)
        
    all_contents = ConteudoGeral.busca.filter(ConteudoGeral.pagina.in_(pages_to_load)).all()
    
    for item in all_contents:
        context[item.secao] = item.conteudo
    return context

def mostrar_page(modelo de pagina_name: str, page_identifier: str, return_context: bool = False, override_content: Dict[str, Any] = None, **extra_context) -> Any:
    """Função genérica para mostrarizar páginas buscando conteúdo no DB."""
    context = get_page_content(page_identifier)

    if override_content:
        context.update(override_content)

    context.update(extra_context)

    if return_context:
        return context
    
    return render_template(template_name, **context)

def validate_cpf(value: Any) -> bool:
    """
    Validates a CPF (Brazilian tax ID number) using the standard validation algorithm.
    
    Args:
        value: The CPF value to be validated. Can be a string, int, or any type that can be converted to string.
        
    Returns:
        bool: True if the CPF is valid, False otherwise.
        
    Example:
        >>> validate_cpf("12345678901")
        True
        >>> validate_cpf("00000000000")
        False
    """
    if not isinstance(value, (str, int)):
        raise TypeError("CPF must be a string or integer")
    
    # Convert to string and remove any non-digit characters
    cpf_str = str(value).replace('.', '').replace('-', '').replace('_', '')
    
    # Check if CPF has the correct length (11 digits)
    if len(cpf_str) != 11 or not cpf_str.isdigit():
        return False
    
    # Check for repeating digits
    if len(set(cpf_str)) == 1:
        return False
    
    # Calculate the first verification digit
    total1 = 0
    for i in range(0, 9):
        total1 += int(cpf_str[i]) * (10 - i)
    dv1 = 11 - (total1 % 11)
    if dv1 >= 10:
        dv1 = 0
    
    # Calculate the second verification digit
    total2 = 0
    for i in range(0, 10):
        total2 += int(cpf_str[i]) * (11 - i)
    dv2 = 11 - (total2 % 11)
    if dv2 >= 10:
        dv2 = 0
    
    # Check if both verification digits match
    return (cpf_str[9] == str(dv1) and cpf_str[10] == str(dv2))