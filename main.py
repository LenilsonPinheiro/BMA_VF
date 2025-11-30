# -*- coding: utf-8 -*-
"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

main.py: Ponto de entrada para o Google App Engine

Este arquivo é necessário para o Google App Engine identificar
e iniciar a aplicação Flask corretamente.
"""
from BelarminoMonteiroAdvogado import create_app

# Cria a instância da aplicação Flask
app = create_app()

if __name__ == '__main__':
    # Executa o servidor de desenvolvimento
    # Em produção, o Gunicorn será usado (configurado no app.yaml)
    app.run(host='0.0.0.0', port=8080, debug=False)
