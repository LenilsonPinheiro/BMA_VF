// JavaScript específico para o Layout Option 4

document.addEventListener('DOMContentLoaded', () => {
    // Inicializa a biblioteca de animações AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, once: true });
    }

    // Lógica do efeito de rolagem do Header
    const header = document.getElementById('mainHeader');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // Lógica de alternância de tema (Dark Mode)
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const body = document.body;
    const logo = document.querySelector('.navbar-brand img');

    function switchTheme(e) {
        if (e.target.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            if(logo) logo.style.filter = "brightness(0) invert(1)"; // Inverte a cor do logo para o modo escuro
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
            if(logo) logo.style.filter = "none"; // Remove a inversão para o modo claro
        }
    }

    if (toggleSwitch) {
        toggleSwitch.addEventListener('change', switchTheme);

        // Verifica o Local Storage na inicialização para aplicar o tema salvo
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme) {
            if (currentTheme === 'dark') {
                toggleSwitch.checked = true;
                body.classList.add('dark-mode');
                if(logo) logo.style.filter = "brightness(0) invert(1)";
            }
        }
    }
});
