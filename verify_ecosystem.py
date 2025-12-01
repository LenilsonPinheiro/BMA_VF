# -*- coding: utf-8 -*-
"""
==============================================================================
AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.)
==============================================================================

QUALQUER ALTERAÇÃO NESTE ARQUIVO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA
INTEIRO DO PROJETO FOR ATUALIZADO.

Isto significa:
1.  **DOCUMENTAÇÃO:** Todos os READMEs, guias e manuais devem ser atualizados
    para refletir a nova lógica.
2.  **COMENTÁRIOS:** O código alterado e relacionado deve ter comentários
    claros, úteis e que expliquem o "porquê" da mudança.
3.  **SCRIPTS DE DIAGNÓSTICO:** Scripts como `diagnostico.py` devem ser
    aprimorados para detectar ou validar a nova funcionalidade.

Esta é a regra mais importante deste projeto. A manutenção a longo prazo
depende da aderência estrita a este princípio. NÃO FAÇA MUDANÇAS ISOLADAS.

==============================================================================
verify_ecosystem.py: Script de verificação de consistência do ecossistema.

Este script garante que a regra mais importante do projeto seja seguida:
a documentação deve ser atualizada junto com o código.

Ele funciona da seguinte maneira:
1. Encontra o arquivo de código Python (.py) modificado mais recentemente.
2. Encontra o arquivo de documentação Markdown (.md) modificado mais recentemente.
3. Compara as datas de modificação.
4. Se o código for mais novo que a documentação, emite um AVISO, pois isso
   sugere que uma mudança foi feita sem a devida atualização dos documentos.

Este script deve ser executado antes de fazer um commit ou como parte do
checklist de um Pull Request.
"""

import os
import datetime

def find_latest_modification_time(root_dir, extensions, exclude_dirs):
    """
    Encontra o tempo de modificação mais recente entre arquivos com as extensões dadas.

    Args:
        root_dir (str): O diretório raiz para iniciar a busca.
        extensions (tuple): Uma tupla de extensões de arquivo a serem consideradas (ex: ('.py',)).
        exclude_dirs (set): Um conjunto de nomes de diretórios a serem ignorados.

    Returns:
        tuple: Uma tupla contendo (timestamp, filepath) do arquivo mais recente, ou (0, None).
    """
    latest_time = 0
    latest_file = None

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove diretórios excluídos da busca para otimização
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename.endswith(extensions):
                filepath = os.path.join(dirpath, filename)
                mod_time = os.path.getmtime(filepath)
                if mod_time > latest_time:
                    latest_time = mod_time
                    latest_file = filepath
    
    return latest_time, latest_file

def main():
    """Função principal que executa a verificação do ecossistema."""
    print("="*60)
    print("VERIFICANDO CONSISTÊNCIA DO ECOSSISTEMA (CÓDIGO vs. DOCUMENTAÇÃO)")
    print("="*60)

    root_directory = os.path.dirname(os.path.abspath(__file__))
    excluded_directories = {'venv', '.git', '__pycache__', 'instance'}

    # Encontra o arquivo de código mais recente
    latest_code_time, latest_code_file = find_latest_modification_time(
        root_directory, ('.py',), excluded_directories
    )

    # Encontra o arquivo de documentação mais recente
    latest_doc_time, latest_doc_file = find_latest_modification_time(
        root_directory, ('.md',), excluded_directories
    )

    if not latest_code_file or not latest_doc_file:
        print("\n[ERRO] Não foi possível encontrar arquivos de código (.py) ou documentação (.md) para comparar.")
        return 1

    print(f"\nÚltimo código modificado: {os.path.basename(latest_code_file)} em {datetime.datetime.fromtimestamp(latest_code_time)}")
    print(f"Última documentação modificada: {os.path.basename(latest_doc_file)} em {datetime.datetime.fromtimestamp(latest_doc_time)}")

    # Compara os tempos, com uma tolerância de 60 segundos para evitar falsos positivos
    if latest_code_time > latest_doc_time + 60:
        print("\n> [!WARNING]")
        print("> AVISO: O código foi modificado mais recentemente que a documentação.")
        print("> Isso pode indicar que a documentação está desatualizada.")
        print("> Por favor, revise e atualize os arquivos .md para refletir as últimas mudanças no código.")
    else:
        print("\n✅ [SUCESSO] A documentação parece estar em dia com as últimas alterações de código.")

    print("\n" + "="*60)
    return 0

if __name__ == "__main__":
    main()