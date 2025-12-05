# 🗺️ Roteiro Mestre do Módulo Administrativo (AI-Native & Enterprise)

> **VISÃO:** Transformar o Admin em um "Sistema Operacional do Escritório", onde a IA (Gemini) atua como copiloto criativo e a segurança é militar.
> **STATUS:** VIVO (Sincronizado com CONTEXTO_ARQUITETURA.md v5.2)

---

**⚠️ PROTOCOLO DE IMPLEMENTAÇÃO:** A cada etapa, consulte este documento e a `CONTEXTO_ARQUITETURA.md`. Não inicie código sem validar a estratégia de dados e segurança primeiro.

---

## 1. 🧠 Módulo de Conteúdo Inteligente (Neuro-Symbolic CMS)

**Objetivo:** Abandonar o editor de texto rico simples. O conteúdo deve ser estruturado (JSON), "Headless-ready" e co-criado por IA.

### 1.1. Editor Visual Baseado em Blocos (React/Vue Embedded ou estrito JS)
* **Estrutura de Dados:** O conteúdo **NÃO** deve ser salvo apenas como HTML. Deve ser um JSON estruturado (`[{"type": "hero", "data": {...}}, {"type": "cta", "data": {...}}]`) para permitir renderização agnóstica (Web, Mobile, Email).
* **Biblioteca de Componentes (Atomic Design):**
    * *Molecules:* Hero, Features, Testimonials, FAQ, Team Grid.
    * *Organisms:* Landing Page de Alta Conversão, Artigo de Blog Otimizado.
* **Live Preview (Split Screen):** Edição à esquerda, visualização em tempo real à direita (injetando CSS do tema).

### 1.2. GenAI Co-Pilot (Integração Gemini Pro)
* **Botão "Melhore isso pra mim":** Em qualquer campo de texto, um botão mágico que reescreve o texto com tom "Jurídico Elegante", "Persuasivo" ou "Simplificado".
* **Gerador de Seções:** "Crie uma seção de benefícios para Direito Previdenciário". O sistema gera o JSON do bloco com ícones e textos.

---

## 2. 🎨 Design System & Customização Global (Theming Engine)

**Objetivo:** Controle granular sobre a identidade visual sem tocar em CSS, alimentando o `ThemeSettings`.

### 2.1. Variáveis Globais (CSS Custom Properties)
* **Color Palette Manager:** Seletor de cores com verificação automática de contraste (WCAG 2.1 AA/AAA).
* **Typography Stack:** Upload de fontes WOFF2 e seletor de Google Fonts com *subsetting* para performance.

### 2.2. Efeitos Especiais (Layer de Modernidade)
* **Toggle de Efeitos:** Checkboxes para ativar classes no `<body>`: `effect-glassmorphism`, `effect-aurora`, `effect-neumorphism`.
* **Preview de Componentes:** Visualizar como um botão ou card fica com o efeito aplicado antes de salvar.

---

## 3. 📸 Digital Asset Management (Smart DAM)

**Objetivo:** Centralizar ativos com processamento inteligente na borda.

### 3.1. Pipeline de Upload Inteligente
* **Conversão Automática:** Todo upload de imagem é convertido para **WebP/AVIF** automaticamente.
* **Sanitização:** Remoção de metadados EXIF e renomeação segura (UUID) para evitar ataques de upload.

### 3.2. AI Vision (Gemini Vision)
* **Auto-Alt Text:** Ao fazer upload, a IA gera automaticamente a descrição `alt` para acessibilidade e SEO.
* **Auto-Tagging:** A IA analisa a imagem (ex: "Advogado", "Tribunal", "Contrato") e aplica tags para busca interna.

---

## 4. 🚀 SEO Técnico & Growth Hacking

**Objetivo:** Transformar o site em uma máquina de captação de leads orgânica.

### 4.1. SEO On-Page Automatizado
* **Schema.org Builder:** Interface visual para preencher JSON-LD (sem tocar em código) para `LegalService`, `Article`, `BreadcrumbList`.
* **Meta-Tag Generator:** A IA lê o conteúdo da página e sugere `Title` e `Meta Description` otimizados para CTR.

### 4.2. Monitoramento de Performance (Core Web Vitals)
* **Lighthouse Integrado:** Um widget no dashboard que mostra o score de performance da Home Page (via API PageSpeed Insights).

---

## 5. 🛡️ Segurança, Usuários & Auditoria (Zero Trust)

**Objetivo:** Proteger o sistema contra ameaças internas e externas.

### 5.1. RBAC (Role-Based Access Control) Granular
* **Roles:** `SuperAdmin` (Deus), `Advogado` (Editor), `Marketing` (Social), `Estagiário` (Rascunho).
* **Escopo:** Permissões definidas por rota e método HTTP.

### 5.2. Trilha de Auditoria (Audit Logs Imutáveis)
* **Registro Total:** "Quem fez o quê, quando e de onde (IP)".
    * *Ex:* `[2025-12-04 14:00] User: admin alterou Configuração: SMTP_PASSWORD`.
* **Visualização:** Tabela pesquisável de logs para compliance.

### 5.3. Autenticação Forte
* **MFA (Multi-Factor Authentication):** Integração opcional com Google Authenticator/TOTP.
* **Session Management:** Forçar logout remoto, visualizar sessões ativas (via Redis).

---

## 6. 📢 Social Hub & Marketing (O Diferencial X-Tudo)

**Objetivo:** Integrar o site às redes sociais e campanhas.

### 6.1. Agendador de Postagens
* **Calendário Visual:** Drag-and-drop de posts para Instagram/LinkedIn.
* **Integração n8n:** Webhooks disparados no horário agendado para publicar via API externa.

### 6.2. Canvas Editor (Edição Rápida)
* **Ferramenta de Crop/Overlay:** Adicionar logo do escritório em fotos antes de postar.

---

## 7. 📊 Observabilidade & Business Intelligence

**Objetivo:** Visão raio-X da saúde técnica e do negócio.

### 7.1. Dashboard Técnico
* **System Health:** Status do Redis, Workers do Celery, Espaço em Disco, Latência do Banco.
* **Error Tracking:** Últimos erros 500 capturados pelo Logger.

### 7.2. Dashboard de Negócio
* **Funil de Leads:** Contatos recebidos -> E-mails enviados -> Conversões (se houver integração CRM).
* **Top Pages:** Quais áreas de atuação estão sendo mais visitadas.

---

## 8. 🛠️ UI/UX do Painel (Apple-Like Experience)

* **Dark Mode Nativo:** O painel deve respeitar a preferência do sistema operacional.
* **Atalhos de Teclado:** `Ctrl+S` para salvar, `Ctrl+K` para busca global (Command Palette).
* **Mobile-First Admin:** Capacidade total de gerenciar o site pelo celular (PWA).