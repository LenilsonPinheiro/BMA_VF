> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# ⚙️ Guia de Configuração do GitHub: Protegendo a Branch `main`

Este guia explica como configurar as **Branch Protection Rules** (Regras de Proteção de Branch) no GitHub. Esta configuração é **obrigatória** para garantir que o workflow de Integração Contínua (`pr_checks.yml`) possa efetivamente bloquear o merge de Pull Requests que falhem nas verificações de qualidade.

## Por que isso é Essencial?

Sem uma regra de proteção, um desenvolvedor poderia, acidentalmente ou não, fazer o merge de uma PR com testes quebrados ou documentação desatualizada, comprometendo a estabilidade da branch `main`. A regra de proteção automatiza o bloqueio, tornando o processo à prova de falhas.

---

## Passo a Passo para Configuração

Siga estes passos no seu repositório GitHub (`LenilsonPinheiro/BMA_VF`):

### 1. Acesse as Configurações do Repositório

Navegue até a página principal do seu repositório e clique na aba **"Settings"** (Configurações).

!GitHub Settings Tab

### 2. Vá para a Seção "Branches"

No menu lateral esquerdo, clique em **"Branches"**.

!Branches Menu

### 3. Adicione uma Nova Regra de Proteção

Clique no botão **"Add branch protection rule"**.

### 4. Configure a Regra para a Branch `main`

Preencha os campos da seguinte forma:

1.  **Branch name pattern (Padrão de nome da branch):** Digite `main`.

2.  **Require status checks to pass before merging (Exigir que as verificações de status passem antes do merge):**
    - Marque esta caixa.
    - Uma nova seção aparecerá abaixo. Marque a opção **"Require branches to be up to date before merging"**.

3.  **Status checks that are required (Verificações de status que são obrigatórias):**
    - Na caixa de busca, digite o nome do seu job do GitHub Actions. O nome padrão que definimos é:
      - `build-and-test`
    - Selecione-o na lista.

!Branch Protection Rule Config

### 5. Salve as Alterações

Role até o final da página e clique em **"Create"** ou **"Save changes"**.

---

## Resultado Final

Com esta regra ativa, o botão "Merge pull request" no GitHub ficará desabilitado para qualquer PR que não tenha o status check "build-and-test" com o status "successful" (verde). Isso efetivamente automatiza o bloqueio e protege sua branch `main`.