# BelarminoMonteiroAdvogado/utils.py
# -*- coding: utf-8 -*-
"""
==============================================================================
Módulo de Utilitários (Parcialmente Obsoleto)
==============================================================================

ATENÇÃO: Este arquivo (`utils.py`) contém uma mistura de funções utilitárias.
A maioria das funções (`from_json_filter`, `get_file_mtime`, `get_nav_pages`,
`get_page_content`, `render_page`) são duplicatas de funções que já existem
e são utilizadas a partir do arquivo principal do projeto
(`BelarminoMonteiroAdvogado/__init__.py`).

Este arquivo parece ser um artefato de um refactoring anterior e não é
importado pela aplicação principal. Portanto, a maior parte do seu conteúdo
está obsoleta.

A única função potencialmente útil e não duplicada aqui é `validate_cpf`.

Recomendação: Mover a função `validate_cpf` para um local apropriado (se
necessário) e remover este arquivo para evitar confusão.
"""
import os
import json
from typing import Dict, Any, List
from flask import current_app, render_template
from sqlalchemy.orm import joinedload
from .models import Pagina, ConteudoGeral

def from_json_filter(value):
    """
    Filtro Jinja para carregar uma string JSON.
    (OBSOLETO: Usar a versão de `BelarminoMonteiroAdvogado/__init__.py`)
    """
    if not value:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

def get_file_mtime(filename):
    """
    Retorna o tempo de modificação do arquivo para cache busting.
    (OBSOLETO: Usar a versão de `BelarminoMonteiroAdvogado/__init__.py`)
    """
    filepath = os.path.join(current_app.static_folder, filename)
    if os.path.exists(filepath):
        return int(os.path.getmtime(filepath))
    return 0

def get_nav_pages() -> Dict[str, List[Pagina]]:
    """
    Busca e organiza todas as páginas ativas para o menu de navegação.
    (OBSOLETO: Usar a versão de `BelarminoMonteiroAdvogado/__init__.py`)
    """
    pages_tree = Pagina.query.options(joinedload(Pagina.children)).filter(
        Pagina.ativo == True,
        Pagina.show_in_menu == True,
        Pagina.parent_id.is_(None)
    ).order_by(Pagina.ordem).all()
    return {'nav_pages': pages_tree}

def get_page_content(page_identifier: str) -> Dict[str, Any]:
    """
    Busca o conteúdo de uma página e as configurações gerais.
    (OBSOLETO: Usar a versão de `BelarminoMonteiroAdvogado/__init__.py`)
    """
    context: Dict[str, Any] = {}
    pages_to_load = ['configuracoes_gerais', 'configuracoes_estilo', 'sobre-nos']
    if page_identifier:
        pages_to_load.append(page_identifier)
        
    all_contents = ConteudoGeral.query.filter(ConteudoGeral.pagina.in_(pages_to_load)).all()
    
    for item in all_contents:
        context[item.secao] = item.conteudo
    return context

def render_page(template_name: str, page_identifier: str, return_context: bool = False, override_content: Dict[str, Any] = None, **extra_context) -> Any:
    """
    Função genérica para renderizar páginas buscando conteúdo no DB.
    (OBSOLETO: Usar a versão de `BelarminoMonteiroAdvogado/__init__.py`)
    """
    context = get_page_content(page_identifier)

    if override_content:
        context.update(override_content)

    context.update(extra_context)

    if return_context:
        return context
    
    return render_template(template_name, **context)

def validate_cpf(value: Any) -> bool:
    """
    Valida um número de CPF (Cadastro de Pessoas Físicas) brasileiro.

    Utiliza o algoritmo padrão de validação dos dígitos verificadores.
    Remove caracteres não numéricos e verifica se todos os dígitos são iguais.

    Args:
        value: O CPF a ser validado. Pode ser uma string, int ou qualquer
               tipo que possa ser convertido para string.
        
    Returns:
        bool: True se o CPF for válido, False caso contrário.
        
    Exemplo:
        >>> validate_cpf("12345678909") # CPF Válido
        True
        >>> validate_cpf("000.000.000-00")
        False
    """
    if not isinstance(value, (str, int)):
        raise TypeError("O CPF deve ser uma string ou um inteiro.")
    
    # Converte para string e remove caracteres não numéricos
    cpf_str = str(value).replace('.', '').replace('-', '').replace('_', '')
    
    # Verifica se o CPF tem 11 dígitos
    if len(cpf_str) != 11 or not cpf_str.isdigit():
        return False
    
    # Verifica se todos os dígitos são iguais (ex: "111.111.111-11"), o que é inválido
    if len(set(cpf_str)) == 1:
        return False
    
    # Calcula o primeiro dígito verificador
    total1 = 0
    for i in range(0, 9):
        total1 += int(cpf_str[i]) * (10 - i)
    dv1 = 11 - (total1 % 11)
    if dv1 >= 10:
        dv1 = 0
    
    # Calcula o segundo dígito verificador
    total2 = 0
    for i in range(0, 10):
        total2 += int(cpf_str[i]) * (11 - i)
    dv2 = 11 - (total2 % 11)
    if dv2 >= 10:
        dv2 = 0
    
    # Verifica se os dígitos verificadores calculados correspondem aos do CPF
    return (cpf_str[9] == str(dv1) and cpf_str[10] == str(dv2))