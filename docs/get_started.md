<!-- https://rxpy.readthedocs.io/en/latest/get_started.html#concurrency -->
<!-- 3087 -->
This documentation introduces the core concepts and basic usage of ReactiveX (RxPY), focusing on `Observable`s, `Observer`s, operators, and concurrency.

### Core Concepts

An `Observable` is the central type in ReactiveX, serially pushing items (emissions) through a series of operators until they are consumed by an `Observer`. This push-based iteration allows for expressing code and concurrency efficiently, treating events as data and data as events.

To consume emissions, an `Observer` subscribes to an `Observable`. The `Observer` can define three callback functions:
*   `on_next`: Called each time the `Observable` emits an item.
*   `on_completed`: Called when the `Observable` finishes emitting items.
*   `on_error`: Called when an error occurs on the `Observable`.

While not all three callbacks are strictly required (a single lambda for `on_next` suffices), providing an `on_error` handler is recommended for production environments to explicitly handle errors.

#### Creating Observables

**`reactivex.create(push_function)`**
Creates an `Observable` by passing it a function that handles item emissions. The `push_function` receives an `observer` and a `scheduler` as arguments, and uses `observer.on_next()`, `observer.on_completed()`, and `observer.on_error()` to emit items, signal completion, or report errors, respectively.

```python
from reactivex import create

def push_five_strings(observer, scheduler):
    observer.on_next("Alpha")
    observer.on_next("Beta")
    observer.on_next("Gamma")
    observer.on_next("Delta")
    observer.on_next("Epsilon")
    observer.on_completed()

source = create(push_five_strings)

source.subscribe(
    on_next = lambda i: print("Received {0}".format(i)),
    on_error = lambda e: print("Error Occurred: {0}".format(e)),
    on_completed = lambda: print("Done!"),
)
```

Output:
```
Received Alpha
Received Beta
Received Gamma
Received Delta
Received Epsilon
Done!
```

**`reactivex.of(*items)`**
A factory method that accepts an argument list, iterates over each argument, emits them as items, and then completes. This simplifies creating Observables from a fixed set of values.

```python
from reactivex import of

source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

source.subscribe(
    on_next = lambda i: print("Received {0}".format(i)),
    on_error = lambda e: print("Error Occurred: {0}".format(e)),
    on_completed = lambda: print("Done!"),
)
```

A single parameter can be provided to the `subscribe` function if completion and error are ignored:

```python
from reactivex import of

source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

source.subscribe(lambda value: print("Received {0}".format(value)))
```

Output:
```
Received Alpha
Received Beta
Received Gamma
Received Delta
Received Epsilon
```

### Operators and Chaining

RxPY provides over 130 operators to transform emissions from a source `Observable`. Each operator yields a new `Observable`. Operators can be chained together using the `pipe()` method to create an "Observable pipeline," which enhances readability and expresses the flow of operations clearly.

**`Observable.pipe(*operators)`**
Applies a series of operators to the `Observable`, returning a new `Observable` that represents the transformed stream.

**`reactivex.operators.map(projection_function)`**
Transforms each item emitted by an `Observable` by applying a function to it.

**`reactivex.operators.filter(predicate_function)`**
Emits only those items from an `Observable` that satisfy a specified predicate.

Example of chaining `map` and `filter` operators:

```python
from reactivex import of, operators as op

source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

composed = source.pipe(
    op.map(lambda s: len(s)),
    op.filter(lambda i: i >= 5)
)
composed.subscribe(lambda value: print("Received {0}".format(value)))
```

Output:
```
Received 5
Received 5
Received 5
Received 7
```

Inlining the pipeline for better readability:

```python
from reactivex import of, operators as op

of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
    op.map(lambda s: len(s)),
    op.filter(lambda i: i >= 5)
).subscribe(lambda value: print("Received {0}".format(value)))
```

### Custom Operators

Custom operators can be implemented as functions and used directly within the `pipe()` operator.

#### Composing Existing Operators

Custom operators can be compositions of other operators using `reactivex.compose()`.

```python
import reactivex
from reactivex import operators as ops

def length_more_than_5():
    # In v4 rx.pipe has been renamed to `compose`
    return reactivex.compose(
        ops.map(lambda s: len(s)),
        ops.filter(lambda i: i >= 5),
    )

reactivex.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
    length_more_than_5()
).subscribe(lambda value: print("Received {0}".format(value)))
```

#### Implementing Custom Subscription Logic

For full control over subscription logic and item emissions, an operator can be implemented by returning a function that takes a source `Observable` and returns a new `Observable` created with `reactivex.create()`. The `subscribe` function within this new `Observable` defines how items from the source are processed and re-emitted.

```python
import reactivex

def lowercase():
    def _lowercase(source):
        def subscribe(observer, scheduler = None):
            def on_next(value):
                observer.on_next(value.lower())

            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler)
        return reactivex.create(subscribe)
    return _lowercase

reactivex.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        lowercase()
     ).subscribe(lambda value: print("Received {0}".format(value)))
```

Output:
```
Received alpha
Received beta
Received gamma
Received delta
Received epsilon
```

### Concurrency

Concurrency in RxPY is achieved using Schedulers and specific operators.

#### CPU Concurrency

**`reactivex.operators.subscribe_on(scheduler)`**
Instructs the source `Observable` at the start of the chain which `Scheduler` to use for its subscription and initial work. Its placement in the chain does not affect its behavior.

**`reactivex.operators.observe_on(scheduler)`**
Switches the `Scheduler` at that specific point in the `Observable` chain, effectively moving emissions from one thread to another.

**`reactivex.scheduler.ThreadPoolScheduler(thread_count)`**
A `Scheduler` that provides a pool of reusable worker threads, suitable for CPU-bound tasks.

**Important Constraint (GIL):** The Python Global Interpreter Lock (GIL) can limit true parallel execution of multiple threads accessing the same line of code simultaneously. While libraries like NumPy can mitigate this by releasing the GIL for intensive computations, and RxPY may minimize thread overlap, it's crucial to test applications with concurrency to ensure actual performance gains. Some `Observable` factories (e.g., `interval()`) and operators (e.g., `delay()`) have default Schedulers and may ignore `subscribe_on()` unless a `Scheduler` is explicitly passed as an argument.

Example of CPU concurrency:

```python
import multiprocessing
import random
import time
from threading import current_thread

import reactivex
from reactivex.scheduler import ThreadPoolScheduler
from reactivex import operators as ops

def intense_calculation(value):
    # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
    time.sleep(random.randint(5, 20) * 0.1)
    return value

# calculate number of CPUs, then create a ThreadPoolScheduler with that number of threads
optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

# Create Process 1
reactivex.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
    ops.map(lambda s: intense_calculation(s)), ops.subscribe_on(pool_scheduler)
).subscribe(
    on_next=lambda s: print("PROCESS 1: {0} {1}".format(current_thread().name, s)),
    on_error=lambda e: print(e),
    on_completed=lambda: print("PROCESS 1 done!"),
)

# Create Process 2
reactivex.range(1, 10).pipe(
    ops.map(lambda s: intense_calculation(s)), ops.subscribe_on(pool_scheduler)
).subscribe(
    on_next=lambda i: print("PROCESS 2: {0} {1}".format(current_thread().name, i)),
    on_error=lambda e: print(e),
    on_completed=lambda: print("PROCESS 2 done!"),
)

# Create Process 3, which is infinite
reactivex.interval(1).pipe(
    ops.map(lambda i: i * 100),
    ops.observe_on(pool_scheduler),
    ops.map(lambda s: intense_calculation(s)),
).subscribe(
    on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
    on_error=lambda e: print(e),
)

input("Press Enter key to exit\n")
```

**OUTPUT:**
```
Press Enter key to exit
PROCESS 1: Thread-1 Alpha
PROCESS 2: Thread-2 1
PROCESS 3: Thread-4 0
PROCESS 2: Thread-2 2
PROCESS 1: Thread-1 Beta
PROCESS 3: Thread-7 100
PROCESS 3: Thread-7 200
PROCESS 2: Thread-2 3
PROCESS 1: Thread-1 Gamma
PROCESS 1: Thread-1 Delta
PROCESS 2: Thread-2 4
PROCESS 3: Thread-7 300
```

#### IO Concurrency

RxPY supports IO concurrency with asynchronous frameworks and their associated Schedulers, such as `AsyncIOScheduler` for `asyncio`. Futures can be used to bridge the RxPY operator chain with the coroutine's event loop.

```python
from collections import namedtuple
import asyncio
import reactivex
import reactivex.operators as ops
from reactivex.subject import Subject
from reactivex.scheduler.eventloop import AsyncIOScheduler

EchoItem = namedtuple('EchoItem', ['future', 'data'])

def tcp_server(sink, loop):
    def on_subscribe(observer, scheduler):
        async def handle_echo(reader, writer):
            print("new client connected")
            while True:
                data = await reader.readline()
                data = data.decode("utf-8")
                if not data:
                    break

                future = asyncio.Future()
                observer.on_next(EchoItem(
                    future=future,
                    data=data
                ))
                await future
                writer.write(future.result().encode("utf-8"))

            print("Close the client socket")
            writer.close()

        def on_next(i):
            i.future.set_result(i.data)

        print("starting server")
        server = asyncio.start_server(handle_echo, '127.0.0.1', 8888)
        loop.create_task(server)

        sink.subscribe(
            on_next=on_next,
            on_error=observer.on_error,
            on_completed=observer.on_completed)

    return reactivex.create(on_subscribe)

loop = asyncio.new_event_loop()
proxy = Subject()
source = tcp_server(proxy, loop)
aio_scheduler = AsyncIOScheduler(loop=loop)

source.pipe(
    ops.map(lambda i: i._replace(data="echo: {}".format(i.data))),
    ops.delay(5.0)
).subscribe(proxy, scheduler=aio_scheduler)

loop.run_forever()
print("done")
loop.close()
```

Example usage via telnet:
```
telnet localhost 8888
Connected to localhost.
Escape character is '^]'.
foo
echo: foo
```

#### Default Scheduler

A default `Scheduler` can be specified in the `subscribe` call, which will then be used by all operators in the pipe unless an operator explicitly provides its own `Scheduler`.

Scheduler selection logic for operators:
1.  If a `Scheduler` is provided directly to the operator, use it.
2.  Else, if a default `Scheduler` is provided in the `subscribe` call, use it.
3.  Otherwise, use the operator's own default `Scheduler` (if any).

```python
source.pipe(
    ...
).subscribe(proxy, scheduler=my_default_scheduler)
```
