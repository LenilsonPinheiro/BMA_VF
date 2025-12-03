#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fix_banner_images.py

Corrige os arquivos de banner corrompidos criando imagens de placeholder
de alta qualidade até que imagens reais sejam fornecidas.

Autor: 
Data: Janeiro 2025
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_banner_placeholder(output_path, width=1920, height=600, text="Banner"):
    """Cria um banner placeholder de alta qualidade"""
    
    # Criar imagem com gradiente
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Adicionar gradiente
    for y in range(height):
        r = int(26 + (52 - 26) * (y / height))
        g = int(26 + (73 - 26) * (y / height))
        b = int(46 + (118 - 46) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Adicionar texto centralizado
    try:
        # Tentar usar fonte do sistema
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
    
    # Calcular posição do texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Desenhar texto com sombra
    draw.text((x+2, y+2), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Salvar
    img.save(output_path, 'JPEG', quality=95)
    print(f" Criado: {output_path}")

def main():
    """Cria banners placeholder"""
    print("Criando banners placeholder de alta qualidade...\n")
    
    banner_dir = Path('BelarminoMonteiroAdvogado/static/images/banners')
    banner_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar banners
    create_banner_placeholder(
        banner_dir / 'inner_bg_default.jpg',
        width=1920,
        height=600,
        text="Belarmino Monteiro Advogado"
    )
    
    create_banner_placeholder(
        banner_dir / 'areas_bg.jpg',
        width=1920,
        height=600,
        text="Áreas de Atuação"
    )
    
    print("\n Banners criados com sucesso!")
    print("Substitua por imagens reais quando disponível.")

if __name__ == '__main__':
    main()
