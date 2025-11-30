#!/usr/bin/env python3
"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Teste completo de TODAS as rotas e links da aplicação.
Verifica se há erros 500, 404 ou problemas de modelo de pagina.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath('.'))

from BelarminoMonteiroAdvogado import create_app
from BelarminoMonteiroAdvogado.models import db, AreaAtuacao, Pagina

def test_all_routes():
    """Testa todas as rotas da aplicação"""
    app = create_app()
    
    with app.app_context():
        # Cria tabelas se não existirem
        db.create_all()
        
        client = app.test_client()
        
        print("=" * 80)
        print(" TESTE COMPLETO DE TODAS AS ROTAS E LINKS")
        print("=" * 80)
        print()
        
        # Lista de rotas para testar
        routes_to_test = [
            # Rotas principais
            ('/', 'Homepage'),
            ('/sobre-nos', 'Sobre Nós'),
            ('/contato', 'Contato'),
            ('/areas-de-atuacao', 'Todas as Áreas'),
            ('/politica-de-privacidade', 'Política de Privacidade'),
            
            # Rotas de autenticação
            ('/auth/login', 'Login'),
            
            # Rotas de serviços (dinâmicas)
            ('/direito-civil', 'Direito Civil'),
            ('/direito-do-consumidor', 'Direito do Consumidor'),
            ('/direito-previdenciario', 'Direito Previdenciário'),
            ('/direito-de-familia', 'Direito de Família'),
            
            # Rotas de sistema
            ('/robots.txt', 'Robots.txt'),
            ('/sitemap.xml', 'Sitemap'),
        ]
        
        total_tests = len(routes_to_test)
        passed = 0
        failed = 0
        errors = []
        
        print(" TESTANDO ROTAS PÚBLICAS:")
        print("-" * 80)
        
        for route, name in routes_to_test:
            try:
                response = client.get(route, follow_redirects=True)
                
                if response.status_code == 200:
                    print(f" {name:30} | {route:40} | Status: 200 OK")
                    passed += 1
                elif response.status_code == 404:
                    print(f"  {name:30} | {route:40} | Status: 404 NOT FOUND")
                    errors.append(f"{name} ({route}): 404 Not Found")
                    failed += 1
                elif response.status_code == 500:
                    print(f" {name:30} | {route:40} | Status: 500 ERROR")
                    # Tenta pegar o erro
                    error_text = response.data.decode('utf-8')
                    if 'home_section' in error_text:
                        errors.append(f"{name} ({route}): ERRO 'home_section' undefined")
                    else:
                        errors.append(f"{name} ({route}): 500 Internal Server Error")
                    failed += 1
                else:
                    print(f"  {name:30} | {route:40} | Status: {response.status_code}")
                    errors.append(f"{name} ({route}): Status {response.status_code}")
                    failed += 1
                    
            except Exception as e:
                print(f" {name:30} | {route:40} | EXCEPTION: {str(e)[:50]}")
                errors.append(f"{name} ({route}): Exception - {str(e)}")
                failed += 1
        
        print()
        print("=" * 80)
        print(" RESULTADOS DO TESTE")
        print("=" * 80)
        print(f"Total de rotas testadas: {total_tests}")
        print(f" Passou: {passed} ({passed/total_tests*100:.1f}%)")
        print(f" Falhou: {failed} ({failed/total_tests*100:.1f}%)")
        print()
        
        if errors:
            print(" ERROS ENCONTRADOS:")
            print("-" * 80)
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
            print()
        
        # Teste de áreas dinâmicas do banco
        print("=" * 80)
        print(" TESTANDO ÁREAS DE ATUAÇÃO DINÂMICAS DO BANCO")
        print("=" * 80)
        
        areas = AreaAtuacao.query.all()
        if areas:
            print(f"Encontradas {len(areas)} áreas no banco de dados:")
            print()
            for area in areas:
                route = f"/{area.slug}"
                try:
                    response = client.get(route)
                    if response.status_code == 200:
                        print(f" {area.titulo:30} | {route:40} | Status: 200 OK")
                    else:
                        print(f" {area.titulo:30} | {route:40} | Status: {response.status_code}")
                except Exception as e:
                    print(f" {area.titulo:30} | {route:40} | EXCEPTION: {str(e)[:50]}")
        else:
            print("  Nenhuma área de atuação encontrada no banco de dados")
        
        print()
        print("=" * 80)
        print(" CONCLUSÃO")
        print("=" * 80)
        
        if failed == 0:
            print(" TODOS OS TESTES PASSARAM!")
            print(" O sistema está 100% funcional!")
            return True
        else:
            print(f" {failed} TESTE(S) FALHARAM")
            print(" Verifique os erros acima e corrija antes de prosseguir")
            return False

if __name__ == '__main__':
    success = test_all_routes()
    sys.exit(0 if success else 1)
