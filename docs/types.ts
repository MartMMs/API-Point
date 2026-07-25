export interface LoginRequest {
  user_id: number;
}

export interface LoginResponse {
  access_token: string;
}

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

export interface ApiErrorResponse {
  detail: string;
}
