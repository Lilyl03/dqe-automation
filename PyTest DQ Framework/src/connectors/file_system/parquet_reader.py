import pandas as pd
import os
from typing import List, Dict, Any


class ParquetReader:
    def __init__(self, base_path: str = "/parquet_data"):
        self.base_path = base_path

    def process(self, relative_path: str, include_subfolders: bool = False) -> List[Dict[str, Any]]:
        """Read parquet files and return as list of dictionaries"""
        try:
            full_path = os.path.join(self.base_path, relative_path)

            if include_subfolders:
                # Read all parquet files in directory and subdirectories
                all_files = []
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        if file.endswith('.parquet'):
                            all_files.append(os.path.join(root, file))

                if not all_files:
                    raise FileNotFoundError(f"No parquet files found in {full_path}")

                dfs = [pd.read_parquet(file) for file in all_files]
                combined_df = pd.concat(dfs, ignore_index=True)
            else:
                if os.path.isdir(full_path):
                    combined_df = pd.read_parquet(full_path)
                else:
                    combined_df = pd.read_parquet(full_path + '.parquet')

            return combined_df.to_dict('records')

        except Exception as e:
            raise Exception(f"Failed to read parquet files: {e}")