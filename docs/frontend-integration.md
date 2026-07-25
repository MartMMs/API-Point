# Frontend Integration Guide

Guia prático para consumir a API PointsExtras no frontend.

## Base URL

Em desenvolvimento:

```ts
const baseUrl = 'http://localhost:8000';
```

Em produção, a URL deve apontar para o domínio publicado da API.

## Autenticação

A API usa JWT via header `Authorization`.

Se o front já usa Axios, vale centralizar o client em um único módulo.

### Client com Axios

```ts
import axios from 'axios';

export const api = axios.create({
  baseURL: baseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}
```

### Login

```ts
async function login(userId: number) {
  const response = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    throw new Error('Falha no login');
  }

  return response.json();
}
```

Resposta esperada:

```ts
{
  access_token: string
}
```

### Uso do token

```ts
function buildAuthHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}
```

## Funcionários

### Criar funcionário

```ts
async function createWorker(token: string) {
  const response = await fetch(`${baseUrl}/workers/`, {
    method: 'POST',
    headers: buildAuthHeaders(token),
    body: JSON.stringify({
      user_id: 1,
      name: 'Maria Silva',
      cpf: '39053344705',
      birth_date: '1990-01-01',
      address: 'Rua Exemplo, 123',
      cep: '12345678',
      sector: 'Desenvolvimento',
      daily_hours: 8,
      auto_lunch: true,
      lunch_duration_minutes: 60,
    }),
  });

  if (!response.ok) {
    throw new Error('Falha ao criar funcionário');
  }

  return response.json();
}
```

### Listar funcionários

```ts
async function listWorkers(token: string) {
  const response = await fetch(`${baseUrl}/workers/?status=active&limit=10&skip=0`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Falha ao listar funcionários');
  }

  return response.json();
}
```

### Atualizar funcionário

```ts
async function updateWorker(token: string, workerId: number) {
  const response = await fetch(`${baseUrl}/workers/${workerId}`, {
    method: 'PUT',
    headers: buildAuthHeaders(token),
    body: JSON.stringify({
      name: 'Maria Souza',
      daily_hours: 9,
    }),
  });

  if (!response.ok) {
    throw new Error('Falha ao atualizar funcionário');
  }

  return response.json();
}
```

### Desativar ou excluir

```ts
async function deactivateWorker(token: string, workerId: number) {
  const response = await fetch(`${baseUrl}/workers/${workerId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Falha ao desativar funcionário');
  }

  return response.json();
}

async function deleteWorkerPermanently(token: string, workerId: number) {
  const response = await fetch(`${baseUrl}/workers/${workerId}?force=true`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Falha ao excluir funcionário');
  }

  return response.json();
}
```

## Pontos

### Registrar ponto

A API aceita estes valores:

- `check_in`
- `lunch_out`
- `lunch_in`
- `check_out`

```ts
async function registerPoint(token: string, type: 'check_in' | 'lunch_out' | 'lunch_in' | 'check_out') {
  const response = await fetch(`${baseUrl}/points/`, {
    method: 'POST',
    headers: buildAuthHeaders(token),
    body: JSON.stringify({ type }),
  });

  if (!response.ok) {
    throw new Error('Falha ao registrar ponto');
  }

  return response.json();
}
```

## Relatórios

### Relatório de horas por período

```ts
async function getReport(token: string, workerId: number, startDate: string, endDate: string) {
  const response = await fetch(
    `${baseUrl}/workers/${workerId}/report?start_date=${startDate}&end_date=${endDate}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error('Falha ao gerar relatório');
  }

  return response.json();
}
```

Exemplo de retorno:

```ts
{
  worker_id: number,
  start_date: string,
  end_date: string,
  total_worked_hours: string,
  total_expected_hours: string,
  total_overtime: string,
  total_negative_time: string,
  daily_summaries: Array<{
    date: string,
    worked_hours: string,
    expected_hours: string,
    overtime: string,
    negative_time: string,
  }>
}
```

## Boas práticas para o front

- Guarde o token em memória ou em storage seguro, conforme a estratégia do app.
- Padronize `cpf` e `cep` como strings.
- Envie datas sempre em `YYYY-MM-DD`.
- Trate `401`, `404` e `409` com mensagens específicas para o usuário.
- Quando usar React, centralize as chamadas em um client de API único.

## Tratamento de erro

```ts
function getApiErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return 'Erro inesperado ao comunicar com a API';
}
```

Essa abordagem ajuda o front a exibir mensagens consistentes quando a API responder com `401`, `404` ou `409`.
