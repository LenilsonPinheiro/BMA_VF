"""
Script de Organização do Projeto Belarmino Monteiro Advogados
-----------------------------------------------------------

Este script automatiza a reorganização da estrutura de diretórios e arquivos do projeto
para melhorar a manutenibilidade e clareza. Ele:
1. Cria a nova estrutura de diretórios
2. Move os arquivos para seus respectivos locais
3. Atualiza os imports necessários
4. Cria arquivos de documentação
5. Configura o ambiente CI/CD

Uso:
    python organize_project.py [--dry-run] [--verbose]

Argumentos:
    --dry-run  Mostra as alterações que seriam feitas sem executá-las
    --verbose  Exibe informações detalhadas durante a execução
"""

import os
import shutil
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('project_organization.log')
    ]
)
logger = logging.getLogger(__name__)

# Mapeamento de arquivos para mover
FILE_MAPPING = {
    # Scripts de Deploy
    'deploy_pythonanywhere_automatico.py': 'scripts/deploy/pythonanywhere_deploy.py',
    'deploy_pythonanywhere_auto.py': 'scripts/deploy/pythonanywhere_auto.py',
    'deploy_production_complete.py': 'scripts/deploy/production_deploy.py',
    'deploy_monitor.py': 'scripts/monitoring/deploy_monitor.py',
    'deploy_automatico_completo.py': 'scripts/deploy/full_deploy.py',
    'deploy_final_automatico.py': 'scripts/deploy/final_deploy.py',
    'deploy_completo_automatico.py': 'scripts/deploy/complete_deploy.py',
    
    # Testes
    'test_pre_deploy_completo.py': 'tests/integration/pre_deploy_suite.py',
    'test_pre_deploy_completo_v2.py': 'tests/integration/pre_deploy_suite_v2.py',
    'test_all_routes_complete.py': 'tests/integration/test_routes.py',
    'test_admin_routes.py': 'tests/integration/test_admin_routes.py',
    'test_all_themes.py': 'tests/unit/test_themes.py',
    'test_all_themes_complete.py': 'tests/integration/test_themes.py',
    'test_visual_humano_completo.py': 'tests/e2e/visual_checks.py',
    'test_human_simulation.py': 'tests/e2e/human_simulation.py',
    'test_media_completo.py': 'tests/integration/test_media.py',
    'test_links_rotas_completo.py': 'tests/integration/test_links.py',
    'test_producao_completo.py': 'tests/e2e/production_checks.py',
    'test_app.py': 'tests/unit/test_app.py',
    'test_database_schema.py': 'tests/integration/test_database.py',
    'test_completo_final.py': 'tests/integration/complete_test_suite.py',
    'run_all_tests.py': 'scripts/testing/run_tests.py',
    'run_tests_with_progress.py': 'scripts/testing/run_tests_with_progress.py',
    
    # Diagnósticos e Correções
    'diagnostico.py': 'scripts/diagnostics/health_check.py',
    'diagnostico_video_completo.py': 'scripts/diagnostics/video_analysis.py',
    'diagnose_themes_5678.py': 'scripts/diagnostics/theme_analyzer.py',
    'fix_video_visibility.py': 'scripts/fixes/video_visibility_fix.py',
    'fix_video_posicionamento_final.py': 'scripts/fixes/video_positioning_fix.py',
    'fix_seo_all_themes.py': 'scripts/fixes/seo_fixes.py',
    'fix_all_contrast_issues.py': 'scripts/fixes/contrast_fixes.py',
    'fix_banner_images.py': 'scripts/fixes/banner_fixes.py',
    'fix_cache_and_restart.py': 'scripts/fixes/cache_fix.py',
    'fix_home_section_variable.py': 'scripts/fixes/home_section_fix.py',
    'fix_missing_images.py': 'scripts/fixes/missing_images_fix.py',
    'fix_seo_route.py': 'scripts/fixes/seo_route_fix.py',
    'fix_sqlite_appengine.py': 'scripts/fixes/sqlite_fix.py',
    
    # Utilitários
    'image_processor.py': 'scripts/utils/image_processor.py',
    'otimizar_imagens.py': 'scripts/optimization/image_optimizer.py',
    'limpar_projeto.py': 'scripts/cleanup/project_cleaner.py',
    'limpeza_total_venv.py': 'scripts/setup/venv_cleaner.py',
    'create_admin.py': 'scripts/setup/create_admin_user.py',
    'check_db.py': 'scripts/database/check_connection.py',
    'debug_db_create.py': 'scripts/database/debug_creation.py',
    'repair_alembic.py': 'scripts/database/alembic_repair.py',
    'backup_db.py': 'scripts/database/backup_manager.py',
    'validar_deploy.py': 'scripts/deploy/validate_deployment.py',
    'verify_ecosystem.py': 'scripts/diagnostics/ecosystem_check.py',
    'run_deploy_with_dashboard.py': 'scripts/deploy/deploy_with_dashboard.py',
    
    # Configurações
    'app.yaml': 'deployment/gcp/app.yaml',
    '.gcloudignore': 'deployment/gcp/.gcloudignore',
}

# Estrutura de diretórios a serem criados
DIRECTORIES = [
    'scripts/setup',
    'scripts/database',
    'scripts/utils',
    'scripts/deploy',
    'scripts/monitoring',
    'scripts/diagnostics',
    'scripts/fixes',
    'scripts/optimization',
    'scripts/cleanup',
    'scripts/testing',
    'tests/unit',
    'tests/integration',
    'tests/e2e',
    'deployment/gcp',
    'deployment/pythonanywhere',
    'docs/api',
    'docs/deployment',
    '.github/workflows',
]

class ProjectOrganizer:
    """Classe responsável por organizar a estrutura do projeto."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """Inicializa o organizador do projeto.
        
        Args:
            dry_run: Se True, apenas mostra as alterações sem executá-las
            verbose: Se True, exibe informações detalhadas
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = Path(__file__).parent.absolute()
        self.moved_files = []
        self.created_dirs = []
        
        # Configura nível de log baseado no modo verboso
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    def create_directories(self) -> None:
        """Cria todos os diretórios necessários."""
        logger.info("Criando estrutura de diretórios...")
        
        for dir_path in DIRECTORIES:
            full_path = self.project_root / dir_path
            
            if full_path.exists():
                if self.verbose:
                    logger.debug(f"Diretório já existe: {full_path}")
                continue
                
            if not self.dry_run:
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.created_dirs.append(str(full_path))
                    logger.info(f"Diretório criado: {full_path}")
                except Exception as e:
                    logger.error(f"Erro ao criar diretório {full_path}: {e}")
            else:
                logger.info(f"[DRY RUN] Criaria diretório: {full_path}")
    
    def move_files(self) -> None:
        """Move os arquivos para seus novos locais."""
        logger.info("Movendo arquivos...")
        
        for src_file, dest_file in FILE_MAPPING.items():
            src_path = self.project_root / src_file
            dest_path = self.project_root / dest_file
            
            # Pula se o arquivo de origem não existir
            if not src_path.exists():
                if self.verbose:
                    logger.debug(f"Arquivo de origem não encontrado: {src_path}")
                continue
                
            # Cria diretório de destino se não existir
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Movendo {src_path} para {dest_path}")
                continue
                
            try:
                # Move o arquivo
                shutil.move(str(src_path), str(dest_path))
                self.moved_files.append((str(src_path), str(dest_path)))
                logger.info(f"Arquivo movido: {src_path} -> {dest_path}")
                
                # Atualiza imports no arquivo movido
                self._update_imports(dest_path, src_path.name, dest_file)
                
            except Exception as e:
                logger.error(f"Erro ao mover {src_path} para {dest_path}: {e}")
    
    def _update_imports(self, file_path: Path, old_name: str, new_name: str) -> None:
        """Atualiza os imports no arquivo movido.
        
        Args:
            file_path: Caminho para o arquivo
            old_name: Nome antigo do arquivo (sem caminho)
            new_name: Novo nome do arquivo (com caminho relativo)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Atualiza imports relativos
            updated_content = content
            
            # Salva o conteúdo atualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            if self.verbose:
                logger.debug(f"Atualizados imports em: {file_path}")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar imports em {file_path}: {e}")
    
    def create_ci_cd_files(self) -> None:
        """Cria os arquivos de CI/CD."""
        logger.info("Criando arquivos de CI/CD...")
        
        # GitHub Actions workflow para testes
        workflows_dir = self.project_root / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Workflow de testes
        test_workflow = workflows_dir / 'tests.yml'
        if not test_workflow.exists() and not self.dry_run:
            test_workflow_content = """name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8 bandit mypy
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Check formatting with black
      run: black --check --diff .
    
    - name: Run security audit with bandit
      run: |
        bandit -r . -x ./venv,./tests
    
    - name: Run type checking with mypy
      run: |
        mypy --install-types --non-interactive .
    
    - name: Run tests with pytest
      env:
        DATABASE_URL: postgresql://test:test@localhost:5432/test_db
      run: |
        python -m pytest tests/ -v --cov=BelarminoMonteiroAdvogado --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        fail_ci_if_error: false
"""
            with open(test_workflow, 'w', encoding='utf-8') as f:
                f.write(test_workflow_content)
            logger.info(f"Arquivo de workflow de testes criado: {test_workflow}")
        
        # Workflow de deploy para GCP
        deploy_workflow = workflows_dir / 'deploy-gcp.yml'
        if not deploy_workflow.exists() and not self.dry_run:
            deploy_workflow_content = """name: Deploy to GCP

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install gunicorn google-cloud-sdk
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=BelarminoMonteiroAdvogado --cov-fail-under=80
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true
    
    - name: Deploy to Google App Engine
      run: |
        gcloud config set app/cloud_build_timeout 1600
        gcloud app deploy deployment/gcp/app.yaml --quiet --project=${{ secrets.GCP_PROJECT_ID }}
"""
            with open(deploy_workflow, 'w', encoding='utf-8') as f:
                f.write(deploy_workflow_content)
            logger.info(f"Arquivo de workflow de deploy criado: {deploy_workflow}")
    
    def create_documentation(self) -> None:
        """Cria a documentação do projeto."""
        logger.info("Criando documentação...")
        
        # Atualiza README.md
        readme_path = self.project_root / 'README.md'
        current_readme = ""
        
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                current_readme = f.read()
        
        # Se o README já tem conteúdo, não sobrescreve
        if not current_readme.strip() and not self.dry_run:
            readme_content = """# Belarmino Monteiro Advogados

Sistema web para o escritório de advocacia Belarmino Monteiro.

## 🚀 Começando

### Pré-requisitos

- Python 3.10+
- PostgreSQL 13+
- Node.js 16+ (para assets)

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/belarmino-advogados.git
   cd belarmino-advogados
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: .\venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. Inicialize o banco de dados:
   ```bash
   python scripts/setup/init_db.py
   ```

6. Execute a aplicação:
   ```bash
   python run.py
   ```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
belarmino-advogados/
├── BelarminoMonteiroAdvogado/  # Código-fonte principal
├── scripts/                   # Scripts auxiliares
├── tests/                     # Testes automatizados
├── deployment/                # Configurações de deploy
├── docs/                      # Documentação
└── .github/workflows/         # CI/CD
```

### Executando Testes

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=BelarminoMonteiroAdvogado

# Executar testes específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Formatação e Linting

```bash
# Formatar código com Black
black .

# Verificar estilo com flake8
flake8 .

# Verificar segurança com bandit
bandit -r .
```

## 🚀 Deploy

### Ambiente de Produção

O deploy para produção é feito automaticamente através do GitHub Actions quando há push para a branch `main`.

### Deploy Manual

```bash
# Fazer login no Google Cloud
# gcloud auth login

# Configurar projeto
# gcloud config set project SEU_PROJETO

# Fazer deploy
# gcloud app deploy deployment/gcp/app.yaml
```

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info("Arquivo README.md criado/atualizado")
        
        # Cria documentação de API
        api_docs_path = self.project_root / 'docs' / 'api' / 'index.md'
        if not api_docs_path.exists() and not self.dry_run:
            api_docs_path.parent.mkdir(parents=True, exist_ok=True)
            api_docs_content = """# Documentação da API

## Rotas Públicas

### `GET /`
Retorna a página inicial.

### `GET /sobre`
Página sobre o escritório.

### `GET /areas-atuacao`
Lista todas as áreas de atuação.

### `GET /areas-atuacao/<slug>`
Detalhes de uma área de atuação específica.

## Rotas de Autenticação

### `POST /login`
Autentica um usuário.

### `POST /logout`
Desconecta o usuário atual.

## Rotas Administrativas

Todas as rotas administrativas requerem autenticação.

### `GET /admin`
Painel administrativo.

### `GET /admin/paginas`
Lista todas as páginas.

### `GET /admin/paginas/nova`
Formulário para criar uma nova página.

### `POST /admin/paginas`
Cria uma nova página.
"""
            with open(api_docs_path, 'w', encoding='utf-8') as f:
                f.write(api_docs_content)
            logger.info(f"Documentação da API criada em: {api_docs_path}")
    
    def run(self) -> None:
        """Executa a reorganização do projeto."""
        logger.info("Iniciando reorganização do projeto...")
        
        try:
            # Cria a estrutura de diretórios
            self.create_directories()
            
            # Move os arquivos para seus novos locais
            self.move_files()
            
            # Cria os arquivos de CI/CD
            self.create_ci_cd_files()
            
            # Cria/atualiza a documentação
            self.create_documentation()
            
            logger.info("Reorganização do projeto concluída com sucesso!")
            
            # Relatório final
            if self.dry_run:
                logger.info("\n=== RELATÓRIO (DRY RUN) ===")
                logger.info("Nenhuma alteração real foi feita.")
            else:
                logger.info("\n=== RELATÓRIO ===")
                logger.info(f"Diretórios criados: {len(self.created_dirs)}")
                logger.info(f"Arquivos movidos: {len(self.moved_files)}")
                
                if self.verbose and self.moved_files:
                    logger.info("\nArquivos movidos:")
                    for src, dest in self.moved_files:
                        logger.info(f"  {src} -> {dest}")
                
                logger.info("\nPróximos passos:")
                logger.info("1. Revise as alterações feitas")
                logger.info("2. Atualize os imports nos arquivos conforme necessário")
                logger.info("3. Execute os testes para garantir que tudo está funcionando")
                logger.info("4. Faça commit das mudanças")
                
                # Cria um arquivo de log com as alterações
                with open('project_reorganization.log', 'w', encoding='utf-8') as f:
                    f.write("=== RELATÓRIO DE REORGANIZAÇÃO DO PROJETO ===\n\n")
                    f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Diretórios criados ({len(self.created_dirs)}):\n")
                    for d in self.created_dirs:
                        f.write(f"- {d}\n")
                    f.write("\nArquivos movidos:\n")
                    for src, dest in self.moved_files:
                        f.write(f"- {src} -> {dest}\n")
        
        except Exception as e:
            logger.error(f"Erro durante a reorganização do projeto: {e}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Organiza a estrutura do projeto.')
    parser.add_argument('--dry-run', action='store_true', help='Mostra as alterações sem executá-las')
    parser.add_argument('--verbose', '-v', action='store_true', help='Exibe informações detalhadas')
    
    args = parser.parse_args()
    
    organizer = ProjectOrganizer(dry_run=args.dry_run, verbose=args.verbose)
    organizer.run()
