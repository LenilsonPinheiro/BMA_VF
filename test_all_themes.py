#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script de teste automatizado para todos os 8 temas do site Belarmino Monteiro Advogado.
Testa a homepage com cada tema configurado no banco de dados.
"""

import sys
import os
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurações
BASE_URL = "http://127.0.0.1:5000"
DATABASE_PATH = "instance/site.db"

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN} {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED} {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE} {text}{Colors.END}")

def change_theme(theme_option):
    """Altera o tema no banco de dados"""
    try:
        engine = create_engine(f'sqlite:///{DATABASE_PATH}')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Atualiza o tema
        session.execute(
            text("UPDATE theme_settings SET theme = :theme WHERE id = 1"),
            {"theme": theme_option}
        )
        session.commit()
        session.close()
        return True
    except Exception as e:
        print_error(f"Erro ao alterar tema no banco: {e}")
        return False

def test_homepage(theme_name, theme_option):
    """Testa a homepage com o tema especificado"""
    print(f"\n{Colors.BOLD}Testando: {theme_name} ({theme_option}){Colors.END}")
    print("-" * 70)
    
    # Altera o tema no banco
    if not change_theme(theme_option):
        print_error(f"Falha ao configurar tema {theme_option}")
        return False
    
    # Aguarda um momento para o banco atualizar
    import time
    time.sleep(0.5)
    
    # Testa a homepage
    try:
        response = requests.get(BASE_URL, timeout=10)
        
        if response.status_code == 200:
            # Verifica se há erros no HTML
            html = response.text.lower()
            
            errors = []
            if 'is undefined' in html:
                errors.append("Variável indefinida encontrada")
            if 'error' in html and '500' in html:
                errors.append("Erro 500 detectado")
            if 'traceback' in html:
                errors.append("Traceback Python encontrado")
            
            if errors:
                print_error(f"Status 200 mas com erros:")
                for error in errors:
                    print(f"  - {error}")
                return False
            else:
                print_success(f"Status: {response.status_code} - OK")
                print_info(f"Tamanho da resposta: {len(response.content)} bytes")
                return True
        else:
            print_error(f"Status: {response.status_code} - FALHOU")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erro na requisição: {e}")
        return False

def main():
    print_header("TESTE AUTOMATIZADO DE TODOS OS TEMAS")
    print_info(f"URL Base: {BASE_URL}")
    print_info(f"Banco de Dados: {DATABASE_PATH}")
    
    # Verifica se o servidor está rodando
    try:
        response = requests.get(BASE_URL, timeout=5)
        print_success("Servidor Flask está rodando")
    except:
        print_error("Servidor Flask não está rodando!")
        print_warning("Execute: python -m flask --app BelarminoMonteiroAdvogado run")
        sys.exit(1)
    
    # Verifica se o banco existe
    if not os.path.exists(DATABASE_PATH):
        print_error(f"Banco de dados não encontrado: {DATABASE_PATH}")
        sys.exit(1)
    
    # Define os temas para testar
    themes = [
        ("Invisible Luxury V1", "option1"),
        ("Titan Executive V1", "option2"),
        ("Golden Boutique V1", "option3"),
        ("Future Tech V1", "option4"),
        ("Invisible Luxury V2", "option5"),
        ("Titan Executive V2", "option6"),
        ("Golden Boutique V2", "option7"),
        ("Future Tech V2", "option8"),
    ]
    
    # Testa cada tema
    results = {}
    for theme_name, theme_option in themes:
        results[theme_option] = test_homepage(theme_name, theme_option)
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    print(f"\n{Colors.BOLD}Total de Temas Testados: {len(results)}{Colors.END}")
    print_success(f"Aprovados: {passed}")
    if failed > 0:
        print_error(f"Reprovados: {failed}")
    
    print("\n" + Colors.BOLD + "Detalhes:" + Colors.END)
    for (theme_name, theme_option), passed in zip(themes, results.values()):
        status = " PASSOU" if passed else " FALHOU"
        color = Colors.GREEN if passed else Colors.RED
        print(f"  {color}{status}{Colors.END} - {theme_name} ({theme_option})")
    
    # Restaura tema padrão
    print(f"\n{Colors.BLUE}Restaurando tema padrão (option1)...{Colors.END}")
    change_theme("option1")
    
    print("\n" + "="*70 + "\n")
    
    # Retorna código de saída
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
