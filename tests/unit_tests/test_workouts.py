from src.services.workouts import WorkoutsService
from tests.base_test import BaseTestService


class TestWorkoutsService(BaseTestService):
    service_name = WorkoutsService

    def setup_method(self):
        super().setup_method()
        self.service = WorkoutsService(db=self.mock_db)

    async def test_get_workouts(self):
        pass

    async def test_get_workout(self):
        pass

    async def test_get_workout_obj_bot_found_failure(self):
        pass

    async def test_add_workout(self):
        pass

    async def test_add_workout_obj_bot_found_failure(self):
        pass

    async def test_add_exercises_to_workout(self):
        pass

    async def test_add_exercises_to_workout_obj_bot_found_failure(self):
        pass

    async def test_add_exercises_to_workout_access_denied_failure(self):
        pass

    async def test_delete_workout(self):
        pass

    async def test_delete_workout_obj_bot_found_failure(self):
        pass

    async def test_partially_update_workout(self):
        pass

    async def test_partially_update_workout_obj_bot_found_failure(self):
        pass

    async def test_partially_update_workout_data_is_empty_failure(self):
        pass