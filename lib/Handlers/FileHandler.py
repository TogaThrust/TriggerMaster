import os
from typing import Type
import pandas as pd
import numpy as np

class FileHandler:
    def __init__(self, logger, error_handler):
        self.logger = logger
        self.error_handler = error_handler
        self.df_raw = None
        self.df_cleaned = None

    def valid_path(self, file_path: str) -> bool:
        if not os.path.exists(path=file_path):
            self.error_handler.raise_error_box(error_type="Invalid File Path",
                                               log_str=f"Invalid File Path: '{file_path}'")
            return False
        return True

    def convertible_csv(self, file_path: str, have_headers: int) -> bool:
        try:
            header = None
            if have_headers:
                header = 'infer'
            df_validated = pd.read_csv(file_path, dtype=str, header=header, encoding='utf-8')
        except UnicodeDecodeError:
            self.error_handler.raise_question_box(error_type="UnicodeDecodeError")
            return False
        self.df_raw = df_validated.copy()
        return True

    @ staticmethod
    def combine_columns(df: pd.DataFrame) -> pd.DataFrame:
        concatenated_columns = []
        for i in range(0, len(df.columns), 2):
            # Concatenate two columns
            if i + 1 < len(df.columns):
                combined = df.iloc[:, i].fillna('') + '%%' + df.iloc[:, i + 1].fillna('')
            else:
                combined = df.iloc[:, i].fillna('')  # Handle odd number of columns
            concatenated_columns.append(combined)
        df_combined = pd.concat(concatenated_columns, axis=1)
        return df_combined

    @ staticmethod
    def change_file_number(file_path: str) -> str:
        try:
            while os.path.exists(file_path):
                number = int(file_path[file_path.index("(") + 1:file_path.index(")")])
                path_sections = file_path.split(f"({number})")
                file_path = f"{path_sections[0]}({number + 1}){path_sections[1]}"
            return file_path
        except ValueError:
            path_sections = file_path.split(".")
            return path_sections[0] + " (1)" + ".csv"

    def get_new_file_path(self, entry_box_path: str) -> str:
        temp_path_list = entry_box_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        if os.path.exists(new_file_path):
            return self.change_file_number(temp_path_list[0] + "_output (1)" + ".csv")
        return new_file_path

    def clean_raw_df(self, have_name_and_code: int) -> Type[AttributeError] | None:
        try:  # Raise exception when df is empty.
            df_to_clean = self.df_raw.apply(lambda col: col.dropna().reset_index(drop=True))
            max_len = df_to_clean.apply(len).max()
            df_to_clean = df_to_clean.apply(lambda col: col.reindex(range(max_len)))
        except AttributeError:
            self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
            return AttributeError
        if have_name_and_code:
            df_to_clean = self.combine_columns(df_to_clean)
        self.df_cleaned = df_to_clean.replace('%%', np.nan, regex=False)
        return None