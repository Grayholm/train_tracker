from unittest.mock import Mock, AsyncMock

from src.services.auth import AuthService


class TestExercisesService:
    mock_db: Mock

    def setup_method(self):
        self.mock_db = Mock()
        self.mock_db.exercises = AsyncMock()
        self.mock_db.commit = AsyncMock()

        self.service = AuthService(db=self.mock_db)