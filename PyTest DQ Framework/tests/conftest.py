import pytest
from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.data_quality.data_quality_validation_library import DataQualityLibrary
from src.connectors.file_system.parquet_reader import ParquetReader

def pytest_addoption(parser):
    parser.addoption("--db_host", action="store", default="localhost", help="Database host")
    parser.addoption("--db_port", action="store", default="5432", help="Database port")
    parser.addoption("--db_name", action="store", default="mydatabase", help="Database name")
    parser.addoption("--db_user", action="store", help="Database user (required)")
    parser.addoption("--db_password", action="store", help="Database password (required)")


def pytest_configure(config):
    required_options = ["--db_user", "--db_password"]
    for option in required_options:
        if not config.getoption(option):
            pytest.fail(f"Missing required option: {option}")


@pytest.fixture(scope='session')
def db_connection(request):
    db_host = request.config.getoption("--db_host")
    db_name = request.config.getoption("--db_name")
    db_port = request.config.getoption("--db_port")
    db_user = request.config.getoption("--db_user")
    db_password = request.config.getoption("--db_password")

    try:
        with PostgresConnectorContextManager(
            db_host=db_host,
            db_name=db_name,
            db_port=int(db_port),
            db_user=db_user,
            db_password=db_password
        ) as db_connector:
            yield db_connector
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnectorContextManager: {e}")


@pytest.fixture(scope='session')
def parquet_reader():
    try:
        reader = ParquetReader()
        yield reader
    except Exception as e:
        pytest.fail(f"Failed to initialize ParquetReader: {e}")


@pytest.fixture(scope='session')
def data_quality_library():
    try:
        dq_library = DataQualityLibrary()
        yield dq_library
    except Exception as e:
        pytest.fail(f"Failed to initialize DataQualityLibrary: {e}")