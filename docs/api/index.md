# Documentação da API

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
