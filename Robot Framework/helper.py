import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pyarrow.parquet as pq


class WebDriverManager:
    def __init__(self, driver_type='Chrome'):
        self.driver = None
        self.driver_type = driver_type

    def __enter__(self):
        try:
            if self.driver_type == 'Chrome':
                self.driver = webdriver.Chrome()
            else:
                raise ValueError("Unsupported driver type")
            return self.driver
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
        return False


def read_html_table_to_dataframe(html_file_path: str, filter_date=None) -> pd.DataFrame:
    with WebDriverManager(driver_type='Chrome') as driver:
        try:
            full_html_path = 'file://' + os.path.abspath(html_file_path)
            driver.get(full_html_path)
            wait = WebDriverWait(driver, 10)
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table")))

            data = {}
            columns = table.find_elements(By.CLASS_NAME, "y-column")

            for col_index, column in enumerate(columns):
                try:
                    header_block = column.find_element(By.CSS_SELECTOR, "g.column-block#header")
                    header_text = header_block.text.strip() if header_block else f"Column_{col_index + 1}"
                except:
                    header_text = f"Column_{col_index + 1}"

                column_cells = []
                column_blocks = column.find_elements(By.CSS_SELECTOR, "g.column-block")

                for block in column_blocks:
                    if block.get_attribute("id") == "header":
                        continue

                    cells = block.find_elements(By.CLASS_NAME, "column-cell")
                    for cell in cells:
                        column_cells.append(cell.text.strip())

                data[header_text] = column_cells

            if not data:
                raise ValueError("No data extracted from table")

            max_len = max(len(v) for v in data.values())
            for key in data:
                if len(data[key]) < max_len:
                    data[key] = data[key] + [''] * (max_len - len(data[key]))

            table_result = pd.DataFrame(data)

            if filter_date and 'Visit Date' in table_result.columns:
                filtered_df = table_result[table_result['Visit Date'] == filter_date].copy()
            else:
                filtered_df = table_result.copy()

            if 'Average Time Spent' in filtered_df.columns:
                filtered_df['Average Time Spent'] = pd.to_numeric(
                    filtered_df['Average Time Spent'],
                    errors='coerce'
                ).fillna(0)
                filtered_df['Average Time Spent'] = filtered_df['Average Time Spent'].round(0).astype('int64')

            return filtered_df

        except TimeoutException:
            print("Error: No table element found within 10 seconds.")
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise


def read_parquet_to_dataframe(folder_path: str, filter_date=None) -> pd.DataFrame:
    try:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Parquet folder not found: {folder_path}")

        dataset = pq.ParquetDataset(folder_path)
        df = dataset.read().to_pandas()

        if filter_date:
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                df[date_col] = pd.to_datetime(df[date_col])
                filter_dt = pd.to_datetime(filter_date)
                df = df[df[date_col].dt.date == filter_dt.date()]

        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'facility' in col_lower and 'type' in col_lower:
                column_mapping[col] = 'Facility Type'
            elif 'visit' in col_lower and 'date' in col_lower:
                column_mapping[col] = 'Visit Date'
            elif 'time' in col_lower or 'avg' in col_lower or 'average' in col_lower:
                column_mapping[col] = 'Average Time Spent'

        if column_mapping:
            df = df.rename(columns=column_mapping)

        required_cols = ['Facility Type', 'Visit Date', 'Average Time Spent']
        for col in required_cols:
            if col not in df.columns:
                for actual_col in df.columns:
                    if col.lower() in actual_col.lower():
                        df = df.rename(columns={actual_col: col})
                        break

        existing_cols = [col for col in required_cols if col in df.columns]
        if existing_cols:
            df = df[existing_cols]

        if 'Average Time Spent' in df.columns:
            df['Average Time Spent'] = pd.to_numeric(df['Average Time Spent'], errors='coerce')
            df['Average Time Spent'] = df['Average Time Spent'].fillna(0)
            df['Average Time Spent'] = df['Average Time Spent'].round(0).astype('int64')

        if 'Visit Date' in df.columns:
            df['Visit Date'] = df['Visit Date'].astype(str)

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Failed to read Parquet: {e}")
        raise


def compare_dataframes(df1, df2):
    try:
        df1_clean = df1.copy().reset_index(drop=True)
        df2_clean = df2.copy().reset_index(drop=True)

        df1_clean.columns = df1_clean.columns.str.strip()
        df2_clean.columns = df2_clean.columns.str.strip()

        sort_cols = []
        if 'Facility Type' in df1_clean.columns and 'Facility Type' in df2_clean.columns:
            sort_cols.append('Facility Type')
        if 'Visit Date' in df1_clean.columns and 'Visit Date' in df2_clean.columns:
            sort_cols.append('Visit Date')

        if sort_cols:
            df1_clean = df1_clean.sort_values(by=sort_cols).reset_index(drop=True)
            df2_clean = df2_clean.sort_values(by=sort_cols).reset_index(drop=True)

        if df1_clean.shape != df2_clean.shape:
            return False, f"Shape mismatch: HTML {df1_clean.shape} vs Parquet {df2_clean.shape}"

        if list(df1_clean.columns) != list(df2_clean.columns):
            return False, f"Column mismatch: {list(df1_clean.columns)} vs {list(df2_clean.columns)}"

        differences = []
        for i in range(len(df1_clean)):
            for col in df1_clean.columns:
                val1 = df1_clean.at[i, col]
                val2 = df2_clean.at[i, col]

                if pd.isna(val1) and pd.isna(val2):
                    continue
                elif pd.isna(val1) or pd.isna(val2) or str(val1) != str(val2):
                    differences.append(f"Row {i}, '{col}': HTML='{val1}' vs Parquet='{val2}'")

        if differences:
            msg = "Differences found:\n" + "\n".join(differences[:10])
            if len(differences) > 10:
                msg += f"\n... and {len(differences) - 10} more differences"
            return False, msg

        return True, "DataFrames match exactly."

    except Exception as e:
        return False, f"Error during comparison: {str(e)}"


def get_facility_type_counts(df):
    """Return facility type counts as a dictionary"""
    if 'Facility Type' in df.columns:
        return df['Facility Type'].value_counts().to_dict()
    return {}


def get_visit_date_counts(df):
    """Return visit date counts as a dictionary"""
    if 'Visit Date' in df.columns:
        return df['Visit Date'].value_counts().to_dict()
    return {}


def get_average_time_stats(df):
    """Return average time spent statistics"""
    if 'Average Time Spent' in df.columns:
        return {
            'mean': float(df['Average Time Spent'].mean()),
            'sum': float(df['Average Time Spent'].sum()),
            'count': int(df['Average Time Spent'].count()),
            'min': float(df['Average Time Spent'].min()),
            'max': float(df['Average Time Spent'].max())
        }
    return {}


def get_missing_value_count(df):
    """Return total count of missing values"""
    return int(df.isnull().sum().sum())


def get_row_count(df):
    """Return number of rows"""
    return int(df.shape[0])


def get_column_count(df):
    """Return number of columns"""
    return int(df.shape[1])

