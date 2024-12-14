import logging
from functools import wraps


def sockthis(func):
    """Too much rizz, only handles important logs"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        logger = logging.getLogger(func.__name__)
        if func.__name__ == "on_message":
            logger.info(args[0])
        elif func.__name__ == "on_error":
            logger.error(args[0])
        return result

    return wrapper
