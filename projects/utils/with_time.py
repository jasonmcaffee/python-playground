import time
import inspect


def with_time(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        signature = inspect.signature(func)
        bound_args = signature.bind(*args, **kwargs)
        # function_call_info = f"{func_name} with params: {bound_args.arguments}" # param text can be really long
        function_call_info = f"{func_name}"

        start_time = time.time()
        result = func(*args, **kwargs)
        duration_ms = (time.time() - start_time) / 1000

        print(f"{function_call_info} took {duration_ms} ms to complete")
        return result

    return wrapper
