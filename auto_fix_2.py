# -*- coding: utf-8 -*-
"""
==============================================================================
Script de Correção Automática: Remover Variável 'home_section'
==============================================================================

Este script foi criado para uma tarefa de refatoração específica: remover todas
as ocorrências da variável Jinja2 `{{ home_section.* }}` de todos os arquivos
`.html` dentro do diretório de templates.

Funcionalidade:
---------------
1.  **Varredura de Templates:** Percorre recursivamente o diretório
    `BelarminoMonteiroAdvogado/templates` em busca de todos os arquivos HTML.
2.  **Remoção por Expressão Regular:** Para cada arquivo, utiliza uma expressão
    regular para encontrar e substituir qualquer chamada à variável
    `home_section` (e seus atributos) por uma string vazia.
3.  **Log de Ações:** Informa no console quais arquivos foram corrigidos,
    permitindo o acompanhamento da operação.

Este tipo de script é útil para limpar código legado ou variáveis que se
tornaram obsoletas após uma mudança na estrutura de dados da aplicação.

Autor: Lenilson Pinheiro
Data: Janeiro 2025
"""
import os
import re
import logging
import traceback

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fix_templates():
    """
    Percorre os templates e remove as referências a 'home_section'.
    """
    templates_dir = 'BelarminoMonteiroAdvogado/templates'
    logger.info(f"Iniciando varredura no diretório: {templates_dir}")
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Usa uma expressão regular para encontrar e remover {{ home_section.* }}
                    new_content, count = re.subn(r'\{\{\s*home_section\..*?\}\}', '', content)
                    
                    if count > 0:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        logger.info(f"Corrigido: {count} ocorrência(s) em {filepath}")
                except Exception as e:
                    logger.error(f"Falha ao processar o arquivo {filepath}: {e}")

if __name__ == '__main__':
    logger.info("Iniciando script para corrigir referências a 'home_section' nos templates...")
    
    try:
        fix_templates()
        logger.info("=====================================================")
        logger.info("TODOS OS ARQUIVOS FORAM VERIFICADOS COM SUCESSO!")
        logger.info("Reinicie o servidor Flask e teste a aplicação.")
        logger.info("=====================================================")
    except Exception as e:
        logger.exception("Ocorreu um erro inesperado durante a execução do script.")
