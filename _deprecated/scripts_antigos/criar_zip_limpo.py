# -*- coding: utf-8 -*-
"""
==============================================================================
Script de Automação: Criar Pacote de Deploy (.zip)
==============================================================================

Este script cria um arquivo `.zip` "limpo" do diretório da aplicação
(`BelarminoMonteiroAdvogado`), pronto para ser enviado para um ambiente de
produção como o PythonAnywhere.

Funcionalidade:
---------------
1.  **Exclusão Inteligente:** Exclui arquivos e diretórios desnecessários para
    um ambiente de produção, como caches (`__pycache__`), ambientes virtuais
    (`venv`), bancos de dados locais (`.db`), backups e arquivos de mídia
    grandes. A lógica de exclusão está na função `should_exclude`.
2.  **Criação de ZIP:** Compacta todos os arquivos restantes em um arquivo
    `BelarminoMonteiroAdvogado_DEPLOY.zip` na raiz do projeto.
3.  **Relatório e Instruções:** Ao final, exibe um resumo do que foi feito
    (tamanho do arquivo, número de arquivos incluídos/excluídos) e imprime
    instruções detalhadas de como realizar o deploy manual no PythonAnywhere
    usando o arquivo gerado.

Este script é uma ferramenta de automação essencial para garantir que apenas
os arquivos necessários sejam enviados para produção, reduzindo o tamanho do
upload e prevenindo a inclusão de dados sensíveis ou de desenvolvimento.
"""
import os
import zipfile
import shutil
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def should_exclude(path: str) -> bool:
    """
    Verifica se um arquivo ou diretório deve ser excluído do pacote de deploy.

    A verificação é baseada em uma lista de padrões de exclusão (`exclude_patterns`)
    que inclui diretórios de cache, ambientes virtuais, bancos de dados, etc.

    Args:
        path (str): O caminho do arquivo ou diretório a ser verificado.

    Returns:
        bool: True se o caminho contiver algum dos padrões de exclusão.
    """
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.pyo',
        'venv',
        'env',
        'instance',
        '.db',
        '.sqlite',
        'images_backup',
        'OLD',
        'vold',
        '.zip',
        'maior-1.mp4',  # Vídeo muito grande
        'maior-1.webm',
        '.log',
        'temp',
        'tmp',
    ]
    
    for pattern in exclude_patterns:
        if pattern in path:
            return True
    return False

def create_clean_zip() -> int:
    """
    Orquestra a criação do arquivo .zip limpo para deploy.

    Returns:
        int: 0 para sucesso, 1 para erro.
    """
    source_dir = 'BelarminoMonteiroAdvogado'
    output_zip = 'BelarminoMonteiroAdvogado_DEPLOY.zip'
    
    logger.info("=" * 70)
    logger.info("CRIANDO ZIP LIMPO PARA DEPLOY")
    logger.info("=" * 70)
    
    if not os.path.exists(source_dir):
        logger.error(f"Pasta de origem não encontrada: {source_dir}")
        return 1
    
    # Remover ZIP antigo se existir
    if os.path.exists(output_zip):
        os.remove(output_zip)
        logger.info(f"Arquivo ZIP antigo removido: {output_zip}")
    
    logger.info(f"Criando {output_zip}...")
    
    file_count = 0
    excluded_count = 0
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Filtra diretórios que devem ser excluídos
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if should_exclude(file_path):
                    excluded_count += 1
                    logger.debug(f"  [SKIP] {file_path}")
                    continue
                
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
                file_count += 1
                logger.debug(f"  [ADD] {arcname}")
    
    zip_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    
    logger.info("=" * 70)
    logger.info("✅ ZIP CRIADO COM SUCESSO!")
    logger.info("=" * 70)
    logger.info(f"Arquivo: {output_zip}")
    logger.info(f"Tamanho: {zip_size_mb:.2f} MB")
    logger.info(f"Arquivos incluídos: {file_count}")
    logger.info(f"Arquivos excluídos: {excluded_count}")
    logger.info("-" * 70)
    logger.info("PRÓXIMOS PASSOS (Deploy em PythonAnywhere):")
    logger.info("1. Acesse: https://www.pythonanywhere.com/user/bmadv/files/home/bmadv/")
    logger.info("2. Delete a pasta 'BelarminoMonteiroAdvogado' antiga, se existir.")
    logger.info(f"3. Faça upload do arquivo: {output_zip}")
    logger.info("4. Em um console Bash no PythonAnywhere, execute:")
    logger.info(f"   unzip {output_zip} && rm {output_zip}")
    logger.info("   cd BelarminoMonteiroAdvogado")
    logger.info("   # Crie e ative um novo ambiente virtual")
    logger.info("   python3.11 -m venv venv")
    logger.info("   source venv/bin/activate")
    logger.info("   # Instale as dependências e configure o banco de dados")
    logger.info("   pip install -r requirements.txt")
    logger.info("   flask db upgrade")
    logger.info("   flask init-db")
    logger.info("5. Recarregue a aplicação na aba 'Web' do PythonAnywhere.")
    logger.info("=" * 70)
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = create_clean_zip()
        exit(exit_code)
    except Exception as e:
        logger.exception("Ocorreu um erro inesperado ao criar o arquivo ZIP.")
        exit(1)
