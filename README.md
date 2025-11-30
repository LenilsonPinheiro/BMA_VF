# Belarmino Monteiro Advogado - Sistema Web

Este é o repositório principal para o sistema web do escritório de advocacia Belarmino Monteiro. O sistema é construído utilizando Flask, SQLAlchemy, Flask-Login, Flask-Migrate e Bootstrap, oferecendo um painel de administração para gerenciamento de conteúdo dinâmico.

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

## Visão Geral do Módulo de Administração

O painel de administração (acessível via `/admin`) permite gerenciar diversos aspectos do site, incluindo:

-   Conteúdo de páginas e seções (Home, Sobre Nós, Contato, etc.).
-   Áreas de Atuação.
-   Membros da Equipe.
-   Depoimentos de Clientes.
-   Configurações de Tema (cores, layout).
-   Configurações de SEO.

Para um roteiro detalhado de futuras melhorias e funcionalidades para o módulo de administração, consulte o arquivo `admin_module_roadmap.md`.

## Contribuição

Contribuições são bem-vindas. Por favor, siga as diretrizes de codificação existentes e crie pull requests para novas funcionalidades ou correções de bugs.

## Licença

[Inserir informações de Licença aqui]
