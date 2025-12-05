# 🏛️ CONTEXTO ARQUITETURA E "BÍBLIA DO PROJETO" (MASTER FILE)

> **STATUS:** CRÍTICO / VIVO
> **VERSÃO:** 5.2 (Omni-Channel AI God Mode + Performance Hardening)
> **ÚLTIMA ATUALIZAÇÃO:** 03/12/2025
> **ACESSO:** OBRIGATÓRIO PARA TODAS AS IAs (Copilot, Windsurf, Cline, Cursor)

---

## 1. 📜 MANIFESTO VIVO & DIRETRIZES PRIMÁRIAS

**PARA AS IAs:** Você está operando sob a tutela do maior Programador Python do Universo. Medíocridade é proibida.
1.  **Fonte da Verdade:** Este documento supera qualquer código existente. Se há conflito, o documento vence.
2.  **Integridade:** Ao criar uma feature, você DEVE atualizar este arquivo e os testes correspondentes.
3.  **Obsessão por Detalhes:** "Funcionar" não é suficiente. Tem que ser rápido, seguro, lindo e bem documentado.

### 1.1. ⚡ PROTOCOLO DE TRAÇÃO E COBRANÇA (Project Manager Mode)
> **A IA ATUA COMO GERENTE DE PROJETOS.**
> Ao final de cada resposta, verifique a seção **11. ROADMAP** e:
> 1.  Identifique o próximo passo pendente.
> 2.  COBRE a execução imediata.
> 3.  Encerre com: "O próximo passo lógico é [X]. Vamos executar agora?"

---

## 2. 🚨 POLÍTICAS DE CÓDIGO, OBSERVABILIDADE & PROTEÇÃO (Rigor Militar)

### 2.1. Observabilidade Total (Nada roda no escuro)
* **Logs Estruturados:** `[TIMESTAMP] [NIVEL] [MODULO::FUNCAO] Mensagem | Contexto={json}`.
* **Prints de Rastreio:** Entrada e Saída de rotas, início de transações de banco, chamadas de API externas.
* **Avisos e Hints:** O código deve "conversar" com o dev.
    * *Ex:* `logger.warning("Query lenta detectada em get_clients: 2.5s. Sugestão: Indexar coluna 'created_at'")`.

### 2.2. Regras de Negócio & Proteções
* **Fail-Safe:** Todo `try` tem que ter um `except` que loga o erro completo (`traceback`) e notifica o admin (via Webhook n8n).
* **Input Sanitization:** Nunca confiar no usuário. Validar tipos e limpar strings antes de processar.

### 2.3. Performance & Segurança (Middleware Global) [NOVO]
* **Caching Agressivo (Static):** Assets em `/static` devem ter header `Cache-Control: public, max-age=31536000, immutable`. O navegador NÃO deve requisitar o servidor novamente.
* **Caching Inteligente (HTML):** Páginas dinâmicas devem ter `Cache-Control: public, max-age=3600, must-revalidate`.
* **Headers de Segurança (Hardening):** Todas as rotas devem retornar:
    * `X-Content-Type-Options: nosniff`
    * `X-Frame-Options: SAMEORIGIN`
* **SEO Técnico:** Obrigatório injetar JSON-LD Schema.org em todas as páginas via componente `_seo_meta.html`.

---

## 3. 🏗️ ARQUITETURA DE ALTA PERFORMANCE (PYTHON + REDIS + GEMINI)

O sistema é agora uma Plataforma de Gestão Completa (ERP + CRM + Social).

### 3.1. Stack Tecnológica
* **Core:** Python (Flask).
* **AI Engine:** **Google Gemini Pro** (Texto/Ideias) + **Imagen/Gemini Vision** (Geração de Imagens).
* **Cache & Sessão:** **Redis** (Obrigatório).
* **Async/Mensageria:** Celery ou RQ para agendamento de posts.
* **Integrações:** Webhooks para **n8n** (Orquestrador de postagens).

---

## 4. 🧠 DIAGNÓSTICO E TRANSIÇÃO (MULTI-TENANT)

### O Problema
Acoplamento excessivo com "Direito". Classes e Pastas hardcoded.

### A Solução
1.  **Core Genérico:** Autenticação, Uploads, Logs, Admin.
2.  **Config Driven:** Tudo que é específico (Cores, Textos, Labels) vem do `TenantConfig`.

---

## 5. 🎨 UX/UI 3.0 - O LAYOUT "X TUDO" (COM EFEITOS MODULARES)

A Home Page deve ser um **Showcase**. Além dos 4 modelos base, teremos uma camada de **Efeitos Ativáveis (Checkbox)** no Admin.

### 5.1. Biblioteca de Efeitos Modernos (CSS Variables + JS)
O Admin terá checkboxes para ativar/desativar estas camadas CSS na classe `body`:
1.  **⬜ Aurora Borealis Background:** Gradientes animados e fluidos no fundo (`filter: blur(80px)`).
2.  **⬜ Glassmorphism (Vidro):** Cards com transparência, borda sutil e desfoque de fundo.
3.  **⬜ Neumorphism (Soft UI):** Elementos que parecem extrudados da tela.
4.  **⬜ Claymorphism:** Elementos 3D fofos, flutuantes (Web3 style).
5.  **⬜ Glitch Mode:** Efeito Cyberpunk nos títulos ao passar o mouse.

### 5.2. Seções Base (Obrigatórias)
1.  **Grid Dinâmico (Bento):** Hover com Zoom + Blur + Contexto.
2.  **Carrossel Hero:** Parallax + Ken Burns Effect.
3.  **Mosaico Masonry:** Shuffle Animation + Video Preview.
4.  **Storytelling:** Scroll Reveal Timeline.

---

## 6. 📢 MÓDULO DE CAMPANHAS & SOCIAL MEDIA (NOVO)

Uma suíte completa para marketing digital dentro do sistema.

### 6.1. O "GenAI Studio" (Powered by Gemini)
Um assistente criativo onde o usuário digita: *"Crie uma campanha para Dia dos Pais focada em Divórcio Consensual"*.
* **Texto:** O Gemini gera 3 opções de Legenda + Hashtags.
* **Imagem:** O Gemini gera o prompt e chama a API de imagem para criar 3 opções visuais.

### 6.2. O "Canvas Editor" (Ferramenta de Ajuste)
Antes de postar, o usuário pode editar o resultado:
* **Features:** Crop, Resize (Stories/Feed), Overlay de Logo do Escritório, Filtros de Cor.
* **Tecnologia:** `Fabric.js` ou `Toast UI Image Editor` integrados no Admin.

### 6.3. Agendador e Publicador (Dispatcher)
* **Dashboard:** Calendário visual (Drag & Drop) para ver os posts agendados.
* **Pipeline:**
    1.  Post aprovado e agendado no Banco.
    2.  Celery acorda no horário.
    3.  Envia Payload (Img + Texto) para Webhook do **n8n**.
    4.  **n8n** distribui para Instagram, LinkedIn, Facebook e WhatsApp Business.

---

## 7. 🚀 NOVAS IDEIAS E FUNCIONALIDADES (GROWTH HACKING)

1.  **Landing Page Generator (One-Click):**
    * Clicar em "Criar LP" num serviço e o sistema gera uma página de alta conversão isolada (sem menu) focada em captura de leads.
2.  **Smart CRM (Comentários):**
    * Se alguém comenta "Eu quero" no post do Instagram, o sistema captura o @usuario e cria um Lead no CRM interno.
3.  **Área do Cliente VIP:**
    * Portal onde o cliente vê o andamento do processo/serviço com barra de progresso visual (estilo Domino's Pizza Tracker).

---

## 8. 🛠️ ADMIN MODULE 2.0 (EXPERIÊNCIA "APPLE-LIKE")

* **Layout:** Dashboard limpo, sidebar colapsável, modo Dark/Light automático.
* **Live Preview:** Ao editar uma cor ou texto, ver o resultado em tempo real (split screen).
* **Drag & Drop:** Reordenar seções da Home Page arrastando cards.

---

## 9. 🧪 QA, TESTES E PROTOCOLO MVP

### 9.1. Verificação Contínua (Zombie Tests)
* A cada nova feature, **RODAR TODOS OS TESTES**.
* Testes obsoletos devem ser removidos. Nada de "skip" permanente.

### 9.2. Seção de Pré-Testes e MVP (Sandbox)
Antes de qualquer merge na `main`:
1.  **Isolamento:** A feature funciona se eu desligar o JavaScript?
2.  **Performance:** O Lighthouse Score caiu?
3.  **Mobile:** Funciona no iPhone SE (tela pequena)?

---

## 10. 🛠️ CHECKLIST DE SUPER-AMBIENTE (30+ ANOS XP)

### Ambiente
- [ ] VS Code (1.99+)
- [ ] Python 3.10+ (Tipagem estrita ativada)
- [ ] Redis Server rodando (Local ou Docker)
- [ ] Conta Google Cloud (Gemini API Key) ativa

### Ferramentas de IA
- [ ] **Windsurf/Cursor:** Para arquitetura e refatoração.
- [ ] **Cline (Ollama/DeepSeek):** Para implementação autônoma.

---

## 11. 📅 ROADMAP PRIORIZADO (FLUXO INTELIGENTE)

A IA deve seguir esta ordem estrita:

### 🟢 Nível 1: Visual & Estrutura Base (Impacto Imediato)
1.  [ ] **Criar `layout_xtudo.html`:** Implementar HTML estático com as 4 seções base e os checkboxes de efeitos.
2.  [ ] **CSS Framework Modular:** Criar `effects.css` (Aurora, Glass, Clay).
3.  [ ] **Mockup do Admin 2.0:** Dashboard administrativo renovado.

### 🟡 Nível 2: Core, Configuração & Dados
4.  [ ] **Redis Setup:** Configurar Flask-Caching e Sessão.
5.  [ ] **Model `TenantConfig`:** Tabela para salvar preferências, API Keys do Gemini e Cores.
6.  [ ] **Refatorar Rotas:** Injetar configuração do Tenant nos templates.

### 🔴 Nível 3: Módulo de Campanhas (Social Hub)
7.  [ ] **Integração Gemini:** Criar `services/ai_service.py` para gerar texto e imagem.
8.  [ ] **Canvas Editor:** Integrar biblioteca JS de edição de imagem no Admin.
9.  [ ] **Agendador:** Criar Models `Campaign` e `Post` e configurar Celery Beat.
10. [ ] **Integração n8n:** Criar disparo de Webhooks para publicação.

### 🟣 Nível 4: Refatoração Deep Backend
11. [ ] **Renomear Models:** Migração do legado (`AreaAtuacao` -> `Service`).
12. [ ] **Tests Audit:** Cobertura 100% nas novas features.