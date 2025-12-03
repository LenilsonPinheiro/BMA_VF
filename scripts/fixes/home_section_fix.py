#!/usr/bin/env python3
"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script para corrigir todas as referências a 'home_section' nos modelo de paginas.
Remove as variáveis dinâmicas e usa valores fixos.
"""

import os
import re

# Arquivos a corrigir
files_to_fix = [
    'BelarminoMonteiroAdvogado/modelo de paginas/home/_testimonials_section.html',
    'BelarminoMonteiroAdvogado/modelo de paginas/home/_clients_section.html',
]

def fix_testimonials():
    """Corrige _testimonials_section.html"""
    filepath = 'BelarminoMonteiroAdvogado/modelo de paginas/home/_testimonials_section.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir as referências a home_section
    content = re.sub(
        r'\{\{\s*home_section\.subtitle\s*\|\s*default\([\'"]O que dizem nossos parceiros[\'"]\)\s*\}\}',
        'O que dizem nossos parceiros',
        content
    )
    
    content = re.sub(
        r'\{\{\s*home_section\.title\s*\|\s*default\([\'"]Excelência Reconhecida[\'"]\)\s*\}\}',
        'Excelência Reconhecida',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f" Corrigido: {filepath}")

def fix_clients():
    """Corrige _clients_section.html"""
    filepath = 'BelarminoMonteiroAdvogado/templates/home/_clients_section.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir as referências a home_section
    content = re.sub(
        r'\{\{\s*home_section\.title\s*\|\s*default\([\'"]A confiança de grandes marcas[\'"]\)\s*\}\}',
        'A confiança de grandes marcas',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f" Corrigido: {filepath}")

if __name__ == '__main__':
    print(" Corrigindo referências a 'home_section' nos templates...")
    print()
    
    try:
        fix_testimonials()
        fix_clients()
        print()
        print(" TODOS OS ARQUIVOS CORRIGIDOS COM SUCESSO!")
        print()
        print("Arquivos corrigidos:")
        print("  1. _testimonials_section.html")
        print("  2. _clients_section.html")
        print()
        print(" Agora reinicie o servidor Flask e teste!")
    except Exception as e:
        print(f" ERRO: {e}")
        import traceback
        traceback.print_exc()
