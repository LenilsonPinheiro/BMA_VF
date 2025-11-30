# Roteiro para o Módulo de Administração (AI Roadmap)

Este documento descreve um roteiro de desenvolvimento para aprimorar significativamente o módulo de administração do sistema Belarmino Monteiro Advogado. O objetivo é transformá-lo em uma ferramenta completa, intuitiva e poderosa, permitindo que qualquer pessoa, sem conhecimentos técnicos aprofundados, possa gerenciar e personalizar o site de forma livre e eficaz. A responsividade, a experiência do usuário (UX) e a interface do usuário (UI) serão prioridades máximas em todas as implementações.

---

**AVISO PARA A IA:** A cada etapa de implementação, VOCÊ DEVE ME QUESTIONAR QUAL PASSO SEGUIR deste roteiro. Não avance para o próximo item sem minha confirmação explícita.

---

## 1. Módulo de Gerenciamento de Conteúdo Dinâmico (Page Builder Visual)

**Descrição Geral:**
Implementação de um editor visual "drag-and-drop" (arrastar e soltar) ou baseado em blocos para a criação e edição de páginas. Esta funcionalidade permitirá total liberdade na disposição de elementos, habilitando ou desabilitando seções, ajustando estilos e personalizando o layout sem tocar no código. O sistema deve abstrair a complexidade de HTML/CSS para o usuário final, oferecendo uma experiência WYSIWYG (What You See Is What You Get).

**Funcionalidades Detalhadas:**

### 1.1. Editor de Blocos/Seções de Conteúdo
-   **Editor Visual:** Interface intuitiva que permite ao usuário adicionar, remover, reordenar e editar blocos de conteúdo diretamente na página (ou em uma representação visual próxima).
-   **Biblioteca de Blocos Pré-definidos:** Oferecer uma galeria de blocos prontos (ex: Hero Section, Seção de Serviços, Equipe, Depoimentos, CTA, Texto Simples, Imagem/Vídeo, Galeria, Formulário de Contato, Mapa, etc.) que podem ser arrastados para a página.
-   **Configuração de Bloco:** Cada bloco deve ter um painel de configuração lateral ou pop-up para ajustes específicos:
    *   **Textos:** Edição in-line de títulos, subtítulos, parágrafos.
    *   **Imagens/Mídia:** Upload de novas mídias, seleção de mídias existentes na biblioteca, ajuste de tamanho, alinhamento, alt text.
    *   **Botões/Links:** Texto do botão, URL, cor, estilo.
    *   **Listas Dinâmicas:** Seleção de quais serviços/membros da equipe/depoimentos exibir e como exibi-los.

### 1.2. Customização de Estilos por Bloco/Elemento
-   **Controles de Layout:** Margens (externa/interna), preenchimento, largura máxima, alinhamento horizontal/vertical.
-   **Controles Tipográficos:** Família da fonte, tamanho da fonte, peso da fonte, cor do texto, altura da linha, espaçamento entre letras.
-   **Controles de Cor:** Cor de fundo, cor do texto, cor de links, cores de acentuação para elementos específicos dentro do bloco (ex: ícones, bordas). Incluir seletor de cores (color picker) e suporte a variáveis de tema.
-   **Controles de Fundo:** Cor sólida, imagem de fundo (com opções de parallax, fixo, tamanho, posição), vídeo de fundo.
-   **Visibilidade:** Opção para habilitar/desabilitar um bloco específico.
-   **Responsividade:** Ajustes específicos para dispositivos móveis (ex: ordem de colunas, visibilidade de elementos).

### 1.3. Gerenciamento de Páginas
-   **Criação/Edição/Exclusão de Páginas:** Interface para gerenciar a estrutura do site, incluindo URLs (slugs), títulos, metadados.
-   **Status da Página:** Publicar/Despublicar, Rascunho.
-   **Modelos de Página:** Possibilidade de salvar layouts de blocos como modelos para reutilização em novas páginas.

## 2. Gerenciamento Centralizado de Mídia

**Descrição Geral:**
Uma biblioteca de mídia robusta para gerenciar todas as imagens, vídeos, documentos e outros ativos digitais do site.

**Funcionalidades Detalhadas:**

### 2.1. Biblioteca de Mídia
-   **Upload:** Arrastar e soltar múltiplos arquivos.
-   **Organização:** Pastas, tags, pesquisa.
-   **Otimização Automática:** Compressão de imagens, redimensionamento para diferentes tamanhos (miniaturas, médio, grande) durante o upload.
-   **Metadados:** Edição de título, descrição, alt text para SEO.
-   **Visualização:** Pré-visualização de imagens e vídeos.

## 3. SEO (Search Engine Optimization) Completo

**Descrição Geral:**
Ferramentas integradas para otimizar o site para motores de busca, garantindo que cada página possa ser encontrada e indexada eficientemente.

**Funcionalidades Detalhadas:**

### 3.1. Meta Tags por Página
-   **Título, Descrição, Palavras-chave:** Campos dedicados para cada página.
-   **Open Graph (OG):** Configurações para Facebook, Twitter (imagens, títulos, descrições para compartilhamento social).
-   **Robots Meta Tag:** Controle sobre indexação e seguimento de links (index, noindex, follow, nofollow).

### 3.2. Sitemaps e Robots.txt Dinâmicos
-   **Geração Automática:** Sitemap.xml e robots.txt dinamicamente atualizados com as páginas publicadas.
-   **Edição Manual (opcional):** Interface para edições avançadas no robots.txt.

## 4. Personalização Avançada de Tema e Design

**Descrição Geral:**
Expansão do atual editor de temas para permitir controle granular sobre a aparência global do site, além dos ajustes por bloco.

**Funcionalidades Detalhadas:**

### 4.1. Configurações Globais de Estilo
-   **Paleta de Cores Global:** Definir cores primárias, secundárias, de acentuação, texto, fundo (claro e escuro) que serão usadas como variáveis CSS em todo o site.
-   **Tipografia Global:** Definir fontes primárias e secundárias para cabeçalhos e corpo do texto, com opções de Google Fonts ou upload de fontes customizadas.
-   **Espaçamento Global:** Definições de espaçamento padrão (margens e paddings) para consistência.
-   **Bordas e Sombras:** Estilos padrão para bordas e sombras de elementos.

### 4.2. Gerenciamento de QR Code (CRUD)
-   **Upload de QR Code:** Campo de upload na seção de configurações de tema para a imagem do QR Code.
-   **Pré-visualização:** Exibição da imagem do QR Code atual.
-   **Remoção:** Botão para remover o QR Code.
-   **Integração:** Garantir que o `qr_code_path` do `ThemeSettings` seja atualizado e utilizado corretamente no frontend.

### 4.3. Custom CSS/JS
-   **Editor de Código:** Área no painel para injeção de CSS e JavaScript customizados (global ou por página).
-   **Validação:** Verificação básica de sintaxe.

## 5. Gerenciamento de Usuários e Permissões

**Descrição Geral:**
Sistema robusto para gerenciar múltiplos usuários do painel de administração com diferentes níveis de acesso e funcionalidades.

**Funcionalidades Detalhadas:**

### 5.1. CRUD de Usuários
-   **Adicionar/Editar/Remover:** Gerenciamento completo de contas de usuários administradores.
-   **Redefinição de Senha:** Funcionalidade de redefinição de senha para usuários.

### 5.2. Definição de Papéis/Permissões
-   **Papéis Pré-definidos:** Administrador (acesso total), Editor (gerenciar conteúdo), Revisor (visualizar, sugerir edições).
-   **Permissões Customizadas:** Capacidade de criar papéis com permissões granulares sobre módulos específicos (ex: permissão para editar páginas, mas não gerenciar temas ou usuários).

## 6. Dashboard e Relatórios (Insights)

**Descrição Geral:**
Um painel de controle centralizado que fornece uma visão geral do desempenho do site, status e atividades.

**Funcionalidades Detalhadas:**

### 6.1. Visão Geral
-   **Estatísticas Básicas:** Número de visitas (integração com Google Analytics/Matomo), contatos recebidos, depoimentos pendentes.
-   **Atividade Recente:** Log de ações recentes dos usuários do painel de administração.
-   **Status do Sistema:** Informações sobre o banco de dados, versão do aplicativo, etc.

## 7. Melhorias de Usabilidade e Acessibilidade (UI/UX)

**Descrição Geral:**
Garantir que o painel de administração seja não apenas funcional, mas também fácil de usar, acessível e visualmente agradável.

**Funcionalidades Detalhadas:**

### 7.1. Navegação Otimizada
-   **Menu Lateral Fixo:** Menu de navegação claro e consistente.
-   **Breadcrumbs:** Para auxiliar na navegação em telas complexas.

### 7.2. Consistência Visual
-   **Design System:** Utilizar um conjunto consistente de componentes de UI (botões, campos de formulário, tabelas, modais).
-   **Feedback Visual:** Mensagens claras de sucesso, erro, aviso.

### 7.3. Acessibilidade
-   **Conformidade:** Garantir que o painel de administração siga diretrizes de acessibilidade (WCAG).

---

Este roteiro é um documento vivo e será atualizado conforme o desenvolvimento avança e novas necessidades surgem. O foco principal é capacitar o usuário a ter controle total sobre seu conteúdo e design, mantendo a robustez e a segurança do sistema.
