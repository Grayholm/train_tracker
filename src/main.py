import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.staticfiles import StaticFiles

sys.path.append(str(Path(__file__).parent.parent))

from src.core.redis_manager import redis_manager
from src.api.auth import router as router_auth
from src.api.exercises import router as router_exercises
from src.api.workouts import router as router_workouts


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI Cache connection initialized")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src"), name="static")

app.include_router(router_auth)
app.include_router(router_exercises)
app.include_router(router_workouts)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
