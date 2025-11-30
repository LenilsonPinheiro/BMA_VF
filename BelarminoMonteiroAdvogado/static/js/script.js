/* BelarminoMonteiroAdvogado/static/js/script.js
   Global Controller - Gerencia interações transversais a todos os temas.
*/

document.addEventListener('DOMContentLoaded', () => {
    
    // =========================================================================
    // 1. SYSTEM CORE (Reset & Configs)
    // =========================================================================
    
    // Evita bugs visuais de scroll ao recarregar a página (AOS Conflict Fix)
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }

    // Inicialização do AOS (Animate On Scroll) Global
    // Verifica se a biblioteca foi carregada antes de iniciar
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true, // Anima apenas na descida
            offset: 60,
            delay: 50   // Pequeno delay para garantir renderização
        });
    }

    // =========================================================================
    // 2. THEME ENGINE (Dark/Light Mode)
    // =========================================================================
    /* Gerencia a troca de temas de forma compatível com todos os layouts.
       Usa a classe 'dark-mode' no body e salva em localStorage.
    */
    
    const themeToggleBtn = document.getElementById('theme-toggle'); // Botão (Option 2/3)
    const themeCheckbox = document.querySelector('.theme-switch input[type="checkbox"]'); // Switch (Option 4)
    const body = document.body;
    const themeIcons = document.querySelectorAll('#theme-icon, .theme-icon'); // Ícones de Sol/Lua

    // Função para aplicar o tema visualmente
    const applyTheme = (isDark) => {
        if (isDark) {
            body.classList.add('dark-mode');
            // Atualiza ícones para "Sol" (indica que pode voltar pro claro)
            themeIcons.forEach(icon => {
                icon.classList.remove('bi-moon-stars-fill', 'bi-moon', 'bi-moon-fill');
                icon.classList.add('bi-sun-fill', 'bi-sun');
            });
            if(themeCheckbox) themeCheckbox.checked = true;
        } else {
            body.classList.remove('dark-mode');
            // Atualiza ícones para "Lua"
            themeIcons.forEach(icon => {
                icon.classList.remove('bi-sun-fill', 'bi-sun');
                icon.classList.add('bi-moon-stars-fill', 'bi-moon');
            });
            if(themeCheckbox) themeCheckbox.checked = false;
        }
    };

    // Carregar preferência salva
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        applyTheme(true);
    } else {
        applyTheme(false);
    }

    // Handler para Botão de Clique (Option 1, 2, 3)
    if (themeToggleBtn) {
        // Remove listeners antigos (se houver inline) clonando o elemento é uma técnica, 
        // mas aqui vamos apenas adicionar. Se o inline já existir, o toggle funciona igual.
        themeToggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const isDark = body.classList.toggle('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Animação de Rotação do Ícone
            const icon = themeToggleBtn.querySelector('i');
            if(icon) {
                icon.style.transform = 'rotate(360deg)';
                setTimeout(() => {
                    applyTheme(isDark);
                    icon.style.transform = 'rotate(0deg)';
                }, 300);
            } else {
                applyTheme(isDark);
            }
        });
    }

    // Handler para Checkbox Switch (Option 4)
    if (themeCheckbox) {
        themeCheckbox.addEventListener('change', (e) => {
            const isDark = e.target.checked;
            if (isDark) {
                body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
            // Não chamamos applyTheme aqui pois o CSS do switch já trata o visual
        });
    }


    // =========================================================================
    // 3. HEADER SCROLL FX (Polymorphic)
    // =========================================================================
    /*
       Detecta o tipo de cabeçalho (qualquer layout) e aplica classe 'scrolled'.
    */
    const header = document.querySelector('header.fixed-top') || document.getElementById('mainHeader') || document.querySelector('.navbar');
    
    if (header) {
        const handleScroll = () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
                // Ajuste específico para Bootstrap Navbars
                if(header.classList.contains('navbar-dark')) {
                    header.dataset.wasDark = "true";
                    header.classList.remove('navbar-dark');
                    header.classList.add('navbar-light');
                }
            } else {
                header.classList.remove('scrolled');
                // Reverte Bootstrap Navbars
                if(header.dataset.wasDark === "true") {
                    header.classList.add('navbar-dark');
                    header.classList.remove('navbar-light');
                }
            }
        };

        window.addEventListener('scroll', handleScroll);
        handleScroll(); // Check inicial
    }


    // =========================================================================
    // 4. MOBILE NAVIGATION (UX Improvements)
    // =========================================================================
    
    // Fecha o menu mobile automaticamente ao clicar em um link (Single Page Nav)
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.nav-link:not(.dropdown-toggle)');
    
    if (navbarCollapse && typeof bootstrap !== 'undefined') {
        const bsCollapse = new bootstrap.Collapse(navbarCollapse, {toggle: false});
        
        navLinks.forEach(l => {
            l.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            });
        });

        // Fecha ao clicar fora
        document.addEventListener('click', (e) => {
            if (navbarCollapse.classList.contains('show') && 
                !navbarCollapse.contains(e.target) && 
                !document.querySelector('.navbar-toggler').contains(e.target)) {
                bsCollapse.hide();
            }
        });
    }


    // =========================================================================
    // 5. GLOBAL SWIPERS (Fallback)
    // =========================================================================
    /* Inicializa carrosséis padrões se não tiverem sido iniciados inline.
       Verifica a existência do elemento antes de tentar.
    */

    if (typeof Swiper !== 'undefined') {
        
        // Carrossel de Clientes (Logos)
        if (document.querySelector('.client-logo-slider')) {
            new Swiper('.client-logo-slider', {
                slidesPerView: 2,
                spaceBetween: 30,
                loop: true,
                autoplay: { delay: 3000, disableOnInteraction: false },
                breakpoints: {
                    576: { slidesPerView: 3 },
                    768: { slidesPerView: 4 },
                    1200: { slidesPerView: 5 },
                },
            });
        }

        // Carrossel de Depoimentos (Se não houver script inline na section)
        if (document.querySelector('.testimonial-swiper') && !document.querySelector('.testimonial-swiper').swiper) {
            new Swiper('.testimonial-swiper', {
                slidesPerView: 1,
                spaceBetween: 30,
                loop: true,
                pagination: { el: '.swiper-pagination', clickable: true },
                autoplay: { delay: 6000 },
                breakpoints: {
                    768: { slidesPerView: 2 },
                    1024: { slidesPerView: 3 },
                },
            });
        }
    }

    // =========================================================================
    // 6. FORM VALIDATION (Visual)
    // =========================================================================
    // Adiciona classe visual 'has-value' para inputs preenchidos (estilo Floating Label)
    const formInputs = document.querySelectorAll('.form-control, .form-control-custom, .form-select');
    
    formInputs.forEach(input => {
        // Check inicial
        if(input.value) input.classList.add('has-value');
        
        input.addEventListener('blur', () => {
            if(input.value) {
                input.classList.add('has-value');
            } else {
                input.classList.remove('has-value');
            }
        });
    });

});