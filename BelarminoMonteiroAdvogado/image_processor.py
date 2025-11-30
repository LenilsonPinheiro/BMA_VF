# -*- coding: utf-8 -*-
"""
BelarminoMonteiroAdvogado/image_processor.py

Processador AUTOMÁTICO de imagens com QUALIDADE MÁXIMA.
Otimiza automaticamente todas as imagens enviadas via upload.

Funcionalidades:
1. Otimização automática ao fazer upload
2. Qualidade 95% (imperceptível ao olho humano)
3. Conversão para WebP
4. Redimensionamento inteligente
5. Backup automático
6. Correção de orientação EXIF

Autor: 
Data: Janeiro 2025
"""

from PIL import Image, ImageOps
from pathlib import Path
import os
from datetime import datetime

class ImageProcessor:
    """
    Processador automático de imagens com qualidade máxima.
    """
    
    def __init__(self, quality=95, max_width=2560, create_backup=True):
        """
        Inicializa o processador de imagens.
        
        Args:
            quality (int): Qualidade da compressão WebP (0-100). Padrão: 95 (imperceptível)
            max_width (int): Largura máxima em pixels. Padrão: 2560
            create_backup (bool): Se deve criar backup das originais. Padrão: True
        """
        self.quality = quality
        self.max_width = max_width
        self.create_backup = create_backup
        
    def optimize_image(self, input_path, output_path=None):
        """
        Otimiza uma imagem mantendo qualidade visual máxima.
        
        Args:
            input_path (str|Path): Caminho da imagem original
            output_path (str|Path): Caminho de saída (opcional, usa .webp por padrão)
            
        Returns:
            tuple: (sucesso, tamanho_original, tamanho_otimizado, caminho_saida)
        """
        try:
            input_path = Path(input_path)
            
            # Definir caminho de saída
            if output_path is None:
                output_path = input_path.with_suffix('.webp')
            else:
                output_path = Path(output_path)
            
            # Criar backup se solicitado
            if self.create_backup and input_path.exists():
                backup_dir = input_path.parent / 'originals'
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / input_path.name
                
                # Copiar apenas se backup não existir
                if not backup_path.exists():
                    import shutil
                    shutil.copy2(input_path, backup_path)
            
            # Abrir e processar imagem
            img = Image.open(input_path)
            original_size = input_path.stat().st_size
            
            # Corrigir orientação EXIF automaticamente
            img = ImageOps.exif_transpose(img)
            
            # Converter para RGB mantendo qualidade
            img = self._convert_to_rgb(img)
            
            # Redimensionar apenas se muito grande
            img, resized = self._smart_resize(img)
            
            # Salvar como WebP com qualidade máxima
            img.save(
                output_path,
                'webp',
                quality=self.quality,
                method=6,  # Melhor compressão
                exact=False  # Permite otimizações
            )
            
            new_size = output_path.stat().st_size
            
            return True, original_size, new_size, str(output_path)
            
        except Exception as e:
            print(f"Erro ao otimizar {input_path}: {str(e)}")
            return False, 0, 0, None
    
    def _convert_to_rgb(self, img):
        """Converte imagem para RGB mantendo qualidade."""
        if img.mode in ('RGBA', 'LA'):
            # Criar fundo branco de alta qualidade
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        elif img.mode == 'P':
            return img.convert('RGB')
        elif img.mode not in ('RGB', 'L'):
            return img.convert('RGB')
        return img
    
    def _smart_resize(self, img):
        """
        Redimensiona imagem apenas se muito grande.
        Mantém proporções e usa algoritmo de alta qualidade.
        """
        if img.width <= self.max_width and img.height <= self.max_width:
            return img, False
        
        # Calcular novo tamanho mantendo proporção
        if img.width > img.height:
            new_width = self.max_width
            new_height = int(img.height * (self.max_width / img.width))
        else:
            new_height = self.max_width
            new_width = int(img.width * (self.max_width / img.height))
        
        # Usar LANCZOS (melhor qualidade)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return img, True
    
    def process_upload(self, file, upload_folder):
        """
        Processa automaticamente uma imagem enviada via upload.
        
        Args:
            file: Arquivo enviado (FileStorage do Flask)
            upload_folder (str|Path): Pasta de destino
            
        Returns:
            tuple: (sucesso, caminho_webp, mensagem)
        """
        try:
            upload_folder = Path(upload_folder)
            upload_folder.mkdir(parents=True, exist_ok=True)
            
            # Gerar nome único
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_name = Path(file.filename).stem
            temp_path = upload_folder / f"{original_name}_{timestamp}{Path(file.filename).suffix}"
            
            # Salvar temporariamente
            file.save(str(temp_path))
            
            # Otimizar automaticamente
            success, orig_size, new_size, webp_path = self.optimize_image(temp_path)
            
            if success:
                # Calcular redução
                reduction = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
                
                message = f"Imagem otimizada com sucesso! Redução: {reduction:.1f}%"
                return True, webp_path, message
            else:
                return False, None, "Erro ao otimizar imagem"
                
        except Exception as e:
            return False, None, f"Erro ao processar upload: {str(e)}"
    
    def batch_optimize(self, directory, extensions=None):
        """
        Otimiza todas as imagens em um diretório.
        
        Args:
            directory (str|Path): Diretório com imagens
            extensions (list): Lista de extensões (padrão: ['.jpg', '.jpeg', '.png'])
            
        Returns:
            dict: Estatísticas da otimização
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        
        directory = Path(directory)
        images = []
        
        # Encontrar todas as imagens
        for ext in extensions:
            images.extend(directory.rglob(f'*{ext}'))
            images.extend(directory.rglob(f'*{ext.upper()}'))
        
        # Remover duplicatas
        images = list(set(images))
        
        # Otimizar cada imagem
        stats = {
            'total': len(images),
            'success': 0,
            'failed': 0,
            'original_size': 0,
            'optimized_size': 0,
            'files': []
        }
        
        for img_path in images:
            success, orig_size, new_size, output_path = self.optimize_image(img_path)
            
            if success:
                stats['success'] += 1
                stats['original_size'] += orig_size
                stats['optimized_size'] += new_size
                stats['files'].append({
                    'input': str(img_path),
                    'output': output_path,
                    'original_size': orig_size,
                    'optimized_size': new_size,
                    'reduction': ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
                })
            else:
                stats['failed'] += 1
        
        return stats


# Instância global do processador
image_processor = ImageProcessor(quality=95, max_width=2560, create_backup=True)


def optimize_uploaded_image(file, upload_folder):
    """
    Função helper para otimizar imagem enviada via upload.
    
    Args:
        file: Arquivo enviado (FileStorage do Flask)
        upload_folder (str): Pasta de destino
        
    Returns:
        tuple: (sucesso, caminho_webp, mensagem)
    """
    return image_processor.process_upload(file, upload_folder)


def optimize_image_file(input_path, output_path=None):
    """
    Função helper para otimizar um arquivo de imagem.
    
    Args:
        input_path (str): Caminho da imagem original
        output_path (str): Caminho de saída (opcional)
        
    Returns:
        tuple: (sucesso, tamanho_original, tamanho_otimizado, caminho_saida)
    """
    return image_processor.optimize_image(input_path, output_path)


def process_and_save_image(file, upload_folder):
    """
    Processa e salva uma imagem enviada via upload.
    Alias para optimize_uploaded_image para compatibilidade.
    
    Args:
        file: Arquivo enviado (FileStorage do Flask)
        upload_folder (str): Pasta de destino
        
    Returns:
        tuple: (sucesso, caminho_webp, mensagem)
    """
    return optimize_uploaded_image(file, upload_folder)


def save_logo(file, filename):
    """
    Salva um logo/imagem com otimização automática.
    
    Args:
        file: Arquivo enviado (FileStorage do Flask)
        filename (str): Nome do arquivo (sem extensão)
        
    Returns:
        str: Caminho relativo da imagem salva
    """
    try:
        from flask import current_app
        
        # Diretório de upload
        upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'BelarminoMonteiroAdvogado/static/images/uploads'))
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        # Salvar temporariamente
        ext = Path(file.filename).suffix
        temp_path = upload_folder / f"{filename}{ext}"
        file.save(str(temp_path))
        
        # Otimizar
        success, orig_size, new_size, webp_path = image_processor.optimize_image(temp_path)
        
        if success:
            # Retornar caminho relativo
            webp_path = Path(webp_path)
            relative_path = str(webp_path.relative_to(Path('BelarminoMonteiroAdvogado/static')))
            return relative_path.replace('\\', '/')
        else:
            # Se falhar, retornar caminho do arquivo original
            relative_path = str(temp_path.relative_to(Path('BelarminoMonteiroAdvogado/static')))
            return relative_path.replace('\\', '/')
            
    except Exception as e:
        print(f"Erro ao salvar logo: {e}")
        # Fallback: salvar sem otimização
        try:
            from flask import current_app
            upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'BelarminoMonteiroAdvogado/static/images/uploads'))
            upload_folder.mkdir(parents=True, exist_ok=True)
            
            ext = Path(file.filename).suffix
            save_path = upload_folder / f"{filename}{ext}"
            file.save(str(save_path))
            
            relative_path = str(save_path.relative_to(Path('BelarminoMonteiroAdvogado/static')))
            return relative_path.replace('\\', '/')
        except:
            return None
