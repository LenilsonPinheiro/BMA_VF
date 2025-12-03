"""
Script para adicionar {% include '_head_meta.html' %} em todos os base_option*.html
Autor: Lenilson Pinheiro
"""

import os
import re

# Diretório dos templates
templates_dir = "BelarminoMonteiroAdvogado/templates"

# Arquivos a serem corrigidos
files_to_fix = [
    "base_option6.html",
    "base_option7.html",
    "base_option8.html"
]

for filename in files_to_fix:
    filepath = os.path.join(templates_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ Arquivo não encontrado: {filepath}")
        continue
    
    # Ler o arquivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já tem o include
    if '{% include \'_head_meta.html\' %}' in content:
        print(f"✓ {filename} já tem o include")
        continue
    
    # Padrão para encontrar o <head> e substituir o conteúdo inicial
    pattern = r'(<head>\s*<meta charset="UTF-8">.*?<meta name="theme-color"[^>]*>)'
    
    replacement = r'<head>\n    {% include \'_head_meta.html\' %}'
    
    # Fazer a substituição
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        # Salvar o arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ {filename} corrigido!")
    else:
        print(f"⚠ {filename} não foi modificado (padrão não encontrado)")

print("\n✅ Correção concluída!")
