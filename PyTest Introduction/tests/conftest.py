import pytest
import csv
import os
from typing import List, Dict



# Fixture to read the CSV file
@pytest.fixture(scope="session")
def csv_data():
    def _read_csv(file_path: str) -> List[Dict]:
        if not os.path.exists(file_path):
            pytest.fail(f"CSV file not found at path: {file_path}")

        data = []
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)

        if not data:
            pytest.fail("CSV file is empty")

        return data

    return _read_csv

@pytest.fixture(scope="session")
def csv_file_path():
    return "src/data/data.csv"

# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def validate_schema():
    def _validate_schema(actual_schema: List[str], expected_schema: List[str]) -> bool:
        if set(actual_schema) != set(expected_schema):
            missing = set(expected_schema) - set(actual_schema)
            extra = set(actual_schema) - set(expected_schema)
            error_msg = f"Schema validation failed. Missing columns: {missing}, Extra columns: {extra}"
            pytest.fail(error_msg)
        return True

    return _validate_schema

@pytest.fixture(scope="session")
def expected_schema():
    #return ["id", "name", "age", "email", "is_active"]
    return ["id", "name", "age", "email"]



# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(config, items):
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)






