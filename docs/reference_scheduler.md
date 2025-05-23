<!-- https://rxpy.readthedocs.io/en/latest/reference_scheduler.html -->
<!-- 11600 -->
The `reactivex.scheduler` module provides various scheduler implementations for controlling when and where scheduled actions are executed. These schedulers manage the execution context, allowing for immediate execution, execution on specific threads, or virtual time-based scheduling.

### `reactivex.scheduler.CatchScheduler`

Wraps an existing scheduler to add exception handling for scheduled actions. The provided `handler` callable determines if an exception is successfully handled or should be escalated.

**Constructor**

*   `__init__(scheduler, handler)`
    *   **Description**: Initializes a `CatchScheduler` instance.
    *   **Parameters**:
        *   `scheduler` (`SchedulerBase`): The scheduler to be wrapped.
        *   `handler` (`Callable[[Exception], bool]`): A callable to handle exceptions raised by the wrapped scheduler. It should return `True` if the exception was handled successfully; otherwise, falsy return values will cause the exception to be re-raised.

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler's current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_periodic(period, action, state=None)`
    *   **Description**: Schedules a periodic piece of work.
    *   **Parameters**:
        *   `period` (`Union[timedelta, float]`): Period (in seconds or `timedelta`) for running the work periodically.
        *   `action` (`Callable[[Optional[_TState]], Optional[_TState]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] Initial state passed to the action upon the first iteration.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled recurring action (best effort).

### `reactivex.scheduler.CurrentThreadScheduler`

Schedules units of work on the current thread. Each instance manages trampolines and queues per thread.

**Important**: You should never schedule timeouts using `CurrentThreadScheduler`, as this will block the thread while waiting.

**Constructor**

*   `__init__()`

**Class Methods**

*   `singleton()`
    *   **Description**: Obtains a singleton instance for the current thread. If this instance is passed to another thread, it will behave as if created by that other thread (separate trampoline and queue).
    *   **Returns**: `CurrentThreadScheduler` - The singleton `CurrentThreadScheduler` instance.

### `reactivex.scheduler.EventLoopScheduler`

Creates an object that schedules units of work on a designated thread.

**Constructor**

*   `__init__(thread_factory=None, exit_if_empty=False)`

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_periodic(period, action, state=None)`
    *   **Description**: Schedules a periodic piece of work.
    *   **Parameters**:
        *   `period` (`Union[timedelta, float]`): Period (in seconds or `timedelta`) for running the work periodically.
        *   `action` (`Callable[[Optional[_TState]], Optional[_TState]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] Initial state passed to the action upon the first iteration.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled recurring action (best effort).

*   `run()`
    *   **Description**: Starts the event loop scheduled on the designated event loop thread. The loop is suspended/resumed using a condition notified by calls to `schedule` or `dispose`.
    *   **Returns**: `None`

*   `dispose()`
    *   **Description**: Ends the thread associated with this scheduler. All remaining work in the scheduler queue is abandoned.
    *   **Returns**: `None`

### `reactivex.scheduler.HistoricalScheduler`

Provides a virtual time scheduler that uses `datetime` for absolute time and `timedelta` for relative time.

**Constructor**

*   `__init__(initial_clock=None)`
    *   **Description**: Creates a new historical scheduler with the specified initial clock value.
    *   **Parameters**:
        *   `initial_clock` (`Optional[datetime]`): Initial value for the clock.

### `reactivex.scheduler.ImmediateScheduler`

Schedules units of work to run immediately on the current thread.

**Important**: You are not allowed to schedule timeouts using the `ImmediateScheduler` as this will block the current thread. Attempts to do so will raise a `WouldBlockException`.

**Static Methods**

*   `__new__(cls)`
    *   **Returns**: `ImmediateScheduler`

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.NewThreadScheduler`

Creates an object that schedules each unit of work on a separate thread.

**Constructor**

*   `__init__(thread_factory=None)`

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_periodic(period, action, state=None)`
    *   **Description**: Schedules a periodic piece of work.
    *   **Parameters**:
        *   `period` (`Union[timedelta, float]`): Period (in seconds or `timedelta`) for running the work periodically.
        *   `action` (`Callable[[Optional[_TState]], Optional[_TState]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] Initial state passed to the action upon the first iteration.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled recurring action (best effort).

### `reactivex.scheduler.ThreadPoolScheduler`

A scheduler that schedules work via the thread pool.

**Constructor**

*   `__init__(max_workers=None)`

**Inner Class**

#### `ThreadPoolThread`

Wraps a concurrent future as a thread.

**Constructor**

*   `__init__(executor, target)`

### `reactivex.scheduler.TimeoutScheduler`

A scheduler that schedules work via a timed callback.

**Static Methods**

*   `__new__(cls)`
    *   **Returns**: `TimeoutScheduler`

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.TrampolineScheduler`

Schedules units of work on the trampoline. Each instance has its own trampoline and queue.

**Important**: You should never schedule timeouts using the `TrampolineScheduler`, as it will block the thread while waiting. The first thread to call a `schedule` method while the trampoline is idle will remain occupied until the queue is empty.

**Constructor**

*   `__init__()`

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_required()`
    *   **Description**: Tests if scheduling is required. Returns `False` if the trampoline is active, `True` otherwise.
    *   **Returns**: `bool`

*   `ensure_trampoline(action)`
    *   **Description**: Method for testing the `TrampolineScheduler`.
    *   **Returns**: `Optional[DisposableBase]`

### `reactivex.scheduler.VirtualTimeScheduler`

A virtual scheduler that can work with `datetime`/`timespan` or integer ticks.

**Constructor**

*   `__init__(initial_clock=0)`
    *   **Description**: Creates a new virtual time scheduler with the specified initial clock value.
    *   **Parameters**:
        *   `initial_clock` (`Union[datetime, float]`): Initial value for the clock.

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler’s current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `start()`
    *   **Description**: Starts the virtual time scheduler.
    *   **Returns**: `Any`

*   `stop()`
    *   **Description**: Stops the virtual time scheduler.
    *   **Returns**: `None`

*   `advance_to(time)`
    *   **Description**: Advances the scheduler's clock to the specified absolute time, running all work until that point.
    *   **Parameters**:
        *   `time` (`Union[datetime, float]`): Absolute time to advance the scheduler's clock to.
    *   **Returns**: `None`

*   `advance_by(time)`
    *   **Description**: Advances the scheduler's clock by the specified relative time, running all work scheduled for that timespan.
    *   **Parameters**:
        *   `time` (`Union[timedelta, float]`): Relative time to advance the scheduler's clock by.
    *   **Returns**: `None`

*   `sleep(time)`
    *   **Description**: Advances the scheduler's clock by the specified relative time.
    *   **Parameters**:
        *   `time` (`Union[timedelta, float]`): Relative time to advance the scheduler's clock by.
    *   **Returns**: `None`

**Class Methods**

*   `add(absolute, relative)`
    *   **Description**: Adds a relative time value to an absolute time value.
    *   **Parameters**:
        *   `absolute` (`Union[datetime, float]`): Absolute virtual time value.
        *   `relative` (`Union[timedelta, float]`): Relative virtual time value to add.
    *   **Returns**: `Union[datetime, float]` - The resulting absolute virtual time sum value.

### `reactivex.scheduler.eventloop.AsyncIOScheduler`

A scheduler that schedules work via the asyncio mainloop. This class does not use the asyncio threadsafe methods. For thread-safe operations, use `AsyncIOThreadSafeScheduler`.

**Constructor**

*   `__init__(loop)`
    *   **Description**: Creates a new `AsyncIOScheduler`.
    *   **Parameters**:
        *   `loop` (`AbstractEventLoop`): Instance of asyncio event loop to use (e.g., `asyncio.get_event_loop()`).

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler’s current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.eventloop.AsyncIOThreadSafeScheduler`

A scheduler that schedules work via the asyncio mainloop, using thread-safe asyncio methods. This is a subclass of `AsyncIOScheduler`.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.eventloop.EventletScheduler`

A scheduler that schedules work via the Eventlet event loop.

**Constructor**

*   `__init__(eventlet)`
    *   **Description**: Creates a new `EventletScheduler`.
    *   **Parameters**:
        *   `eventlet` (`Any`): The `eventlet` module to use (e.g., `import eventlet`).

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler’s current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.eventloop.GEventScheduler`

A scheduler that schedules work via the GEvent event loop.

**Constructor**

*   `__init__(gevent)`
    *   **Description**: Creates a new `GEventScheduler`.
    *   **Parameters**:
        *   `gevent` (`Any`): The `gevent` module to use (e.g., `import gevent`).

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler’s current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.eventloop.IOLoopScheduler`

A scheduler that schedules work via the Tornado I/O main event loop. As of Tornado 6, this is a wrapper around the asyncio loop.

**Constructor**

*   `__init__(loop)`
    *   **Description**: Creates a new `IOLoopScheduler`.
    *   **Parameters**:
        *   `loop` (`Any`): The ioloop to use (e.g., `tornado.ioloop.IOLoop.current()`).

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler’s current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.eventloop.TwistedScheduler`

A scheduler that schedules work via the Twisted reactor mainloop.

**Constructor**

*   `__init__(reactor)`
    *   **Description**: Creates a new `TwistedScheduler`.
    *   **Parameters**:
        *   `reactor` (`Any`): The reactor to use (e.g., `from twisted.internet import reactor`).

**Properties**

*   `now` (`datetime`)
    *   **Description**: Represents the scheduler’s current notion of time.
    *   **Returns**: The scheduler’s current time as a `datetime` instance.

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.mainloop.GtkScheduler`

A scheduler that schedules work via the GLib main loop used in GTK+ applications.

**Constructor**

*   `__init__(glib)`
    *   **Description**: Creates a new `GtkScheduler`.
    *   **Parameters**:
        *   `glib` (`Any`): The GLib module to use (e.g., `from gi.repository import GLib`).

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_periodic(period, action, state=None)`
    *   **Description**: Schedules a periodic piece of work to be executed in the loop.
    *   **Parameters**:
        *   `period` (`Union[timedelta, float]`): Period (in seconds) for running the work repeatedly.
        *   `action` (`Callable[[Optional[_TState]], Optional[_TState]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] Initial state passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.mainloop.PyGameScheduler`

A scheduler that schedules work for PyGame.

**Important**: This class expects the caller to invoke `run()` repeatedly.

**Constructor**

*   `__init__(pygame)`
    *   **Description**: Creates a new `PyGameScheduler`.
    *   **Parameters**:
        *   `pygame` (`Any`): The PyGame module to use (e.g., `import pygame`).

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.mainloop.QtScheduler`

A scheduler for a PyQt5/PySide2 event loop.

**Constructor**

*   `__init__(qtcore)`
    *   **Description**: Creates a new `QtScheduler`.
    *   **Parameters**:
        *   `qtcore` (`Any`): The QtCore instance to use (e.g., `import PyQt5.QtCore` or `import PySide2.QtCore`).

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_periodic(period, action, state=None)`
    *   **Description**: Schedules a periodic piece of work to be executed in the loop.
    *   **Parameters**:
        *   `period` (`Union[timedelta, float]`): Period (in seconds) for running the work repeatedly.
        *   `action` (`Callable[[Optional[_TState]], Optional[_TState]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] Initial state passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.mainloop.TkinterScheduler`

A scheduler that schedules work via the Tkinter main event loop.

**Constructor**

*   `__init__(root)`
    *   **Description**: Creates a new `TkinterScheduler`.
    *   **Parameters**:
        *   `root` (`Any`): The Tk instance to use (e.g., `tkinter.Tk()`).

**Methods**

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

### `reactivex.scheduler.mainloop.WxScheduler`

A scheduler for a wxPython event loop.

**Constructor**

*   `__init__(wx)`
    *   **Description**: Creates a new `WxScheduler`.
    *   **Parameters**:
        *   `wx` (`Any`): The `wx` module to use (e.g., `import wx`).

**Methods**

*   `cancel_all()`
    *   **Description**: Cancels all scheduled actions. This should be called when destroying wx controls to prevent accessing dead wx objects in pending actions.
    *   **Returns**: `None`

*   `schedule(action, state=None)`
    *   **Description**: Schedules an action to be executed.
    *   **Parameters**:
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_relative(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed after a specified relative time.
    *   **Parameters**:
        *   `duetime` (`Union[timedelta, float]`): Relative time (in seconds or `timedelta`) after which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_absolute(duetime, action, state=None)`
    *   **Description**: Schedules an action to be executed at a specified absolute time.
    *   **Parameters**:
        *   `duetime` (`Union[datetime, float]`): Absolute time (as `datetime` or float timestamp) at which to execute the action.
        *   `action` (`Callable[[SchedulerBase, Optional[_TState]]], Optional[DisposableBase]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] State to be passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).

*   `schedule_periodic(period, action, state=None)`
    *   **Description**: Schedules a periodic piece of work to be executed in the loop.
    *   **Parameters**:
        *   `period` (`Union[timedelta, float]`): Period (in seconds) for running the work repeatedly.
        *   `action` (`Callable[[Optional[_TState]], Optional[_TState]]`): The action to be executed.
        *   `state` (`Optional[_TState]`): [Optional] Initial state passed to the action function.
    *   **Returns**: `DisposableBase` - An object used to cancel the scheduled action (best effort).
