import time
from concurrent.futures import ThreadPoolExecutor

def long_running_task():
    """A task that simulates a long-running operation."""
    print("Starting long-running task...")
    time.sleep(30) # Simulate a long task
    print("Long-running task completed.")

executor = ThreadPoolExecutor(max_workers=2)
executor.submit(long_running_task)
print("Main thread completed.")

