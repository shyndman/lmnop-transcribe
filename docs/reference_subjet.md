<!-- https://rxpy.readthedocs.io/en/latest/reference_subject.html -->
<!-- 749 -->
This document summarizes the `Subject` classes within the `reactivex` library, which act as both observable sequences and observers, broadcasting notifications to subscribed observers.

### `reactivex.subject.Subject`

Represents an object that is both an observable sequence and an observer. Each notification is broadcasted to all subscribed observers.

#### `__init__(subscribe=None)`

Creates an observable sequence object.

*   **Parameters**:
    *   `subscribe` (`Optional`): [Optional] Subscription function.

#### `on_next(value)`

Notifies all subscribed observers with the value.

*   **Parameters**:
    *   `value` (`TypeVar(_T)`): The value to send to all subscribed observers.
*   **Returns**: `None`

#### `on_error(error)`

Notifies all subscribed observers with the exception.

*   **Parameters**:
    *   `error` (`Exception`): The exception to send to all subscribed observers.
*   **Returns**: `None`

#### `on_completed()`

Notifies all subscribed observers of the end of the sequence.

*   **Returns**: `None`

#### `dispose()`

Unsubscribes all observers and releases resources.

*   **Returns**: `None`

### `reactivex.subject.BehaviorSubject(value)`

Represents a value that changes over time. Observers can subscribe to the subject to receive the last (or initial) value and all subsequent notifications.

#### `__init__(value)`

Initializes a new instance of the `BehaviorSubject` class. This subject caches its last value and starts with the specified initial value.

*   **Parameters**:
    *   `value` (`TypeVar(_T)`): Initial value sent to observers when no other value has been received by the subject yet.

#### `dispose()`

Releases all resources used by the current instance of the `BehaviorSubject` class and unsubscribes all observers.

*   **Returns**: `None`

### `reactivex.subject.ReplaySubject(buffer_size=None, window=None, scheduler=None)`

Represents an object that is both an observable sequence and an observer. Each notification is broadcasted to all subscribed and future observers, subject to buffer trimming policies.

#### `__init__(buffer_size=None, window=None, scheduler=None)`

Initializes a new instance of the `ReplaySubject` class with the specified buffer size, window, and scheduler.

*   **Parameters**:
    *   `buffer_size` (`Optional[int]`): [Optional] Maximum element count of the replay buffer.
    *   `window` (`Optional`): [Optional] Maximum time length of the replay buffer.
    *   `scheduler` (`Optional[SchedulerBase]`): [Optional] Scheduler the observers are invoked on.

#### `dispose()`

Releases all resources used by the current instance of the `ReplaySubject` class and unsubscribes all observers.

*   **Returns**: `None`

### `reactivex.subject.AsyncSubject`

Represents the result of an asynchronous operation. The last value before the close notification, or the error received through `on_error`, is sent to all subscribed observers.

#### `__init__()`

Creates a subject that can only receive one value, and that value (the last one before completion) is cached for all future observations.

#### `dispose()`

Unsubscribes all observers and releases resources.

*   **Returns**: `None`
