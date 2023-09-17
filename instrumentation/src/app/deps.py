from typing import Callable, Generator, Optional

from fastapi import Header, HTTPException, Request, status
from fastapi.security import HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from loguru import logger
import sqlalchemy.ext.asyncio
from starlette.websockets import WebSocket

import app.database.session

from . import app_config, cache


async def db_session() -> Generator[sqlalchemy.ext.asyncio.AsyncSession, None, None]:
    session_ = None
    try:
        session_ = app.database.session.SessionLocal()
        yield session_
    finally:
        if session_ is not None:
            await session_.close()


def verify_sa_identity(sa_email: str) -> Callable:
    async def verify_identity(request: Request) -> None:
        if app_config.environment in ("local", "test"):
            return

        http_bearer = HTTPBearer()
        http_authorization_credentials = await http_bearer(request)
        try:
            id_info = id_token.verify_oauth2_token(
                http_authorization_credentials.credentials,
                request=requests.Request(),
                audience=str(request.url.replace(scheme="https")),
            )
            if id_info["email"] != sa_email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Unauthorized. Email does not match. Given email: {id_info['email']}",
                )

        except ValueError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return verify_identity


def ws_verify_sa_identity(sa_email: str) -> Callable:
    async def verify_identity(websocket: WebSocket, authorization: Optional[str] = Header(None)) -> bool:
        if app_config.environment in ("local", "test"):
            return True

        if authorization is None:
            logger.error("Authorization header is not present")
            return False

        bearer, _, token = authorization.partition(" ")
        if bearer.lower() != "bearer" or token == "":
            logger.error(f"Invalid token received. token: {authorization}")
            return False

        try:
            id_info = id_token.verify_oauth2_token(
                token,
                request=requests.Request(),
                audience=str(websocket.url.replace(scheme="wss")),
            )
            if id_info["email"] != sa_email:
                logger.error(f"Invalid email on authorization. expected: {sa_email}, received: {id_info['email']}")
                return False

        except ValueError as ex:
            logger.error(f"Unexpected verify token. Err: {repr(ex)}")
            return False

        return True

    return verify_identity


async def redis_session() -> Generator[cache.RedisClient, None, None]:
    redis_client = None

    try:
        redis_client = cache.get_redis_client()
        yield redis_client
    finally:
        if redis_client is not None:
            await redis_client.close()


async def lock_for_migration():
    raise HTTPException(503, detail="Service locked for migration, try again soon.")
