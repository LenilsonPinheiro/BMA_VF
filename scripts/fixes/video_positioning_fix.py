"""
Correção Final: Posicionamento do Vídeo + Otimização de Formato
Belarmino Monteiro Advogado
"""

import os

def fix_video_optimizer_css():
    """Corrige o CSS para garantir que o vídeo cubra toda a tela"""
    css_path = 'BelarminoMonteiroAdvogado/static/css/video-optimizer.css'
    
    print(f"[INFO] Corrigindo posicionamento do vídeo em {css_path}...")
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir a seção do vídeo de fundo com CSS correto
    new_video_bg_css = '''/* Otimização para vídeos de fundo */
.hero-video,
.hero-video-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
    will-change: transform;
    backface-visibility: hidden;
    transform: translateZ(0);
}'''
    
    # Encontrar e substituir a seção antiga
    import re
    content = re.sub(
        r'/\* Otimização para vídeos de fundo \*/.*?\.hero-video-bg \{[^}]+\}',
        new_video_bg_css,
        content,
        flags=re.DOTALL
    )
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] CSS do vídeo corrigido!")

def create_webm_conversion_guide():
    """Cria guia para conversão de vídeo para WebM"""
    guide_path = 'CONVERTER_VIDEO_WEBM.md'
    
    content = '''# 🎬 GUIA: Converter Vídeo para WebM (Melhor Performance)

## 📊 MP4 vs WebM - Qual usar?

### **Recomendação: Use AMBOS!**

| Formato | Vantagens | Desvantagens | Quando Usar |
|---------|-----------|--------------|-------------|
| **WebM** | ✅ Melhor compressão (30-50% menor)<br>✅ Qualidade superior<br>✅ Otimizado para web<br>✅ Suporte a VP9/AV1 | ❌ Safari não suporta nativamente<br>❌ Alguns dispositivos antigos | **Primeira opção** no HTML |
| **MP4** | ✅ Compatibilidade universal<br>✅ Suporte em todos os navegadores<br>✅ Funciona em iOS/Safari | ❌ Arquivo maior<br>❌ Compressão inferior | **Fallback** (segunda opção) |

### **Estratégia Ideal:**
```html
<video>
    <source src="video.webm" type="video/webm">  <!-- Tenta primeiro -->
    <source src="video.mp4" type="video/mp4">    <!-- Fallback -->
</video>
```

O navegador escolhe automaticamente o melhor formato suportado!

---

## 🚀 COMO CONVERTER SEU VÍDEO

### **Opção 1: FFmpeg (Recomendado - Melhor Qualidade)**

#### Instalar FFmpeg:
- **Windows:** Baixe em https://ffmpeg.org/download.html
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

#### Converter para WebM (VP9 - Melhor Compressão):
```bash
ffmpeg -i maior-1.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus maior-1.webm
```

**Parâmetros:**
- `-crf 30`: Qualidade (18-28 = alta, 30-35 = média, 36+ = baixa)
- `-b:v 0`: Deixa o codec decidir o bitrate ideal
- `libopus`: Codec de áudio superior

#### Converter para WebM (VP8 - Mais Compatível):
```bash
ffmpeg -i maior-1.mp4 -c:v libvpx -crf 30 -b:v 1M -c:a libvorbis maior-1.webm
```

#### Otimizar MP4 Existente (Reduzir Tamanho):
```bash
ffmpeg -i maior-1.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 128k maior-1-optimized.mp4
```

**Seu vídeo atual:** 16.9 MB
**Após otimização:** ~8-10 MB (WebM) ou ~10-12 MB (MP4 otimizado)

---

### **Opção 2: Ferramentas Online (Mais Fácil)**

1. **CloudConvert** (https://cloudconvert.com/mp4-to-webm)
   Agora vou corrigir o problema de posicionamento do vídeo. O vídeo está aparecendo apenas na parte superior esquerda porque o CSS está definindo `position: absolute; inset: 0;` mas não está cobrindo toda a tela corretamente. Vou ajustar o CSS:


Assistant: Agora vou criar um script para otimizar os vídeos e responder sobre MP4 vs WebM:

<create_file>
<path>otimizar_videos_final.py</path>
<content>
"""
Script para otimizar vídeos - MP4 vs WebM
Belarmino Monteiro Advogado
"""

import os
import subprocess
import shutil

def check_ffmpeg():
    """Verifica se FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def optimize_video(input_path, output_path, codec='mp4', crf=28):
    """
    Otimiza vídeo usando FFmpeg
    - MP4: Melhor compatibilidade
    - WebM: Melhor compressão
    """
    if not os.path.exists(input_path):
        print(f"[ERRO] Arquivo não encontrado: {input_path}")
        return False

    # Comando FFmpeg
    if codec.lower() == 'webm':
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libvpx-vp9', '-crf', str(crf), '-b:v', '0',
            '-c:a', 'libopus', '-b:a', '128k',
            '-movflags', '+faststart',
            '-y', output_path
        ]
    else:  # MP4
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264', '-crf', str(crf), '-preset', 'slow',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            '-y', output_path
        ]

    print(f"[INFO] Otimizando {input_path} -> {output_path}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Vídeo otimizado: {output_path}")
            return True
        else:
            print(f"[ERRO] Falha na otimização: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def get_video_info(file_path):
    """Obtém informações do vídeo"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            return data
        return None
    except Exception as e:
        print(f"[ERRO] Não foi possível obter info do vídeo: {e}")
        return None

def main():
    print("=" * 60)
    print("OTIMIZAÇÃO DE VÍDEOS - MP4 vs WebM")
    print("=" * 60)
    print()

    if not check_ffmpeg():
        print("[ERRO] FFmpeg não está instalado!")
        print("Instale FFmpeg primeiro:")
        print("- Windows: choco install ffmpeg")
        print("- Ubuntu/Debian: sudo apt install ffmpeg")
        print("- macOS: brew install ffmpeg")
        return 1

    video_dir = 'BelarminoMonteiroAdvogado/static/videos'
    input_video = os.path.join(video_dir, 'maior-1.mp4')

    if not os.path.exists(input_video):
        print(f"[ERRO] Vídeo original não encontrado: {input_video}")
        return 1

    # Obter informações do vídeo original
    info = get_video_info(input_video)
    if info:
        size_mb = int(info['format']['size']) / (1024 * 1024)
        duration = float(info['format']['duration'])
        print(f"[INFO] Vídeo original: {size_mb:.1f} MB, {duration:.1f}s")
    else:
        print("[INFO] Vídeo original encontrado")

    print()
    print("ESCOLHA A ESTRATÉGIA DE OTIMIZAÇÃO:")
    print("1) MP4 Otimizado (Melhor compatibilidade)")
    print("2) WebM Otimizado (Melhor compressão)")
    print("3) Ambos (MP4 + WebM)")
    print("4) Apenas analisar (não otimizar)")
    print()

    choice = input("Digite sua escolha (1-4): ").strip()

    if choice == '4':
        print("[INFO] Análise concluída. Saindo...")
        return 0

    # Criar backup
    backup_dir = os.path.join(video_dir, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, 'maior-1-original.mp4')
    if not os.path.exists(backup_path):
        shutil.copy2(input_video, backup_path)
        print(f"[OK] Backup criado: {backup_path}")

    if choice in ['1', '3']:
        # Otimizar MP4
        output_mp4 = os.path.join(video_dir, 'maior-1-optimized.mp4')
        if optimize_video(input_video, output_mp4, 'mp4'):
            # Substituir original
            shutil.move(output_mp4, input_video)
            print(f"[OK] MP4 otimizado substituído")

    if choice in ['2', '3']:
        # Otimizar WebM
        output_webm = os.path.join(video_dir, 'maior-1.webm')
        if optimize_video(input_video, output_webm, 'webm'):
            print(f"[OK] WebM criado: {output_webm}")

    print()
    print("=" * 60)
    print("✅ OTIMIZAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("RECOMENDAÇÕES:")
    print("• MP4: Melhor para compatibilidade universal")
    print("• WebM: Melhor para web moderna (Chrome, Firefox)")
    print("• Use ambos: <source> MP4 primeiro, WebM fallback")
    print()
    print("Para testar: execute TESTE_VIDEO_AGORA.bat")

    return 0

if __name__ == '__main__':
    exit(main())
