import itertools
import pandas as pd
import time
from typing import Type
from multiprocessing import Pool, cpu_count

class CombinationsGenerator:
    def __init__(self, logger, error_handler):
        self.logger = logger
        self.error_handler = error_handler
        self.process_thread = None
        self.expected_output = 0
        self.total_processed = 0
        self.write_path = ""
        self.error_flag = False

    def get_expected_output(self, df) -> None:
        number_in_column = df.notna().sum()
        expected_combinations = number_in_column.prod()
        self.expected_output = expected_combinations
        return None

    # Raise exception when data to process is too large.
    def limit_check(self, df, warning_limit: int = 1_000_000) -> str | None:
        self.get_expected_output(df)
        if self.expected_output > warning_limit:
            return self.error_handler.raise_question_box(error_type="LimitWarning")
        return None

    @ staticmethod
    def split_columns(df: pd.DataFrame) -> pd.DataFrame | Type[AttributeError | TypeError]:
        df_split = pd.DataFrame()
        try:
            for col in df.columns:
                split_cols = df[col].str.split('%%', expand=True)
                split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                df_split = pd.concat([df_split, split_cols], axis=1)
        except AttributeError: # Probably got to do with UTC-8 conversion
            return AttributeError
        except TypeError: # Mismatch between two columns
            return TypeError
        return df_split

    @ staticmethod
    def process_chunk(columns, start: int, end: int):
        generator = itertools.product(*columns)
        chunk = list(itertools.islice(generator, start, end))
        processed_chunk = [list(combo) for combo in chunk] # Convert tuples to lists
        df_output = pd.DataFrame(processed_chunk)
        df_output.dropna(inplace=False)
        return df_output

    def thread_handler(self, df, original_columns: list , have_name_and_code: int, enable_buttons,
                       chunk_size: int = 100_000) -> None | str | Type[AttributeError | TypeError]:
        start_time = time.perf_counter()
        self.total_processed = 0
        columns = [df[col].dropna().unique() for col in df.columns]
        chunk_ranges = [(i, min(i + chunk_size, self.expected_output)) for i in range(0, self.expected_output, chunk_size)]
        with Pool(cpu_count()-1) as pool:
            results = pool.starmap(self.process_chunk, [(columns, start, end) for start, end in chunk_ranges])
        with open(self.write_path, mode='w', newline='', encoding='utf-8-sig') as file:
            for i, df_output in enumerate(results):
                if have_name_and_code:
                    df_output = self.split_columns(df_output)
                    if type(df_output) == pd.DataFrame:
                        df_output.columns = original_columns
                    else: # pandas df have typing issues :(
                        self.error_flag = True
                        if df_output == AttributeError:
                            self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
                            return AttributeError
                        elif df_output == TypeError:
                            self.error_handler.raise_error_box(error_type="RuntimeError", log_str=None)
                            return TypeError
                df_output.to_csv(file, header=(i == 0), index=False, encoding='utf-8-sig')
                self.total_processed += df_output.shape[0]
                percentage_complete = round((self.total_processed / self.expected_output) * 100, 2)
                self.logger.log(log_str=f"{percentage_complete}% complete.", log_type="update")
        end_time = time.perf_counter()
        time_taken = round((end_time - start_time), 2)
        self.toggle_all("NORMAL")
        if not self.error_flag:
            self.logger.log(log_str=f"Time taken: {time_taken}", log_type="instance record")
            self.logger.log(log_str=f"Processed {self.total_processed} combinations to path {self.write_path}",
                            log_type="instance record")
        return None