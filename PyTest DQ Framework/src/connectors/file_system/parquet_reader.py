import pandas as pd
import os
from typing import List, Optional


class ParquetReader:
    def __init__(self, base_path: str = "/parquet_data"):
        self.base_path = base_path

    def process(self, relative_path: str, include_subfolders: bool = False) -> pd.DataFrame:
        full_path = os.path.join(self.base_path, relative_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Path does not exist: {full_path}")

        if os.path.isfile(full_path):
            return pd.read_parquet(full_path, engine='auto')  # 'auto' will use available engine
        else:
            return self._read_directory(full_path, include_subfolders)

    def _read_directory(self, directory_path: str, include_subfolders: bool) -> pd.DataFrame:
        parquet_files = []

        if include_subfolders:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.parquet'):
                        parquet_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                if file.endswith('.parquet'):
                    parquet_files.append(os.path.join(directory_path, file))

        if not parquet_files:
            raise FileNotFoundError(f"No Parquet files found in: {directory_path}")

        dataframes = []
        for file_path in parquet_files:
            df = pd.read_parquet(file_path, engine='auto')
            dataframes.append(df)

        return pd.concat(dataframes, ignore_index=True)