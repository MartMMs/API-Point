# PointsExtras TypeScript Types

Tipos TypeScript sugeridos para consumir a API PointsExtras no frontend.

## Auth

```ts
export interface LoginRequest {
  user_id: number;
}

export interface LoginResponse {
  access_token: string;
}
```

## Workers

```ts
export type Sector =
  | 'Cozinha'
  | 'Administrativo'
  | 'Limpeza'
  | 'Desenvolvimento'
  | 'RH'
  | 'Marketing'
  | 'Vendas'
  | 'Recepção'
  | 'Financeiro'
  | 'Bares'
  | 'Segurança'
  | 'Restaurante'
  | 'Manutenção'
  | 'TI'
  | 'Almoxarifado'
  | 'Governança'
  | 'Guest Services'
  | 'Lazer';

export type WorkerStatus = 'active' | 'inactive';

export interface WorkerCreateRequest {
  user_id: number;
  name: string;
  cpf: string;
  birth_date: string;
  address: string;
  cep: string;
  sector: Sector;
  daily_hours?: number;
  auto_lunch?: boolean;
  lunch_duration_minutes?: number;
}

export interface WorkerUpdateRequest {
  name?: string;
  cpf?: string;
  birth_date?: string;
  address?: string;
  cep?: string;
  sector?: Sector;
  daily_hours?: number;
  auto_lunch?: boolean;
  lunch_duration_minutes?: number;
  status?: WorkerStatus;
}

export interface Worker {
  id: number;
  user_id: number;
  name: string;
  cpf: string;
  birth_date: string;
  address: string;
  cep: string;
  sector: Sector;
  daily_hours: number;
  auto_lunch: boolean;
  lunch_duration_minutes: number;
  registration: string;
  dismissal_date: string | null;
  status: WorkerStatus;
  created_at: string;
  age: number;
}
```

## Points

```ts
export type PointType = 'check_in' | 'lunch_out' | 'lunch_in' | 'check_out';

export interface RegisterPointRequest {
  type: PointType;
}

export interface Point {
  id: number;
  worker_id: number;
  type: PointType;
  created_at: string;
}

export interface DailySummary {
  date: string;
  worked_hours: string;
  expected_hours: string;
  overtime: string;
  negative_time: string;
}

export interface ReportResponse {
  worker_id: number;
  start_date: string;
  end_date: string;
  total_worked_hours: string;
  total_expected_hours: string;
  total_overtime: string;
  total_negative_time: string;
  daily_summaries: DailySummary[];
}
```

## API Error

```ts
export interface ApiErrorResponse {
  detail: string;
}
```

## Example client

```ts
import axios from 'axios';
import type {
  LoginRequest,
  LoginResponse,
  Worker,
  WorkerCreateRequest,
  WorkerUpdateRequest,
  RegisterPointRequest,
  ReportResponse,
} from './types';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export function setToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export async function login(payload: LoginRequest) {
  const { data } = await api.post<LoginResponse>('/auth/login', payload);
  return data;
}

export async function createWorker(payload: WorkerCreateRequest) {
  const { data } = await api.post<Worker>('/workers/', payload);
  return data;
}

export async function updateWorker(workerId: number, payload: WorkerUpdateRequest) {
  const { data } = await api.put<Worker>(`/workers/${workerId}`, payload);
  return data;
}

export async function registerPoint(payload: RegisterPointRequest) {
  const { data } = await api.post('/points/', payload);
  return data;
}

export async function getReport(workerId: number, startDate: string, endDate: string) {
  const { data } = await api.get<ReportResponse>(`/workers/${workerId}/report`, {
    params: { start_date: startDate, end_date: endDate },
  });
  return data;
}
```
