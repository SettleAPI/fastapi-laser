from typing import Sequence, Union

import sqlalchemy.ext.asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.orm

from app import app_config
from app.models.base_model import Base


engine = sqlalchemy.ext.asyncio.create_async_engine(app_config.postgres.uri, pool_pre_ping=True)
SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def as_committed(obj: Union[Base, Sequence[Base]], session: AsyncSession) -> Union[Base, Sequence[Base]]:
    await add_and_commit(obj, session)
    # TODO: add check for instanceof list

    if isinstance(obj, Base):
        await session.refresh(obj)
    else:
        for o in obj:
            # TODO: find a way to perform this as a bulk transaction
            await session.refresh(o)

    return obj


async def add_and_commit(obj: Union[Base, Sequence[Base]], session: AsyncSession) -> None:
    adder = session.add if isinstance(obj, Base) else session.add_all
    adder(obj)
    await session.commit()
