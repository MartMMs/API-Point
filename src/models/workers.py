import sqlalchemy as sa
from database import metadata

workers = sa.Table(
    "workers",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("user_id", sa.Integer, nullable=False, index=True, unique=True),
    # name, cpf, address e cep sao gravados criptografados (bem maiores que o texto original), por isso Text
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("cpf", sa.Text, nullable=False),
    sa.Column("birth_date", sa.Date, nullable=False),
    sa.Column("address", sa.Text, nullable=False),
    sa.Column("cep", sa.Text, nullable=False),
    sa.Column("sector", sa.String(50), nullable=False),
    sa.Column("registration", sa.String(20), unique=True, index=True, nullable=False),
    sa.Column("daily_hours", sa.Integer, default=8, nullable=False),
    sa.Column("auto_lunch", sa.Boolean, default=True, nullable=False),
    sa.Column("lunch_duration_minutes", sa.Integer, default=60, nullable=False),
    sa.Column("status", sa.String(20), default="active", nullable=False),
    sa.Column("dismissal_date", sa.Date, nullable=True),
    sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
)