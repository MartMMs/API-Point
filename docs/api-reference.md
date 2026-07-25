# PointsExtras API Reference

Referência rápida da API para integração com o frontend.

## Base URL

- Desenvolvimento: `http://localhost:8000`
- Produção: a URL publicada do backend

## Autenticação

Todas as rotas protegidas usam `Authorization: Bearer <token>`.

### Fluxo

1. O front chama `POST /auth/login` com `user_id`.
2. A API devolve `access_token`.
3. O front reutiliza esse token nas chamadas protegidas.

## Endpoints

| Método | Rota | Auth | Descrição |
| --- | --- | --- | --- |
| POST | `/auth/login` | Não | Gera token JWT |
| GET | `/auth/test-token/{user_id}` | Não | Token de teste, somente fora de produção |
| POST | `/workers/` | Sim | Cria funcionário |
| GET | `/workers/` | Sim | Lista funcionários |
| GET | `/workers/{worker_id}` | Sim | Busca funcionário por ID |
| PUT | `/workers/{worker_id}` | Sim | Atualiza funcionário |
| DELETE | `/workers/{worker_id}` | Sim | Desativa ou exclui funcionário |
| GET | `/workers/{worker_id}/point` | Sim | Lista pontos do funcionário |
| GET | `/workers/{worker_id}/report` | Sim | Gera relatório de horas |
| POST | `/points/` | Sim | Registra ponto do usuário autenticado |

## Auth

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

### `POST /workers/`

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

Query params:

- `status`: `active` ou `inactive`
- `limit`: padrão `10`
- `skip`: padrão `0`

### `GET /workers/{worker_id}/report`

Query params:

- `start_date`: `YYYY-MM-DD`
- `end_date`: `YYYY-MM-DD`

Response resumida:

```json
{
  "worker_id": 1,
  "start_date": "2026-07-24",
  "end_date": "2026-07-24",
  "total_worked_hours": "08:00:00",
  "total_expected_hours": "08:00:00",
  "total_overtime": "00:00:00",
  "total_negative_time": "00:00:00",
  "daily_summaries": []
}
```

## Points

### `POST /points/`

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

## Status Codes

- `200`: sucesso
- `201`: criação de funcionário
- `401`: token ausente ou inválido
- `404`: recurso não encontrado
- `409`: regra de negócio violada

## Observações

- `cpf` e `cep` devem ser tratados como strings no frontend.
- Datas devem seguir o formato ISO `YYYY-MM-DD`.
- Em produção, o endpoint de teste `/auth/test-token/{user_id}` não fica disponível.
