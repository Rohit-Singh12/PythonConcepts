# Concurrency and Parallelism
[Python Docs](https://docs.python.org/3/library/concurrent.futures.html)

Before diving into Concurrency and Parallelism in Python, let's first get some fundamentals clear.

- GIL
- Process
- Threads


## GIL (Global Interpreter Lock)

### What is the GIL?
The **Global Interpreter Lock (GIL)** is a mutex used by CPython that protects access to Python objects and ensures only one native thread executes Python bytecode at a time in a single interpreter instance.

### What does it mean?
Imagine a single-lane bridge where only one car (thread) can pass at a time. Even on a multi-core machine, threads executing Python bytecode in the same CPython interpreter take turns.

Refer to this video for a visual interpretation:
[Visual Explanation](https://youtu.be/bHFz94fe0Co?si=BfxkEUG-xtirg-oC&t=50)

### What does it affect?
- **Limits CPU-bound parallelism in CPython:** multiple threads cannot execute Python bytecode simultaneously in the same interpreter instance because of the GIL.
- **Not usually a problem for I/O-bound work:** many blocking I/O operations release the GIL, allowing other threads to run while one waits for I/O.
- **For CPU-bound work use multiprocessing or native code that releases the GIL:** `multiprocessing` (or `concurrent.futures.ProcessPoolExecutor`) runs separate interpreter processes (each with its own GIL), or use C/C++ extensions or libraries (NumPy, native BLAS) that release the GIL for heavy computation.

Note: `asyncio` provides concurrency for I/O-bound tasks (single-threaded, event loop) but does not bypass the GIL for CPU-bound work — it is not a substitute for `multiprocessing` when you need true CPU parallelism.

We will look into how to do multithreading and multiprocessing in Python later. *Just keep reading!*

But what is threads and processes are related to Concurrency and Parallelism. For that let's understand them first-

## Threads and Processes

### Core Differences

#### Process
A process is an independent instance of a program with its **own dedicated memory space, file handles, and system resources**. Each process is completely isolated from others.


Its the responsibility of OS to allocate memory and system resources to each process. Let's say you have opened Chrome and Notepad, OS will allocate separate code, memory (Stack + Heap) to each program. Here each program acts as process though they can open separate subprocesses. For example- you are opening new tab in Browser, this new subprocess will have duplicate code from the Browser program but it will allocate separate memory. This makes creating processes a heavy operation. 

Let's say you have single CPU with multiple cores - let's say, 4-cores (Core1, Core2, Core3 and Core4), now OS will allocate these processes to separate cores, meaning meaning process, let's say - Process1 and Process2 are mapped to separate cores Core1 and Core2 respectively. **This way the Processes can run in parallel.**

Now, since each process run separately and independently, they don't share resources and one process is not affected by the other process. If you want communication they its done through IPC (Inter-Process Communication) by OS which adds extra overhead.

In case of Python, if you are spawning two processes then they will have their own separate Memory, code, Interpreter and GIL. This way two processes can run in parallel avoid GIL restriction we talked earlier - that only one thread can execute a code at a time. 
```
┌──────────────────┐    ┌──────────────────┐
│   PROCESS 1      │    │   PROCESS 2      │
├──────────────────┤    ├──────────────────┤
│ Memory Space 1   │    │ Memory Space 2   │
│ Global Vars      │    │ Global Vars      │
│ Own Interpreter  │    │ Own Interpreter  │
│ Own GIL          │    │ Own GIL          │
└──────────────────┘    └──────────────────┘
         ↕                      ↕
    (Inter-Process Communication)
    Queues, Pipes, Sockets
    
```

**Key Characteristics:**
- **Own Memory Space**: Each process has its own isolated memory (heap, stack, code, data)
- **Data Sharing**: Cannot directly access another process's memory - must use inter-process communication (queues, pipes, sockets)
- **Heavy**: Creating processes has higher overhead due to resource allocation
- **True Parallelism**: Each process gets its own GIL, allowing simultaneous execution on multiple CPU cores
- **Independent**: If one process crashes, others are unaffected
- **Own Python Interpreter**: Each process runs its own Python interpreter

#### Thread
A **thread** is the smallest unit of execution within a process. Multiple threads share the same process's memory space and resources.

In process, we looked that spawning multiple processes creates overhead and for single CPU multi-processing is happening by OS by allocating some clock-cycle to all the processes in sequence, meaning OS is switching between several process.

Before going further, and understanding how multi-threading is useful, let's go through some data.

Let's say it takes a CPU 1 nano-second to complete a single CPU-intensive task. Now, you started a task (Task1) which is I/O bound. Let's say it takes 1 milli-second to fetch some data. If this Task1 on a thread and this thread after 1 nano-second makes a call to fetch data then this thread is waiting for 1 milli-second doing nothing. Imaging, now many CPU-bound tasks can be done by this thread when it is sitting idle. 

- 1 CPU task - 1ns
- Number of CPU tasks in 1ms => 10^-3/10^-9 = 10^6 CPU tasks

Table summary:

| Item | Time | Equivalent CPU micro-tasks in 1 ms |
|------|------:|-----------------------------------:|
| CPU micro-task | 1 ns (1e-9 s) | 1,000,000 |
| I/O call       | 1 ms (1e-3 s) | can hide ~1,000,000 micro-tasks |

Imagine how much more can be done just by not keeping the thread idle `10^6` tasks.

## Why Multithreading Shines for I/O-Bound Tasks in Python

This is where multithreading shines. In Python, when your workload is I/O-bound, multithreading can significantly improve performance. During I/O operations—such as reading from a file, waiting for a network response, or interacting with a database—the **GIL is automatically released**. This allows other threads to run while the current thread is waiting for the I/O operation to finish.

Because of this behavior, multiple threads can make progress concurrently even though only one thread executes Python bytecode at a time. As a result, multithreading is highly effective for I/O-bound tasks and can lead to substantial speed-ups in real-world applications.

A very important point to note here- Spawning thread is very less intensive than the spawning new process. Also, threads have access to `shared data` unlike `multiprocessing`. 
```
┌─────────────────────────────────────────┐
│          PROCESS (Single Memory)        │
├─────────────────────────────────────────┤
│  Global Variables                       │
│  Shared Data                            │
│  ┌─────────────┬─────────────────────┐  │
│  │  Thread 1   │   Thread 2          │  │
│  │  (Stack)    │   (Stack)           │  │
│  │  (Local)    │   (Local)           │  │
│  └─────────────┴─────────────────────┘  │
│  File Handles, Network Connections      │
└─────────────────────────────────────────┘
```

**Key Characteristics:**
- **Shared Memory Space**: All threads within a process share the same memory, heap, and global variables
- **Direct Data Access**: Threads can directly access and modify shared data (but requires synchronization)
- **Lightweight**: Creating threads is fast with minimal overhead
- **Concurrent, Not Parallel**: Due to GIL, only one thread executes Python code at a time (within a process)
- **Single Point of Failure**: If one thread crashes, it can crash the entire process
- **Shared Resources**: All threads share file handles, connections, and other process resources

### Real-World Analogies

#### Restaurant Kitchen (Threads vs Processes)

**Threads = Same Kitchen, Multiple Cooks**
- All cooks (threads) work in the **same kitchen** (shared memory)
- They can see and use the same ingredients (shared variables)
- Only one cook can use the stove (GIL) at a time
- Communication is easy - just talk to each other
- If the kitchen's main power fails, everyone stops working
- Quick to hire a new cook (lightweight creation)

**Processes = Separate Restaurants**
- Each restaurant (process) has its own kitchen (own memory)
- Cooks in Restaurant A can't directly use Restaurant B's ingredients
- They must order ingredients via delivery (inter-process communication)
- Each restaurant has its own stove - cooks can work simultaneously (true parallelism)
- If Restaurant A's power fails, Restaurant B still operates
- Takes longer to open a new restaurant (higher overhead)
---

### Comparison Table

| Aspect | Threads | Processes |
|--------|---------|-----------|
| **Memory** | Shared within process | Isolated per process |
| **Data Access** | Direct (fast) | Via IPC (slow) |
| **Creation** | Lightweight | Heavyweight |
| **Overhead** | Low | High |
| **CPU Parallelism** | No (GIL limits) | Yes (own GIL each) |
| **Synchronization** | Complex (locks needed) | Simple (isolated data) |
| **Fault Isolation** | Low (shared process) | High (separate process) |
| **Best For** | I/O-bound tasks | CPU-bound tasks |
| **Context Switching** | Fast | Slower |
| **Communication** | Variables/queues | Queues/pipes only |
| **Scaling** | Limited | Unlimited (cores) |

---

### Important Consideration while choosing between Multi-threading and Multi-Processing

You may wonder what happens if you use multithreading for CPU-intensive tasks in Python. Because of the **Global Interpreter Lock (GIL)**, only one thread can execute Python bytecode at a time. This means CPU-bound multithreaded programs do **not** run in parallel and may even perform worse than single-threaded programs due to thread-switching overhead. In such cases, it is better to use Python’s **multiprocessing**, which bypasses the GIL by using separate processes and achieves true parallelism.

For I/O-bound tasks, you might think multiprocessing could still be used — but it usually isn’t ideal. Threads are lightweight and much cheaper to create compared to processes. Creating multiple processes introduces significant overhead in memory usage, startup time, and inter-process communication. Since I/O-bound threads spend most of their time waiting (e.g., for a response from a file, network, or database), using heavy processes would waste system resources without improving performance. Therefore, for I/O-bound workloads, **multithreading (concurrency)** is typically the best fit.

Finally, adding more processes does not guarantee proportional speedup. Performance gains depend on the number of available CPU cores and the overhead of process scheduling, memory sharing, and OS context switching. After a certain point, increasing the number of processes can even degrade performance instead of improving it.

### Decision Tree

```
Do you have CPU-intensive work?
├─ YES → Use MULTIPROCESSING
│        (image processing, math, ML, etc.)
│
└─ NO → Is it I/O-heavy?
         ├─ YES → Use THREADING
         │        (web scraping, API calls, file I/O, etc.)
         │
         └─ NO → Use ASYNCIO (even better for I/O)
```

[Visual Explanation](https://youtu.be/AZnGRKFUU0c?si=uclNR5IxdqIbWAEi)

### Important points about GIL, threads, and I/O
- The GIL is released by CPython during many blocking I/O operations, and well-behaved C extensions can release it during long computations.
- Python's `threading` module is great for I/O-bound tasks (network calls, disk I/O, waiting on sockets).
- For CPU-bound workloads, use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` so separate interpreter processes run on multiple cores.


### Practical considerations and tools
- Use `threading` and `queue.Queue` for simple I/O concurrency.
- Use `concurrent.futures.ThreadPoolExecutor` for a higher-level thread pool API.
- Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` for CPU-bound parallelism.
- IPC/communication between processes often requires pickling objects (costly). For large shared buffers, consider `multiprocessing.shared_memory` (Python 3.8+) or specialized libraries.
- Synchronization primitives: `threading.Lock`, `RLock`, `Condition`, `Event`; for processes: `multiprocessing.Lock`, `Manager`, and `SharedMemory`.

## Python Concurrent.futures
[Python Docs](https://docs.python.org/3/library/concurrent.futures.html#interpreterpoolexecutor)

The `concurrent.futures` module provides a high-level interface for asynchronously executing callables (functions, methods, etc.).

You can execute tasks using multiple threads or processes (or, in newer Python versions, separate interpreters) — but regardless of which, you use a common interface built around an Executor and Future objects.

---
### Executor Objects

At the core is the abstract class Executor. You don’t use Executor directly; rather, you use one of its concrete subclasses. The key methods provided by an Executor are:

- `submit(fn, *args, **kwargs)` — schedules a callable for execution, returns a Future. 

- `map(fn, *iterables, timeout=None, chunksize=1, buffersize=None)` — like the built-in `map()`, but executes calls asynchronously and returns an iterator of results in input order. Python documentation

- `shutdown(wait=True, cancel_futures=False)` — signal that no more tasks will be submitted, and free resources once pending tasks complete.

---

#### `submit(fn, *args, **kwargs)`

`submit` schedules the callable `fn` to be executed as `fn(*args, **kwargs)` and immediately returns a `concurrent.futures.Future` object representing that execution.

Key points:
- **Return value**: a `Future`. Call `future.result()` to retrieve the return value (or have any exception re-raised).
- **Non-blocking**: `submit` only schedules work; it does not wait for completion. Use `future.result(timeout=...)`, `as_completed()`, or `concurrent.futures.wait()` to wait.
- **Cancellation**: `future.cancel()` attempts to cancel the task before it starts; if the task is already running, cancellation may fail.
- **Exception handling**: exceptions from the worker are stored and re-raised by `future.result()`.

When to prefer `submit`:
- Need per-task control (inspect, cancel, or query status).
- Want results in completion order — pair `submit` with `as_completed()` to iterate results as tasks finish.

```
Example reference: see the `thread_pool_example()` in `Concurreny_and_Parallelism/concurrency.py` which uses `ThreadPoolExecutor.submit()` and `as_completed()` to process results as they complete.
```

---

#### `map(fn, *iterables, timeout=None, chunksize=1, buffersize=None)`

`map` applies `fn` to every item from the given iterable(s) and returns an iterator that yields results in the same order as the input sequence. It is similar to the built-in `map()`, but the function calls are scheduled concurrently on the executor's workers.

Parameters and notes:
- `fn`: callable to apply.
- `*iterables`: one or more iterables. If multiple iterables are provided, `fn` is called with parallel items (like `zip`). All iterables should be the same length.
- `timeout`: maximum seconds to wait while retrieving results from the iterator. If the whole map operation doesn't complete within `timeout`, a `concurrent.futures.TimeoutError` is raised.
- `chunksize`: (Process/Interpreter executors only) how many items to group together into a single task sent to a worker. Larger `chunksize` reduces scheduling overhead for many small tasks. Ignored by `ThreadPoolExecutor`.
- `buffersize`: (Python 3.13+; Process/Interpreter executors only) how many chunks to prefetch (keep ready in the internal queue) so workers have queued work; trades memory for throughput.

Behavioral details:
- Results are produced in *input order*. If you need completion order instead, use `submit` + `as_completed()`.
- `map` returns an iterator — workers may produce results lazily as you iterate. Wrap with `list()` to eagerly evaluate all results.

When to prefer `map`:
- When you have a simple function to apply to many inputs and want the results in the same order as the inputs.
- You don't need individual task cancellation or fine-grained inspection.

```
Example reference: see `process_pool_example()` in `Concurreny_and_Parallelism/concurrency.py` which demonstrates `ProcessPoolExecutor.map()` with `timeout`, `chunksize`, and `buffersize` configured for CPU-bound workloads.
```

----

#### Deadlock scenario
Deadlocks can occur when the callable associated with a Future waits on the results of another Future.
```py
def wait_on_future():
    f = executor.submit(pow, 5, 2)
    # This will never complete because there is only one worker thread and
    # it is executing this function.
    print(f.result())

executor = ThreadPoolExecutor(max_workers=1)
executor.submit(wait_on_future)
```

---

### Threadpool Executor  Key points

**All threads enqueued to ThreadPoolExecutor will be joined before the interpreter can exit.**

Python guarantees:

✔ Before the Python interpreter shuts down, these worker threads will be joined (waited on).

This means:

Python will not exit until all threads finish.

    - Even if the main thread crashes or reaches the end, Python waits for the worker threads.

    - This behavior is built into Python before `atexit` handlers run.

```
To demonstrate that - Run `deadlock_example()` in `concurrency.py` file
When you run it, then deadlock will occur. If you try to exit the program with `ctrl + c`, it won't exit because all the threads must join before python can exit.
```

**Exceptions in the main thread must be caught and handled in order to signal threads to exit gracefully**
What this means:

If the main thread hits an unhandled exception:

- ❌ The main thread ends abruptly
- ❌ Your threads are still running
- ✔ Python will block and wait for all threads to complete
- ❌ But they may never complete → program appears frozen

Therefore:

👉 You must catch exceptions in the main thread
👉 And shutdown the executor manually (executor.shutdown(cancel_futures=True))

Otherwise, worker threads will prevent interpreter exit.

---

**Avoid long-running tasks with ThreadPool**

When you run ```long_running_task_threadpool.py``` file.
```py
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
```
👉 What happens?

Even though the main script ends immediately, Python still waits 30 seconds
because thread must finish before interpreter exits.

So,even if main thread has exited, your program can't exit unit all the threads complete their tasks

---

**Crash Scenario**
Now, observe the below crash scenario
```py
import time
from concurrent.futures import ThreadPoolExecutor

def long_task():
    print("Thread running...")
    time.sleep(30)

executor = ThreadPoolExecutor(max_workers=2)
executor.submit(long_task)

print("Main thread about to crash...")
raise RuntimeError("Oops!")
```

If you run the `crash_scenario.py` file, you will see that main thread has crashed but python still waits for 30 seconds until thread is free.
Interpreter doesn't exit until task is completed and program appears to be freezed.

*Correct way to catch Exception in main thread*
```py
import time
from concurrent.futures import ThreadPoolExecutor

def long_task():
    time.sleep(30)

executor = ThreadPoolExecutor(max_workers=2)

try:
    executor.submit(long_task)
    print("Main doing work...")
    raise RuntimeError("Crash!")  # simulate crash
except Exception as e:
    print("Caught:", e)
finally:
    print("Shutting down executor...")
    executor.shutdown(cancel_futures=True)

```
Main thread exception must be handled properly as shown.
```py
import time
from concurrent.futures import ThreadPoolExecutor

def long_task():
    time.sleep(30)

executor = ThreadPoolExecutor(max_workers=2)

try:
    executor.submit(long_task)
    print("Main doing work...")
    raise RuntimeError("Crash!")  # simulate crash
except Exception as e:
    print("Caught:", e)
finally:
    print("Shutting down executor...")
    executor.shutdown(cancel_futures=True)

```

---

### ProcessPool Executor  Key points

**ProcessPoolExecutor uses the multiprocessing module, which allows it to side-step the Global Interpreter Lock but also means that only picklable objects can be executed and returned.**

`Pickable` meaning the object can be serialized by Python's `pickle` module.

As explained above you use executor.map() to parallelize CPU-bound tasks.
Refer to example `process_pool_example()` in  `concurrency.py` file.

---

## Python multiprocessing module

[Python Docs](https://docs.python.org/3/library/multiprocessing.html)

Multiprocessing module achieves true parallelism by spawning multiple processes each with its own interpreter, effectively side-stepping the Global Interpreter Lock by using subprocesses instead of threads. Due to this, the multiprocessing module allows the programmer to fully leverage multiple processors on a given machine.

Example included from the document only for reference.

```py
from multiprocessing import Process
import os

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name):
    info('function f')
    print('hello', name)

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()
```

Using Pool
```py
from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    with Pool(5) as p:
        print(p.map(f, [1, 2, 3]))
```

Using
```py

if __name__ == "__main__":
```

is mandatory when using Python’s multiprocessing module on Windows, macOS, and sometimes Linux.
It prevents infinite process spawning, recursive imports, and ensures that the multiprocess program starts safely.

---

 🛑 **1. Why the Infinite Loop Happens (The "Spawn" Method)**

On Windows and macOS, the Python interpreter cannot efficiently *fork* a process (which is standard on Linux). Instead, it uses the **"spawn"** start method.

### Spawn Method Mechanics

When a new process is **spawned**:

1.  A **new Python interpreter** is launched.
2.  Your script/module is **re-imported**.
3.  **All top-level code runs again** in the new process.

### 🔥 The Danger Without the Guard

Consider this simple multiprocessing code without a guard:

```python
from multiprocessing import Process

def worker_function():
    print("Worker is running...")

# Top-level code runs immediately upon import
p = Process(target=worker_function)
p.start()
```

…will cause:

🔥 Infinite process creation

**Why?**

Because:

 - Main process imports the script → creates a Process → starts it

 - Child process launches → re-imports the script

 - The script again creates a Process → starts it

 - Step 2 repeats → infinite loop

**Result:**

 - 100s of child processes

 - CPU fully used

 - System freeze

---

🟩 **2. How if __name__ == "__main__" solves this**
```py
from multiprocessing import Process

def work():
    print("Working...")

if __name__ == "__main__":
    p = Process(target=work)
    p.start()
    p.join()
```

**When a new process is spawned:**

 - The module is re-imported

 - But __name__ becomes "__mp_main__" (not "__main__")

 - So the block inside if __name__ == "__main__" does not run

- No new processes are spawned

 - No infinite recursion

This ensures only the parent process runs the process-creation code.

---









