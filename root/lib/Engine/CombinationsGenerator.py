import itertools
import multiprocessing
import pandas as pd
from typing import Type
from multiprocessing import Pool, cpu_count, Lock
from root.lib.util.decorators import time_taken

class CombinationsGenerator:
    def __init__(self, logger, error_handler):
        self.logger = logger
        self.error_handler = error_handler
        self.process_thread = None
        self.expected_output = 0
        self.write_path = ""

    @ staticmethod
    def _init_pool_processes(lock_inner, header_inner, total_processed_inner):
        """Inherits the lock variable as parsing variables into the process is not allowed."""
        global lock
        global header
        global total_processed
        lock = lock_inner
        header = header_inner
        total_processed = total_processed_inner

    @ staticmethod # method need to be static as tkinter objects are not pickle-able.
    def _split_columns(df: pd.DataFrame) -> tuple[pd.DataFrame | None, Type[AttributeError | TypeError] | None]:
        """For each column split columns if it contains the '%%' token, otherwise keeps the column as is."""
        # Probably should have written this in the File handler, but I am not going to pass it here to create
        # unnecessary mess.
        df_split = pd.DataFrame()
        try:
            for col in df.columns:
                if df[col].str.contains('%%').any():  # Check if any rows contain '%%'
                    split_cols = df[col].str.split('%%', expand=True)
                    split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                    df_split = pd.concat(objs=[df_split, split_cols], axis=1)
                else:
                    df_split = pd.concat(objs=[df_split, df[[col]]], axis=1)
        except AttributeError: # Probably got to do with UTC-8 conversion
            return None, AttributeError
        except TypeError: # Mismatch between two columns
            return None, TypeError
        return df_split, None

    @ staticmethod # need to be static as tkinter object cannot be pickled
    def _process_chunk(write_path: str, columns, original_columns:list, split_columns, dates: list,
                      start: int, end: int) -> None | pd.DataFrame | Type[AttributeError | TypeError]:
        """Generates the actual product values for each column using a generator which takes in
            start and end number of rows for chunking."""
        # Honestly generator written by GPT, not going to pretend to know what's going on there.
        generator = itertools.product(*columns)
        chunk = list(itertools.islice(generator, start, end))
        processed_chunk = [list(combo) for combo in chunk] # Convert tuples to lists
        df_output = pd.DataFrame(processed_chunk)
        df_output.dropna(inplace=False)
        df_output, error = split_columns(df_output)
        if error:
            return error
        original_columns = original_columns[:-2]
        df_output.columns = original_columns
        for date_header in dates: # add in date columns that we have generated
            df_output[date_header] = 0
        temp_header = 'infer' if header.value else None
        with lock:
            df_output.to_csv(path_or_buf=write_path, header=temp_header, index=False, mode='a', encoding='utf-8-sig')
            total_processed.value += df_output.shape[0]
            header.value = 0  # only write headers to 1
        return df_output

    def _error_flag(self, results: list) -> bool:
        """When results from the processes returns error value we handle them here."""
        for result in results: # pandas df have typing issues :(
            if isinstance(result, pd.DataFrame):
                return False
            elif Type[result] == Type[AttributeError]:
                self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
                return True
            elif Type[result] == Type[TypeError]:
                self.error_handler.raise_error_box(error_type="RuntimeError", log_str=None)
                return True
        return False

    def start_generator(self, df, enable_buttons, original_columns: list, dates: list, display_df,
                           chunk_size: int = 100_000) -> None:
        """Main wrapper around the main process in which we declare some variables
            to be processed by each process thread."""
        columns = [df[col].dropna().unique() for col in df.columns]
        ranges = [(i, min(i + chunk_size, self.expected_output)) for i in range(0, self.expected_output, chunk_size)]
        lock = Lock()
        header = multiprocessing.Value('i', 1)
        total_processed = multiprocessing.Value('i', 0)
        # Initiate multithreading.
        @time_taken
        def multi_threading(self):
            with Pool(cpu_count() - 1,
                      initializer=self._init_pool_processes,
                      initargs=(lock, header, total_processed)) as pool:
                results = pool.starmap_async(self._process_chunk, [(self.write_path,
                                                                    columns,
                                                                    original_columns,
                                                                    self._split_columns,
                                                                    dates,
                                                                    start, end) for start, end in ranges])
                while not results.ready():
                    self.logger.log(
                        log_str=f"{round((total_processed.value / self.expected_output) * 100, 2)}% complete.",
                        log_type="update")
                pool.close()
                pool.join()
            return results.get()
        results = multi_threading(self)
        if self._error_flag(results):
            return None
        display_df(results[0])
        enable_buttons("NORMAL")
        if total_processed.value > 100:
            sub = f'Showing first {100} combinations.'
        else:
            sub = "Process Complete."
        self.logger.log(log_str=f"Processed {total_processed.value} combinations to path {self.write_path}",
                        log_type="instance record")
        self.logger.log(log_str=sub + ' Click "View Log" for more info.', log_type="instance update")
        return None