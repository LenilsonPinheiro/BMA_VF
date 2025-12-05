/**
 * Service Worker - Cache Agressivo e Offline First
 * Força o cache de todos os recursos críticos
 */

const CACHE_VERSION = 'v1.0.1';
const CACHE_NAME = `belarmino-${CACHE_VERSION}`;

// Recursos que DEVEM ser cacheados imediatamente
const CRITICAL_ASSETS = [
    '/',
    '/static/videos/maior-1.webm',
    '/static/videos/maior-1.mp4',
    '/static/videos/institucional.webm',
    '/static/images/Belarmino.png',
    '/static/images/Taise.png',
    '/static/images/BM.png',
    '/static/images/Escolhidas%20Escritorio/3S5A1373.jpg',
    '/static/images/Escolhidas%20Escritorio/3S5A1400.jpg',
    '/static/images/Escolhidas%20Escritorio/3S5A1485.jpg',
    '/static/css/theme.css',
    '/static/css/video-optimizer.css',
    '/static/js/video-optimizer.js',
    '/static/js/aggressive-cache.js',
    '/static/js/script.js'
];

// Instalação - Cacheia recursos críticos
self.addEventListener('install', event => {
    console.log('[SW] Instalando Service Worker...');
    
    setTimeout(() => {
        event.waitUntil(
            caches.open(CACHE_NAME)
                .then(cache => {
                    console.log('[SW] Cacheando recursos críticos após 5 segundos...');
                    return cache.addAll(CRITICAL_ASSETS);
                })
                .then(() => {
                    console.log('[SW] ✓ Recursos críticos cacheados');
                    return self.skipWaiting();
                })
                .catch(error => {
                    console.error('[SW] Erro ao cachear recursos:', error);
                })
        );
    }, 5000); // Delay de 5 segundos
});

// Ativação - Limpa caches antigos
self.addEventListener('activate', event => {
    console.log('[SW] Ativando Service Worker...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(name => name !== CACHE_NAME)
                        .map(name => {
                            console.log('[SW] Removendo cache antigo:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] ✓ Service Worker ativado');
                return self.clients.claim();
            })
    );
});

// Fetch - Estratégia Cache First com Network Fallback
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Ignora requisições de outros domínios
    if (url.origin !== location.origin) {
        return;
    }

    // Estratégia específica para vídeos
    if (isVideoRequest(request)) {
        event.respondWith(handleVideoRequest(request));
        return;
    }

    // Estratégia específica para imagens
    if (isImageRequest(request)) {
        event.respondWith(handleImageRequest(request));
        return;
    }

    // Estratégia padrão: Cache First
    event.respondWith(
        caches.match(request)
            .then(cachedResponse => {
                if (cachedResponse) {
                    // Retorna do cache e atualiza em background
                    updateCacheInBackground(request);
                    return cachedResponse;
                }

                // Busca da rede e cacheia
                return fetch(request)
                    .then(response => {
                        if (response.ok) {
                            const responseClone = response.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => cache.put(request, responseClone));
                        }
                        return response;
                    });
            })
            .catch(() => {
                // Fallback offline
                return caches.match('/offline.html');
            })
    );
});

/**
 * Verifica se é requisição de vídeo
 */
function isVideoRequest(request) {
    return request.url.includes('/videos/') || 
           request.headers.get('accept')?.includes('video');
}

/**
 * Verifica se é requisição de imagem
 */
function isImageRequest(request) {
    return request.url.includes('/images/') || 
           request.headers.get('accept')?.includes('image');
}

/**
 * Trata requisições de vídeo com Range support
 */
async function handleVideoRequest(request) {
    try {
        const cache = await caches.open(CACHE_NAME);
        let cachedResponse = await cache.match(request);

        if (cachedResponse) {
            console.log('[SW] ✓ Vídeo do cache:', request.url);
            return cachedResponse;
        }

        console.log('[SW] Baixando vídeo:', request.url);
        const response = await fetch(request);

        if (response.ok) {
            // Cacheia apenas se for uma resposta completa (não range)
            if (response.status === 200) {
                cache.put(request, response.clone());
            }
        }

        return response;
    } catch (error) {
        console.error('[SW] Erro ao buscar vídeo:', error);
        throw error;
    }
}

/**
 * Trata requisições de imagem
 */
async function handleImageRequest(request) {
    try {
        const cache = await caches.open(CACHE_NAME);
        let cachedResponse = await cache.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        const response = await fetch(request);

        if (response.ok) {
            cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        console.error('[SW] Erro ao buscar imagem:', error);
        // Retorna imagem placeholder se disponível
        return caches.match('/static/images/placeholder.png');
    }
}

/**
 * Atualiza cache em background
 */
function updateCacheInBackground(request) {
    fetch(request)
        .then(response => {
            if (response.ok) {
                caches.open(CACHE_NAME)
                    .then(cache => cache.put(request, response));
            }
        })
        .catch(() => {
            // Silenciosamente falha se offline
        });
}

/**
 * Mensagens do cliente
 */
self.addEventListener('message', event => {
    if (event.data.action === 'skipWaiting') {
        self.skipWaiting();
    }

    if (event.data.action === 'clearCache') {
        event.waitUntil(
            caches.keys()
                .then(names => Promise.all(names.map(name => caches.delete(name))))
                .then(() => {
                    event.ports[0].postMessage({ success: true });
                })
        );
    }
});
