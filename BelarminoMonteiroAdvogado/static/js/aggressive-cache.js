/**
 * Sistema de Cache Agressivo e Compulsório
 * Força o download e armazenamento de todos os recursos críticos
 */

const CACHE_NAME = 'belarmino-v1';
const CRITICAL_RESOURCES = [
    // Vídeos
    '/static/videos/maior-1.webm',
    '/static/videos/maior-1.mp4',
    '/static/videos/institucional.webm',
    
    // Imagens críticas
    '/static/images/Belarmino.png',
    '/static/images/Taise.png',
    '/static/images/BM.png',
    '/static/images/Escolhidas%20Escritorio/3S5A1373.jpg',
    '/static/images/Escolhidas%20Escritorio/3S5A1400.jpg',
    '/static/images/Escolhidas%20Escritorio/3S5A1485.jpg',
    
    // CSS
    '/static/css/theme.css',
    '/static/css/video-optimizer.css',
    
    // JS
    '/static/js/video-optimizer.js',
    '/static/js/script.js'
];

class AggressiveCacheManager {
    constructor() {
        this.initServiceWorker();
        this.forcePreloadResources();
        this.setupVideoOptimization();
    }

    /**
     * Inicializa Service Worker para cache offline
     */
    initServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('[Cache] Service Worker registrado:', registration.scope);
                    this.checkForUpdates(registration);
                })
                .catch(error => {
                    console.error('[Cache] Erro ao registrar Service Worker:', error);
                });
        }
    }

    /**
     * Força o preload de todos os recursos críticos
     */
    async forcePreloadResources() {
        console.log('[Cache] Iniciando preload agressivo de recursos...');
        
        const promises = CRITICAL_RESOURCES.map(url => {
            return this.forceDownload(url);
        });

        try {
            await Promise.all(promises);
            console.log('[Cache] ✓ Todos os recursos foram baixados e cacheados');
            this.markResourcesAsReady();
        } catch (error) {
            console.error('[Cache] Erro ao cachear recursos:', error);
        }
    }

    /**
     * Força o download de um recurso específico
     */
    async forceDownload(url) {
        try {
            // Tenta buscar do cache primeiro
            const cache = await caches.open(CACHE_NAME);
            let response = await cache.match(url);

            if (!response) {
                console.log(`[Cache] Baixando: ${url}`);
                response = await fetch(url, {
                    cache: 'force-cache',
                    credentials: 'same-origin'
                });

                if (response.ok) {
                    await cache.put(url, response.clone());
                    console.log(`[Cache] ✓ Cacheado: ${url}`);
                }
            } else {
                console.log(`[Cache] ✓ Já em cache: ${url}`);
            }

            return response;
        } catch (error) {
            console.error(`[Cache] Erro ao baixar ${url}:`, error);
            throw error;
        }
    }

    /**
     * Otimiza vídeos para reprodução fluida
     */
    setupVideoOptimization() {
        document.addEventListener('DOMContentLoaded', () => {
            const videos = document.querySelectorAll('video');
            
            videos.forEach(video => {
                // Configurações de performance
                video.preload = 'auto';
                video.setAttribute('playsinline', '');
                video.setAttribute('webkit-playsinline', '');
                
                // Force WebM como primeira opção
                const sources = video.querySelectorAll('source');
                sources.forEach(source => {
                    if (source.type === 'video/webm') {
                        source.setAttribute('data-priority', 'high');
                    }
                });

                // Otimizações de buffer
                this.optimizeVideoBuffer(video);
                
                // Monitora performance
                this.monitorVideoPerformance(video);
            });
        });
    }

    /**
     * Otimiza o buffer do vídeo
     */
    optimizeVideoBuffer(video) {
        video.addEventListener('loadstart', () => {
            console.log('[Video] Iniciando carregamento:', video.currentSrc);
        });

        video.addEventListener('loadeddata', () => {
            console.log('[Video] ✓ Dados carregados:', video.currentSrc);
            
            // Força o buffer completo
            if (video.buffered.length > 0) {
                const bufferedEnd = video.buffered.end(video.buffered.length - 1);
                console.log(`[Video] Buffer: ${bufferedEnd.toFixed(2)}s de ${video.duration.toFixed(2)}s`);
            }
        });

        video.addEventListener('canplaythrough', () => {
            console.log('[Video] ✓ Pronto para reprodução sem interrupções');
        });

        video.addEventListener('stalled', () => {
            console.warn('[Video] ⚠ Stalled - tentando recuperar...');
            video.load();
        });

        video.addEventListener('waiting', () => {
            console.warn('[Video] ⚠ Aguardando buffer...');
        });
    }

    /**
     * Monitora performance do vídeo
     */
    monitorVideoPerformance(video) {
        let lastTime = 0;
        let frameCount = 0;

        video.addEventListener('timeupdate', () => {
            const currentTime = video.currentTime;
            
            if (currentTime - lastTime > 0.1) {
                frameCount++;
                lastTime = currentTime;
            }

            // Detecta travamentos
            if (video.paused && !video.ended && video.readyState < 3) {
                console.warn('[Video] ⚠ Possível travamento detectado');
                this.handleVideoStall(video);
            }
        });
    }

    /**
     * Trata travamentos de vídeo
     */
    handleVideoStall(video) {
        console.log('[Video] Tentando recuperar de travamento...');
        
        const currentTime = video.currentTime;
        video.load();
        
        video.addEventListener('loadeddata', function onLoaded() {
            video.currentTime = currentTime;
            video.play().catch(e => console.error('[Video] Erro ao retomar:', e));
            video.removeEventListener('loadeddata', onLoaded);
        });
    }

    /**
     * Verifica atualizações do Service Worker
     */
    checkForUpdates(registration) {
        setInterval(() => {
            registration.update();
        }, 60000); // Verifica a cada minuto
    }

    /**
     * Marca recursos como prontos
     */
    markResourcesAsReady() {
        document.body.classList.add('resources-cached');
        
        // Dispara evento customizado
        const event = new CustomEvent('resourcesCached', {
            detail: { timestamp: Date.now() }
        });
        document.dispatchEvent(event);
    }

    /**
     * Limpa cache antigo
     */
    async clearOldCache() {
        const cacheNames = await caches.keys();
        const oldCaches = cacheNames.filter(name => name !== CACHE_NAME);
        
        await Promise.all(
            oldCaches.map(name => caches.delete(name))
        );
        
        console.log('[Cache] ✓ Cache antigo limpo');
    }
}

// Inicializa o sistema de cache agressivo
const cacheManager = new AggressiveCacheManager();

// Exporta para uso global
window.AggressiveCacheManager = cacheManager;
