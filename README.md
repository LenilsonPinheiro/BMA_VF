# Belarmino Monteiro Advocacia - Projeto Flask

Este projeto é uma aplicação web completa desenvolvida em Flask, projetada para ser um sistema de gerenciamento de conteúdo (CMS) flexível para um escritório de advocacia, com um sistema de temas robusto e personalizável.

## Estrutura do Projeto

- **/BelarminoMonteiroAdvogado**: Contém o código-fonte principal da aplicação Flask.
  - **/static**: Arquivos estáticos (CSS, JS, imagens).
  - **/templates**: Templates Jinja2, incluindo os diferentes layouts do site.
  - `__init__.py`: Fábrica da aplicação (`create_app`). Configura DB, Rotas e **Middleware Global de Segurança/Cache**.
  - `models.py`: Define os modelos de dados do SQLAlchemy (ex: `User`, `Pagina`, `ThemeSettings`).
  - `routes/`: Contém os blueprints que organizam as rotas da aplicação (ex: `main_routes.py`, `admin_routes.py`).
- **/tests**: Contém a suíte de testes do Pytest.
  - `conftest.py`: Configuração central dos testes e fixtures.
  - **/unit**: Testes de unidade.
- `run.bat`: Script para automatizar a configuração e execução do ambiente de desenvolvimento.

## Setup e Execução

1.  **Ambiente Virtual**: Recomenda-se criar e ativar um ambiente virtual Python.
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
2.  **Instalar Dependências**: Instale todas as dependências listadas no `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
3.  **Executar a Aplicação**: Utilize o script `run.bat` para inicializar o banco de dados e iniciar o servidor de desenvolvimento.
    ```bash
    .\run.bat
    ```
    A aplicação estará disponível em `http://127.0.0.1:5000`.

## Arquitetura de Performance & Segurança (Novo v5.0)

O sistema implementa um middleware global (`after_request`) que impõe políticas estritas:

### Estratégia de Caching
1.  **Assets Estáticos (`/static`)**: 
    * `Cache-Control: public, max-age=31536000, immutable` (1 Ano).
    * Isso força o navegador a nunca requisitar o arquivo novamente até que o nome mude (cache busting via `?v=timestamp`).
2.  **Conteúdo Dinâmico (HTML)**:
    * `Cache-Control: public, max-age=3600, must-revalidate` (1 Hora).
    * Garante que o conteúdo seja fresco, mas alivia a carga do servidor em navegações frequentes.

### Cabeçalhos de Segurança (Hardening)
* `X-Content-Type-Options: nosniff`: Previne ataques de MIME sniffing.
* `X-Frame-Options: SAMEORIGIN`: Protege contra Clickjacking (impede o site de rodar em iframes de terceiros).

## Arquitetura de Temas (CSS)

O sistema de temas foi refatorado para uma arquitetura moderna, escalável e de fácil manutenção, utilizando variáveis CSS.

### Conceito

A aparência de cada layout é controlada por uma cascata de três níveis de arquivos CSS:

1.  **Base (`base.css`)**: Contém toda a estrutura, resets, e estilos de componentes que são comuns a **todos** os layouts. Este arquivo não contém cores, apenas a estrutura e o posicionamento. Ele utiliza variáveis CSS (ex: `var(--color-primary)`) para definir cores.

2.  **Temas Globais (`theme-light.css` e `theme-dark.css`)**: Estes arquivos contêm **apenas** as definições das variáveis CSS para os modos claro e escuro, respectivamente. Eles definem a paleta de cores padrão.
    ```css
    /* theme-dark.css */
    body.dark-mode {
        --color-primary: #d63030;
        --color-background: #000000;
        --color-surface: #121212;
        --color-text: #e0e0e0;
    }
    ```

3.  **Variáveis de Layout (`theme-optionX.css`)**: Cada layout possui seu próprio arquivo de variáveis (ex: `theme-option2.css`). Este arquivo é usado para:
    * Sobrescrever as variáveis de cor globais (se necessário).
    * Definir variáveis específicas para aquele layout, como famílias de fontes.
    ```css
    /* theme-option2.css */
    :root {
        --color-primary: #002F49; /* Sobrescreve a cor primária global */
        --font-heading: 'Barlow', sans-serif; /* Define uma fonte para títulos */
    }
    ```

### Como Funciona

Todos os templates de layout (`base_optionX.html`) agora carregam os arquivos CSS nesta ordem específica:
1.  `base.css`
2.  `theme-light.css`
3.  `theme-dark.css`
4.  `theme-optionX.css` (o arquivo específico do layout)

Isso garante que a estrutura base seja aplicada primeiro, seguida pelas cores globais, e finalmente, as personalizações do layout específico têm a prioridade final para sobrescrever qualquer estilo.

### Vantagens da Nova Arquitetura

-   **Manutenibilidade**: Alterações estruturais são feitas em um único arquivo (`base.css`).
-   **Consistência**: Garante que componentes compartilhados tenham a mesma aparência em todos os layouts.
-   **Escalabilidade**: Para criar um novo tema, basta criar um novo arquivo `theme-optionX.css` com as variáveis desejadas, sem precisar reescrever toda a estrutura CSS.
-   **Redução de Código**: Elimina a massiva duplicação de código que existia anteriormente.