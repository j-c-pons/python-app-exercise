import unittest

from unittest.mock import patch, MagicMock
from datetime import datetime
from io import StringIO
from pydantic import ValidationError

from src.Services.ApiService import ApiService, STORAGE_FOLDER
from src.Models.Todo import Todo

TEST_TODO_DATA = [
                {
                    "userId": 1,
                    "id": 1,
                    "title": "delectus aut autem",
                    "completed": False
                },
                {
                    "userId": 1,
                    "id": 2,
                    "title": "quis ut nam facilis et officia qui",
                    "completed": False,
                },
            ]

TEST_TODO_DATA_INVALID = [
                {
                    "userId": "wrong data",
                    "id": 1,
                    "title": "delectus aut autem",
                    "completed": 3
                },
            ]


class TestApiService(unittest.TestCase):
    api_service = ApiService()

    @patch('src.Services.ApiService.requests.get')
    def test_fetch_todos(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = TEST_TODO_DATA
        mock_get.return_value = mock_response

        todos = self.api_service.fetch_todos()

        self.assertIsInstance(todos[0], Todo)
        self.assertEqual(len(todos), 2)

    @patch('src.Services.ApiService.requests.get')
    def test_fetch_todos_invalid_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = TEST_TODO_DATA_INVALID
        mock_get.return_value = mock_response

        # Asserting that fetch_todos raises a  pydantic ValidationError
        with self.assertRaises(ValidationError):
            self.api_service.fetch_todos()

    def test_process_write_threaded(self):
        with patch.object(self.api_service, 'write_to_csv', MagicMock()):
            mocked_todos = [MagicMock() for _ in range(5)]

            self.api_service.process_write_threaded(mocked_todos)

            # Assert that write_to_csv was called once for each Todo object
            self.assertEqual(
                self.api_service.write_to_csv.call_count,
                len(mocked_todos)
            )

    @patch('src.Services.ApiService.datetime')
    @patch('src.Services.ApiService.stderr', new_callable=StringIO)
    @patch('src.Services.ApiService.open', create=True)
    def test_write_to_csv(self, mock_open, mock_stderr, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 4, 30)
        todo = Todo(**TEST_TODO_DATA[0])

        self.api_service.write_to_csv(todo)

        # Verify that the open function is called with the correct arguments
        mock_open.assert_called_once_with(
            STORAGE_FOLDER / "2024_04_30_1.csv",
            "w",
            newline=""
        )

        # Assert that write() has been called twice (1 for headers, 1 for row)
        self.assertEqual(
            mock_open.return_value.__enter__.return_value.write.call_count,
            2
        )
        self.assertEqual(mock_stderr.getvalue(), "")


if __name__ == '__main__':
    unittest.main()
