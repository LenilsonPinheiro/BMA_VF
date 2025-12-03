"""
Script para corrigir o problema de vídeos invisíveis
Belarmino Monteiro Advogado
"""

import os
import re

def fix_video_optimizer_css():
    """Remove o opacity: 0 inicial que está escondendo os vídeos"""
    css_path = 'BelarminoMonteiroAdvogado/static/css/video-optimizer.css'
    
    print(f"[INFO] Corrigindo {css_path}...")
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover o opacity: 0 inicial e a transição que está causando o problema
    content = re.sub(
        r'video \{[^}]*?opacity: 0;[^}]*?transition: opacity[^;]*;[^}]*?\}',
        '''video {
    /* Aceleração por hardware */
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
    perspective: 1000px;
    
    /* Garantir que o vídeo cubra toda a área */
    object-fit: cover;
    width: 100%;
    height: 100%;
    
    /* VÍDEO VISÍVEL POR PADRÃO - Corrigido */
    opacity: 1;
}''',
        content,
        flags=re.DOTALL
    )
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] CSS corrigido!")

def fix_video_optimizer_js():
    """Simplifica o JavaScript para não interferir com a visibilidade"""
    js_path = 'BelarminoMonteiroAdvogado/static/js/video-optimizer.js'
    
    print(f"[INFO] Corrigindo {js_path}...")
    
    content = '''/**
 * Otimizador de Vídeos - VERSÃO CORRIGIDA
 * Belarmino Monteiro Advogado
 */

document.addEventListener('DOMContentLoaded', function() {
    const videos = document.querySelectorAll('video');
    
    if (videos.length === 0) return;
    
    console.log(`[Video Optimizer] ${videos.length} vídeo(s) encontrado(s)`);
    
    // Aplicar otimizações a todos os vídeos
    videos.forEach((video, index) => {
        console.log(`[Video Optimizer] Otimizando vídeo ${index + 1}`);
        
        // Otimizações de performance
        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');
        
        // Forçar aceleração por hardware
        video.style.willChange = 'transform';
        video.style.transform = 'translateZ(0)';
        video.style.backfaceVisibility = 'hidden';
        
        // GARANTIR QUE O VÍDEO ESTEJA VISÍVEL
        video.style.opacity = '1';
        video.style.display = 'block';
        
        // Tentar reproduzir automaticamente
        if (video.hasAttribute('autoplay')) {
            video.play().catch(err => {
                console.log(`[Video Optimizer] Autoplay bloqueado para vídeo ${index + 1}:`, err);
                // Adicionar botão de play se autoplay falhar
                addPlayButton(video);
            });
        }
        
        // Eventos de log
        video.addEventListener('loadeddata', function() {
            console.log(`[Video Optimizer] Vídeo ${index + 1} carregado`);
            video.classList.add('loaded');
        });
        
        video.addEventListener('error', function(e) {
            console.error(`[Video Optimizer] Erro ao carregar vídeo ${index + 1}:`, e);
            console.error('Detalhes do erro:', {
                error: video.error,
                networkState: video.networkState,
                readyState: video.readyState,
                src: video.currentSrc
            });
        });
        
        video.addEventListener('play', function() {
            console.log(`[Video Optimizer] Vídeo ${index + 1} reproduzindo`);
        });
        
        video.addEventListener('pause', function() {
            console.log(`[Video Optimizer] Vídeo ${index + 1} pausado`);
        });
        
        video.addEventListener('canplay', function() {
            console.log(`[Video Optimizer] Vídeo ${index + 1} pronto para reproduzir`);
        });
    });
    
    console.log('[Video Optimizer] Otimização concluída');
});

// Função para adicionar botão de play manual
function addPlayButton(video) {
    // Verificar se já existe botão
    if (video.parentNode.querySelector('.video-play-button')) {
        return;
    }
    
    const playButton = document.createElement('button');
    playButton.textContent = '▶ Reproduzir Vídeo';
    playButton.className = 'video-play-button';
    playButton.setAttribute('aria-label', 'Reproduzir vídeo');
    playButton.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
        padding: 15px 35px;
        background: rgba(185, 32, 39, 0.95);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    `;
    
    playButton.onclick = function() {
        video.play().then(() => {
            playButton.style.display = 'none';
        }).catch(err => {
            console.error('Erro ao reproduzir vídeo:', err);
        });
    };
    
    // Garantir que o container seja relativo
    if (video.parentNode.style.position !== 'relative' && 
        video.parentNode.style.position !== 'absolute') {
        video.parentNode.style.position = 'relative';
    }
    
    video.parentNode.appendChild(playButton);
}

// Preload de vídeos em segundo plano
window.addEventListener('load', function() {
    const videos = document.querySelectorAll('video[preload="auto"]');
    videos.forEach(video => {
        if (video.readyState < 3) {
            console.log('[Video Optimizer] Pré-carregando vídeo...');
            video.load();
        }
    });
});
'''
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] JavaScript corrigido!")

def main():
    """
    Definição de main.
    Componente essencial para a arquitetura do sistema.
    """
    print("=" * 60)
    print("CORREÇÃO DE VÍDEOS INVISÍVEIS")
    print("=" * 60)
    print()
    
    try:
        fix_video_optimizer_css()
        print()
        fix_video_optimizer_js()
        print()
        print("=" * 60)
        print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("PRÓXIMOS PASSOS:")
        print("1. Limpe o cache do navegador (Ctrl+Shift+Delete)")
        print("2. Reinicie o servidor Flask")
        print("3. Recarregue a página (Ctrl+F5)")
        print()
        print("Se ainda não funcionar, verifique:")
        print("- Se o arquivo maior-1.mp4 existe em static/videos/")
        print("- Se o arquivo não está corrompido")
        print("- Console do navegador (F12) para erros")
        
    except Exception as e:
        print(f"[ERRO] {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
