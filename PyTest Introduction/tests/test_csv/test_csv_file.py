import pytest
import re
import pytest
import csv
import os
from typing import List, Dict


def read_csv_data(file_path: str = "src/data/data.csv") -> List[Dict]:
    if not os.path.exists(file_path):
        pytest.fail(f"CSV file not found at path: {file_path}")

    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)

    return data


def test_file_not_empty():
    data = read_csv_data()
    assert len(data) > 0, "CSV file should not be empty"


@pytest.mark.xfail
def test_duplicates():
    data = read_csv_data()
    seen_rows = set()
    duplicates = []

    for i, row in enumerate(data, start=2):
        row_identifier = (row['id'], row['name'], row['age'], row['email'], row['is_active'])
        if row_identifier in seen_rows:
            duplicates.append(f"Row {i}: Duplicate row found - ID: {row['id']}, Name: {row['name']}")
        seen_rows.add(row_identifier)

    assert len(duplicates) == 0, f"Duplicate rows found: {duplicates}"

#Validate the schema of the file (id, name, age, email). Honestly I don't know if I should
#add is_active because with it it was not failing but without it it is failing
#so I will just leave it as a comment


@pytest.mark.validate_csv
def test_validate_schema():
    data = read_csv_data()
    expected_schema = ["id", "name", "age", "email"]

    if not data:
        pytest.fail("CSV file is empty")

    actual_schema = list(data[0].keys())

    missing_columns = set(expected_schema) - set(actual_schema)
    extra_columns = set(actual_schema) - set(expected_schema)

    assert len(missing_columns) == 0, f"Missing columns: {missing_columns}"
    assert len(extra_columns) == 0, f"Extra columns: {extra_columns}"


# @pytest.mark.validate_csv
# def test_validate_schema():
#     data = read_csv_data()
#     expected_schema = ["id", "name", "age", "email", "is_active"]
#
#     if not data:
#         pytest.fail("CSV file is empty")
#
#     actual_schema = list(data[0].keys())
#
#     missing_columns = set(expected_schema) - set(actual_schema)
#     extra_columns = set(actual_schema) - set(expected_schema)
#
#     assert len(missing_columns) == 0, f"Missing columns: {missing_columns}"
#     assert len(extra_columns) == 0, f"Extra columns: {extra_columns}"

@pytest.mark.validate_csv
@pytest.mark.skip
def test_age_column_valid():
    data = read_csv_data()
    invalid_ages = []

    for i, row in enumerate(data, start=2):
        try:
            age = int(row['age'])
            if not (0 <= age <= 100):
                invalid_ages.append(f"Row {i}: Age '{age}' is not between 0-100")
        except ValueError:
            invalid_ages.append(f"Row {i}: Age '{row['age']}' is not a valid integer")

    assert len(invalid_ages) == 0, f"Invalid age values found: {invalid_ages}"


@pytest.mark.validate_csv
def test_email_column_valid():
    data = read_csv_data()
    invalid_emails = []

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    for i, row in enumerate(data, start=2):
        email = row['email'].strip()
        if not re.match(email_pattern, email):
            invalid_emails.append(f"Row {i} (id={row['id']}): Email '{email}' has invalid format")

    assert len(invalid_emails) == 0, f"Invalid email formats found: {invalid_emails}"


@pytest.mark.parametrize("id_value,is_active", [
    ("1", "False"),
    ("2", "True"),
])
def test_active_players(id_value, is_active):
    data = read_csv_data()

    matching_rows = [row for row in data if row['id'] == id_value]
    assert len(matching_rows) > 0, f"No row found with id={id_value}"

    actual_active = matching_rows[0]['is_active']
    assert actual_active == is_active, f"Expected is_active={is_active} for id={id_value}, but got {actual_active}"


def test_active_player():
    data = read_csv_data()

    matching_rows = [row for row in data if row['id'] == '2']
    assert len(matching_rows) > 0, "No row found with id=2"

    actual_active = matching_rows[0]['is_active']
    expected_active = "True"
    assert actual_active == expected_active, f"Expected is_active={expected_active} for id=2, but got {actual_active}"
