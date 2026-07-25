from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, computed_field, field_validator
from typing import Optional, Union


class SectorEnum(str, Enum):
    cozinha = "Cozinha"
    administrativo = "Administrativo"
    limpeza = "Limpeza"
    desenvolvimento = "Desenvolvimento"
    RH = "RH"
    marketing = "Marketing"
    vendas = "Vendas"
    recepcao = "Recepção"
    financeiro = "Financeiro"
    Bares = "Bares"
    seguranca = "Segurança"
    Restaurante = "Restaurante"
    manutencao = "Manutenção"
    TI = "TI"
    almoxarifado = "Almoxarifado"
    gorvernanca = "Governança"
    Guest_Services = "Guest Services"
    Lazer = "Lazer"

class WorkerStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class WorkersIn(BaseModel):
    """Schema para validação dos dados ao CADASTRAR um funcionário."""
    user_id: int
    name: str = Field(..., min_length=3, max_length=100, description="Nome completo do funcionário.")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do funcionário (pode incluir pontos e traço).")
    birth_date: date = Field(..., description="Data de nascimento (formato: DD-MM-AAAA).")
    address: str = Field(..., max_length=255, description="Endereço completo.")
    cep: str = Field(..., min_length=8, max_length=9, description="CEP (pode incluir traço).")
    sector: SectorEnum = Field(..., description="Setor onde o funcionário trabalha.")

    # Regras de negócio embutidas no schema (valores padrão)
    daily_hours: int = Field(default=8, ge=1, le=24, description="Carga horária diária esperada.")
    auto_lunch: bool = Field(default=True, description="Define se o almoço é descontado automaticamente.")
    lunch_duration_minutes: int = Field(default=60, ge=0, description="Minutos de almoço.")

    @field_validator("cpf")
    @classmethod
    def validate_and_clean_cpf(cls, v: str) -> str:
        """Valida um CPF e retorna apenas os dígitos."""
        if not isinstance(v, str):
            raise ValueError("CPF deve ser uma string.")

        # 1. Remove pontuações e espaços
        cpf = "".join(filter(str.isdigit, v))

        # 2. Verifica o tamanho e se todos os dígitos são iguais
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            raise ValueError("Formato de CPF inválido.")

        # 3. Cálculo do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito_1 = (soma * 10 % 11) % 10
        if digito_1 != int(cpf[9]):
            raise ValueError("CPF inválido.")

        # 4. Cálculo do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito_2 = (soma * 10 % 11) % 10
        if digito_2 != int(cpf[10]):
            raise ValueError("CPF inválido.")

        return cpf # Retorna o CPF limpo (apenas números)

    @field_validator("cep")
    @classmethod
    def clean_cep(cls, v: str) -> str:
        """Remove a pontuação do CEP para padronizar o armazenamento."""
        return "".join(filter(str.isdigit, v))

class WorkersUpdate(BaseModel):
    """Schema para ATUALIZAR um funcionário. Todos os campos são opcionais."""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Nome completo do funcionário.")
    cpf: Optional[str] = Field(None, min_length=11, max_length=14, description="CPF do funcionário.")
    birth_date: Optional[date] = Field(None, description="Data de nascimento (formato: DD-MM-AAAA).")
    address: Optional[str] = Field(None, max_length=255, description="Endereço completo.")
    cep: Optional[str] = Field(None, min_length=8, max_length=9, description="CEP.")
    sector: Optional[SectorEnum] = Field(None, description="Setor onde o funcionário trabalha.")
    daily_hours: Optional[int] = Field(None, ge=1, le=24, description="Carga horária diária esperada.")
    auto_lunch: Optional[bool] = Field(None, description="Define se o almoço é descontado automaticamente.")
    lunch_duration_minutes: Optional[int] = Field(None, ge=0, description="Minutos de almoço.")
    status: Optional[WorkerStatus] = Field(None, description="Status do funcionário (ativo ou inativo).")

    # Reutiliza a mesma lógica de validação do CPF
    validate_cpf = field_validator("cpf", check_fields=False)(WorkersIn.validate_and_clean_cpf)

class WorkersOut(WorkersIn):
    """
    Schema para formatar a SAÍDA de dados.
    Ele herda tudo do WorkersIn e adiciona o ID e a data gerados pelo banco.
    """
    id: int
    registration: str = Field(..., description="Matrícula única gerada pelo sistema.")
    dismissal_date: Optional[date] = Field(None, description="Data de demissão, se aplicável.")
    status: WorkerStatus
    created_at: datetime

    @computed_field
    @property
    def age(self) -> int:
        """Calcula a idade do funcionário com base na data de nascimento."""
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age

    # Permite que o Pydantic leia diretamente os registros do SQLAlchemy/databases
    model_config = ConfigDict(from_attributes=True)