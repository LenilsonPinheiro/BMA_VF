> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# 🛡️ Protocolo de Gestão de Segredos e Falsos Positivos (SecDevOps)

> **Contexto Zero Trust:** No modelo de segurança Enterprise, tratamos credenciais hardcoded como vulnerabilidades críticas (CVSS High/Critical). O `detect-secrets` atua como nosso *Gatekeeper* de prevenção contra vazamento de dados.

Este documento define o procedimento padrão para lidar com bloqueios de commit causados pela detecção de entropia ou padrões de credenciais.

---

## 🚨 O que fazer quando o commit é bloqueado?

Quando o `pre-commit` falha com `Detect Secrets.........................................................Failed`, siga este fluxograma rigoroso:

### 1. 🛑 ANÁLISE DE VULNERABILIDADE (Triage)

Verifique o output do terminal. Ele mostrará o arquivo e a linha suspeita.

* **CENÁRIO A: É um Segredo Real (API Key, Senha, Token, Chave Privada)**
    * **AÇÃO IMEDIATA:** Aborte o commit.
    * **CORREÇÃO:**
        1.  Mova o segredo para o **Google Secret Manager** (Produção) ou `.env` (Local - e verifique se está no `.gitignore`).
        2.  Substitua o valor no código por `os.environ.get('NOME_DA_VARIAVEL')`.
    * **INCIDENTE:** Se este segredo já foi commitado anteriormente no histórico git:
        1.  Considere-o **COMPROMETIDO**.
        2.  Revogue a credencial no provedor imediatamente.
        3.  Gere uma nova chave.

* **CENÁRIO B: É um Falso Positivo (Hash de exemplo, ID público, UUID)**
    * **AÇÃO:** Prossiga para o Passo 2 (Auditoria).

---

## 2. 🕵️‍♂️ AUDITORIA DA LINHA DE BASE (Allowlisting)

O arquivo `.secrets.baseline` é a nossa "Lista de Exceções Auditada". Para adicionar um novo falso positivo, **não edite o arquivo manualmente**. Use a ferramenta interativa.

### Execução do Protocolo de Auditoria

No terminal, na raiz do projeto:

```bash
# Windows / Linux / Mac
detect-secrets audit .secrets.baseline