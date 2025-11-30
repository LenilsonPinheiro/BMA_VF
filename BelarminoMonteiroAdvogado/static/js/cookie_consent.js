/* BelarminoMonteiroAdvogado/static/js/cookie_consent.js
   PRIVACY GUARDIAN ENGINE - Gerencia consentimento LGPD/GDPR e ativação de scripts.
*/

const CookieConsent = {
    key: 'bm_privacy_consent',
    
    // Cache de elementos do DOM
    elements: {},

    init() {
        this.cacheElements();
        
        // Segurança: Se o banner não estiver no HTML (ex: erro de include), aborta silenciosamente.
        if (!this.elements.banner) return;

        // Verifica se já existe consentimento salvo no navegador
        const consent = localStorage.getItem(this.key);
        
        if (!consent) {
            // Delay de entrada para não ser intrusivo imediatamente (Melhor UX)
            setTimeout(() => {
                this.elements.banner.classList.add('show');
            }, 2000);
        } else {
            // Se já tem consentimento, aplica as regras silenciosamente
            this.applyConsent(JSON.parse(consent));
        }
    },

    cacheElements() {
        this.elements = {
            banner: document.getElementById('cookie-consent-banner'),
            prefPanel: document.getElementById('cc-pref-panel'),
            mainActions: document.getElementById('cc-main-actions'),
            manageBtn: document.getElementById('cc-manage-btn'),
            analyticsCheckbox: document.getElementById('cc-analytics')
        };
    },

    /* --- Lógica de Interface --- */

    togglePreferences() {
        const { prefPanel, mainActions, manageBtn } = this.elements;
        
        if (prefPanel.style.display === 'block') {
            // Fechar preferências
            prefPanel.style.display = 'none';
            mainActions.style.display = 'grid'; // Volta para grid (desktop) ou block (mobile via CSS)
            manageBtn.style.display = 'block';
        } else {
            // Abrir preferências
            prefPanel.style.display = 'block';
            mainActions.style.display = 'none';
            manageBtn.style.display = 'none';
        }
    },

    /* --- Lógica de Decisão --- */

    acceptAll() {
        const preferences = {
            essential: true,
            analytics: true,
            marketing: true,
            timestamp: new Date().toISOString()
        };
        this.saveAndClose(preferences);
    },

    rejectAll() {
        const preferences = {
            essential: true,
            analytics: false,
            marketing: false,
            timestamp: new Date().toISOString()
        };
        this.saveAndClose(preferences);
    },

    savePreferences() {
        // Captura o estado real dos checkboxes
        const analyticsState = this.elements.analyticsCheckbox ? this.elements.analyticsCheckbox.checked : false;
        
        const preferences = {
            essential: true, // Sempre true
            analytics: analyticsState,
            marketing: false, // Expansível futuramente
            timestamp: new Date().toISOString()
        };
        this.saveAndClose(preferences);
    },

    saveAndClose(preferences) {
        localStorage.setItem(this.key, JSON.stringify(preferences));
        this.elements.banner.classList.remove('show');
        this.applyConsent(preferences);
    },

    /* --- Motor de Execução (Onde a mágica acontece) --- */

    applyConsent(preferences) {
        // Aqui é onde você dispara os scripts reais baseados na permissão.
        // Isso garante que cookies não sejam setados antes do "Sim".

        if (preferences.analytics) {
            console.log(' Privacy Guardian: Analytics Permitido. Iniciando rastreadores...');
            
            // EXEMPLO: Google Analytics / GTM
            /*
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'UA-XXXXX-Y');
            */
           
           // Se usar GTM, você pode dar um push no dataLayer aqui:
           // window.dataLayer.push({'event': 'consent_granted'});

        } else {
            console.log(' Privacy Guardian: Analytics Bloqueado pelo usuário.');
            
            // Opcional: Limpar cookies existentes se o usuário revogar consentimento
            // (Requer lógica avançada de manipulação de cookies)
        }
    }
};

// Inicializa o Guardião assim que o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => CookieConsent.init());