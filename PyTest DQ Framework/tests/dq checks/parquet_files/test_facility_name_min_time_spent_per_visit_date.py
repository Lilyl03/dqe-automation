"""
Description: Data Quality checks for facility_name_min_time_spent_per_visit_date dataset
Requirement(s): Validate transformation from PostgreSQL to Parquet files
Author(s): Lilit Levonyan
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    SELECT 
        f.facility_name,
        DATE(v.visit_timestamp) as visit_date,
        MIN(v.duration_minutes) as min_time_spent
    FROM visits v
    JOIN facilities f ON v.facility_id = f.id  -- CHANGED THIS LINE
    GROUP BY f.facility_name, DATE(v.visit_timestamp)
    ORDER BY f.facility_name, visit_date
    """
    source_data = db_connection.get_data_sql(source_query)
    return source_data

@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = 'facility_name_min_time_spent_per_visit_date'
    target_data = parquet_reader.process(target_path, include_subfolders=True)
    return target_data


# Smoke Tests
@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_source_dataset_is_not_empty(source_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(source_data)


@pytest.mark.skip(reason="Expected data transformation difference - for homework demonstration")
@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_data_full_data_set(source_data, target_data, data_quality_library):
    data_quality_library.check_data_full_data_set(source_data, target_data)


# Data Quality Tests
@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(
        target_data,
        ['facility_name', 'visit_date', 'min_time_spent']
    )

@pytest.mark.skip(reason="Expected duplicate data in aggregation - for homework demonstration")
@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_uniqueness(target_data, data_quality_library):
    data_quality_library.check_duplicates(
        target_data,
        ['facility_name', 'visit_date']
    )


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_source_not_null_values(source_data, data_quality_library):
    data_quality_library.check_not_null_values(
        source_data,
        ['facility_name', 'visit_date', 'min_time_spent']
    )