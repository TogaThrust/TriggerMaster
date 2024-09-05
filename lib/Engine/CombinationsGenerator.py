import itertools
import threading
import pandas as pd
from typing import Type

class CombinationsGenerator:
    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.stop_event = threading.Event()
        self.process_thread = None
        self.expected_output = 0
        self.total_processed = 0
        self.write_path = ""

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

    def split_columns(self, df) -> pd.DataFrame | str:
        df_split = pd.DataFrame
        try:
            for col in df.columns:
                split_cols = df[col].str.split('%%', expand=True)
                split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                df_split = pd.concat([df_split, split_cols], axis=1)
        except AttributeError: # Probably got to do with UTC-8 conversion
            return self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
        except TypeError: # Mismatch between two columns
            return self.error_handler.raise_error_box(error_type="RuntimeError",log_str=None)
        return df_split

    @ staticmethod
    def chunk_generator(df, chunk_size: int) -> list | None:
        generator = itertools.product(*[df[col] for col in df.columns])
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
                    have_name_and_code: int) -> Type[RuntimeError | ValueError] | None:
        df_output = pd.DataFrame(chunk, columns=df.columns)
        df_output.dropna(inplace=True)
        if have_name_and_code:
            df_output = self.split_columns(df_output)
            df_output.columns = original_columns
        # fixme chinese char breaks when writing from df to csv
        print("Still Running")
        file_lock = threading.Lock()
        with file_lock:
            df_output.to_csv(self.write_path, index=False, header=write_header, mode='a')
        self.total_processed += df_output.shape[0]
        percent_complete = round((self.total_processed / self.expected_output) * 100, 2)
        self.error_handler.logger(f"Loading... {percent_complete}% complete.", is_update=True)
        return None

    # fixme find out where the extra data coming from, and how to exit the main program when finished.
    def thread_handler(self, df, original_columns: list , have_name_and_code: int,
                       chunk_size: int = 100_000) -> None | str:
        self.total_processed = 0
        max_threads = 4
        threads = []
        for i, chunk in enumerate(self.chunk_generator(df, chunk_size=chunk_size)):
            print(f"chunk size: {len(chunk)}") # todo remove debug line
            write_header = (i == 0)
            thread = threading.Thread(target=self.write_chunk,
                                      args=(chunk, write_header, df, original_columns, have_name_and_code),
                                      daemon=True)
            threads.append(thread)
            self.stop_event.clear()
            thread.start()
            if len(threads) >= max_threads:
                for t in threads:
                    t.join()  # Wait for current threads to finish
                threads = []  # Clear the list for the next batch
        for t in threads:
            t.join()
        self.error_handler.logger(f"Processed {self.total_processed} combinations to path {self.write_path}")
        return None