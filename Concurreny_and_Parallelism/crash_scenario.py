import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def task(n):
    """A simple task that simulates work by returning the square of the input after a delay."""
    time.sleep(31)  # Simulate a time-consuming task
    return n * n

executor = ThreadPoolExecutor(max_workers=2)
executor.submit(task, 10)
raise Exception("Simulated crash in main thread")