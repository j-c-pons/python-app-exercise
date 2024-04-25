import unittest
import os

from unittest.mock import patch, MagicMock
from datetime import datetime
from io import StringIO

from src.Services.ApiService import ApiService, STORAGE_FOLDER_PATH
from src.Models.Todo import Todo


class TestApiService(unittest.TestCase):
    api_service = ApiService()

    @patch('src.Services.ApiService.requests.get')
    def test_fetch_todos(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "userId": 1,
                "id": 1,
                "title": "delectus aut autem",
                "completed": False},
            {
                "userId": 1,
                "id": 2,
                "title": "quis ut nam facilis et officia qui",
                "completed": False,
            },
        ]
        mock_get.return_value = mock_response

        todos = self.api_service.fetch_todos()

        self.assertIsInstance(todos[0], Todo)
        self.assertEqual(len(todos), 2)

    def test_process_write_threaded(self):
        # Mock the write_to_csv method to do nothing
        self.api_service.write_to_csv = MagicMock()
        todos = [MagicMock() for _ in range(5)]  # Create 5 mock Todo objects
        
        self.api_service.process_write_threaded(todos)

        # Assert that write_to_csv was called once for each Todo object
        self.assertEqual(self.api_service.write_to_csv.call_count, len(todos))

    @patch('src.Services.ApiService.datetime')
    @patch('src.Services.ApiService.stderr', new_callable=StringIO)
    @patch('src.Services.ApiService.open', create=True)
    def test_write_to_csv(self, mock_open, mock_stderr, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 4, 30)
        todo = Todo(userId=1, id=1, title="Test", completed=False)

        self.api_service.write_to_csv(todo)

        # Verify that the open function is called with the correct arguments
        mock_open.assert_called_once_with(
            os.path.join(STORAGE_FOLDER_PATH, "2024_04_30_1.csv"),
            "w",
            newline=""
        )

        self.assertEqual(mock_stderr.getvalue(), "")

    def test_get_file_name(self):
        # Test cases with different Todo IDs and current date
        test_cases = [
            (1, "2024_05_01_1.csv"),
            (10, "2024_05_01_10.csv"),
            (100, "2024_05_01_100.csv")
        ]

        # Iterate over test cases and verify the generated file names
        for todo_id, expected_file_name in test_cases:
            with self.subTest(todo_id=todo_id):
                generated_file_name = self.api_service.get_file_name(todo_id)
                self.assertEqual(generated_file_name, expected_file_name)


if __name__ == '__main__':
    unittest.main()
