> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# 🛡️ Guia de Gerenciamento de Falsos Positivos no `detect-secrets`

O `detect-secrets` é uma ferramenta poderosa, mas às vezes pode identificar "falsos positivos" - trechos de código que parecem segredos, mas não são (ex: hashes de exemplo, IDs longos, etc.).

Quando o hook de pre-commit do `detect-secrets` falha, **NUNCA ignore o aviso sem investigar**. Siga este guia para gerenciar a situação de forma segura.

## O que é o `.secrets.baseline`?

O arquivo `.secrets.baseline` é o "cérebro" do `detect-secrets` no nosso projeto. Ele contém uma lista de todos os segredos (ou falsos positivos) que já foram encontrados e explicitamente marcados como "seguros" para este repositório.

Quando você faz um commit, o `detect-secrets` compara os novos segredos encontrados com a lista no `.secrets.baseline`. Se um segredo for novo e não estiver na linha de base, o commit é bloqueado.

---

## 🚀 Fluxo de Trabalho para Lidar com um Falso Positivo

Quando o `pre-commit` falhar devido a um novo segredo detectado, siga estes passos:

### Passo 1: Analise o Segredo Detectado

Primeiro, verifique o que foi detectado. **É realmente um falso positivo?**

-   **Se for um segredo real (chave de API, senha):** **NÃO continue.** Remova o segredo do código imediatamente e utilize uma variável de ambiente ou um sistema de gerenciamento de segredos.
-   **Se for um falso positivo:** Prossiga para o próximo passo.

### Passo 2: Audite a Linha de Base

A maneira correta de adicionar um falso positivo à lista de permissões é através do comando de auditoria interativa.

1.  **Execute o comando de auditoria:**
    ```powershell
    detect-secrets audit .secrets.baseline
    ```

2.  **Analise cada segredo:** A ferramenta irá apresentar cada segredo encontrado, um por um. Para cada um, você terá opções:
    -   `(s)kip`: Pular e decidir depois.
    -   `(m)ark as not a secret`: **Esta é a opção que você usará para falsos positivos.**
    -   `(r)emove`: Remover da linha de base (raramente usado).
    -   `(q)uit`: Sair da auditoria.

3.  **Marque o falso positivo:** Quando a ferramenta mostrar o falso positivo que bloqueou seu commit, pressione `m` para marcá-lo como "não é um segredo".

4.  **Salve e saia:** Continue o processo até o fim ou pressione `q` para sair e salvar as alterações.

### Passo 3: Adicione a Linha de Base Atualizada ao seu Commit

O comando de auditoria modificou o arquivo `.secrets.baseline`. Agora, você precisa adicionar essa mudança ao seu commit.

```powershell
# Adicione o arquivo de linha de base atualizado
git add .secrets.baseline

# Tente fazer o commit novamente
git commit -m "Sua mensagem de commit"
```

Desta vez, o hook de pre-commit passará, pois o `detect-secrets` agora reconhece o falso positivo como seguro.