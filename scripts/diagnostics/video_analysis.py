# -*- coding: utf-8 -*-
"""
Diagnóstico Completo do Problema do Vídeo
"""

import os
from pathlib import Path

print("=" * 80)
print("DIAGNÓSTICO COMPLETO DO VÍDEO")
print("=" * 80)

# 1. Verificar arquivos de vídeo
print("\n1. VERIFICANDO ARQUIVOS DE VÍDEO:")
print("-" * 80)

videos_dir = Path("BelarminoMonteiroAdvogado/static/videos")

if videos_dir.exists():
    print(f"✓ Diretório existe: {videos_dir}")
    
    for video_file in videos_dir.glob("*"):
        if video_file.is_file():
            size_mb = video_file.stat().st_size / (1024 * 1024)
            print(f"  - {video_file.name}: {size_mb:.2f} MB")
else:
    print(f"✗ Diretório NÃO existe: {videos_dir}")

# 2. Verificar template
print("\n2. VERIFICANDO TEMPLATE home_option1.html:")
print("-" * 80)

template_path = Path("BelarminoMonteiroAdvogado/templates/home/home_option1.html")

if template_path.exists():
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Procurar tag video
    if '<video' in content:
        print("✓ Tag <video> encontrada")
        
        # Extrair seção do vídeo
        start = content.find('<video')
        end = content.find('</video>', start) + len('</video>')
        video_section = content[start:end]
        
        print("\nCódigo do vídeo:")
        print("-" * 40)
        print(video_section[:500])  # Primeiros 500 caracteres
        print("-" * 40)
        
        # Verificar sources
        if 'maior-1.mp4' in content:
            print("✓ Source MP4 encontrado")
        else:
            print("✗ Source MP4 NÃO encontrado")
            
        if 'maior-1.webm' in content:
            print("✓ Source WebM encontrado")
        else:
            print("✗ Source WebM NÃO encontrado")
    else:
        print("✗ Tag <video> NÃO encontrada")
else:
    print(f"✗ Template NÃO existe: {template_path}")

# 3. Verificar se Flask está servindo corretamente
print("\n3. TESTE DE ROTA:")
print("-" * 80)
print("Execute no navegador:")
print("  http://127.0.0.1:5000/static/videos/maior-1.mp4")
print("\nSe o vídeo baixar/reproduzir, o arquivo está OK.")
print("Se der erro 404, o arquivo não está sendo servido.")

# 4. Verificar CSS que pode estar escondendo o vídeo
print("\n4. POSSÍVEIS PROBLEMAS CSS:")
print("-" * 80)
print("Abra o console do navegador (F12) e digite:")
print("  document.querySelector('.hero-video-bg')")
print("\nSe retornar 'null', o vídeo não está no DOM.")
print("Se retornar um elemento, o vídeo está lá mas pode estar escondido.")

# 5. Instruções finais
print("\n5. PRÓXIMOS PASSOS:")
print("-" * 80)
print("1. Pressione Ctrl + Shift + R no navegador (hard reload)")
print("2. Abra o console (F12)")
print("3. Vá na aba 'Network'")
print("4. Filtre por 'media'")
print("5. Recarregue a página")
print("6. Veja se 'maior-1.mp4' aparece na lista")
print("7. Se aparecer, clique nele e veja o status (200 = OK, 404 = não encontrado)")

print("\n" + "=" * 80)
print("DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)
