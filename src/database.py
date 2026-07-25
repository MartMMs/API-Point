import databases
import sqlalchemy as sa
from config import settings

database = databases.Database(settings.database_url)
metadata = sa.MetaData()

if settings.environment == "production":
    engine = sa.create_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=20,
    )
else:
    engine = sa.create_engine(
        settings.database_url,
        echo=True
    )