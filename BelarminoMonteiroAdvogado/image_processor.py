# -*- coding: utf-8 -*-
"""
==============================================================================
Módulo de Processamento e Otimização de Imagens
==============================================================================

Este módulo fornece uma classe `ImageProcessor` e funções auxiliares para
lidar com o upload, otimização e gerenciamento de imagens na aplicação.
O objetivo é garantir a máxima qualidade visual com o menor tamanho de
arquivo possível, melhorando a performance do site.

Funcionalidades Principais:
---------------------------
1.  **Otimização Automática:** Comprime imagens (JPG, PNG, etc.) de forma
    inteligente, convertendo-as para o formato WebP, que é altamente
    eficiente para a web.
2.  **Controle de Qualidade:** Permite definir um nível de qualidade (padrão 95),
    encontrando um equilíbrio entre tamanho do arquivo e fidelidade visual.
3.  **Redimensionamento Inteligente:** Redimensiona imagens que excedem uma
    largura máxima definida (padrão 2560px), mantendo a proporção original
    para evitar distorções.
4.  **Correção de Orientação EXIF:** Lê os metadados EXIF de fotos (comuns
    em celulares) e rotaciona a imagem automaticamente para a orientação
    correta.
5.  **Backup Automático:** Cria uma cópia da imagem original em um
    subdiretório 'originals' antes de qualquer modificação, garantindo que
    nenhum dado seja perdido.
6.  **Processamento em Lote:** Oferece um método para otimizar todas as
    imagens de um diretório de uma só vez.

Uso:
----
A instância global `image_processor` pode ser importada e utilizada
diretamente para processar uploads de formulários ou arquivos existentes.

Autor: Lenilson Pinheiro
Data: Janeiro 2025
"""

from PIL import Image, ImageOps
from pathlib import Path
import os
from datetime import datetime
from typing import List, Tuple, Optional, Union # Importações adicionadas para corrigir o erro
from flask import current_app # Importar current_app para logging no contexto da aplicação

class ImageProcessor:
    """
    Encapsula a lógica de otimização de imagens com foco em performance para web.

    Esta classe oferece métodos para otimizar imagens individuais, processar
    uploads de formulários e otimizar diretórios inteiros (em lote).
    As configurações como qualidade, dimensões máximas e backups são
    configuráveis na instanciação.
    """
    
    def __init__(self, quality: int = 95, max_width: int = 2560, create_backup: bool = True):
        """
        Inicializa o processador de imagens com as configurações desejadas.
        
        Args:
            quality (int): A qualidade de compressão para o formato WebP (0-100).
                           Valores próximos a 95 são geralmente imperceptíveis em perdas.
                           Padrão: 95.
            max_width (int): A largura máxima em pixels para a imagem otimizada.
                             Imagens maiores serão redimensionadas para esta largura,
                             mantendo a proporção. Padrão: 2560.
            create_backup (bool): Se `True`, um backup da imagem original será criado
                                  em um subdiretório 'originals' antes da otimização.
                                  Padrão: True.
        """
        self.quality = quality
        self.max_width = max_width
        self.create_backup = create_backup
        
    def optimize_image(self, input_path: Union[Path, str], output_path: Union[Path, str] = None) -> Tuple[bool, int, int, Optional[str]]:
        """
        Otimiza uma imagem convertendo-a para WebP, redimensionando-a e corrigindo a orientação EXIF.
        
        Args:
            input_path (str | Path): Caminho completo para a imagem original.
            output_path (str | Path, optional): Caminho de destino para a imagem otimizada.
                                              Se omitido, a imagem original será substituída
                                              por sua versão .webp no mesmo diretório.
                                              Padrão: None.
            
        Returns:
            tuple: Uma tupla contendo:
                - bool: `True` se a otimização foi bem-sucedida, `False` caso contrário.
                - int: Tamanho do arquivo original em bytes.
                - int: Tamanho do arquivo otimizado em bytes.
                - str | None: Caminho completo para a imagem otimizada (WebP) ou None em caso de falha.
        """
        try:
            input_path = Path(input_path)
            
            # Define o caminho de saída para a imagem otimizada.
            if output_path is None:
                output_path = input_path.with_suffix('.webp')
            else:
                output_path = Path(output_path)
            
            # Cria um backup da imagem original, se a opção estiver ativada e o arquivo existir.
            if self.create_backup and input_path.exists():
                backup_dir = input_path.parent / 'originals'
                backup_dir.mkdir(exist_ok=True) # Garante que o diretório de backup exista
                backup_path = backup_dir / input_path.name
                
                # Copia o arquivo original para o backup apenas se ele ainda não existir lá.
                if not backup_path.exists():
                    import shutil
                    shutil.copy2(input_path, backup_path)
                    current_app.logger.debug(f"Backup de '{input_path.name}' criado em '{backup_path}'.")
            
            # Abre a imagem usando Pillow
            img = Image.open(input_path)
            original_size = input_path.stat().st_size
            
            # Corrige a orientação da imagem usando dados EXIF (se presentes).
            img = ImageOps.exif_transpose(img)
            
            # Converte a imagem para o modo RGB para garantir compatibilidade com WebP e evitar problemas de transparência.
            img = self._convert_to_rgb(img)
            
            # Redimensiona a imagem de forma inteligente se ela exceder a largura máxima configurada.
            img, resized = self._smart_resize(img)
            if resized:
                current_app.logger.debug(f"Imagem '{input_path.name}' redimensionada para largura máxima de {self.max_width}px.")
            
            # Salva a imagem como WebP com a qualidade especificada.
            img.save(
                output_path,
                'webp',
                quality=self.quality,
                method=6,  # 'method=6' otimiza o tempo de compressão versus tamanho do arquivo para WebP.
                exact=False  # Permite que a Pillow faça otimizações adicionais.
            )
            
            new_size = output_path.stat().st_size
            
            current_app.logger.info(f"Imagem '{input_path.name}' otimizada para '{output_path.name}'. Original: {original_size} bytes, Otimizado: {new_size} bytes.")
            return True, original_size, new_size, str(output_path)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao otimizar imagem '{input_path}': {str(e)}", exc_info=True)
            return False, 0, 0, None
    
    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """
        Converte uma imagem para o modo RGB, lidando com diferentes modos de imagem e transparência.
        Garante que a imagem esteja em um formato compatível para salvar como WebP.
        
        Args:
            img (Image.Image): Objeto de imagem PIL.

        Returns:
            Image.Image: O objeto de imagem PIL convertido para RGB.
        """
        if img.mode in ('RGBA', 'LA'):
            # Cria um fundo branco para imagens com transparência, prevenindo artefatos em WebP sem alfa.
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        elif img.mode == 'P': # Imagens com paleta
            return img.convert('RGB')
        elif img.mode not in ('RGB', 'L'): # Outros modos (CMYK, etc.)
            return img.convert('RGB')
        return img
    
    def _smart_resize(self, img: Image.Image) -> Tuple[Image.Image, bool]:
        """
        Redimensiona a imagem apenas se sua largura exceder 'self.max_width',
        mantendo a proporção original. Utiliza o algoritmo LANCZOS para alta qualidade.
        
        Args:
            img (Image.Image): Objeto de imagem PIL.

        Returns:
            tuple: Uma tupla contendo:
                - Image.Image: O objeto de imagem PIL (redimensionado ou original).
                - bool: `True` se a imagem foi redimensionada, `False` caso contrário.
        """
        if img.width <= self.max_width and img.height <= self.max_width:
            return img, False
        
        # Calcula as novas dimensões mantendo a proporção original.
        if img.width > img.height:
            new_width = self.max_width
            new_height = int(img.height * (self.max_width / img.width))
        else:
            new_height = self.max_width
            new_width = int(img.width * (self.max_width / img.height))
        
        # Redimensiona usando o filtro LANCZOS para a melhor qualidade visual.
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return img, True
    
    def process_upload(self, file, upload_folder: Union[Path, str]) -> Tuple[bool, Optional[str], str]:
        """
        Processa automaticamente um arquivo de imagem enviado via upload (e.g., de um formulário Flask).
        Salva o arquivo temporariamente, otimiza-o e retorna o caminho para a versão WebP otimizada.
        
        Args:
            file (werkzeug.datastructures.FileStorage): Objeto de arquivo de upload do Flask.
            upload_folder (str | Path): O diretório de destino para salvar a imagem processada.
            
        Returns:
            tuple: Uma tupla contendo:
                - bool: `True` se o processamento foi bem-sucedido, `False` caso contrário.
                - str | None: Caminho completo para a imagem otimizada (WebP) ou None em caso de falha.
                - str: Uma mensagem de status ou erro.
        """
        try:
            upload_folder = Path(upload_folder)
            upload_folder.mkdir(parents=True, exist_ok=True) # Garante que a pasta de upload exista
            
            # Gera um nome de arquivo temporário único para evitar colisões.
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f') # Adicionado microsegundos para maior unicidade
            original_name = Path(file.filename).stem
            temp_path = upload_folder / f"{original_name}_{timestamp}{Path(file.filename).suffix}"
            
            # Salva o arquivo enviado temporariamente.
            file.save(str(temp_path))
            current_app.logger.debug(f"Arquivo temporário salvo em: '{temp_path}'.")
            
            # Otimiza a imagem temporária.
            success, orig_size, new_size, webp_path = self.optimize_image(temp_path)
            
            if success:
                # Calcula a redução de tamanho e prepara a mensagem de sucesso.
                reduction = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
                message = f"Imagem otimizada com sucesso! Redução: {reduction:.1f}% para WebP."
                current_app.logger.info(message)
                return True, webp_path, message
            else:
                message = "Erro ao otimizar imagem durante o processamento de upload."
                current_app.logger.warning(message)
                return False, None, message
                
        except Exception as e:
            message = f"Erro inesperado ao processar upload da imagem: {str(e)}"
            current_app.logger.error(message, exc_info=True)
            return False, None, message
    
    def batch_optimize(self, directory: Union[Path, str], extensions: List[str] = None) -> dict:
        """
        Otimiza todas as imagens em um diretório especificado, convertendo-as para WebP.
        
        Args:
            directory (str | Path): O caminho para o diretório contendo as imagens a serem otimizadas.
            extensions (list, optional): Uma lista de extensões de arquivo a serem consideradas.
                                        Padrão: ['.jpg', '.jpeg', '.png', '.gif', '.bmp'].
            
        Returns:
            dict: Um dicionário contendo estatísticas da operação em lote, incluindo
                  total de arquivos, sucesso, falhas, tamanhos e detalhes de cada arquivo.
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        
        directory = Path(directory)
        images = []
        
        # Encontra todas as imagens no diretório e subdiretórios com as extensões especificadas.
        for ext in extensions:
            images.extend(directory.rglob(f'*{ext}'))
            images.extend(directory.rglob(f'*{ext.upper()}')) # Inclui extensões em maiúsculas
        
        # Remove quaisquer duplicatas que possam ter sido adicionadas (e.g., se o glob for sensível a maiúsculas/minúsculas).
        images = list(set(images))
        
        stats = {
            'total_files': len(images),
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'original_total_size': 0,
            'optimized_total_size': 0,
            'files_processed': []
        }
        
        current_app.logger.info(f"Iniciando otimização em lote de {stats['total_files']} imagens em '{directory}'.")
        for img_path in images:
            success, orig_size, new_size, output_path = self.optimize_image(img_path)
            
            if success:
                stats['successful_optimizations'] += 1
                stats['original_total_size'] += orig_size
                stats['optimized_total_size'] += new_size
                reduction = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
                stats['files_processed'].append({
                    'input_path': str(img_path),
                    'output_path': output_path,
                    'original_size_bytes': orig_size,
                    'optimized_size_bytes': new_size,
                    'size_reduction_percent': f"{reduction:.1f}%"
                })
                current_app.logger.debug(f"Lote: Otimizado '{img_path.name}'. Redução: {reduction:.1f}%.")
            else:
                stats['failed_optimizations'] += 1
                current_app.logger.warning(f"Lote: Falha ao otimizar '{img_path.name}'.")
        
        current_app.logger.info(f"Otimização em lote concluída. Sucesso: {stats['successful_optimizations']}, Falhas: {stats['failed_optimizations']}.")
        return stats


# Instância global do processador de imagens para ser reutilizada pela aplicação.
# Configurado para qualidade de 95%, largura máxima de 2560px e criação de backups.
image_processor = ImageProcessor(quality=95, max_width=2560, create_backup=True)


def optimize_uploaded_image(file, upload_folder: Union[str, Path]) -> Tuple[bool, Optional[str], str]:
    """
    Função auxiliar para otimizar um arquivo de imagem recebido via upload de formulário.
    Encapsula a lógica de `ImageProcessor.process_upload`.
    
    Args:
        file (werkzeug.datastructures.FileStorage): O objeto de arquivo enviado.
        upload_folder (str | Path): O diretório onde a imagem otimizada será salva.
        
    Returns:
        tuple: (bool: sucesso, str|None: caminho_webp, str: mensagem de status/erro).
    """
    return image_processor.process_upload(file, upload_folder)


def optimize_image_file(input_path: Union[str, Path], output_path: Union[str, Path] = None) -> Tuple[bool, int, int, Optional[str]]:
    """
    Função auxiliar para otimizar um arquivo de imagem existente no sistema de arquivos.
    Encapsula a lógica de `ImageProcessor.optimize_image`.
    
    Args:
        input_path (str | Path): Caminho para a imagem original.
        output_path (str | Path, optional): Caminho de destino para a imagem otimizada.
                                           Se omitido, a imagem original será substituída
                                           por sua versão .webp no mesmo diretório.
        
    Returns:
        tuple: (bool: sucesso, int: tamanho_original, int: tamanho_otimizado, str|None: caminho_saida).
    """
    return image_processor.optimize_image(input_path, output_path)


def process_and_save_image(file, upload_folder: Union[str, Path]) -> Tuple[bool, Optional[str], str]:
    """
    Função auxiliar para processar e salvar uma imagem de upload.
    Este é um alias para `optimize_uploaded_image` para compatibilidade com nomes anteriores ou clareza.
    
    Args:
        file (werkzeug.datastructures.FileStorage): O objeto de arquivo enviado.
        upload_folder (str | Path): O diretório onde a imagem otimizada será salva.
        
    Returns:
        tuple: (bool: sucesso, str|None: caminho_webp, str: mensagem de status/erro).
    """
    current_app.logger.warning("A função `process_and_save_image` está obsoleta. Use `optimize_uploaded_image` em seu lugar.")
    return optimize_uploaded_image(file, upload_folder)


def save_logo(file, filename: str) -> Optional[str]:
    """
    Salva um arquivo de logo ou imagem, otimizando-o automaticamente.
    Gera um caminho relativo para ser armazenado no banco de dados.
    
    Args:
        file (werkzeug.datastructures.FileStorage): O objeto de arquivo de upload.
        filename (str): O nome base do arquivo (sem extensão) para salvar.
        
    Returns:
        str | None: O caminho relativo da imagem otimizada (WebP) dentro do diretório 'static'
                    ou o caminho relativo da imagem original se a otimização falhar.
                    Retorna None se ocorrer um erro insuperável.
    """
    try:
        from flask import current_app
        
        # Define o diretório de upload, usando a configuração da aplicação.
        upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'BelarminoMonteiroAdvogado/static/images/uploads'))
        upload_folder.mkdir(parents=True, exist_ok=True) # Garante que a pasta de upload exista
        
        # Salva o arquivo temporariamente com a extensão original.
        ext = Path(file.filename).suffix
        temp_path = upload_folder / f"{filename}{ext}"
        file.save(str(temp_path))
        current_app.logger.debug(f"Logo '{filename}{ext}' salvo temporariamente para otimização em '{temp_path}'.")
        
        # Otimiza a imagem salva.
        success, orig_size, new_size, webp_path = image_processor.optimize_image(temp_path)
        
        if success:
            webp_path = Path(webp_path)
            # Retorna o caminho relativo da imagem otimizada.
            relative_path = str(webp_path.relative_to(Path('BelarminoMonteiroAdvogado/static')))
            current_app.logger.info(f"Logo '{filename}' otimizado e salvo em '{relative_path}'.")
            return relative_path.replace('\\', '/')
        else:
            # Se a otimização falhar, retorna o caminho do arquivo original.
            current_app.logger.warning(f"Falha ao otimizar logo '{filename}'. Retornando caminho do original.")
            relative_path = str(temp_path.relative_to(Path('BelarminoMonteiroAdvogado/static')))
            return relative_path.replace('\\', '/')
            
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao salvar logo '{filename}': {e}. Tentando fallback...", exc_info=True)
        # Fallback: tenta salvar o arquivo original sem otimização em caso de erro.
        try:
            from flask import current_app
            upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'BelarminoMonteiroAdvogado/static/images/uploads'))
            upload_folder.mkdir(parents=True, exist_ok=True)
            
            ext = Path(file.filename).suffix
            save_path = upload_folder / f"{filename}{ext}"
            file.save(str(save_path))
            
            relative_path = str(save_path.relative_to(Path('BelarminoMonteiroAdvogado/static')))
            current_app.logger.info(f"Logo '{filename}' salvo via fallback (sem otimização) em '{relative_path}'.")
            return relative_path.replace('\\', '/')
        except Exception as fallback_e:
            current_app.logger.error(f"Erro crítico ao tentar fallback para salvar logo '{filename}': {fallback_e}", exc_info=True)
            return None