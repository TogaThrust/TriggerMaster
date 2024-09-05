import itertools
import threading
from typing import Type

import pandas as pd

class CombinationsGenerator:
    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.stop_event = threading.Event()
        self.process_thread = None
        self.expected_output = 0
        self.total_processed = 0
        self.write_path = ""

    @staticmethod
    def get_expected_output(df) -> int:
        number_in_column = df.notna().sum()
        expected_combinations = number_in_column.prod()
        return expected_combinations

    # Raise exception when data to process is too large.
    def limit_check(self, df, warning_limit: int = 1_000_000) -> tuple[int, str | None]:
        expected_outputs = self.get_expected_output(df)
        if expected_outputs > warning_limit:
            return expected_outputs, self.error_handler.raise_question_box(error_type="LimitWarning")
        return expected_outputs, None

    @ staticmethod
    def split_columns(df) -> object | AttributeError:
        df_split = None
        try:
            for col in df.columns:
                split_cols = df[col].str.split('%%', expand=True)
                split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                df_split = pd.concat([df_split, split_cols], axis=1)
        except AttributeError:
            return AttributeError
        return df_split

    @ staticmethod
    def chunk_generator(df, chunk_size: int) -> list | None:
        generator = itertools.product(*[df.df_cleaned[col] for col in df.df_cleaned.columns])
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
                    have_name_and_code: int) -> Type[RuntimeError | ValueError] | str:
        df_output = pd.DataFrame(chunk, columns=df.columns)
        df_output.dropna(inplace=True)
        if df_output.empty:
            return ValueError
        if have_name_and_code:
            df_output = self.split_columns(df_output)
            if df_output == AttributeError:
                return RuntimeError
            df_output.columns = original_columns
        # fixme chinese char breaks when writing from df to csv
        file_lock = threading.Lock()
        with file_lock:
            df_output.to_csv(self.write_path, index=False, header=write_header, mode='a')
        self.total_processed += df_output.shape[0]
        percent_complete = round((self.total_processed / self.expected_output) * 100, 2)
        return f"Loading... {percent_complete}% complete."

    # fixme find out where the extra data coming from, and how to exit the main program when finished.
    def thread_handler(self, df, original_columns: list , have_name_and_code: int,
                       chunk_size: int = 100_000) -> None:
        yield "Process to create new combinations has started."
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
        return self.total_processed, self.write_path