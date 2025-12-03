# -*- coding: utf-8 -*-
"""
Script para DELETAR COMPLETAMENTE o ambiente virtual (venv).

AVISO: Este script modifica diretamente os arquivos das bibliotecas instaladas.
Esta é a solução recomendada para corrigir erros de "Fatal error in launcher"
ou outros problemas de corrupção de ambiente.

Após a execução, você precisará rodar 'run.ps1' para recriar o ambiente e
reinstalar as dependências.
"""
import os
import shutil
from pathlib import Path
import time

def main():
    """Função principal."""
    print("="*80)
    print("INICIANDO REMOÇÃO COMPLETA DO AMBIENTE VIRTUAL 'venv'")
    print("="*80)
    print("\nAVISO: Esta operação irá deletar permanentemente a pasta 'venv' e todas as bibliotecas instaladas nela.")
    print("Esta é a solução correta para erros de 'launcher' ou ambiente corrompido.\n")
    
    proceed = input("Você tem certeza que deseja continuar? (s/n): ")
    if proceed.lower() != 's':
        print("Operação cancelada.")
        return

    venv_path = Path(__file__).parent / "venv"
    if not venv_path.is_dir():
        print(f"ERRO: Diretório 'venv' não encontrado em {venv_path}")
        return

    print(f"\n[INFO] Removendo a pasta '{venv_path}'...")
    try:
        shutil.rmtree(venv_path)
        # Pequena pausa para o sistema de arquivos finalizar
        time.sleep(1)
        print("\n" + "="*80)
        print("✅ SUCESSO: O ambiente virtual 'venv' foi completamente removido.")
        print("="*80)
        print("\nPróximo passo: Execute o script 'run.ps1' para recriar o ambiente e reinstalar tudo do zero.")
    except Exception as e:
        print(f"\n[ERRO] Não foi possível remover a pasta 'venv'.")
        print(f"Detalhes: {e}")
        print("Por favor, feche todos os terminais e editores de código e tente deletar a pasta 'venv' manualmente.")

if __name__ == '__main__':
    main()
