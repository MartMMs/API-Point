import enum
import sqlalchemy as sa
from database import metadata


class PointType(str, enum.Enum):
    check_in = "check_in"
    lunch_out = "lunch_out"
    lunch_in = "lunch_in"
    check_out = "check_out"


points = sa.Table(
    "points",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("worker_id", sa.Integer, sa.ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True),
    sa.Column("type", sa.Enum(PointType, name="point_type_enum"), nullable=False),
    sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
)