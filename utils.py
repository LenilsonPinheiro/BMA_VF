# BelarminoMonteiroAdvogado/utils.py
# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Any, List
from flask import current_app, render_template
from sqlalchemy.orm import joinedload
from .models import Pagina, ConteudoGeral

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