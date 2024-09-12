import time

def time_taken(func, debug_mode=False):
    """Used in object classes, remove self for functions. Also takes in a logger object to handle reporting."""
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        time_elapsed = end_time - start_time
        self.logger.log(log_str=f"Time taken: {time_elapsed:.4f}s.", log_type="instance record")
        if debug_mode:
            print(f"Time taken for {func.__name__}: {time_elapsed:.4f} seconds")
        return result
    return wrapper