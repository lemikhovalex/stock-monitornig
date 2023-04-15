import json
import typing as tp
from abc import ABC, abstractmethod

import redis.asyncio as redis


class BaseConsumer(ABC):
    @abstractmethod
    async def consume(self, **kwargs) -> None:
        ...


class RedisFieldConsumer(BaseConsumer):
    def __init__(self, host: str, port: int, connector_kwargs: dict | None = None):
        if connector_kwargs is None:
            connector_kwargs = dict()
        self.client = redis.Redis(host=host, port=port, **connector_kwargs)

    async def consume(self, data: dict):
        await self.client.mset({k: json.dumps(v) for k, v in data.items()})

    async def get(self, names: list[tp.Any]) -> tp.Any:
        resp = await self.client.mget(keys=names)
        resp = [json.loads(r) if r is not None else None for r in resp]
        return resp
