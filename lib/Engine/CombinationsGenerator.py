import itertools
import multiprocessing
import pandas as pd
from typing import Type
from multiprocessing import Pool, cpu_count, Lock


# noinspection PyGlobalUndefined
def init_pool_processes(lock_inner, header_inner, total_processed_inner):
    """Initialize each process with a global variable lock."""
    global lock
    global header
    global total_processed
    lock = lock_inner
    header = header_inner
    total_processed = total_processed_inner

class CombinationsGenerator:
    def __init__(self, logger, error_handler):
        self.logger = logger
        self.error_handler = error_handler
        self.process_thread = None
        self.expected_output = 0
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

    @ staticmethod # method need to be static as tkinter objects are not pickle-able.
    def split_columns(df: pd.DataFrame) -> tuple[pd.DataFrame | None, Type[AttributeError | TypeError] | None]:
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
    def process_chunk(write_path: str, columns, original_columns:list, have_name_and_code:int,
                      split_columns, dates: list,
                      start: int, end: int) -> pd.DataFrame | Type[AttributeError | TypeError]:
        generator = itertools.product(*columns)
        chunk = list(itertools.islice(generator, start, end))
        processed_chunk = [list(combo) for combo in chunk] # Convert tuples to lists
        df_output = pd.DataFrame(processed_chunk)
        df_output.dropna(inplace=False)
        if have_name_and_code:
            df_output, error = split_columns(df_output)
            if error:
                return error
            original_columns = original_columns[:-2]
            df_output.columns = original_columns
        for date_header in dates: # add in date columns that we have generated
            df_output[date_header] = 0
        temp_header = 'infer' if header.value else None
        with lock:
            # noinspection PyTypeChecker
            df_output.to_csv(path_or_buf=write_path, header=temp_header, index=False, mode='a', encoding='utf-8-sig')
            total_processed.value += df_output.shape[0]
            header.value = 0 # only write headers to 1
        return df_output

    def error_flag(self, results: list) -> bool:
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

    # noinspection PyShadowingNames
    def thread_handler(self, df, original_columns: list , have_name_and_code: int, dates: list, enable_buttons,
                       display_df, chunk_size: int = 100_000) -> None:
        columns = [df[col].dropna().unique() for col in df.columns]
        chunk_ranges = [(i, min(i + chunk_size, self.expected_output))
                        for i in range(0, self.expected_output, chunk_size)]
        lock = Lock()
        header = multiprocessing.Value('i', 1)
        total_processed = multiprocessing.Value('i', 0)
        # Initiate multithreading.
        with Pool(cpu_count()-1, initializer=init_pool_processes, initargs=(lock, header, total_processed)) as pool:
            results = pool.starmap_async(self.process_chunk, [(self.write_path, columns,original_columns,
                                                               have_name_and_code, self.split_columns, dates,
                                                               start, end) for start, end in chunk_ranges])
            while not results.ready():
                self.logger.log(f"Percentage Complete: "
                                f"{round((total_processed.value / self.expected_output) * 100, 2)}%.",
                                log_type="update")
            pool.close()
            pool.join()
        results = results.get()
        if self.error_flag(results):
            return None
        display_df(results[0].head(100))
        enable_buttons("NORMAL")
        self.logger.log(log_str=f"Processed {total_processed.value} combinations to path {self.write_path}",
                        log_type="instance record")
        if total_processed.value > 100:
            self.logger.log(log_str=f'Showing first {100} combinations. Click "View Log" for more info.',
                            log_type="instance update")
        return None
