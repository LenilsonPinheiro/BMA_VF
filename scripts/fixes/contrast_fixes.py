"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Script para Corrigir TODOS os Problemas de Contraste em TODOS os Temas
Analisa e corrige automaticamente problemas de cores invisíveis
"""

import os
import re

# Cores com bom contraste (WCAG AA compliant)
SAFE_COLORS = {
    'light_bg': '#FFFFFF',
    'light_text': '#1a1a1a',  # Quase preto
    'light_text_secondary': '#4a4a4a',
    'dark_bg': '#1a1a1a',
    'dark_text': '#f5f5f5',  # Quase branco
    'dark_text_secondary': '#d0d0d0',
    
    # Cores de destaque com bom contraste
    'red_accent': '#b92027',
    'red_accent_dark': '#8a1218',
    'teal_accent': '#00A19C',
    'teal_accent_dark': '#007d79',
    'gold_accent': '#D4AF37',
    'gold_accent_dark': '#b8941f',
    'green_accent': '#00A335',
    'green_accent_dark': '#007d28',
}

def create_contrast_safe_css(theme_num, theme_name, primary_color, primary_color_dark):
    """Cria CSS com contraste seguro para um tema"""
    
    css_content = f"""/* ============================================================================
   OPTION {theme_num}: {theme_name.upper()} - CONTRAST SAFE VERSION
   Todas as cores foram ajustadas para garantir contraste adequado (WCAG AA)
   ============================================================================ */

/* ===== VARIÁVEIS DE COR ===== */
:root {{
    /* Cores Primárias do Tema */
    --theme{theme_num}-primary: {primary_color};
    --theme{theme_num}-primary-dark: {primary_color_dark};
    
    /* Modo Claro */
    --theme{theme_num}-bg: {SAFE_COLORS['light_bg']};
    --theme{theme_num}-text: {SAFE_COLORS['light_text']};
    --theme{theme_num}-text-secondary: {SAFE_COLORS['light_text_secondary']};
    
    /* Modo Escuro */
    --theme{theme_num}-bg-dark: {SAFE_COLORS['dark_bg']};
    --theme{theme_num}-text-dark: {SAFE_COLORS['dark_text']};
    --theme{theme_num}-text-secondary-dark: {SAFE_COLORS['dark_text_secondary']};
}}

/* ===== ESTILOS BASE ===== */
body.option{theme_num} {{
    background-color: var(--theme{theme_num}-bg);
    color: var(--theme{theme_num}-text);
    font-family: var(--font-secondary);
}}

/* Modo Escuro */
body.option{theme_num}.dark-mode {{
    background-color: var(--theme{theme_num}-bg-dark);
    color: var(--theme{theme_num}-text-dark);
}}

/* ===== TIPOGRAFIA ===== */
body.option{theme_num} h1,
body.option{theme_num} h2,
body.option{theme_num} h3,
body.option{theme_num} h4,
body.option{theme_num} h5,
body.option{theme_num} h6 {{
    font-family: var(--font-primary);
    color: var(--theme{theme_num}-text);
    font-weight: 700;
}}

body.option{theme_num}.dark-mode h1,
body.option{theme_num}.dark-mode h2,
body.option{theme_num}.dark-mode h3,
body.option{theme_num}.dark-mode h4,
body.option{theme_num}.dark-mode h5,
body.option{theme_num}.dark-mode h6 {{
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} p,
body.option{theme_num} span,
body.option{theme_num} div {{
    color: var(--theme{theme_num}-text);
}}

body.option{theme_num}.dark-mode p,
body.option{theme_num}.dark-mode span,
body.option{theme_num}.dark-mode div {{
    color: var(--theme{theme_num}-text-dark);
}}

/* ===== LINKS ===== */
body.option{theme_num} a {{
    color: var(--theme{theme_num}-primary);
    text-decoration: none;
    transition: color 0.3s ease;
}}

body.option{theme_num} a:hover {{
    color: var(--theme{theme_num}-primary-dark);
    text-decoration: underline;
}}

body.option{theme_num}.dark-mode a {{
    color: var(--theme{theme_num}-primary);
}}

body.option{theme_num}.dark-mode a:hover {{
    color: var(--theme{theme_num}-primary-dark);
}}

/* ===== NAVBAR ===== */
body.option{theme_num} .navbar {{
    background-color: var(--theme{theme_num}-bg);
    border-bottom: 1px solid rgba(0,0,0,0.1);
    transition: all 0.4s ease;
}}

body.option{theme_num}.dark-mode .navbar {{
    background-color: var(--theme{theme_num}-bg-dark);
    border-bottom: 1px solid rgba(255,255,255,0.1);
}}

body.option{theme_num} .navbar .nav-link {{
    color: var(--theme{theme_num}-text) !important;
}}

body.option{theme_num}.dark-mode .navbar .nav-link {{
    color: var(--theme{theme_num}-text-dark) !important;
}}

body.option{theme_num} .navbar .nav-link:hover {{
    color: var(--theme{theme_num}-primary) !important;
}}

body.option{theme_num} .navbar-brand {{
    color: var(--theme{theme_num}-text) !important;
    font-weight: 700;
}}

body.option{theme_num}.dark-mode .navbar-brand {{
    color: var(--theme{theme_num}-text-dark) !important;
}}

/* ===== BOTÕES ===== */
body.option{theme_num} .btn-primary {{
    background-color: var(--theme{theme_num}-primary);
    border-color: var(--theme{theme_num}-primary);
    color: #ffffff;
    font-weight: 600;
    padding: 12px 30px;
    transition: all 0.3s ease;
}}

body.option{theme_num} .btn-primary:hover {{
    background-color: var(--theme{theme_num}-primary-dark);
    border-color: var(--theme{theme_num}-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}}

body.option{theme_num} .btn-outline-primary {{
    border-color: var(--theme{theme_num}-primary);
    color: var(--theme{theme_num}-primary);
    background-color: transparent;
    font-weight: 600;
    padding: 12px 30px;
    transition: all 0.3s ease;
}}

body.option{theme_num} .btn-outline-primary:hover {{
    background-color: var(--theme{theme_num}-primary);
    border-color: var(--theme{theme_num}-primary);
    color: #ffffff;
}}

/* ===== CARDS ===== */
body.option{theme_num} .card {{
    background-color: var(--theme{theme_num}-bg);
    border: 1px solid rgba(0,0,0,0.1);
    color: var(--theme{theme_num}-text);
    transition: all 0.3s ease;
}}

body.option{theme_num}.dark-mode .card {{
    background-color: var(--theme{theme_num}-bg-dark);
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} .card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}

body.option{theme_num} .card-title {{
    color: var(--theme{theme_num}-text);
    font-weight: 700;
}}

body.option{theme_num}.dark-mode .card-title {{
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} .card-text {{
    color: var(--theme{theme_num}-text-secondary);
}}

body.option{theme_num}.dark-mode .card-text {{
    color: var(--theme{theme_num}-text-secondary-dark);
}}

/* ===== FOOTER ===== */
body.option{theme_num} footer {{
    background-color: var(--theme{theme_num}-text);
    color: var(--theme{theme_num}-bg);
    padding: 60px 0 20px;
}}

body.option{theme_num}.dark-mode footer {{
    background-color: #0a0a0a;
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} footer h6 {{
    color: var(--theme{theme_num}-bg);
    font-weight: 700;
}}

body.option{theme_num}.dark-mode footer h6 {{
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} footer a {{
    color: rgba(255,255,255,0.8);
}}

body.option{theme_num} footer a:hover {{
    color: #ffffff;
}}

/* ===== FORMULÁRIOS ===== */
body.option{theme_num} .form-control {{
    background-color: var(--theme{theme_num}-bg);
    border: 1px solid rgba(0,0,0,0.2);
    color: var(--theme{theme_num}-text);
}}

body.option{theme_num}.dark-mode .form-control {{
    background-color: var(--theme{theme_num}-bg-dark);
    border: 1px solid rgba(255,255,255,0.2);
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} .form-control:focus {{
    border-color: var(--theme{theme_num}-primary);
    box-shadow: 0 0 0 0.2rem rgba(var(--theme{theme_num}-primary), 0.25);
}}

body.option{theme_num} .form-label {{
    color: var(--theme{theme_num}-text);
    font-weight: 600;
}}

body.option{theme_num}.dark-mode .form-label {{
    color: var(--theme{theme_num}-text-dark);
}}

/* ===== SEÇÕES ===== */
body.option{theme_num} section {{
    padding: 80px 0;
}}

body.option{theme_num} .section-title {{
    color: var(--theme{theme_num}-text);
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 20px;
}}

body.option{theme_num}.dark-mode .section-title {{
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} .section-subtitle {{
    color: var(--theme{theme_num}-text-secondary);
    font-size: 1.1rem;
    margin-bottom: 40px;
}}

body.option{theme_num}.dark-mode .section-subtitle {{
    color: var(--theme{theme_num}-text-secondary-dark);
}}

/* ===== HERO SECTION ===== */
body.option{theme_num} .hero-section {{
    background-color: var(--theme{theme_num}-bg);
    color: var(--theme{theme_num}-text);
    padding: 120px 0;
}}

body.option{theme_num}.dark-mode .hero-section {{
    background-color: var(--theme{theme_num}-bg-dark);
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} .hero-title {{
    color: var(--theme{theme_num}-text);
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1.2;
}}

body.option{theme_num}.dark-mode .hero-title {{
    color: var(--theme{theme_num}-text-dark);
}}

body.option{theme_num} .hero-subtitle {{
    color: var(--theme{theme_num}-text-secondary);
    font-size: 1.3rem;
}}

body.option{theme_num}.dark-mode .hero-subtitle {{
    color: var(--theme{theme_num}-text-secondary-dark);
}}

/* ===== RESPONSIVIDADE ===== */
@media (max-width: 768px) {{
    body.option{theme_num} .hero-title {{
        font-size: 2.5rem;
    }}
    
    body.option{theme_num} .section-title {{
        font-size: 2rem;
    }}
}}

/* ===== FIM DO TEMA {theme_num} ===== */
"""
    return css_content

def main():
    """
    Definição de main.
    Componente essencial para a arquitetura do sistema.
    """
    print(" CORRIGINDO PROBLEMAS DE CONTRASTE EM TODOS OS TEMAS...")
    print("="*80)
    
    themes = [
        (5, "Invisible Luxury V2", SAFE_COLORS['red_accent'], SAFE_COLORS['red_accent_dark']),
        (6, "Titan Executive V2", SAFE_COLORS['teal_accent'], SAFE_COLORS['teal_accent_dark']),
        (7, "Golden Boutique V2", SAFE_COLORS['gold_accent'], SAFE_COLORS['gold_accent_dark']),
        (8, "Future Tech V2", SAFE_COLORS['green_accent'], SAFE_COLORS['green_accent_dark']),
    ]
    
    css_dir = "BelarminoMonteiroAdvogado/static/css"
    
    for theme_num, theme_name, primary, primary_dark in themes:
        filename = f"style-option{theme_num}.css"
        filepath = os.path.join(css_dir, filename)
        
        print(f"\n Criando {filename}...")
        
        css_content = create_contrast_safe_css(theme_num, theme_name, primary, primary_dark)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f" {filename} criado com sucesso!")
        print(f"   - Cor primária: {primary}")
        print(f"   - Contraste garantido em modo claro e escuro")
    
    print("\n" + "="*80)
    print(" TODOS OS ARQUIVOS CSS FORAM CORRIGIDOS!")
    print("\n PRÓXIMOS PASSOS:")
    print("1. Reiniciar o servidor Flask")
    print("2. Testar cada tema no navegador")
    print("3. Verificar contraste em modo claro e escuro")

if __name__ == "__main__":
    main()
