from src.repositories.exercises import ExercisesRepository
from src.repositories.users import UsersRepository
from src.repositories.workouts import WorkoutsRepository, WorkoutExerciseRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.workouts = WorkoutsRepository(self.session)
        self.workout_exercises = WorkoutExerciseRepository(self.session)
        self.exercises = ExercisesRepository(self.session)

        return self

    async def __aexit__(self, *args):
        if self.session is not None:
            await self.session.rollback()
            await self.session.close()

    async def commit(self):
        if self.session is not None:
            await self.session.commit()
        else:
            raise RuntimeError("Session is not initialized")
