# PointsExtras API

API em FastAPI para controle de funcionários e registro de ponto.

## Produção

Use `ENVIRONMENT=production` no ambiente real. Nesse modo, o endpoint de teste `/auth/test-token/{user_id}` fica desabilitado.

### Variáveis de ambiente

- `DATABASE_URL`: string de conexão com o PostgreSQL.
- `ENVIRONMENT`: `production` ou `development`.
- `JWT_SECRET`: chave usada para assinar os tokens. Obrigatória.
- `JWT_ALGORITHM`: algoritmo JWT, normalmente `HS256`.

Veja o modelo em [/.env.example](.env.example).

## Criptografia

A chave de criptografia é gerada automaticamente na primeira execução e salva em `instance/encryption.key`.

Se você apagar esse arquivo, os dados já criptografados por ele não poderão ser lidos novamente.

Esse arquivo representa a identidade criptográfica da instância da API.

## Autenticação

O frontend deve enviar `Authorization: Bearer <token>` nas rotas protegidas.

Fluxo básico:

1. O frontend chama `POST /auth/login` com `user_id`.
2. A API retorna `access_token`.
3. O frontend usa esse token nas demais chamadas.

### `POST /auth/login`

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

## Workers

Prefixo: `/workers`

### `POST /workers/`

Cria um funcionário.

Request:

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

### `GET /workers/`

Lista funcionários.

Query params:

- `status`: `active` ou `inactive`
- `limit`: padrão `10`
- `skip`: padrão `0`

### `GET /workers/{worker_id}`

Busca um funcionário por ID.

### `PUT /workers/{worker_id}`

Atualiza um funcionário. Todos os campos são opcionais.

### `DELETE /workers/{worker_id}`

Por padrão faz soft delete.

Query params:

- `force=true`: remove permanentemente.

### `GET /workers/{worker_id}/point`

Lista os pontos do funcionário.

### `GET /workers/{worker_id}/report`

Gera o relatório de horas.

Query params:

- `start_date`: `YYYY-MM-DD`
- `end_date`: `YYYY-MM-DD`

## Points

Prefixo: `/points`

### `POST /points/`

Registra ponto do usuário autenticado.

Request:

```json
{
  "type": "check_in"
}
```

Valores aceitos:

- `check_in`
- `lunch_out`
- `lunch_in`
- `check_out`

## Respostas úteis para o frontend

- `200`: sucesso.
- `201`: criação de funcionário.
- `401`: token ausente ou inválido.
- `404`: recurso não encontrado.
- `409`: regra de negócio violada.

## Endpoints auxiliares

- `GET /docs`: Swagger UI.
- `GET /redoc`: desabilitado no app atual.

## Observações de integração

- Os campos sensíveis do funcionário são criptografados na API.
- O frontend deve tratar `cpf` e `cep` como strings.
- As datas são aceitas no formato ISO `YYYY-MM-DD`.

## Coleção Postman

Use a coleção em [docs/PointsExtras.postman_collection.json](docs/PointsExtras.postman_collection.json) para importar a API no Postman ou no Insomnia.

## Arquivo HTTP

Para testar direto no VS Code, use [docs/PointsExtras.api.http](docs/PointsExtras.api.http).

## Guia do Frontend

Veja o guia com exemplos de integração em [docs/frontend-integration.md](docs/frontend-integration.md).

## Referência da API

Veja a visão resumida dos endpoints em [docs/api-reference.md](docs/api-reference.md).

## Tipos TypeScript

Veja os tipos sugeridos para o frontend em [docs/typescript-types.md](docs/typescript-types.md) e o arquivo pronto para importação em [docs/types.ts](docs/types.ts).