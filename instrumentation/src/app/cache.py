from dataclasses import dataclass
import json
from typing import Optional, Union

import redis.asyncio as redis

from app import app_config


CacheValue = Union[str, int, bool, dict, float]


@dataclass
class RedisClient:
    client: redis.Redis

    async def set_key(self, key: str, value: CacheValue, ttl: Optional[int] = None) -> None:
        prefix = app_config.project_id
        if isinstance(value, dict):
            value = json.dumps(value)

        await self.client.set(f"{prefix}__{key}", value, ex=ttl)

    async def get_key(self, key: str) -> Optional[CacheValue]:
        prefix = app_config.project_id

        return await self.client.get(f"{prefix}__{key}")

    async def close(self) -> None:
        await self.client.close()

    async def flush_all(self) -> None:
        await self.client.flushall()


def get_redis_client() -> RedisClient:
    """Returns a RedisClient which is a wrapper over aioredis standard client"""
    redis_client = redis.from_url(app_config.redis.uri)

    return RedisClient(redis_client)
