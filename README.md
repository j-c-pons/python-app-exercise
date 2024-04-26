# Python App Exercise

## App setup

# Virtual environment

```
cd <Your_path>/python-app-exercise
python -m venv env
env\Scripts\activate (Windows)/ env/bin/activate (Unix, MacOS)
pip install -r requirements.txt
```

# Main script

```
python main.py
```

# Testing

```
python -m unittest tests/test_api_service.py
```

## Exercise

- Use the ApiService to fetch TODOs from an API and save them into the _storage_ folder
  - TODOs can be accessed from this URL: https://jsonplaceholder.typicode.com/todos/
  - Each TODO should be saved on a single file in CSV format
  - The filename must contain the TODO "id" prefixed with the current date.
    - Example: 2021_04_28_123.csv

## Extra points

- Use _requests_ library from [PyPI](https://pypi.org/project/requests/)
