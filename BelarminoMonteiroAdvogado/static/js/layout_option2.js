// JavaScript específico para o Layout Option 2

document.addEventListener('DOMContentLoaded', function() {
    // Init Swiper (carrossel para a seção Hero)
    var swiper = new Swiper(".mySwiper", {
        loop: true,
        effect: "fade",
        fadeEffect: { crossFade: true },
        speed: 1500, // Velocidade da transição entre slides
        autoplay: { 
            delay: 5000, // Tempo de exibição de cada slide
            disableOnInteraction: false // Continua autoplay mesmo após interação do usuário
        },
        pagination: { 
            el: ".swiper-pagination", 
            clickable: true 
        },
        navigation: { 
            nextEl: ".swiper-button-next", 
            prevEl: ".swiper-button-prev" 
        },
    });

    // Navbar Scroll Effect (muda a aparência do header ao rolar a página)
    const header = document.getElementById('main-header');
    const logo = document.querySelector('.navbar-brand img');
    
    if (header && logo) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
                // Remove navbar-dark e adiciona navbar-light para mudar a cor do texto/ícones
                header.classList.remove('navbar-dark');
                header.classList.add('navbar-light');
            } else {
                header.classList.remove('scrolled');
                header.classList.remove('navbar-light');
                header.classList.add('navbar-dark'); // Retorna ao estado inicial (texto claro)
            }
        });
    }

    // Dark Mode Logic (alterna entre temas claro e escuro)
    const themeBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const body = document.body;
    
    if (themeBtn && themeIcon && body) {
        // Verifica o Local Storage na inicialização para aplicar o tema salvo
        if (localStorage.getItem('theme') === 'dark') {
            body.classList.add('dark-mode');
            themeIcon.classList.replace('bi-moon-stars-fill', 'bi-sun-fill');
        }

        // Adiciona event listener para o botão de toggle do tema
        themeBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light'); // Salva a preferência no Local Storage
            
            // Animação e troca de ícone (lua/sol)
            themeIcon.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                themeIcon.classList.toggle('bi-moon-stars-fill');
                themeIcon.classList.toggle('bi-sun-fill');
                themeIcon.style.transform = 'rotate(0deg)';
            }, 200); // Duração da animação
        });
    }
});
