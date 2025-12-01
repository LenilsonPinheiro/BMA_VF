> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO.
>
> Isto significa:
> 1.  **DOCUMENTAÇÃO:** Todos os READMEs, guias (`.md`) e manuais devem ser atualizados para refletir a nova lógica.
> 2.  **COMENTÁRIOS NO CÓDIGO:** O código alterado e relacionado deve ter comentários claros, úteis e que expliquem o "porquê" da mudança.
> 3.  **SCRIPTS DE DIAGNÓSTICO:** Scripts como `diagnostico.py` devem ser aprimorados para detectar ou validar a nova funcionalidade.
>
> Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# Belarmino Monteiro Advogado - Sistema Web

Este é o repositório principal para o sistema web do escritório de advocacia Belarmino Monteiro. O sistema é construído utilizando Flask, SQLAlchemy, Flask-Login, Flask-Migrate e Bootstrap, oferecendo um painel de administração para gerenciamento de conteúdo dinâmico.

## 🚀 Quick Start

### Desenvolvimento Local
```powershell
# Startup (tudo automatizado)
.\run.ps1

# Reset do banco de dados
.\run.ps1 clean

# Aplicação estará em: http://127.0.0.1:5000
```

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin`

### Verificações Automáticas de Qualidade

Este projeto usa duas ferramentas para garantir a qualidade do código automaticamente:

1.  **Pre-commit Hooks:** Antes de cada commit, os seguintes hooks são executados:
    - **`black`**: Formata automaticamente todo o código Python para um padrão consistente.
    - **`verify_ecosystem.py`**: Garante que a documentação (`.md`) foi atualizada junto com o código.
    - **`detect-secrets`**: Impede que segredos (chaves de API, senhas) sejam commitados. (Instalado via `requirements.txt`)
    - **Setup (uma única vez):**
      ```powershell
      pip install pre-commit
      pre-commit install
      ```
2.  **GitHub Actions (CI/CD):** A cada Pull Request para a branch `main`, uma verificação automática é executada para:
    - Rodar todos os testes (`run_all_tests.py`).
    - Verificar a formatação do código (`black --check`).
    - Verificar vazamento de segredos (`detect-secrets`).
    - **Se qualquer verificação falhar, o workflow falha e o merge da PR é bloqueado.**

> **Configuração Obrigatória no GitHub:** Para que o bloqueio funcione, você deve configurar uma **Branch Protection Rule** para a branch `main`, exigindo que o status check "Verificação de Qualidade e Ecossistema da PR" passe antes do merge.
> Para um guia passo a passo, consulte **`GITHUB_SETUP_GUIDE.md`**.

### 🤝 Fluxo de Contribuição

Todas as alterações neste projeto devem seguir um fluxo estrito para garantir a qualidade e a estabilidade da branch `main`.

1.  Crie uma `feature-branch` ou `fix-branch` a partir da `main`.
2.  Faça suas alterações e commits.
3.  Abra uma **Pull Request** para a `main`.
4.  Aguarde a aprovação das verificações automáticas e da revisão manual.

Para um guia detalhado, consulte **`BRANCHING_STRATEGY.md`**.


### Antes de Fazer Deploy
```powershell
# Executar todos os testes
python run_all_tests.py

# Fazer backup do BD
python backup_db.py

# Deploy automático
python deploy_production_complete.py
```

---

## 📖 Documentação Completa

### Para Desenvolvedores & AI Agents
- **`.github/copilot-instructions.md`** - Guia técnico completo para AI agents
  - Arquitetura de aplicação (blueprints, modelos, templates)
  - Todos os 40+ scripts Python com relacionamentos e dependências
  - Padrões de código e fluxos de automação
  - Troubleshooting e debugging

### Para Automação & CI/CD
- **`SCRIPTS_AUTOMATION_GUIDE.md`** - Guia de automações com fluxos completos
  - 5 automation flows (Dev → Commit → Deploy → Recover → Reset)
  - Cada fluxo com comandos exatos, logs esperados, timing e dependências
  - Matriz de dependência entre scripts
  - Checklists de segurança pré-deploy e pós-deploy
  - Troubleshooting decision tree

### Para Governança e Processos
- **`BRANCHING_STRATEGY.md`** - Guia obrigatório sobre como criar branches e fazer Pull Requests.
- **`GITHUB_SETUP_GUIDE.md`** - Como configurar as regras de proteção de branch no GitHub.
- **`REVERT_GUIDE.md`** - Guia de segurança para reverter um merge feito por engano.
- **`MERGE_CONFLICT_GUIDE.md`** - Guia passo a passo para resolver conflitos de merge.
- **`FALSE_POSITIVES_GUIDE.md`** - Como gerenciar falsos positivos no `detect-secrets`.
- **`MERGE_CONFLICT_GUIDE.md`** - Guia passo a passo para resolver conflitos de merge.

### Para Administração
- **`admin_module_roadmap.md`** - Roadmap de melhorias do painel admin

---

## Estrutura do Projeto

-   `BelarminoMonteiroAdvogado/`: Contém a aplicação Flask principal, incluindo modelos de banco de dados, rotas, formulários e templates.
-   `migrations/`: Contém os scripts de migração do banco de dados gerenciados pelo Alembic/Flask-Migrate.
-   `instance/`: Armazena dados específicos da instância, como o banco de dados SQLite (`site.db`) e backups.
-   `venv/`: Ambiente virtual Python.
-   `run.ps1`: Script PowerShell para configurar o ambiente de desenvolvimento, gerenciar o banco de dados e iniciar a aplicação.
-   `auto_fix.py`: Script auxiliar para automatizar o setup do banco de dados e migrações.
-   `admin_module_roadmap.md`: Documento detalhado com o roteiro de desenvolvimento para o módulo de administração.

## Configuração e Execução (Desenvolvimento)

Para configurar e executar o projeto em ambiente de desenvolvimento, utilize o script `run.ps1`:

1.  **Abra o PowerShell** no diretório raiz do projeto (`d:\PROJETOS PYTHON 2025\BMA_VF`).
2.  **Execute o script:**
    ```powershell
    .\run.ps1
    ```
    Este comando irá:
    -   Ativar o ambiente virtual.
    -   Instalar/atualizar as dependências Python (se `requirements.txt` existir).
    -   Garantir a existência da pasta `instance`.
    -   Executar o `auto_fix.py` para gerenciar as migrações do banco de dados.
    -   Executar o comando `flask init-db` para popular dados essenciais e criar o usuário administrador padrão.
    -   Iniciar o servidor de desenvolvimento Flask em `http://127.0.0.1:5000`.

### Resetando o Banco de Dados (Opção `clean`)

Se você precisar resetar completamente o banco de dados e as migrações (por exemplo, para iniciar do zero ou resolver problemas de inconsistência), use o argumento `clean`:

```powershell
.\run.ps1 clean
```
Este comando removerá o `site.db` existente e a pasta `migrations/` antes de recriar tudo.

## Credenciais Padrão do Administrador

Após a execução do `flask init-db`, um usuário administrador padrão é criado:

-   **Usuário:** `admin`
-   **Senha:** `admin`

Recomenda-se alterar a senha após o primeiro login.

---

## 🔄 Fluxos de Automação Principais

Para workflow completo com exemplos de logs esperados, veja **`SCRIPTS_AUTOMATION_GUIDE.md`**.

### Desenvolvimento Local
```
run.ps1 → auto_fix.py (backup + migrations) → flask init-db → dev server
```
**Duração:** 2-5 minutos

### Antes de Commit
```
pytest test_app.py → run_all_tests.py → limpar_projeto.py → git commit
```
**Duração:** 2-3 minutos

### Deploy para Produção
```
backup_db.py → run_all_tests.py → otimizar_imagens.py → deploy_production_complete.py → validar_deploy.py
```
**Duração:** 15-20 minutos

### Recovery (BD Corrompido)
```
backup_db.py → check_db.py → repair_alembic.py → run.ps1 → verify
```
**Duração:** 5-10 minutos

### Reset Completo
```
backup_db.py --remove-migrations → limpeza_total_venv.py → run.ps1 clean → diagnostico.py
```
**Duração:** 10-15 minutos

---

## 🐛 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| App não inicia | `python check_db.py` → `python auto_fix.py` |
| Erro "Fatal error in launcher" ou "Acesso negado" | Seu ambiente virtual (`venv`) está corrompido. Feche todos os terminais/editores, delete a pasta `venv` manualmente e execute `.\run.ps1` para recriá-la do zero. (Detect-secrets e Black serão instalados automaticamente) |
| Testes falhando | `python run_all_tests.py` (veja output detalhado) |
| BD corrompido | `python backup_db.py` → `python repair_alembic.py` |
| Login não funciona | `python create_admin.py` (criar novo admin) |
| Imagens não otimizadas | `python otimizar_imagens.py` |

Para troubleshooting completo, veja **[`SCRIPTS_AUTOMATION_GUIDE.md` - Decision Tree](SCRIPTS_AUTOMATION_GUIDE.md)**.

---

## 📊 Scripts Python Disponíveis

### Core (sempre usados)
- `run.ps1` - Startup da aplicação (use sempre!)
- `auto_fix.py` - Manutenção do BD e migrações (automático via run.ps1)
- `create_admin.py` - Criar novo admin

### Testing & Validation
- `run_all_tests.py` - Master test runner (descobre e executa todos os testes `test_*.py`)
- `test_*.py` - Testes individuais (descobertos por `run_all_tests.py`)
- `verify_ecosystem.py` - Verifica se a documentação está sincronizada com o código
- **`PYTEST_USAGE_GUIDE.md`** - Como executar testes específicos para acelerar o desenvolvimento.

### Deployment & Operations
- `backup_db.py` - Backup BD (execute SEMPRE antes de mudanças!)
- `deploy_production_complete.py` - Deploy full stack
- `validar_deploy.py` - Validar depois de deploy

### Database & Repair
- `check_db.py` - Validar integridade do BD
- `repair_alembic.py` - Reparar migrações quebradas

### Optimization & Maintenance
- `otimizar_imagens.py` - Converter imagens para WebP
- `limpar_projeto.py` - Limpeza de temporários
- `diagnostico.py` - Diagnóstico do sistema

Para referência completa de cada script, veja **[`.github/copilot-instructions.md` - Per-Script Detailed Reference](.github/copilot-instructions.md)**.

---

## 🔧 Configurações Importantes

### Variáveis de Ambiente
```
FLASK_APP=BelarminoMonteiroAdvogado
FLASK_ENV=development (dev) ou production (prod)
DATABASE_URL=sqlite:///instance/site.db (dev) ou postgres://... (prod)
SECRET_KEY=generated-secret-key (production)
```

### Pastas Críticas
```
instance/          → Dados da instância (BD, backups)
instance/backups/  → Backups automáticos de BD
migrations/        → Alembic migration scripts
static/images/     → Assets estáticos
static/images/uploads/  → User-uploaded content (otimizado para WebP)
```

---

## 🌐 Visão Geral do Módulo de Administração

O painel de administração (acessível via `/admin`) permite gerenciar diversos aspectos do site, incluindo:

-   Conteúdo de páginas e seções (Home, Sobre Nós, Contato, etc.).
-   Áreas de Atuação.
-   Membros da Equipe.
-   Depoimentos de Clientes.
-   Configurações de Tema (cores, layout).
-   Configurações de SEO.

Para um roteiro detalhado de futuras melhorias e funcionalidades para o módulo de administração, consulte o arquivo `admin_module_roadmap.md`.

---

## 🤖 Para AI Agents

Este repositório inclui guias completos para AI coding agents:

1. **[`.github/copilot-instructions.md`](.github/copilot-instructions.md)** - Leia isto PRIMEIRO
   - Arquitetura completa do projeto
   - Todos os 40+ scripts com relacionamentos
   - Data models e query patterns
   - Common gotchas e anti-patterns
   - Decision trees para troubleshooting

2. **[`SCRIPTS_AUTOMATION_GUIDE.md`](SCRIPTS_AUTOMATION_GUIDE.md)** - Para operações de automação
   - 5 automation flows com sequência exata de comandos
   - Expected logs e timing para cada passo
   - Security checklists e dependency matrix
   - Troubleshooting guide

---

## Contribuição

Contribuições são bem-vindas. Por favor, siga as diretrizes de codificação existentes e crie pull requests para novas funcionalidades ou correções de bugs.

Ao contribuir:
1. Revise **[`.github/copilot-instructions.md`](.github/copilot-instructions.md)** para entender a arquitetura
2. Siga os padrões de banco de dados (ConteudoGeral query pattern, migrations, etc.)
3. Execute `python run_all_tests.py` antes de fazer commit
4. Use `python backup_db.py` antes de operações críticas

## Licença

[Inserir informações de Licença aqui]
