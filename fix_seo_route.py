"""
Script para corrigir main.index para main.home no _seo_meta.html
Autor: Lenilson Pinheiro
"""

import os

filepath = "BelarminoMonteiroAdvogado/templates/_seo_meta.html"

print(f"Corrigindo {filepath}...")

# Ler o arquivo
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir todas as ocorrências
content = content.replace("main.index", "main.home")

# Salvar o arquivo
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Arquivo corrigido! Todas as ocorrências de 'main.index' foram substituídas por 'main.home'")
