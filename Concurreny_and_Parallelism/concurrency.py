from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor, TimeoutError

## A simple example of using ThreadPoolExecutor for concurrency
def task(n):
    """A simple task that simulates work by returning the square of the input after a delay."""
    import time
    time.sleep(1)  # Simulate a time-consuming task
    return n * n

# submit(fn, /, *args, **kwargs)¶
def thread_pool_example():
    '''
    Example of using ThreadPoolExecutor to submit tasks and retrieve results as they complete.
    
    max_workers: The maximum number of threads that can be used to execute the given calls.
    5 threads will be used to execute tasks concurrently. By limiting the number of threads, 
    it helps you manage system resources effectively. 
    Each thread consumes memory, and an excessive number of threads 
    can lead to high context-switching overhead, which can actually slow down your program.
    '''
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(task, i) for i in range(21)]
        
        for future in as_completed(futures):
            result = future.result()
            print(f"Task completed with result: {result}")
        

# map(fn, *iterables, timeout=None, chunksize=1, buffersize=None)

def process_pool_example():
    '''
    Example of using ProcessPoolExecutor to map tasks with additional parameters.
    ProcessPoolExecutor is used for CPU-bound tasks, as it creates separate processes.
    This example demonstrates how to use the timeout, chunksize, and buffersize parameters.
    
    map: Applies the function to the items of the given iterables, returning an iterator of results.
    map parameters:
    - timeout: If specified, the call will raise a TimeoutError if the entire result 
      iterator is not returned within the given number of seconds.
      - chunksize: The size of the chunks the iterable will be split into. Larger chunks can reduce the overhead of task scheduling.
      - buffersize: The number of results to prefetch. This can help improve performance by reducing wait times for results.'''
    try:
        with ProcessPoolExecutor() as executor:
            results = executor.map(
                task,
                list(range(21)),
                timeout=5,        # must finish within 5 seconds
                chunksize=5,   # send items in chunks of 5
                # buffersize=2  # prefetch 10 items(BUFFERSIZE is not supported for version >= 3.12)
            )

            print(list(results))
    except TimeoutError:
        print("A task took too long and timed out.")
        

## Threadpool deadlock example
def deadlock_example():
    '''
    Deadlocks can occur when the callable associated with a Future waits on the results of another Future.
    
    Example demonstrating a potential deadlock scenario with ThreadPoolExecutor.
    In this example, tasks submit new tasks to the same executor, which can lead to deadlock
    if the number of worker threads is insufficient to handle the nested submissions.
    '''
    def nested_task(executor, n):
        if n > 0:
            future = executor.submit(nested_task, executor, n - 1)
            return future.result()
        return "Task completed"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(nested_task, executor, 5) for _ in range(2)]
        
        for future in as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    print("Thread Pool Example:")
    thread_pool_example()
    
    print("\nProcess Pool Example:")
    process_pool_example()
    
    print("\nDeadlock Example:")
    deadlock_example()