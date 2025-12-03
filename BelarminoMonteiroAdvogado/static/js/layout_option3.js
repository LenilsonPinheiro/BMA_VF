// JavaScript específico para o Layout Option 3

document.addEventListener('DOMContentLoaded', () => {
    // Inicializa a biblioteca de animações AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 1000, once: true });
    }

    // Lógica do efeito de rolagem da Navbar
    const header = document.getElementById('mainHeader');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // Lógica de alternância de tema (Dark Mode)
    const themeBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const body = document.body;

    if (themeBtn && themeIcon && body) {
        // Verifica o Local Storage na inicialização para aplicar o tema salvo
        if (localStorage.getItem('theme') === 'dark') {
            body.classList.add('dark-mode');
            themeIcon.classList.replace('bi-moon', 'bi-sun'); // Altera o ícone para sol
        }

        // Adiciona event listener para o botão de toggle do tema
        themeBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light'); // Salva a preferência no Local Storage
            
            // Alterna o ícone (lua/sol)
            themeIcon.classList.toggle('bi-moon');
            themeIcon.classList.toggle('bi-sun');
        });
    }
});
