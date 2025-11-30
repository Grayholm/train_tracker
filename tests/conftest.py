# #type: noqa: F401

# import pytest
# from src.core.config import Settings
# from src.core.db import Base
# from src.core.db import engine
# from src.models import (
#     ExercisesModel,
#     WorkoutsModel,
#     WorkoutExerciseModel,
#     UsersModel,
# )


# @pytest.fixture(scope="session", autouse=True)
# async def async_main():
#     assert Settings.MODE == "TEST"
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#         await conn.run_sync(Base.metadata.drop_all)