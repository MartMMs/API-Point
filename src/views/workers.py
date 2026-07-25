from pydantic import BaseModel, AwareDatetime, NaiveDatetime, ConfigDict
from models.point import PointType


class WorkersOut(BaseModel):
    id: int
    user_id: int
    name: str
    registration: str
    daily_hours: int
    auto_lunch: bool
    lunch_duration_minutes: int
    created_at: AwareDatetime | NaiveDatetime

    # Permite que o Pydantic leia o resultado (Record) direto do banco de dados
    model_config = ConfigDict(from_attributes=True)


class PointOut(BaseModel):
    id: int
    worker_id: int
    type: PointType
    created_at: AwareDatetime | NaiveDatetime

    model_config = ConfigDict(from_attributes=True)