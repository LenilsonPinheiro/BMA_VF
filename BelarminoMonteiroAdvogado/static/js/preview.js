/* BelarminoMonteiroAdvogado/static/js/preview.js
   LIVE PREVIEW ENGINE - Conecta o Admin ao Front-end em tempo real.
*/

(function() {
    'use strict';

    // Configuração de segurança (Opcional: restrinja ao seu domínio de admin)
    // const ALLOWED_ORIGIN = 'https://seu-admin.com'; 

    window.addEventListener('message', function(event) {
        // if (ALLOWED_ORIGIN && event.origin !== ALLOWED_ORIGIN) return;

        const data = event.data;

        if (!data || !data.type) return;

        switch (data.type) {
            case 'updateStyle':
                handleStyleUpdate(data.payload);
                break;
            
            case 'updateContent':
                handleContentUpdate(data.payload);
                break;

            case 'changeTheme':
                handleThemeSwitch(data.payload.theme);
                break;

            case 'reload':
                window.location.reload();
                break;
        }
    });

    /**
     * Atualiza Variáveis CSS em tempo real.
     * Mapeia as chaves de configuração do banco para as variáveis do CSS.
     */
    function handleStyleUpdate(payload) {
        const root = document.documentElement;

        // MAPA DE TRADUÇÃO: Config Key (DB) -> CSS Variable (Front)
        // Isso garante que uma config do admin afete o local certo no tema.
        const variableMap = {
            // Option 1 (Luxo)
            'cor_primaria_tema1': ['--prm-accent-red', '--lawer-red', '--lux-gold'],
            
            // Option 2 (Titan)
            'cor_primaria_tema2': ['--titan-gold', '--page-accent'],
            'cor_secundaria_tema2': ['--titan-navy', '--page-text-dark'],
            
            // Option 3 (Boutique)
            'cor_primaria_tema3': ['--gold-primary', '--btq-gold', '--page-accent'],
            
            // Option 4 (Tech)
            'cor_primaria_tema4': ['--tech-primary', '--intelbras-green', '--page-accent'],
            
            // Genéricos
            'font_heading': ['--font-heading', '--font-primary'],
            'font_body': ['--font-body', '--font-secondary']
        };

        for (const key in payload) {
            if (payload.hasOwnProperty(key)) {
                const value = payload[key];

                // 1. Tenta usar o mapa de tradução
                if (variableMap[key]) {
                    variableMap[key].forEach(cssVar => {
                        root.style.setProperty(cssVar, value);
                    });
                } 
                
                // 2. Fallback: Converte snake_case para kebab-case (--cor-primaria)
                // Útil para variáveis novas que não estão no mapa
                const genericVar = `--${key.replace(/_/g, '-')}`;
                root.style.setProperty(genericVar, value);
            }
        }
    }

    /**
     * Atualiza Textos e Imagens em tempo real (Seletor + Valor).
     * Exemplo payload: { 'h1.hero-title': 'Novo Título', '#logo-img': 'url...' }
     */
    function handleContentUpdate(payload) {
        for (const selector in payload) {
            const element = document.querySelector(selector);
            if (element) {
                const value = payload[selector];
                
                // Se for imagem
                if (element.tagName === 'IMG') {
                    element.src = value;
                } 
                // Se for texto
                else {
                    element.innerHTML = value; // innerHTML permite tags simples como <br>
                }
            }
        }
    }

    /**
     * Troca a classe do body para simular mudança de layout base
     */
    function handleThemeSwitch(themeName) {
        if (!themeName) return;
        
        // Remove classes antigas de tema
        document.body.classList.remove('option1', 'option2', 'option3', 'option4');
        
        // Adiciona a nova
        document.body.classList.add(themeName);
        
        // Opcional: Forçar recarregamento se a mudança de estrutura for muito drástica
        // window.location.reload(); 
    }

    console.log('Preview Engine Loaded: Listening for updates...');

})();