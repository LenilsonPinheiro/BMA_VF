// JavaScript específico para o Layout Option 1

document.addEventListener('DOMContentLoaded', () => {
    // Navbar Scroll Effect Logic (Layout Option 1)
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
                // Remove navbar-dark e adiciona navbar-light para mudar a cor do texto/ícones
                navbar.classList.remove('navbar-dark'); 
                navbar.classList.add('navbar-light');
            } else {
                navbar.classList.remove('scrolled');
                navbar.classList.remove('navbar-light');
                navbar.classList.add('navbar-dark'); // Retorna ao estado inicial (texto claro)
            }
        });
    }
});
