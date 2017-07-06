import functools
import warnings


def deprecation_warn(message: str = ""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            output = "Deprecated function {} called. {}".format(func.__name__, message)
            warnings.warn(output, UserWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
