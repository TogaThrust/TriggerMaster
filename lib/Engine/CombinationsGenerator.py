import itertools
import pandas as pd
import time
from typing import Type
from multiprocessing import Pool, cpu_count, Lock, Queue

def init_pool_processes(the_lock, the_queue):
    """Initialize each process with a global variable lock.
    """
    global lock
    global queue
    lock = the_lock
    queue = the_queue

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
        print(f"Number of rows:\n{number_in_column}")
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
                      split_columns, dates: list, expected_output: int,
                      start: int, end: int) -> pd.DataFrame | Type[AttributeError | TypeError]:
        print("Thread started")
        generator = itertools.product(*columns)
        chunk = list(itertools.islice(generator, start, end))
        processed_chunk = [list(combo) for combo in chunk] # Convert tuples to lists
        df_output = pd.DataFrame(processed_chunk)
        df_output.dropna(inplace=False)
        total_processed = 0
        if have_name_and_code:
            df_output, error = split_columns(df_output)
            if error:
                return error
            original_columns = original_columns[:-2]
            df_output.columns = original_columns
        for header in dates:
            df_output[header] = 0
        with lock:
            print("Lock acquired.")
            df_output.to_csv(write_path, mode='a', header=False, index=False, encoding='utf-8-sig')
            print("Writen to csv.")
            total_processed += df_output.shape[0]
            percentage_complete = round((total_processed / expected_output) * 100, 2)
            queue.put((percentage_complete,total_processed))
        print("Thread ended.")
        return df_output

    def thread_handler(self, df, original_columns: list , have_name_and_code: int, dates: list, enable_buttons,
                       display_df, chunk_size: int = 100_000) -> None | str | Type[AttributeError | TypeError]:
        start_time = time.perf_counter()
        self.total_processed = 0
        columns = [df[col].dropna().unique() for col in df.columns]
        chunk_ranges = [(i, min(i + chunk_size, self.expected_output))
                        for i in range(0, self.expected_output, chunk_size)]
        lock = Lock()
        queue = Queue()
        # Initiate multithreading.
        with Pool(cpu_count()-1, initializer=init_pool_processes, initargs=(lock,queue)) as pool:
            results = pool.starmap(self.process_chunk,
                                   [(self.write_path, columns,original_columns,have_name_and_code,
                                     self.split_columns, dates, self.expected_output,
                                     start, end) for start, end in chunk_ranges])
        # Error flag.
        if any(isinstance(result, (AttributeError, TypeError)) for result in results): # pandas df have typing issues :(
            self.error_flag = True
            for error in enumerate(results):
                if isinstance(error, AttributeError):
                    self.error_handler.raise_error_box(error_type="AttributeError", log_str=None)
                    return AttributeError
                elif isinstance(error, TypeError):
                    self.error_handler.raise_error_box(error_type="RuntimeError", log_str=None)
                    return TypeError
            display_df(results[0].head(100))
        while not queue.empty():
            results = queue.get()
            self.logger.log(f"Percentage Complete: {results[0]}%.", log_type="update") # fixme this shit not updating in my UI
            self.total_processed += results[1]
        end_time = time.perf_counter()
        time_taken = round((end_time - start_time), 2)
        enable_buttons("NORMAL")
        if not self.error_flag:
            self.logger.log(log_str=f"Time taken: {time_taken}", log_type="instance record")
            self.logger.log(log_str=f"Processed {self.total_processed} combinations to path {self.write_path}",
                            log_type="instance record")
            self.logger.log(log_str=f'Showing first {100} combinations. Click "View Log" for more info.',
                            log_type="instance update")
        return None