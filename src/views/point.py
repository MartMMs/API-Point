from pydantic import BaseModel, AwareDatetime, NaiveDatetime, ConfigDict
from models.point import PointType


class PointOut(BaseModel):
    id: int
    worker_id: int
    type: PointType
    created_at: AwareDatetime | NaiveDatetime

    model_config = ConfigDict(from_attributes=True)