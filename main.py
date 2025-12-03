# -*- coding: utf-8 -*-
"""
==============================================================================
Ponto de Entrada da Aplicação (Entry Point)
==============================================================================

Este arquivo serve como o ponto de entrada principal para a aplicação Flask,
sendo essencial para ambientes de produção e para o servidor de desenvolvimento.

Funcionalidade:
---------------
1.  **Criação da Aplicação:** Importa a função `create_app` (Application Factory)
    do pacote `BelarminoMonteiroAdvogado` e a utiliza para criar uma instância
    da aplicação Flask.
2.  **Servidor de Desenvolvimento:** Quando executado diretamente
    (`python main.py`), inicia o servidor de desenvolvimento embutido do Flask.
    Isso é útil para testes e desenvolvimento local.
3.  **Produção (Gunicorn/App Engine):** Em um ambiente de produção como o Google
    App Engine, um servidor WSGI (como Gunicorn) importará a variável `app`
    deste módulo para servir a aplicação. A configuração para isso
    geralmente está em um arquivo como `app.yaml`.

Autor: Lenilson Pinheiro
Data: Janeiro 2025
"""
from BelarminoMonteiroAdvogado import create_app

# Cria a instância da aplicação Flask
app = create_app()

if __name__ == '__main__':
    # Executa o servidor de desenvolvimento
    # Em produção, o Gunicorn será usado (configurado no app.yaml)
    app.run(host='0.0.0.0', port=8080, debug=False)
