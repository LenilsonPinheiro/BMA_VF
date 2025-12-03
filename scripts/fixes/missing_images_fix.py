"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script para corrigir todas as referências de imagens faltando nos modelo de paginas
"""
import os
import re

# Mapeamento de imagens faltando para imagens existentes
IMAGE_REPLACEMENTS = {
    'images/banners/office_meeting.jpg': 'images/Escolhidas Escritorio/3S5A1400.jpg',
    'images/banners/contact_bg.jpg': 'images/banners/inner_bg_default.jpg',
    'images/banners/slide1.jpg': 'images/Escolhidas Escritorio/3S5A1373.jpg',
}

def fix_modelo de pagina(filepath):
    """Corrige as referências de imagens em um modelo de pagina"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Substitui cada imagem faltando
        for old_path, new_path in IMAGE_REPLACEMENTS.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                changes_made.append(f"  - {old_path} → {new_path}")
        
        # Se houve mudanças, salva o arquivo
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f" {filepath}")
            for change in changes_made:
                print(change)
            return True
        return False
    except Exception as e:
        print(f" Erro em {filepath}: {e}")
        return False

def main():
    """Processa todos os modelo de paginas"""
    print(" Corrigindo imagens faltando nos templates...\n")
    
    templates_dir = 'BelarminoMonteiroAdvogado/templates'
    fixed_count = 0
    
    # Processa todos os arquivos .html recursivamente
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if fix_template(filepath):
                    fixed_count += 1
    
    print(f"\n✨ Concluído! {fixed_count} arquivo(s) corrigido(s).")

if __name__ == '__main__':
    main()
