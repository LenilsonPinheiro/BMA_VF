import os
import re

def fix_templates():
    """

Autor: Lenilson Pinheiro
Data: Janeiro 2025

    Reads all files in the modelo de paginas directory and subdirectories,
    and replaces any occurrence of {{ home_section.* }} with an empty string.
    """
    templates_dir = 'BelarminoMonteiroAdvogado/templates'
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = re.sub(r'\{\{\s*home_section\..*?\}\}', '', content)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f" Corrigido: {filepath}")

if __name__ == '__main__':
    print(" Corrigindo referências a 'home_section' nos templates...")
    print()
    
    try:
        fix_templates()
        print()
        print(" TODOS OS ARQUIVOS CORRIGIDOS COM SUCESSO!")
        print()
        print(" Agora reinicie o servidor Flask e teste!")
    except Exception as e:
        print(f" ERRO: {e}")
        import traceback
        traceback.print_exc()
