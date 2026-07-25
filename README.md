# PointsExtras API

API em FastAPI para controle de funcionários e registro de ponto.

## Visão Geral

O sistema cobre autenticação JWT, cadastro de funcionários, registro de ponto e geração de relatórios de horas.

## Estrutura

- [src/](src) contém o código da API.
- [docs/](docs) contém documentação para frontend e integração.
- [pyproject.toml](pyproject.toml) define dependências e configuração.

## Requisitos de Ambiente

- `DATABASE_URL`: string de conexão com o PostgreSQL.
- `ENVIRONMENT`: `production` ou `development`.
- `JWT_SECRET`: chave usada para assinar os tokens.
- `JWT_ALGORITHM`: algoritmo JWT, normalmente `HS256`.

Use [/.env.example](.env.example) como base para configurar o ambiente local.

## Criptografia

A chave de criptografia é gerada automaticamente na primeira execução e salva em `instance/encryption.key`.

Esse arquivo identifica a instância da API. Se ele for apagado, os dados já criptografados não poderão ser lidos novamente.

## Autenticação

As rotas protegidas exigem `Authorization: Bearer <token>`.

Fluxo básico:

1. O frontend chama `POST /auth/login` com `user_id`.
2. A API retorna `access_token`.
3. O frontend usa esse token nas demais chamadas.

### Login

Request:

```json
{
  "user_id": 1
}
```

Response:

```json
{
  "access_token": "jwt..."
}
```

## Endpoints Principais

### Auth

- `POST /auth/login`
- `GET /auth/test-token/{user_id}` somente fora de produção

### Workers

- `POST /workers/`
- `GET /workers/`
- `GET /workers/{worker_id}`
- `PUT /workers/{worker_id}`
- `DELETE /workers/{worker_id}`
- `GET /workers/{worker_id}/point`
- `GET /workers/{worker_id}/report`

### Points

- `POST /points/`

## Exemplos Rápidos

### Criar funcionário

```json
{
  "user_id": 1,
  "name": "Maria Silva",
  "cpf": "39053344705",
  "birth_date": "1990-01-01",
  "address": "Rua Exemplo, 123",
  "cep": "12345678",
  "sector": "Desenvolvimento",
  "daily_hours": 8,
  "auto_lunch": true,
  "lunch_duration_minutes": 60
}
```

### Registrar ponto

```json
{
  "type": "check_in"
}
```

Valores aceitos: `check_in`, `lunch_out`, `lunch_in`, `check_out`.

## Respostas Úteis

- `200`: sucesso.
- `201`: criação de funcionário.
- `401`: token ausente ou inválido.
- `404`: recurso não encontrado.
- `409`: regra de negócio violada.

## Documentação Complementar

- [Referência da API](docs/api-reference.md)
- [Guia do Frontend](docs/frontend-integration.md)
- [Coleção Postman](docs/PointsExtras.postman_collection.json)
- [Arquivo HTTP](docs/PointsExtras.api.http)
- [Tipos TypeScript](docs/types.ts)

## Observações

- `cpf` e `cep` devem ser tratados como strings no frontend.
- As datas são aceitas no formato ISO `YYYY-MM-DD`.
- O Swagger fica disponível em `GET /docs`.