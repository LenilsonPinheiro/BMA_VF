# -*- coding: utf-8 -*-
"""
Script para remover em massa referências ao GitHub de dentro do diretório venv.

AVISO: Este script modifica diretamente os arquivos das bibliotecas instaladas.
Isso é uma operação de risco e pode corromper seu ambiente virtual.
Use por sua conta e risco. Recomenda-se recriar o venv como uma alternativa mais segura.
"""
import os
from pathlib import Path

def replace_in_file(file_path):
    """Substitui URLs do GitHub em um único arquivo."""
    try:
        # Usamos 'latin-1' como fallback, pois alguns arquivos podem não ser utf-8
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERRO] Não foi possível ler {file_path}: {e}")
        return 0

    replacements = [
        ('https://github.com', '[URL-REMOVED]'),
        ('http://github.com', '[URL-REMOVED]'),
    ]

    original_content = content
    count = 0
    for old, new in replacements:
        count += content.count(old)
        content = content.replace(old, new)

    if content != original_content:
        try:
            with open(file_path, 'w', encoding='latin-1') as f:
                f.write(content)
            print(f"  [MODIFICADO] {file_path} ({count} substituições)")
            return count
        except Exception as e:
            print(f"  [ERRO] Não foi possível escrever em {file_path}: {e}")
    
    return 0

def main():
    """Função principal."""
    print("="*80)
    print("INICIANDO LIMPEZA PROFUNDA DO DIRETÓRIO 'venv'")
    print("="*80)
    print("\nAVISO: Esta operação é arriscada e pode corromper seu ambiente virtual.\n")
    
    proceed = input("Você tem certeza que deseja continuar? (s/n): ")
    if proceed.lower() != 's':
        print("Operação cancelada.")
        return

    venv_path = Path(__file__).parent / 'venv'
    if not venv_path.is_dir():
        print(f"ERRO: Diretório 'venv' não encontrado em {venv_path}")
        return

    print(f"\nIniciando varredura em: {venv_path}\n")
    
    total_files_scanned = 0
    total_files_modified = 0
    total_replacements = 0

    for root, _, files in os.walk(venv_path):
        for name in files:
            file_path = Path(root) / name
            total_files_scanned += 1
            replacements_made = replace_in_file(file_path)
            if replacements_made > 0:
                total_files_modified += 1
                total_replacements += replacements_made

    print("\n" + "="*80)
    print("LIMPEZA DO VENV CONCLUÍDA")
    print("="*80)
    print(f"\nResumo:")
    print(f"  - Arquivos totais verificados: {total_files_scanned}")
    print(f"  - Arquivos modificados: {total_files_modified}")
    print(f"  - Total de substituições: {total_replacements}")
    print("\nO processo está finalizado.")

if __name__ == '__main__':
    main()
