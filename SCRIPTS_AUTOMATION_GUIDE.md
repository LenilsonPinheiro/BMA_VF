# 📚 Guia Completo de Automações e Scripts Python - BMA_VF

## 🎯 Sumário Executivo

Este documento fornece uma referência completa sobre:
- **O quê cada script faz** (propósito)
- **Dependências e pré-requisitos** (o que precisa estar pronto)
- **Ordem correta de execução** (sequência recomendada)
- **Como usar cada script** (exemplos práticos)
- **Logs esperados** (o que você verá durante execução)
- **Casos de uso reais** (automações completas)

---

## 📋 Índice de Scripts por Categoria

### 🔧 **Infraestrutura & Setup**
1. `run.ps1` - Orquestrador principal (PowerShell)
2. `auto_fix.py` - Automação de banco de dados

### 🧪 **Testes & Validação**
3. `test_app.py` - Testes unitários core
4. `run_all_tests.py` - Master test runner
5. `diagnostico.py` - Diagnóstico de saúde do sistema

### 🚀 **Deploy & Produção**
6. `deploy_production_complete.py` - Deploy completo
7. `validar_deploy.py` - Validação pós-deploy

### 💾 **Banco de Dados**
8. `backup_db.py` - Backup de database
9. `check_db.py` - Verificação de integridade
10. `repair_alembic.py` - Reparo de migrations

### 🎨 **Media & Assets**
11. `otimizar_imagens.py` - Otimização de imagens para WebP

### 🧹 **Manutenção & Limpeza**
12. `limpar_projeto.py` - Limpeza de temporários
13. `limpeza_total_venv.py` - Reset completo de venv

---

## 🚀 Fluxos de Automação Completos

### Fluxo 1: **Desenvolvimento Local - Início do Dia**

**Objetivo**: Garantir que o ambiente local está pronto para desenvolvimento.

**Sequência**:
```powershell
# 1️⃣ SETUP - Orquestra tudo automaticamente
.\run.ps1

# 2️⃣ VERIFY - Confirma que tudo está funcionando
python check_db.py

# 3️⃣ DIAGNOSTIC - Vê status completo do sistema
python diagnostico.py
```

**Logs Esperados**:
```
[12:00:00] INFO auto_fix: starting maintenance run
[12:00:05] INFO auto_fix: found database at d:\...\instance\site.db
[12:00:08] INFO auto_fix: backup created at instance/backups/site.db.20251130_120008
[12:00:10] INFO auto_fix: FLASK_APP=BelarminoMonteiroAdvogado
[12:00:15] INFO auto_fix: flask db upgrade succeeded
[12:00:20] INFO auto_fix: completed successfully

✓ Connected to SQLite: instance/site.db
✓ Tables: 14 found
✓ User table: Accessible
✓ Status: Database OK

Python 3.11.4 ✓
Database: instance/site.db ✓
Flask app: OK ✓
Routes: 47 found ✓
Migrations: Up-to-date ✓
```

**Tempo Total**: ~2-5 minutos

**Dependências**:
- Python 3.11+
- `venv` ativado
- `requirements.txt` instalado
- `FLASK_APP=BelarminoMonteiroAdvogado` (set by run.ps1)

---

### Fluxo 2: **Antes de Fazer Commit**

**Objetivo**: Garantir que seu código não quebra nada antes de commitar.

**Sequência**:
```powershell
# 1️⃣ QUICK TEST - Testa core functionality
pytest test_app.py -v

# 2️⃣ FULL TEST - Roda todos os testes
python run_all_tests.py

# 3️⃣ CHECK CLEANUP - Remove arquivos temporários
python limpar_projeto.py

# 4️⃣ GIT - Commit se tudo passou
git add .
git commit -m "feature: description"
```

**Logs Esperados (run_all_tests.py)**:
```
2025-11-30 12:35:00 INFO bma_vf: run_all_tests: starting test run in d:\...
2025-11-30 12:35:05 INFO bma_vf: run_all_tests: discovered 13 test files

Running: test_pre_deploy_completo_v2.py (1/13)
✅ PASSOU

Running: test_database_schema.py (2/13)
✅ PASSOU

Running: test_all_themes_complete.py (3/13)
✅ PASSOU

...

2025-11-30 12:36:30 INFO bma_vf: run_all_tests: finished in 90.45s - passed=13 failed=0

✅ DEPLOY LIBERADO!
Todos os testes passaram
Sistema pronto para produção!
```

**Tempo Total**: ~2-3 minutos

**Dependências**:
- pytest instalado
- Testes localizados em raiz do projeto
- Base de dados em estado válido

---

### Fluxo 3: **Deploy para Produção**

**Objetivo**: Fazer deploy seguro e validado para produção.

**Sequência**:
```powershell
# 1️⃣ BACKUP - Sempre primeiro!
python backup_db.py
# Verifica que backup foi criado
ls instance/backups/

# 2️⃣ OPTIMIZE - Reduz tamanho de media
python otimizar_imagens.py --src static/images/uploads --backup-dir instance/backups/images

# 3️⃣ FULL TEST - Todas as validações devem passar
python run_all_tests.py

# 4️⃣ PRE-DEPLOY VALIDATION
python diagnostico.py

# 5️⃣ DEPLOY (Google App Engine)
gcloud app deploy --version=1

# 6️⃣ POST-DEPLOY VALIDATION
python validar_deploy.py --base-url=https://seu-app.appspot.com
```

**Logs Esperados**:
```
[Passo 1 - backup_db.py]
INFO: backup_db: backing up site.db -> instance/backups/site.db.20251130_143000
INFO: backup_db: backup completed -> instance/backups/site.db.20251130_143000
INFO: backup_db: finished successfully

[Passo 2 - otimizar_imagens.py]
INFO: otimizar_imagens: scanning static/images/uploads for images
INFO: otimizar_imagens: found 124 images, processing...
INFO: otimizar_imagens: logo.png -> logo.webp (orig: 2.3MB, new: 0.6MB)
INFO: otimizar_imagens: hero.jpg -> hero.webp (orig: 5.1MB, new: 1.2MB)
INFO: otimizar_imagens: finished. processed=124 skipped=5 saved_bytes=380MB

[Passo 3 - run_all_tests.py]
2025-11-30 14:30:00 INFO bma_vf: run_all_tests: discovered 13 test files
2025-11-30 14:31:30 INFO bma_vf: run_all_tests: finished in 90.45s - passed=13 failed=0
✅ DEPLOY LIBERADO!

[Passo 4 - diagnostico.py]
Python 3.11.4 ✓
Flask app: OK ✓
Database: instance/site.db ✓
Routes: 47 found ✓
...

[Passo 5 - gcloud]
Updating service [default]... done
Deployed to: https://seu-app.appspot.com

[Passo 6 - validar_deploy.py]
validar_deploy: / returned 200
validar_deploy: /admin returned 302 (redirect to login)
validar_deploy: /api/health returned 200
validar_deploy: database connectivity OK
✅ DEPLOYMENT VALIDATION PASSED
```

**Tempo Total**: ~15-20 minutos

**Dependências**:
- Google Cloud SDK instalado
- `gcloud` configurado com credenciais
- Última versão do código no main branch
- Testes passando localmente

---

### Fluxo 4: **Recuperação de Erro - Database Corrompido**

**Objetivo**: Recuperar-se de erro de banco de dados mantendo dados.

**Sequência**:
```powershell
# 1️⃣ BACKUP PRIMEIRO - NUNCA PULE ISSO!
python backup_db.py
# Output: Backup criado em instance/backups/site.db.20251130_145000

# 2️⃣ DIAGNOSTICAR O PROBLEMA
python check_db.py
# Se houver erro de conexão: goto passo 3

# 3️⃣ REPARAR ALEMBIC (migrations)
python repair_alembic.py

# 4️⃣ REINICIAR AUTOMAÇÕES
.\run.ps1

# 5️⃣ VALIDAR
python check_db.py
python diagnostico.py
```

**Logs Esperados**:
```
[Passo 1]
INFO: backup_db: backing up site.db -> instance/backups/site.db.20251130_145000
INFO: backup_db: finished successfully

[Passo 2]
❌ ERROR: check_db: cannot open database at instance/site.db
   OR
✓ Connected to SQLite: instance/site.db
✗ alembic_version table corrupted

[Passo 3]
INFO: repair_alembic: found database at instance/site.db
INFO: repair_alembic: detected migration issue
INFO: repair_alembic: attempting repair for alembic_version
INFO: repair_alembic: alembic_version updated successfully

[Passo 4]
[auto_fix: starting maintenance run]
[auto_fix: backup created at...]
[auto_fix: flask db upgrade succeeded]
[auto_fix: completed successfully]

[Passo 5]
✓ Status: Database OK
Python 3.11.4 ✓
Database: instance/site.db ✓
```

**Tempo Total**: ~5 minutos

---

### Fluxo 5: **Reset Completo (Quando Nada Mais Funciona)**

**Objetivo**: Reconstruir ambiente do zero - última opção.

**Sequência**:
```powershell
# ⚠️ BACKUP TUDO ANTES!
python backup_db.py --remove-migrations

# Limpar arquivos temporários
python limpeza_total_venv.py

# Reset completo
.\run.ps1 clean

# Verificar
python diagnostico.py
```

**Logs Esperados**:
```
[backup_db.py]
INFO: backup_db: backing up site.db -> instance/backups/site.db.20251130_150000
WARNING: backup_db: --remove-migrations used: removing migrations/ (ensure you have backup)
INFO: backup_db: finished successfully

[limpeza_total_venv.py]
Removendo venv/ (size: 220MB)
INFO: venv removido
Reinstalando dependências...
Successfully installed Flask==3.0.0 SQLAlchemy==2.0.23 ...

[run.ps1 clean]
Removendo instance/site.db
Removendo migrations/
Reconstruindo do zero...
[auto_fix: starting maintenance run]
[auto_fix: flask db init]
[auto_fix: flask db stamp head]
[auto_fix: flask db migrate -m "initial"]
[auto_fix: flask db upgrade succeeded]
[auto_fix: completed successfully]

[diagnostico.py]
Python 3.11.4 ✓
Database: Novo banco criado com sucesso ✓
Flask app: OK ✓
Routes: 47 found ✓
```

**Tempo Total**: ~10-15 minutos

**⚠️ CUIDADO**: Este fluxo RESETA tudo. Use apenas em emergência!

---

## 📊 Matriz de Decisão: Qual Script Usar?

| Situação | Script(s) | Tempo | Risco |
|----------|-----------|-------|-------|
| Iniciar desenvolvimento | `run.ps1` | 2-5m | Baixo |
| Verificar saúde do sistema | `diagnostico.py` | 30s | Nenhum (read-only) |
| Testar antes de commit | `run_all_tests.py` | 2-3m | Baixo |
| Fazer backup do DB | `backup_db.py` | 30s | Nenhum |
| Verificar integridade do DB | `check_db.py` | 10s | Nenhum (read-only) |
| Reparar migrations quebradas | `repair_alembic.py` | 1m | Médio (backup antes!) |
| Otimizar imagens | `otimizar_imagens.py` | 5-30m | Baixo (tem backup automático) |
| Deploy para produção | `deploy_production_complete.py` | 15-20m | Médio (testa antes) |
| Validar deploy realizado | `validar_deploy.py` | 2-3m | Nenhum (read-only) |
| Limpeza de temporários | `limpar_projeto.py` | 30s | Baixo |
| Reset de venv corrompido | `limpeza_total_venv.py` | 10m | Médio |
| Reset TOTAL de emergência | `run.ps1 clean` | 10-15m | Alto (backup antes!) |

---

## 🔐 Checklist de Segurança por Fluxo

### ✅ Antes de Deploy
- [ ] Rodou `run_all_tests.py` com sucesso
- [ ] Verificou `python diagnostico.py` - tudo OK
- [ ] Executou `python backup_db.py` - backup confirmado em `instance/backups/`
- [ ] Executou `python otimizar_imagens.py` - media otimizado
- [ ] Revisou últimas alterações no código (`git log --oneline -10`)
- [ ] Confirmou que nenhuma senha/chave privada está no código

### ✅ Após Deploy
- [ ] Executou `python validar_deploy.py` com sucesso
- [ ] Verificou logs em produção (CloudWatch, etc)
- [ ] Testou fluxo crítico no ambiente produção (login, criar item, etc)
- [ ] Verificou que backup anterior still existe em `instance/backups/`

### ✅ Antes de Reset Completo
- [ ] Backup feito: `python backup_db.py --remove-migrations`
- [ ] Backup verificado: `ls instance/backups/` tem arquivo recente
- [ ] Avisou o time (se aplicável)
- [ ] Documentou motivo do reset

---

## 📝 Dependências Globais

Todos os scripts dependem de:

```
Python 3.11+                    # Versão mínima
pip (package manager)           # Instalado com Python
requirements.txt                # Instale com: pip install -r requirements.txt
```

### Principais Dependências (via pip)
```
Flask==3.0.0                    # Framework web
SQLAlchemy==2.0.23              # ORM para banco de dados
Flask-Migrate==4.0.5            # Migrações (Alembic)
Pillow==10.0.0                  # Image processing (otimizar_imagens.py)
pytest==7.4.3                   # Testes
pytest-cov==4.1.0               # Coverage de testes
```

### Verificar Dependências Instaladas
```powershell
pip list | grep -E "Flask|SQLAlchemy|Pillow|pytest"
```

---

## 🚨 Guia de Troubleshooting

### ❌ Erro: "FLASK_APP not found"
```
Solução:
1. Verificar que BelarminoMonteiroAdvogado/ existe
2. Se rodando manualmente: $env:FLASK_APP = "BelarminoMonteiroAdvogado"
3. Usar run.ps1 que já seta automaticamente
```

### ❌ Erro: "alembic_version corrupted"
```
Solução:
1. python backup_db.py
2. python repair_alembic.py
3. .\run.ps1
```

### ❌ Erro: "Cannot import module X"
```
Solução:
1. pip install -r requirements.txt
2. python -m pip install --upgrade pip
3. python -m pip install -r requirements.txt --force-reinstall
```

### ❌ Erro: "Port 5000 already in use"
```
Solução:
1. Encontre processo usando porta: netstat -ano | findstr :5000
2. Mate processo: taskkill /PID {PID} /F
3. Ou mude porta em run.ps1: $env:FLASK_PORT = 5001
```

---

## 📚 Referência de Variáveis de Ambiente

| Variável | Valor Esperado | Obrigatória? | Usado Por |
|----------|----------------|-------------|-----------|
| `FLASK_APP` | `BelarminoMonteiroAdvogado` | ✅ Sim | Todos scripts Flask |
| `FLASK_ENV` | `development` ou `production` | ❌ Não | Flask config |
| `DATABASE_URL` | `sqlite:///instance/site.db` ou PostgreSQL | ❌ Não (padrão SQLite) | auto_fix.py |
| `PYTHONPATH` | Diretório raiz do projeto | ❌ Não | Scripts Python |

---

## 🎓 Boas Práticas

1. **Sempre Backup Antes de Operações Destrutivas**
   ```powershell
   python backup_db.py
   # Depois faça a operação
   python limpeza_total_venv.py
   ```

2. **Use run.ps1 Para Setup Inicial**
   - Não rode `pip install` e `flask run` manualmente
   - `run.ps1` orquestra tudo na ordem correta

3. **Teste Antes de Deploy**
   ```powershell
   python run_all_tests.py
   # Tem que passar com sucesso antes de gcloud deploy
   ```

4. **Monitore Logs**
   - Local: `run_log.txt` é criado automaticamente
   - Produção: Veja Google Cloud Logging ou PythonAnywhere logs

5. **Mantenha Backups**
   - `instance/backups/` tem histórico automático
   - Regularmente copie backups para storage externo

---

## 🔗 Próximos Passos

- Ver `.github/copilot-instructions.md` para referência técnica detalhada
- Ver `README.md` para overview geral
- Ver arquivos de script individuais para comentários de código
- Levantar issue se encontrar problema ou inconsistência

---

**Última atualização**: 30 de Novembro de 2025  
**Versão**: 1.0  
**Mantido por**: Time de Desenvolvimento BMA_VF
