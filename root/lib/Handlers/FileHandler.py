import os
import pandas as pd
import numpy as np

class FileHandler:
    def __init__(self, logger, error_handler):
        self.logger = logger
        self.error_handler = error_handler
        self.df_raw = None
        self.df_cleaned = None

    @ staticmethod
    def _change_file_number(file_path: str) -> str:
        # Managed to recreate what Windows does with old file names with a bit of brainstorming.
        try:
            while os.path.exists(file_path):
                number = int(file_path[file_path.index("(") + 1:file_path.index(")")])
                path_sections = file_path.split(f"({number})")
                file_path = f"{path_sections[0]}({number + 1}){path_sections[1]}"
            return file_path
        except ValueError:
            path_sections = file_path.split(".")
            return path_sections[0] + " (1)" + ".csv"

    def valid_path(self, file_path: str) -> bool:
        if not os.path.exists(path=file_path):
            self.error_handler.raise_error_box(error_type="Invalid File Path",
                                               log_str=f"Invalid File Path: '{file_path}'")
            return False
        return True

    def get_new_file_path(self, entry_box_path: str) -> str:
        """Generates write path from read path."""
        temp_path_list = entry_box_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        if os.path.exists(new_file_path):
            return self._change_file_number(temp_path_list[0] + "_output (1)" + ".csv")
        return new_file_path

    def _remove_last_two_nan_columns(self, df: pd.DataFrame) -> pd.DataFrame | bool:
        """Removes the last 2 columns if they are blank."""
        # Have to write this as input file has a pre-set format.
        if df.shape[1] >= 2:
            if df.iloc[:, -2:].isna().all().all():
                df = df.iloc[:, :-2]
                self.logger.log("Empty date columns identified and removed.", log_type="record")
            else:
                user_input = self.error_handler.raise_question_box(error_type="DateIdentifierWarning")
                if user_input == "cancel":
                    return False
        return df

    def convertible_file(self, file_path: str) -> bool:
        """Handles any cases where data cannot be converted into a numpy DataFrame object."""
        df_validated = pd.DataFrame()
        try:
            header = None
            if file_path.endswith('.csv'):
                df_validated = pd.read_csv(file_path, dtype=str, header='infer', encoding='utf-8')
            elif file_path.endswith('.xlsx'):
                df_validated = pd.read_excel(file_path, dtype=str, header=0, sheet_name = 'Sheet1')
        except UnicodeDecodeError or ValueError:
            self.error_handler.raise_error_box(error_type="UnicodeDecodeError", log_str=None)
            return False
        except pd.errors.EmptyDataError:
            self.error_handler.raise_error_box(error_type="EmptyDataError", log_str=None)
            return False
        if not isinstance(self._remove_last_two_nan_columns(df_validated), pd.DataFrame):
            return False
        self.df_raw = df_validated.copy()
        return True

    def _get_expected_output(self, df) -> None:
        """Product of len of each column."""
        number_in_column = df.notna().sum()
        expected_combinations = number_in_column.prod()
        self.expected_output = expected_combinations
        return None

    # Raise exception when data to process is too large.
    def _limit_check(self, warning_limit: int = 1_000_000) -> str | None:
        """Warns users if processing will take longer. Totally necessary."""
        self._get_expected_output(self.df_cleaned)
        if self.expected_output > warning_limit:
            user_input = self.error_handler.raise_question_box(error_type="LimitWarning")
            self.logger.log(log_str="Data exceeds output limit."
                                    + "Recommended to reduce number of dimensions or rows of data.", log_type="record")
            if user_input == "cancel":
                return user_input
        self.logger.log(log_str=f"{self.expected_output} rows expected.", log_type="record")
        return None

    def _combine_columns(self, df: pd.DataFrame) -> pd.DataFrame | bool:
        """For every 2 columns that is not named 'Level' or 'Account', we concat them with a '%%' seperator.
            This ensures that when we run the generator to get the product, there will not be mismatching."""
        concatenated_columns = []
        for i in range(0, len(df.columns), 2):
            if len(df.columns) % 2 != 0: # check number of columns is even
                self.error_handler.raise_error_box(error_type="RuntimeError", log_str=None)
                return False
            col_name = df.columns[i]
            if col_name in ["Account", "Level Code"]:
                concatenated_columns.append(df.iloc[:, i])
                if i + 1 < len(df.columns):  # Also append the next column if it exists
                    concatenated_columns.append(df.iloc[:, i + 1])
            else:
                combined = df.iloc[:, i] + '%%' + df.iloc[:, i + 1]
                concatenated_columns.append(combined)
        df_combined = pd.concat(concatenated_columns, axis=1)
        df_combined = df_combined.iloc[:, :-1]
        return df_combined

    def df_cleanable(self) -> bool:
        try:
            df_to_clean = self.df_raw.apply(lambda col: col.dropna().reset_index(drop=True))
            max_len = df_to_clean.apply(len).max()
            df_to_clean = df_to_clean.apply(lambda col: col.reindex(range(max_len)))
        except ValueError: # Raise exception when df is empty.
            self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
            return False
        df_to_clean = self._combine_columns(df_to_clean)
        if not isinstance(df_to_clean, pd.DataFrame):
            return False
        self.df_cleaned = df_to_clean.replace('%%', np.nan, regex=False)
        self.df_cleaned = self.df_cleaned.infer_objects(copy=False)
        self._limit_check()
        return True