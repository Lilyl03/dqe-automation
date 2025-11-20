import psycopg2
import pandas as pd
class PostgresConnectorContextManager:
    def __init__(self, db_host: str, db_name: str, db_port: int, db_user: str, db_password: str):
        # init
        self.db_host = db_host
        self.db_name = db_name
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.connection = None
        self.cursor = None

    def __enter__(self):
        # create conn
        try:
            self.connection = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password
            )
            self.cursor = self.connection.cursor()
            return self
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")

    def __exit__(self, exc_type, exc_value, exc_tb):
        # close conn
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def get_data_sql(self, sql):
        # exec query, result = pandas df
        if not self.connection:
            raise RuntimeError("Database connection not established")

        try:
            self.cursor.execute(sql)
            columns = [desc[0] for desc in self.cursor.description]
            data = self.cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")


