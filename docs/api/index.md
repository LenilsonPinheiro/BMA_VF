# Documentação da API - Belarmino Monteiro Advogados

> **Nota:** Esta documentação reflete as rotas definidas nos Blueprints da aplicação Flask (v5.2).

## 1. Rotas Públicas (Main Blueprint)
*Prefixo:* `/`

### Navegação & Conteúdo
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | Página Inicial (Home). Renderiza dinamicamente baseada no tema. |
| `GET` | `/xtudo` | Showcase do Framework V5 (Layout X-Tudo). |
| `GET` | `/areas-de-atuacao` | Lista todas as áreas de atuação (Serviços). |
| `GET` | `/politica-de-privacidade` | Página de termos e privacidade. |
| `GET` | `/<slug>` | **Rota Dinâmica (Catch-all)**. Renderiza páginas do banco (ex: `/sobre-nos`, `/direito-civil`). |

### Funcionalidades
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/search?q=termo` | Busca global no site (Áreas e Setores). |
| `GET`, `POST` | `/contato` | Exibe e processa o formulário de contato (Envia E-mail). |
| `GET`, `POST` | `/depoimento/submit/<token>` | Formulário seguro para clientes enviarem depoimentos. |

### SEO & Sistema
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/sitemap.xml` | Mapa do site XML dinâmico para indexação. |
| `GET` | `/robots.txt` | Diretrizes para crawlers. |
| `GET` | `/service-worker.js` | Script para suporte PWA. |

---

## 2. Rotas de Autenticação (Auth Blueprint)
*Prefixo:* `/auth` (Definido em `__init__.py`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET`, `POST` | `/auth/login` | Tela de login e processamento de credenciais. |
| `GET` | `/auth/logout` | Encerra a sessão do usuário. |

---

## 3. Rotas Administrativas (Admin Blueprint)
*Prefixo:* `/admin` (Requer Login `@login_required`)

### Dashboard & Gestão
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/admin/` | Dashboard principal (Visão geral). |
| `GET` | `/admin/configuracoes` | Configurações gerais do site (Cores, SEO, Contato). |

### Gerenciamento de Conteúdo
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET`, `POST` | `/admin/paginas` | Listagem e criação de páginas. |
| `GET`, `POST` | `/admin/areas-atuacao` | CRUD de Áreas de Atuação. |
| `GET`, `POST` | `/admin/membros` | Gestão da Equipe. |
| `GET`, `POST` | `/admin/depoimentos` | Moderação de depoimentos. |