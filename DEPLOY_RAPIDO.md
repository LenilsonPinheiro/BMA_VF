# DEPLOY RÁPIDO - Belarmino Monteiro Advocacia

Este documento fornece um guia rápido para o deploy da aplicação no Google Cloud App Engine.

## Pré-requisitos

1.  **Google Cloud SDK:** Certifique-se de que o `gcloud` CLI está instalado e configurado.
2.  **Autenticação:** Autentique-se com o Google Cloud:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
3.  **Projeto:** Configure o projeto de destino:
    ```bash
    gcloud config set project SEU_PROJECT_ID
    ```

## Deploy

1.  **Navegue até a raiz do projeto.**
2.  **Execute o comando de deploy:**
    ```bash
    gcloud app deploy BelarminoMonteiroAdvogado/app.yaml
    ```

3.  **Verifique o status do deploy e acesse a aplicação através da URL fornecida.**

---
*Este documento deve ser mantido atualizado a cada alteração no processo de deploy.*
