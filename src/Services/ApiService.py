import requests
import os
import csv
import threading

from sys import stderr
from datetime import datetime

from src.Models.Todo import Todo


API_ENDPOINT = "https://jsonplaceholder.typicode.com/todos/"
STORAGE_FOLDER_PATH = "./storage"


class ApiService:
    def __init__(self):
        pass

    def run(self):
        print('Running ApiService')
        todos = self.fetch_todos()
        self.process_write_threaded(todos)
        print('ApiService runned successfully')

    def fetch_todos(self):
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()
        todos = response.json()
        return [Todo(**todo) for todo in todos]

    def process_write_threaded(self, todos: list[Todo]):
        """ Multi threading isn't really necessary here, but it still offers
        a nice perfmance improvment in relative terms"""
        threads = []
        for todo in todos:
            thread = threading.Thread(target=self.write_to_csv, args=(todo,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def write_to_csv(self, todo: Todo):
        fields = todo.model_fields.keys()
        fname = self.get_file_name(todo.id)
        fpath = os.path.join(STORAGE_FOLDER_PATH,  fname)
        test = STORAGE_FOLDER_PATH / fname
        print(test)
        try:
            with open(fpath, "w", newline="") as csvf:
                writer = csv.DictWriter(csvf, fieldnames=fields)
                writer.writeheader()
                writer.writerow(todo.model_dump())
        except IOError as e:
            print(f"Error writing to CSV: {e}", file=stderr)

    def get_file_name(self, id: int) -> str:
        date = datetime.now().strftime('%Y_%m_%d')
        return f"{date}_{id}.csv"
