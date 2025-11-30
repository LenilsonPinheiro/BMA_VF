"""
Cria ZIP limpo da pasta BelarminoMonteiroAdvogado
Exclui arquivos desnecessários e vídeos grandes
"""

import os
import zipfile
import shutil

def should_exclude(path):
    """Verifica se o arquivo/pasta deve ser excluído"""
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

def create_clean_zip():
    """Cria ZIP limpo"""
    source_dir = 'BelarminoMonteiroAdvogado'
    output_zip = 'BelarminoMonteiroAdvogado_DEPLOY.zip'
    
    print("=" * 70)
    print("CRIANDO ZIP LIMPO PARA DEPLOY")
    print("=" * 70)
    print()
    
    if not os.path.exists(source_dir):
        print(f"[ERRO] Pasta {source_dir} não encontrada!")
        return 1
    
    # Remover ZIP antigo se existir
    if os.path.exists(output_zip):
        os.remove(output_zip)
        print(f"[INFO] ZIP antigo removido")
    
    print(f"[INFO] Criando {output_zip}...")
    print()
    
    file_count = 0
    excluded_count = 0
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Filtrar diretórios
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if should_exclude(file_path):
                    excluded_count += 1
                    print(f"  [SKIP] {file_path}")
                    continue
                
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
                file_count += 1
                print(f"  [ADD] {arcname}")
    
    zip_size = os.path.getsize(output_zip) / (1024 * 1024)  # MB
    
    print()
    print("=" * 70)
    print("✅ ZIP CRIADO COM SUCESSO!")
    print("=" * 70)
    print()
    print(f"Arquivo: {output_zip}")
    print(f"Tamanho: {zip_size:.2f} MB")
    print(f"Arquivos incluídos: {file_count}")
    print(f"Arquivos excluídos: {excluded_count}")
    print()
    print("PRÓXIMOS PASSOS:")
    print()
    print("1. Acesse: https://www.pythonanywhere.com/user/bmadv/files/home/bmadv/")
    print("2. Delete a pasta 'BelarminoMonteiroAdvogado' antiga")
    print("3. Faça upload do arquivo:", output_zip)
    print("4. No console, execute:")
    print()
    print("   cd /home/bmadv")
    print(f"   unzip {output_zip}")
    print(f"   rm {output_zip}")
    print("   cd BelarminoMonteiroAdvogado")
    print("   python3.11 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
    print("   python -c \"from BelarminoMonteiroAdvogado import create_app, db; app = create_app(); app.app_context().push(); db.create_all()\"")
    print()
    print("5. Reload: https://www.pythonanywhere.com/user/bmadv/webapps/")
    print()
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    try:
        exit(create_clean_zip())
    except Exception as e:
        print(f"[ERRO] {e}")
        exit(1)
