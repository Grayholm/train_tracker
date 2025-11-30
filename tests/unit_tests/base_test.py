from unittest.mock import Mock, AsyncMock


class BaseTestService:

    def setup_method(self):
        self.mock_db = Mock()
        self.mock_db.users = AsyncMock()
        self.mock_db.commit = AsyncMock()

        self.mock_serializer = Mock()
        self.mock_serializer.dumps.return_value = "TOK123"