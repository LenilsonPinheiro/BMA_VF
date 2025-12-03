#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes Unitários da Aplicação.
"""
import pytest
from BelarminoMonteiroAdvogado import create_app

@pytest.fixture
def client():
    """Fixture do cliente."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_page_loads(client):
    """Testa login."""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_create_service(client):
    """Testa serviço."""
    assert True