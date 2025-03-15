import logging
from functools import wraps
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from typing import overload, Union, List, Tuple


@overload
def llke(x: str, y: str, threshold: float = 0.8) -> bool: ...


@overload
def llke(
    x: List[Union[str, int]], y: List[Union[str, int]], threshold: float = 0.8
) -> bool: ...


@overload
def llke(
    x: Tuple[Union[str, int]], y: Tuple[Union[str, int]], threshold: float = 0.8
) -> bool: ...


def llke(
    x: Union[str, List[Union[str, int]], Tuple[Union[str, int]]],
    y: Union[str, List[Union[str, int]], Tuple[Union[str, int]]],
    threshold: float = 0.8,
) -> bool:
    """Checks the equality between the given elements."""
    similarity = SequenceMatcher(None, x, y).ratio()
    return similarity >= threshold

def updated_timestamp(date: datetime = None, minutes: int = 0) -> int:
    if date is None:
        return int(datetime.now().timestamp() * 1000)

    updated_date = date + timedelta(minutes=minutes)
    updated_date = updated_date.replace(second=0, microsecond=0)

    return int(updated_date.timestamp() * 1000)

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
