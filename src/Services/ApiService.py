import requests
import csv
import concurrent.futures

from sys import stderr
from datetime import datetime
from pathlib import Path

from src.Models.Todo import Todo

API_ENDPOINT = "https://jsonplaceholder.typicode.com/todos/"
STORAGE_FOLDER = Path("./storage")


class ApiService:
    def __init__(self):
        pass

    def run(self):
        print('Running ApiService', file=stderr)
        todos = self.fetch_todos()
        self.process_write_threaded(todos)
        print('ApiService runned successfully')

    def fetch_todos(self) -> list[Todo]:
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()
        todos = response.json()
        return [Todo(**todo) for todo in todos]

    def process_write_threaded(self, todos: list[Todo]):
        """ Multi threading isn't really necessary here, but it still offers
        a significant performance improvment"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.write_to_csv, todo) for todo in todos
            ]
            self.handle_futures(futures)

    def write_to_csv(self, todo: Todo):
        fields = todo.model_fields.keys()
        fname = self.get_file_name(todo.id)
        fpath = STORAGE_FOLDER / fname
        try:
            with open(fpath, "w", newline="") as csvf:
                writer = csv.DictWriter(csvf, fieldnames=fields)
                writer.writeheader()
                writer.writerow(todo.model_dump())
        except IOError as e:
            print(f"Error writing to CSV: {e}, File: {fpath}", file=stderr)

    def get_file_name(self, id: int) -> str:
        date = datetime.now().strftime('%Y_%m_%d')
        return f"{date}_{id}.csv"

    def handle_futures(self, futures: list):
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error: {e}", file=stderr)
