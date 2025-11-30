/**
 * Resource Preloader - Sistema de pré-carregamento inteligente
 * Carrega vídeos e imagens críticas em cache após 5 segundos
 * para garantir uma experiência fluida
 */

(function() {
    'use strict';

    // Configuração
    const CONFIG = {
        delayBeforePreload: 5000, // 5 segundos
        videoQuality: 'auto', // auto, high, medium, low
        enableServiceWorker: true,
        enableIndexedDB: true
    };

    // Lista de recursos críticos para preload
    const CRITICAL_RESOURCES = {
        videos: [
            '/static/videos/maior-1.webm',
            '/static/videos/institucional.webm',
            '/static/videos/maior-1_logo.mp4'
        ],
        images: [
            '/static/images/Belarmino.png',
            '/static/images/Taise.png',
            '/static/images/BM.png',
            '/static/images/Escolhidas Escritorio/3S5A1373.jpg',
            '/static/images/Escolhidas Escritorio/3S5A1400.jpg',
            '/static/images/Escolhidas Escritorio/3S5A1485.jpg'
        ]
    };

    /**
     * Verifica se o navegador suporta as APIs necessárias
     */
    function checkBrowserSupport() {
        return {
            serviceWorker: 'serviceWorker' in navigator,
            indexedDB: 'indexedDB' in window,
            fetch: 'fetch' in window,
            cache: 'caches' in window
        };
    }

    /**
     * Detecta a velocidade da conexão
     */
    function getConnectionSpeed() {
        if ('connection' in navigator) {
            const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            if (conn) {
                return {
                    effectiveType: conn.effectiveType, // 4g, 3g, 2g, slow-2g
                    downlink: conn.downlink, // Mbps
                    rtt: conn.rtt, // ms
                    saveData: conn.saveData // boolean
                };
            }
        }
        return { effectiveType: '4g', downlink: 10, rtt: 50, saveData: false };
    }

    /**
     * Decide se deve fazer preload baseado na conexão
     * SEMPRE RETORNA TRUE - Cache automático e atômico OBRIGATÓRIO
     */
    function shouldPreload() {
        const conn = getConnectionSpeed();
        
        // Log da conexão mas SEMPRE faz preload
        console.log('[Preloader] Conexão detectada:', conn.effectiveType);
        console.log('[Preloader] Cache AUTOMÁTICO e ATÔMICO ativado (obrigatório)');
        
        // SEMPRE retorna true - cache é obrigatório
        return true;
    }

    /**
     * Preload de vídeos usando Cache API
     */
    async function preloadVideos() {
        if (!('caches' in window)) {
            console.warn('[Preloader] Cache API não suportada');
            return;
        }

        try {
            const cache = await caches.open('video-cache-v1');
            
            for (const videoUrl of CRITICAL_RESOURCES.videos) {
                try {
                    // Verifica se já está em cache
                    const cachedResponse = await cache.match(videoUrl);
                    if (cachedResponse) {
                        console.log(`[Preloader] Vídeo já em cache: ${videoUrl}`);
                        continue;
                    }

                    // Faz o download e armazena em cache
                    console.log(`[Preloader] Baixando vídeo: ${videoUrl}`);
                    const response = await fetch(videoUrl, {
                        mode: 'cors',
                        credentials: 'same-origin'
                    });

                    if (response.ok) {
                        await cache.put(videoUrl, response.clone());
                        console.log(`[Preloader] Vídeo armazenado em cache: ${videoUrl}`);
                    }
                } catch (error) {
                    console.error(`[Preloader] Erro ao cachear vídeo ${videoUrl}:`, error);
                }
            }
        } catch (error) {
            console.error('[Preloader] Erro ao abrir cache:', error);
        }
    }

    /**
     * Preload de imagens usando Cache API
     */
    async function preloadImages() {
        if (!('caches' in window)) {
            console.warn('[Preloader] Cache API não suportada');
            return;
        }

        try {
            const cache = await caches.open('image-cache-v1');
            
            for (const imageUrl of CRITICAL_RESOURCES.images) {
                try {
                    // Verifica se já está em cache
                    const cachedResponse = await cache.match(imageUrl);
                    if (cachedResponse) {
                        console.log(`[Preloader] Imagem já em cache: ${imageUrl}`);
                        continue;
                    }

                    // Faz o download e armazena em cache
                    console.log(`[Preloader] Baixando imagem: ${imageUrl}`);
                    const response = await fetch(imageUrl, {
                        mode: 'cors',
                        credentials: 'same-origin'
                    });

                    if (response.ok) {
                        await cache.put(imageUrl, response.clone());
                        console.log(`[Preloader] Imagem armazenada em cache: ${imageUrl}`);
                    }
                } catch (error) {
                    console.error(`[Preloader] Erro ao cachear imagem ${imageUrl}:`, error);
                }
            }
        } catch (error) {
            console.error('[Preloader] Erro ao abrir cache:', error);
        }
    }

    /**
     * Preload usando link rel="prefetch" (fallback)
     */
    function preloadWithLinkTags() {
        console.log('[Preloader] Usando link prefetch como fallback');
        
        // Preload de vídeos
        CRITICAL_RESOURCES.videos.forEach(videoUrl => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = videoUrl;
            link.as = 'video';
            document.head.appendChild(link);
        });

        // Preload de imagens
        CRITICAL_RESOURCES.images.forEach(imageUrl => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = imageUrl;
            link.as = 'image';
            document.head.appendChild(link);
        });
    }

    /**
     * Mostra progresso do preload (opcional)
     */
    function showPreloadProgress(current, total) {
        const percentage = Math.round((current / total) * 100);
        console.log(`[Preloader] Progresso: ${percentage}% (${current}/${total})`);
        
        // Você pode adicionar uma barra de progresso visual aqui se desejar
        // Exemplo: document.getElementById('preload-progress').style.width = percentage + '%';
    }

    /**
     * Limpa cache antigo (manutenção)
     */
    async function cleanOldCache() {
        if (!('caches' in window)) return;

        try {
            const cacheNames = await caches.keys();
            const currentCaches = ['video-cache-v1', 'image-cache-v1'];
            
            // Remove caches antigos
            for (const cacheName of cacheNames) {
                if (!currentCaches.includes(cacheName)) {
                    console.log(`[Preloader] Removendo cache antigo: ${cacheName}`);
                    await caches.delete(cacheName);
                }
            }
        } catch (error) {
            console.error('[Preloader] Erro ao limpar cache:', error);
        }
    }

    /**
     * Inicializa o sistema de preload
     */
    async function initPreloader() {
        console.log('[Preloader] Iniciando sistema de pré-carregamento...');
        
        // Verifica suporte do navegador
        const support = checkBrowserSupport();
        console.log('[Preloader] Suporte do navegador:', support);

        // Verifica se deve fazer preload
        if (!shouldPreload()) {
            console.log('[Preloader] Preload cancelado');
            return;
        }

        // Aguarda 5 segundos antes de iniciar
        console.log(`[Preloader] Aguardando ${CONFIG.delayBeforePreload / 1000}s antes de iniciar...`);
        await new Promise(resolve => setTimeout(resolve, CONFIG.delayBeforePreload));

        // Limpa cache antigo primeiro
        await cleanOldCache();

        // Inicia preload
        const totalResources = CRITICAL_RESOURCES.videos.length + CRITICAL_RESOURCES.images.length;
        let loadedResources = 0;

        console.log(`[Preloader] Iniciando preload de ${totalResources} recursos...`);

        // Preload de vídeos
        if (support.cache) {
            await preloadVideos();
            loadedResources += CRITICAL_RESOURCES.videos.length;
            showPreloadProgress(loadedResources, totalResources);
        }

        // Preload de imagens
        if (support.cache) {
            await preloadImages();
            loadedResources += CRITICAL_RESOURCES.images.length;
            showPreloadProgress(loadedResources, totalResources);
        }

        // Fallback para navegadores sem Cache API
        if (!support.cache) {
            preloadWithLinkTags();
        }

        console.log('[Preloader] Preload concluído!');
        
        // Dispara evento customizado
        window.dispatchEvent(new CustomEvent('preloadComplete', {
            detail: { totalResources, loadedResources }
        }));
    }

    /**
     * Registra Service Worker (opcional, para cache offline)
     */
    async function registerServiceWorker() {
        if (!CONFIG.enableServiceWorker || !('serviceWorker' in navigator)) {
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('[Preloader] Service Worker registrado:', registration);
        } catch (error) {
            console.error('[Preloader] Erro ao registrar Service Worker:', error);
        }
    }

    // Inicia quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initPreloader();
            registerServiceWorker();
        });
    } else {
        initPreloader();
        registerServiceWorker();
    }

    // Expõe API pública
    window.ResourcePreloader = {
        init: initPreloader,
        cleanCache: cleanOldCache,
        getConnectionSpeed: getConnectionSpeed,
        checkSupport: checkBrowserSupport
    };

})();
