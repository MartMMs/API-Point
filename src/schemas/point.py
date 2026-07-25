from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List
from models.point import PointType

class PointIn(BaseModel):
    """Schema para o POST de bater o ponto."""
    type: PointType

    @field_validator("type", mode="before")
    @classmethod
    def normalize_point_type(cls, value):
        if isinstance(value, str):
            value = value.replace("-", "_")
        return value

class PointOut(BaseModel):
    """Schema para listar o histórico de batidas de ponto."""
    id: int
    worker_id: int
    type: PointType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailySummary(BaseModel):
    """Schema para o resumo de horas de um único dia."""
    date: date
    worked_hours: str
    expected_hours: str
    overtime: str
    negative_time: str

class ReportOut(BaseModel):
    """Schema para o relatório completo de um período."""
    worker_id: int
    start_date: date
    end_date: date
    total_worked_hours: str
    total_expected_hours: str
    total_overtime: str
    total_negative_time: str
    daily_summaries: List[DailySummary]