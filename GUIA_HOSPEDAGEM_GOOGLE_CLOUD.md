# GUIA COMPLETO DE HOSPEDAGEM - Google Cloud Platform

Este documento detalha a arquitetura e o processo de hospedagem da aplicação **Belarmino Monteiro Advocacia** no Google Cloud Platform (GCP).

## 1. Arquitetura da Solução

A aplicação está conteinerizada e hospedada no **Google App Engine (Standard Environment)**, que oferece escalabilidade automática, gerenciamento de versões e segurança integrada.

-   **Runtime:** Python 3.11
-   **Servidor WSGI:** Gunicorn
-   **Banco de Dados:** Cloud SQL (PostgreSQL) para produção (Recomendado). O ambiente de desenvolvimento utiliza SQLite.
-   **Arquivos Estáticos:** O App Engine é configurado para servir arquivos estáticos diretamente, otimizando a performance.
-   **Segurança:** As chaves de API e segredos são gerenciados via Secret Manager e injetados como variáveis de ambiente no `app.yaml`.

## 2. Configuração do Ambiente

### 2.1. `app.yaml`

O arquivo `app.yaml` é o descritor de serviço para o App Engine.

-   `runtime: python311`: Define o ambiente de execução.
-   `entrypoint: gunicorn -b :$PORT main:app`: Especifica o comando para iniciar a aplicação, utilizando o Gunicorn como servidor de produção. A porta é fornecida pela variável de ambiente `$PORT`.
-   `handlers`: Mapeia URLs para servir arquivos estáticos de forma eficiente.
-   `env_variables`: Utilizado para carregar segredos do Secret Manager.

### 2.2. `.gcloudignore`

Este arquivo é fundamental para evitar o upload de arquivos desnecessários, como ambientes virtuais, caches, bancos de dados locais e arquivos de configuração de desenvolvimento. Garante um deploy mais rápido e seguro.

## 3. Processo de Deploy (Detalhado)

1.  **Preparação:**
    -   Garanta que o `requirements.txt` está congelado com as dependências de produção.
    -   Rode a suíte de testes de integração para validar a saúde da aplicação: `python tests/integration/pre_deploy_suite_v2.py`
    -   Rode o script de validação de deploy: `python scripts/deploy/validate_deployment.py`

2.  **Configuração do Projeto GCP:**
    -   Crie um novo projeto no console do GCP.
    -   Ative as APIs necessárias: App Engine Admin API, Cloud SQL Admin API, Secret Manager API.
    -   Configure um banco de dados Cloud SQL (PostgreSQL) se necessário.
    -   Adicione os segredos (como `SECRET_KEY`) ao Secret Manager.

3.  **Deploy via gcloud CLI:**
    -   Autentique-se e configure o projeto conforme o `DEPLOY_RAPIDO.md`.
    -   Execute o deploy:
        ```bash
        gcloud app deploy BelarminoMonteiroAdvogado/app.yaml
        ```
    -   Para promover a nova versão sem dividir o tráfego:
        ```bash
        gcloud app deploy BelarminoMonteiroAdvogado/app.yaml --promote --stop-previous-version
        ```

## 4. Observabilidade e Manutenção

-   **Logs:** Acesse os logs da aplicação no **Cloud Logging**.
-   **Monitoramento:** Utilize o **Cloud Monitoring** para acompanhar a performance, latência e taxas de erro.
-   **Atualizações:** Para atualizar a aplicação, basta executar o comando de deploy novamente com o código mais recente. O App Engine criará uma nova versão.

---
*Este guia é um documento vivo e deve ser atualizado para refletir qualquer mudança na arquitetura ou processo.*
