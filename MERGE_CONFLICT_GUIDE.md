> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# ⚔️ Guia de Resolução de Conflitos de Merge

Este guia explica o processo para resolver **conflitos de merge** que podem ocorrer quando você tenta atualizar sua branch de feature com as mudanças mais recentes da branch `main`.

## O que é um Conflito de Merge?

Um conflito de merge acontece quando o Git não consegue juntar duas branches automaticamente. Isso ocorre quando duas pessoas (ou uma pessoa e a branch `main`) alteram a **mesma linha** no **mesmo arquivo** de maneiras diferentes.

O Git não sabe qual versão manter, então ele para o processo e pede para você, o desenvolvedor, resolver a disputa manualmente.

---

## 🚀 Fluxo de Trabalho para Resolver Conflitos

Siga estes passos para resolver um conflito de forma segura na sua branch local.

### Passo 1: Atualize sua Branch com a `main`

Na sua branch de feature (ex: `feature/novo-gerenciador-de-temas`), puxe as últimas atualizações da `main`. É neste momento que o conflito aparecerá.

```powershell
# 1. Garanta que você está na sua branch de feature
git checkout feature/novo-gerenciador-de-temas

# 2. Puxe as mudanças da 'main' para a sua branch
git pull origin main
```

Se houver um conflito, o Git irá avisar com uma mensagem como:
`CONFLICT (content): Merge conflict in arquivo_conflitante.py`

### Passo 2: Identifique e Abra os Arquivos Conflitantes

O Git irá marcar os arquivos que têm conflitos. Abra esses arquivos no seu editor de código (o VS Code é excelente para isso, pois destaca visualmente os conflitos).

Você verá marcações especiais adicionadas pelo Git:

```python
<<<<<<< HEAD
# Seu código (o que está na sua branch)
minha_variavel = "valor da feature"
=======
# Código que veio da 'main'
minha_variavel = "valor atualizado na main"
>>>>>>> commit-sha-da-main
```

-   `<<<<<<< HEAD`: O início das suas alterações.
-   `=======`: Separa as suas alterações das alterações que vieram da `main`.
-   `>>>>>>> ...`: O fim das alterações que vieram da `main`.

### Passo 3: Resolva o Conflito

Sua tarefa é editar o arquivo para deixar apenas o código final desejado e **remover completamente** as marcações `<<<<<<<`, `=======`, e `>>>>>>>`.

Você pode:
-   Manter apenas o seu código.
-   Manter apenas o código que veio da `main`.
-   Combinar os dois, criando uma nova versão.

**Exemplo de Resolução:**
```python
# Código final após a resolução manual
minha_variavel = "valor combinado da feature e da main"
```

### Passo 4: Finalize o Merge

Depois de editar e salvar todos os arquivos conflitantes, você precisa informar ao Git que os conflitos foram resolvidos.

```powershell
# 1. Adicione os arquivos resolvidos ao stage
git add .

# 2. Finalize o commit de merge (o Git geralmente cria uma mensagem padrão)
git commit

# 3. Envie as alterações resolvidas para o seu repositório remoto
git push origin feature/novo-gerenciador-de-temas
```

Pronto! O conflito foi resolvido e sua branch agora contém tanto as suas alterações quanto as atualizações mais recentes da `main`. Sua Pull Request no GitHub será atualizada automaticamente.