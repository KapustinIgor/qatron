"""Helper utilities for test automation."""
import time
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


def wait_for(
    condition: Callable[[], T],
    timeout: int = 30,
    interval: float = 0.5,
    error_message: Optional[str] = None,
) -> T:
    """
    Wait for a condition to become true.

    Args:
        condition: Callable that returns truthy value when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
        error_message: Custom error message

    Returns:
        The result of the condition when it becomes true

    Raises:
        TimeoutError: If condition is not met within timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = condition()
        if result:
            return result
        time.sleep(interval)

    error_msg = error_message or f"Condition not met within {timeout} seconds"
    raise TimeoutError(error_msg)


def retry(
    func: Callable[[], T],
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
) -> T:
    """
    Retry a function call.

    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Result of the function call

    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                raise
    raise last_exception
