from app.core.db.session import engine
from app.api.v1.models.models import Base


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
