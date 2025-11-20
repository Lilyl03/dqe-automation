import pandas as pd


class DataQualityLibrary:

    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            duplicates = df.duplicated(subset=column_names)
        else:
            duplicates = df.duplicated()

        duplicate_count = duplicates.sum()
        assert duplicate_count == 0, f"Found {duplicate_count} duplicate rows"

    @staticmethod
    def check_count(df1, df2):
        count1 = len(df1)
        count2 = len(df2)
        assert count1 == count2, f"Row count mismatch: Source={count1}, Target={count2}"

    @staticmethod
    def check_data_full_data_set(df1, df2):
        for col in df1.columns:
            if 'date' in col.lower():
                df1[col] = pd.to_datetime(df1[col])
                df2[col] = pd.to_datetime(df2[col])
        merged = pd.merge(df1, df2, how='left', indicator=True)
        missing_rows = merged[merged['_merge'] == 'left_only']

        missing_count = len(missing_rows)
        assert missing_count == 0, f"Found {missing_count} rows missing in target data"

    @staticmethod
    def check_dataset_is_not_empty(df):
        assert len(df) > 0, "Dataset is empty"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        for column in column_names:
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame")

            null_count = df[column].isnull().sum()
            assert null_count == 0, f"Column '{column}' has {null_count} null values"
