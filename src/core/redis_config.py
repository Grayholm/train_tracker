import json
import redis.asyncio as redis
import logging


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        logging.info(f"Начинаю подключение к Redis host={self.host}, port={self.port}")
        self.redis = await redis.Redis(host=self.host, port=self.port)
        logging.info(f"Успешное подключение к Redis host={self.host}, port={self.port}")

    async def set(self, key: str, value: str, expire: int = 3600):
        value_schemas: list[dict] = [f.model_dump() for f in value]
        value_json = json.dumps(value_schemas)
        await self.redis.set(key, value=value_json, ex=expire)

    async def get(self, key: str):
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()


# Пример использования:
# redis_manager = RedisManager(redis_url="redis://localhost")
# await redis_manager.connect()
# await redis_manager.set("key", "value", expire=60)
# value = await redis_manager.get("key")
# await redis_manager.delete("key")
# await redis_manager.close()