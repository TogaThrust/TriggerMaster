import os
from typing import Type

import pandas as pd
import numpy as np

class FileHandler:
    def __init__(self, error_handler):
        self.df_raw = None
        self.df_cleaned = None
        self.error_handler = error_handler

    def validate_file_path(self, file_path: str, have_headers: bool | int) -> str | None:
        if not os.path.exists(path=file_path):
            return self.error_handler.raise_error_box(error_type="Invalid File Path",
                                                      log_str=f"Invalid File Path: '{file_path}'")
        try:
            header = None
            if have_headers:
                header = 'infer'
            df_validated = pd.read_csv(file_path, dtype=str, header=header, encoding='utf-8')
        except UnicodeDecodeError:
            return self.error_handler.raise_question_box(error_type="UnicodeDecodeError")
        self.df_raw = df_validated.copy()
        return None

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

    def clean_raw_df(self, have_name_and_code: int) -> Type[AttributeError] | None:
        # df_to_clean = pd.DataFrame()
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

    @staticmethod
    def get_new_file_path(entry_box_path: str) -> str:
        temp_path_list = entry_box_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        while os.path.exists(new_file_path):  # fixme file names checked for duplicates not very profound
            temp_path_list = new_file_path.split(".")
            new_file_path = temp_path_list[0] + "(1)" + ".csv"
        return new_file_path