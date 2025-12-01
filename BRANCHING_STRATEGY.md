> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# 📖 Guia de Branching e Fluxo de Contribuição

Este documento descreve a estratégia de branches e o fluxo de trabalho obrigatório para fazer qualquer alteração de código neste projeto. O objetivo é garantir a estabilidade da branch `main` e a qualidade de todo código novo.

## 📜 A Regra de Ouro

**Ninguém, sob nenhuma circunstância, deve fazer `commit` diretamente na branch `main`.** Todas as alterações devem ser feitas em uma branch separada e integradas via Pull Request (PR).

---

## 🌳 Modelo de Branching

Usamos um modelo simples baseado em "Feature Branches".

- **`main`**: Esta é a branch principal. Ela deve ser **sempre estável** e pronta para deploy. O código aqui já foi testado e revisado.
- **`feature/<nome-da-feature>`**: Para novas funcionalidades. Ex: `feature/page-builder`, `feature/seo-improvements`.
- **`fix/<nome-da-correcao>`**: Para correções de bugs. Ex: `fix/login-redirect-bug`, `fix/image-upload-error`.

---

## 🚀 Fluxo de Trabalho Passo a Passo (Do Início ao Fim)

Siga estes passos para qualquer nova funcionalidade ou correção de bug.

### Passo 1: Crie sua Branch

Antes de escrever qualquer código, crie uma nova branch a partir da versão mais recente da `main`.

```powershell
# 1. Garanta que sua branch 'main' local está atualizada
git checkout main
git pull origin main

# 2. Crie sua nova branch com um nome descritivo
git checkout -b feature/novo-gerenciador-de-temas
# ou para um bug
git checkout -b fix/erro-no-formulario-de-contato
```

### Passo 2: Desenvolva e Faça Commits

Faça suas alterações na nova branch. Use o `run.ps1` para rodar o ambiente de desenvolvimento. Faça commits pequenos e atômicos com mensagens claras.

```powershell
# Inicie o ambiente de desenvolvimento
.\run.ps1

# Após fazer suas alterações...
git add .
git commit -m "feat: Adiciona editor de cores ao painel de temas"
# ou
git commit -m "fix: Corrige validação de e-mail no formulário de contato"
```

### Passo 3: Verificações Locais (Obrigatório)

Antes de enviar seu código, execute as verificações de qualidade locais. O hook de pre-commit fará isso automaticamente a cada `git commit`, mas é uma boa prática rodar manualmente também.

```powershell
# 1. Verifique a sincronia do ecossistema (código vs. documentação)
python verify_ecosystem.py

# 2. Execute a suíte completa de testes
python run_all_tests.py
```
**Se qualquer um desses scripts falhar, corrija os problemas antes de continuar.**

### Passo 4: Envie sua Branch e Abra uma Pull Request (PR)

Envie sua branch para o repositório remoto e abra uma Pull Request para a branch `main`.

```powershell
git push origin feature/novo-gerenciador-de-temas
```

Acesse o GitHub e clique em "Compare & pull request". Preencha o template da PR (`PULL_REQUEST_TEMPLATE.md`) com detalhes sobre suas mudanças.

### Passo 5: Revisão Automática e Manual

1.  **Revisão Automática (GitHub Actions):** Assim que a PR for aberta, nosso sistema de Integração Contínua (CI) irá:
    - Executar todos os testes (`run_all_tests.py`).
    - Verificar a sincronia do ecossistema (`verify_ecosystem.py`).
    - Postar um comentário na PR com os resultados.
    - **O merge será bloqueado se qualquer verificação falhar.**

2.  **Revisão Manual:** Um outro desenvolvedor (ou o líder do projeto) irá revisar seu código para garantir que ele segue os padrões de qualidade e arquitetura.

### Passo 6: Merge

Após a aprovação das revisões automática e manual, a Pull Request poderá ser "squashed and merged" na branch `main`. Isso mantém o histórico da `main` limpo e organizado.

Parabéns, sua contribuição agora faz parte da base de código principal!