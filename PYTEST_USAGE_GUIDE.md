> [!IMPORTANT]
> **AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.) E DESENVOLVEDORES**
>
> QUALQUER ALTERAÇÃO NESTE PROJETO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA INTEIRO FOR ATUALIZADO. Esta é a regra mais importante deste projeto. A manutenção a longo prazo depende da aderência estrita a este princípio. **NÃO FAÇA MUDANÇAS ISOLADAS.**

---

# 🧪 Guia de Uso do `pytest`: Executando Testes Específicos

Enquanto o `run_all_tests.py` é perfeito para a validação completa antes de um deploy, durante o desenvolvimento é muito mais eficiente executar apenas os testes relevantes para a funcionalidade que você está trabalhando.

O `pytest` oferece uma sintaxe poderosa para selecionar exatamente quais testes rodar.

## Pré-requisitos

Certifique-se de que seu ambiente virtual (`venv`) está ativado:
```powershell
.\venv\Scripts\Activate.ps1
```

---

## 🚀 Comandos Essenciais

### 1. Executar todos os testes em um único arquivo

Para rodar todos os testes contidos em `test_admin_routes.py`:
```powershell
pytest test_admin_routes.py
```

### 2. Executar uma única classe de testes dentro de um arquivo

Se o seu arquivo de teste tem classes, você pode rodar todos os testes de uma classe específica.
```powershell
# Sintaxe: pytest [arquivo]::[NomeDaClasse]
pytest test_app.py::TestPreDeploy
```

### 3. Executar um único teste (função)

Este é o comando mais útil para depuração. Para rodar apenas a função `test_login_success` dentro de `test_app.py`:
```powershell
# Sintaxe: pytest [arquivo]::[nome_da_funcao]
pytest test_app.py::test_login_success
```

### 4. Executar testes por palavra-chave ou marcador

Use a flag `-k` para rodar testes cujos nomes contenham uma determinada string.
```powershell
# Executa todos os testes que contenham "login" no nome
pytest -k "login"

# Executa todos os testes em `test_admin_routes.py` que contenham "dashboard"
pytest test_admin_routes.py -k "dashboard"
```

### Dica de Produtividade

Adicione a flag `-v` (verbose) para obter uma saída mais detalhada sobre quais testes estão passando ou falhando.
```powershell
pytest -v test_app.py::test_login_success
```