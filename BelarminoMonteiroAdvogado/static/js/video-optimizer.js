/**
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
