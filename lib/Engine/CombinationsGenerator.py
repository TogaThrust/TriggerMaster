import itertools
import threading
import pandas as pd
from typing import Type

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

    def split_columns(self, df: pd.DataFrame) -> pd.DataFrame | Type[AttributeError | TypeError]:
        df_split = pd.DataFrame()
        try:
            for col in df.columns:
                split_cols = df[col].str.split('%%', expand=True)
                split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                df_split = pd.concat([df_split, split_cols], axis=1)
        except AttributeError: # Probably got to do with UTC-8 conversion
            self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
            return AttributeError
        except TypeError: # Mismatch between two columns
            self.error_handler.raise_error_box(error_type="RuntimeError",log_str=None)
            return TypeError
        return df_split

    @ staticmethod
    def chunk_generator(df, chunk_size: int = 100_000) -> list | None:
        columns = [df[col].dropna().unique() for col in df.columns]
        generator = itertools.product(*columns)
        chunk = []
        for i, combination in enumerate(generator):
            chunk.append(combination)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
        return None

    def write_chunk(self, chunk: list, write_header: bool, df, original_columns: list,
                    have_name_and_code: int) -> Type[RuntimeError] | None:
        df_output = pd.DataFrame(chunk, columns=df.columns)
        df_output.dropna(inplace=False)
        if have_name_and_code:
            df_output = self.split_columns(df_output)
            if type(df_output) != pd.DataFrame:
                self.error_flag = True
                return RuntimeError
            df_output.columns = original_columns
        # fixme chinese char breaks when writing from df to csv
        file_lock = threading.Lock()
        with file_lock:
            df_output.to_csv(self.write_path, index=False, header=write_header, mode='a')
            self.total_processed += df_output.shape[0]
            percent_complete = round((self.total_processed / self.expected_output) * 100, 2)
            self.logger.log(log_str=f"Loading... {percent_complete}% complete.", log_type="update")
        return None

    def thread_handler(self, df, original_columns: list , have_name_and_code: int, max_threads: int = 4) -> None | str:
        self.total_processed = 0
        threads = []
        for i, chunk in enumerate(self.chunk_generator(df)):
            write_header = (i == 0)
            thread = threading.Thread(name=str(i), target=self.write_chunk, daemon=True,
                                      args=(chunk, write_header, df, original_columns, have_name_and_code))
            thread.start()
            print(f"thread started with chunk size: {len(chunk)}")
            threads.append(thread)
            print(threads)
            if len(threads) >= max_threads:
                for t in threads:
                    t.join()  # Wait for current threads to finish
                    print(f"thread {t.name} joined")
                    print(threads)
                threads = []  # Clear the list for the next batch
        for t in threads:
            t.join()
            print(f"thread {t.name} joined")
            print(threads)
        if not self.error_flag:
            self.logger.log(log_str=f"Processed {self.total_processed} combinations to path {self.write_path}",
                            log_type="instance record")
        return None