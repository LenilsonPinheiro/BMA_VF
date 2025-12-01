> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# ⏪ Guia de Reversão de Pull Requests

Este documento descreve o processo seguro para reverter uma Pull Request (PR) que foi integrada (`merged`) à branch `main` por engano ou que introduziu um bug crítico.

## 📜 A Filosofia: `git revert` vs. `git reset`

Neste projeto, **SEMPRE** usamos `git revert`.

-   **`git revert` (Seguro ✅):** Cria um **novo commit** que desfaz as alterações do commit original. Ele não reescreve o histórico do Git, preservando a integridade e o registro de tudo o que aconteceu. É a maneira segura de corrigir erros em branches compartilhadas como a `main`.

-   **`git reset` (Perigoso ❌):** Apaga commits e reescreve o histórico do Git. Esta é uma operação destrutiva e **PROIBIDA** na branch `main`, pois pode causar perda de trabalho e inconsistências para outros desenvolvedores.

---

## 🚀 Fluxo de Trabalho para Reverter uma PR

Siga estes passos para reverter uma PR de forma segura.

### Passo 1: Identifique o Commit de Merge

1.  Vá para a aba "Pull requests" no GitHub e clique na aba "Closed".
2.  Encontre a PR que você deseja reverter.
3.  Clique no link do commit de merge. Ele terá uma mensagem como "Merge pull request #123 from...".
4.  Copie o **SHA completo** do commit de merge (o código alfanumérico longo).

    *Exemplo de SHA: `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0`*

### Passo 2: Crie uma Branch de Reversão

No seu terminal, a partir da branch `main` atualizada, crie uma nova branch para a reversão.

```powershell
# 1. Garanta que sua branch 'main' local está atualizada
git checkout main
git pull origin main

# 2. Crie uma nova branch para a reversão
git checkout -b fix/revert-pr-123
```

### Passo 3: Execute o `git revert`

Execute o comando `git revert` com o SHA do commit de merge que você copiou.

```powershell
# -m 1 informa ao Git para manter o lado da 'main' como a linha principal
git revert -m 1 <SHA_DO_COMMIT_DE_MERGE>
```

Um editor de texto abrirá para você confirmar a mensagem do commit de reversão. A mensagem padrão geralmente é suficiente. Salve e feche o editor.

### Passo 4: Envie a Branch e Abra uma Nova Pull Request

Envie a sua branch de reversão para o GitHub e abra uma nova PR.

```powershell
git push origin fix/revert-pr-123
```

No GitHub, abra uma PR da branch `fix/revert-pr-123` para a `main`.

-   **Título da PR:** `Revert: Título da PR Original`
-   **Descrição:** Explique por que a reversão é necessária (ex: "Revertendo PR #123 devido a um bug crítico na página de login.").

### Passo 5: Faça o Merge da PR de Reversão

A PR de reversão passará pelas mesmas verificações automáticas. Após a aprovação, faça o merge. A branch `main` agora estará no estado em que estava antes da PR original ser integrada.

---

### O que fazer depois?

Se a PR original continha uma funcionalidade que ainda é desejada, você pode criar uma nova branch a partir da branch original (antes da reversão) para corrigir o bug e, em seguida, abrir uma nova PR quando estiver pronta.