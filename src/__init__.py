from src.core.config import settings
from src.core.redis_config import RedisManager

redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)