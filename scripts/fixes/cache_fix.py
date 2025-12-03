"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script para limpar memoria temporaria do Flask e reiniciar o servidor
"""
import os
import shutil
import sys

print("=" * 80)
print(" LIMPANDO CACHE E REINICIANDO SERVIDOR")
print("=" * 80)

# 1. Limpar memoria temporaria Python
print("\n[1/4] Limpando cache Python (__pycache__)...")
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        cache_path = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(cache_path)
            print(f"    Removido: {cache_path}")
        except Exception as e:
            print(f"     Erro ao remover {cache_path}: {e}")

# 2. Limpar arquivos .pyc
print("\n[2/4] Limpando arquivos .pyc...")
count = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                print(f"     Erro ao remover {file_path}: {e}")
print(f"    {count} arquivos .pyc removidos")

# 3. Verificar tema ativo
print("\n[3/4] Verificando tema ativo no banco de dados...")
try:
    from BelarminoMonteiroAdvogado import create_app
    from BelarminoMonteiroAdvogado.models import ThemeSettings
    
    app = create_app()
    with app.app_context():
        theme_settings = ThemeSettings.query.first()
        if theme_settings:
            print(f"   ️  Tema ativo: {theme_settings.theme}")
        else:
            print("     Nenhuma configuração de tema encontrada!")
except Exception as e:
    print(f"     Erro ao verificar tema: {e}")

# 4. Instruções finais
print("\n[4/4] Próximos passos:")
print("   1. Pressione Ctrl+C no terminal do servidor Flask")
print("   2. Execute: python run.py")
print("   3. Limpe o cache do navegador (Ctrl+Shift+Del)")
print("   4. Acesse http://localhost:5000")

print("\n" + "=" * 80)
print(" LIMPEZA CONCLUÍDA!")
print("=" * 80)
