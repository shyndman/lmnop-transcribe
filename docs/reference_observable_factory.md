<!-- https://rxpy.readthedocs.io/en/latest/reference_observable_factory.html -->
<!-- 7024 -->
This document describes the Observable Factory methods and related classes within the `reactivex` library, which are used to create and manage observable sequences.

### reactivex.amb(*\*sources*)

Propagates the observable sequence that emits first.

**Parameters:**

*   `sources` (`Observable`[`TypeVar`(`_T`)]) – Sequence of observables to monitor for first emission.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence that surfaces any of the given sequences, whichever emitted the first element.

**Example:**

```
>>> winner = reactivex.amb(xs, ys, zs)
```

### reactivex.case(*mapper*, *sources*, *default_source=None*)

Uses a mapper function to determine which source in a dictionary of sources to use.

**Parameters:**

*   `mapper` – The function which extracts the value to test in a case statement.
*   `sources` – An object which has keys that correspond to the case statement labels.
*   `default_source` (Optional) – The observable sequence or Future that will be run if the sources are not matched. If not provided, it defaults to `empty()`.

**Returns:**

*   An observable sequence which is determined by a case statement.

**Examples:**

```
>>> res = reactivex.case(mapper, { '1': obs1, '2': obs2 })
>>> res = reactivex.case(mapper, { '1': obs1, '2': obs2 }, obs0
```

### reactivex.catch(*\*sources*)

Continues observable sequences that are terminated with an exception by switching over to the next observable sequence.

**Parameters:**

*   `sources` (`Observable`[`TypeVar`(`_T`)]) – Sequence of observables.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence containing elements from consecutive observables from the sequence of sources until one of them terminates successfully.

**Examples:**

```
>>> res = reactivex.catch(xs, ys, zs)
```

### reactivex.catch_with_iterable(*sources*)

Continues observable sequences that are terminated with an exception by switching over to the next observable sequence.

**Parameters:**

*   `sources` (`Iterable`[[`Observable`[`TypeVar`(`_T`)]]]) – An Iterable of observables; a generator can also be used here.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence containing elements from consecutive observables from the sequence of sources until one of them terminates successfully.

**Examples:**

```
>>> res = reactivex.catch([xs, ys, zs])
>>> res = reactivex.catch(src for src in [xs, ys, zs])
```

### reactivex.create(*subscribe*)

Creates an observable sequence object from the specified subscription function.

**Parameters:**

*   `subscribe` (`Callable`[[`ObserverBase`[`TypeVar`(`_T`)], `Optional`[`SchedulerBase`]], `DisposableBase`]) – Subscription function.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence that can be subscribed to via the given subscription function.

### reactivex.combine_latest(*\*\_\_sources*)

Merges the specified observable sequences into one observable sequence by creating a tuple whenever any of the observable sequences emits an element.

**Parameters:**

*   `sources` – Sequence of observables.

**Returns:**

*   `Observable`[`Any`] – An observable sequence containing the result of combining elements from each source in given sequence.

**Examples:**

```
>>> obs = rx.combine_latest(obs1, obs2, obs3)
```

### reactivex.compose(*\*operators*)

Composes multiple operators left to right. A composition of zero operators gives back the source.

**Returns:**

*   `Callable`[[`Any`], `Any`] – The composed observable.

**Examples:**

```
>>> pipe()(source) == source
>>> pipe(f)(source) == f(source)
>>> pipe(f, g)(source) == g(f(source))
>>> pipe(f, g, h)(source) == h(g(f(source)))
```

### reactivex.concat(*\*sources*)

Concatenates all of the specified observable sequences.

**Parameters:**

*   `sources` (`Observable`[`TypeVar`(`_T`)]) – Sequence of observables.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence that contains the elements of each source in the given sequence, in sequential order.

**Examples:**

```
>>> res = reactivex.concat(xs, ys, zs)
```

### reactivex.concat_with_iterable(*sources*)

Concatenates all of the specified observable sequences.

**Parameters:**

*   `sources` (`Iterable`[[`Observable`[`TypeVar`(`_T`)]]]) – An Iterable of observables; thus, a generator can also be used here.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence that contains the elements of each given sequence, in sequential order.

**Examples:**

```
>>> res = reactivex.concat_with_iterable([xs, ys, zs])
>>> res = reactivex.concat_with_iterable(for src in [xs, ys, zs])
```

### class reactivex.ConnectableObservable(*source*, *subject*)

Represents an observable that can be connected and disconnected.

#### \_\_init\_\_(*source*, *subject*)

Creates an observable sequence object from the specified subscription function.

**Parameters:**

*   `subscribe` (Optional) – Subscription function.

#### connect(*scheduler=None*)

Connects the observable.

**Returns:**

*   `Optional`[`DisposableBase`]

#### auto_connect(*subscriber_count=1*)

Returns an observable sequence that stays connected to the source indefinitely. Providing a `subscriber_count` will cause it to `connect()` after that many subscriptions occur. A `subscriber_count` of 0 will result in emissions firing immediately without waiting for subscribers.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)]

### reactivex.defer(*factory*)

Returns an observable sequence that invokes the specified factory function whenever a new observer subscribes.

**Parameters:**

*   `factory` – Observable factory function to invoke for each observer which invokes `subscribe()` on the resulting sequence. The factory takes a single argument, the scheduler used.

**Returns:**

*   An observable sequence whose observers trigger an invocation of the given factory function.

**Example:**

```
>>> res = reactivex.defer(lambda scheduler: of(1, 2, 3))
```

### reactivex.empty(*scheduler=None*)

Returns an empty observable sequence.

**Parameters:**

*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler instance to send the termination call on. By default, this will use an instance of `ImmediateScheduler`.

**Returns:**

*   `Observable`[`Any`] – An observable sequence with no elements.

**Example:**

```
>>> obs = reactivex.empty()
```

### reactivex.fork_join(*\*sources*)

Waits for observables to complete and then combine last values they emitted into a tuple. Whenever any of those observables completes without emitting any value, the result sequence will complete at that moment as well.

**Parameters:**

*   `sources` (`Observable`[`Any`]) – Sequence of observables.

**Returns:**

*   `Observable`[`Any`] – An observable sequence containing the result of combining the last element from each source in the given sequence.

**Examples:**

```
>>> obs = reactivex.fork_join(obs1, obs2, obs3)
```

### reactivex.from_callable(*supplier*, *scheduler=None*)

Returns an observable sequence that contains a single element generated by the given supplier, using the specified scheduler to send out observer messages.

**Parameters:**

*   `supplier` (`Callable`[[], `TypeVar`(`_T`)]) – Function which is invoked to obtain the single element.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler instance to schedule the values on. If not specified, the default is to use an instance of `CurrentThreadScheduler`.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence containing the single element obtained by invoking the given supplier function.

**Examples:**

```
>>> res = reactivex.from_callable(lambda: calculate_value())
>>> res = reactivex.from_callable(lambda: 1 / 0) # emits an error
```

### reactivex.from_callback(*func*, *mapper=None*)

Converts a callback function to an observable sequence.

**Parameters:**

*   `func` (`Callable`[`...`, `Callable`[`...`, `None`]]) – Function with a callback as the last argument to convert to an Observable sequence.
*   `mapper` (`Optional`[`Callable`[[`Any`], `Any`]]) – [Optional] A mapper which takes the arguments from the callback to produce a single item to yield on next.

**Returns:**

*   `Callable`[[], [`Observable`[`Any`]]] – A function that, when executed with the required arguments minus the callback, produces an Observable sequence with a single value of the arguments to the callback as a list.

### reactivex.from_future(*future*)

Converts a Future to an Observable sequence.

**Parameters:**

*   `future` – A Python 3 compatible future.

**Returns:**

*   An observable sequence which wraps the existing future success and failure.

### reactivex.from_iterable(*iterable*, *scheduler=None*)

Converts an iterable to an observable sequence.

**Parameters:**

*   `iterable` (`Iterable`[`TypeVar`(`_T`)]) – An Iterable to change into an observable sequence.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler instance to schedule the values on. If not specified, the default is to use an instance of `CurrentThreadScheduler`.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – The observable sequence whose elements are pulled from the given iterable sequence.

**Example:**

```
>>> reactivex.from_iterable([1,2,3])
```

### class reactivex.GroupedObservable(*key*, *underlying_observable*, *merged_disposable=None*)

#### \_\_init\_\_(*key*, *underlying_observable*, *merged_disposable=None*)

Creates an observable sequence object from the specified subscription function.

**Parameters:**

*   `subscribe` (Optional) – Subscription function.

### reactivex.never()

Returns a non-terminating observable sequence, which can be used to denote an infinite duration (e.g., when using reactive joins).

**Returns:**

*   `Observable`[`Any`] – An observable sequence whose observers will never get called.

### class reactivex.Notification

Represents a notification to an observer.

#### \_\_init\_\_()

Default constructor used by derived types.

#### accept(*on_next*, *on_error=None*, *on_completed=None*)

Invokes the delegate corresponding to the notification or an observer and returns the produced result.

**Parameters:**

*   `on_next` (`Union`[`Callable`[[`TypeVar`(`_T`)], `None`], `ObserverBase`[`TypeVar`(`_T`)]]) – Delegate to invoke for an OnNext notification.
*   `on_error` (`Optional`[`Callable`[[`Exception`], `None`]]) – [Optional] Delegate to invoke for an OnError notification.
*   `on_completed` (`Optional`[`Callable`[[], `None`]]) – [Optional] Delegate to invoke for an OnCompleted notification.

**Returns:**

*   `None` – Result produced by the observation.

**Examples:**

```
>>> notification.accept(observer)
>>> notification.accept(on_next, on_error, on_completed)
```

#### to_observable(*scheduler=None*)

Returns an observable sequence with a single notification, using the specified scheduler, else the immediate scheduler.

**Parameters:**

*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler to send out the notification calls on.

**Returns:**

*   `ObservableBase`[`TypeVar`(`_T`)] – An observable sequence that surfaces the behavior of the notification upon subscription.

#### equals(*other*)

Indicates whether this instance and a specified object are equal.

**Returns:**

*   `bool`

#### \_\_eq\_\_(*other*)

Return self==value.

**Returns:**

*   `bool`

#### \_\_hash\_\_ *= None*

### reactivex.on_error_resume_next(*\*sources*)

Continues an observable sequence that is terminated normally or by an exception with the next observable sequence.

**Parameters:**

*   `sources` – Sequence of sources, each of which is expected to be an instance of either `Observable` or `Future`.

**Returns:**

*   An observable sequence that concatenates the source sequences, even if a sequence terminates with an exception.

**Examples:**

```
>>> res = reactivex.on_error_resume_next(xs, ys, zs)
```

### reactivex.of(*\*args*)

This method creates a new observable sequence whose elements are taken from the arguments. This is a wrapper for `reactivex.from_iterable(args)`.

**Parameters:**

*   `args` (`TypeVar`(`_T`)) – The variable number elements to emit from the observable.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – The observable sequence whose elements are pulled from the given arguments.

**Example:**

```
>>> res = reactivex.of(1,2,3)
```

### class reactivex.Observable(*subscribe=None*)

Observable base class. Represents a push-style collection, which you can `pipe` into `operators`.

#### \_\_init\_\_(*subscribe=None*)

Creates an observable sequence object from the specified subscription function.

**Parameters:**

*   `subscribe` (`Optional`[`Callable`[[`ObserverBase`[`TypeVar`(`_T_out`, covariant=True)], `Optional`[`SchedulerBase`]], `DisposableBase`]]) – [Optional] Subscription function.

#### subscribe(*on_next=None*, *on_error=None*, *on_completed=None*, *\**, *scheduler=None*)

Subscribe an observer to the observable sequence. You may subscribe using an observer or callbacks, not both; if the first argument is an instance of `Observer` or if it has a (callable) attribute named `on_next`, then any callback arguments will be ignored.

**Parameters:**

*   `observer` (Optional) – The object that is to receive notifications.
*   `on_error` (`Optional`[`Callable`[[`Exception`], `None`]]) – [Optional] Action to invoke upon exceptional termination of the observable sequence.
*   `on_completed` (`Optional`[`Callable`[[], `None`]]) – [Optional] Action to invoke upon graceful termination of the observable sequence.
*   `on_next` (`Union`[`ObserverBase`[`TypeVar`(`_T_out`, covariant=True)], `Callable`[[`TypeVar`(`_T_out`, covariant=True)], `None`], `None`]) – [Optional] Action to invoke for each element in the observable sequence.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] The default scheduler to use for this subscription.

**Returns:**

*   `DisposableBase` – Disposable object representing an observer’s subscription to the observable sequence.

**Examples:**

```
>>> source.subscribe()
>>> source.subscribe(observer)
>>> source.subscribe(observer, scheduler=scheduler)
>>> source.subscribe(on_next)
>>> source.subscribe(on_next, on_error)
>>> source.subscribe(on_next, on_error, on_completed)
>>> source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)
```

#### pipe(*\*operators*)

Composes multiple operators left to right. A composition of zero operators gives back the original source.

**Parameters:**

*   `operators` (`Callable`[[`Any`], `Any`]) – Sequence of operators.

**Returns:**

*   `Any` – The composed observable.

**Examples:**

```
>>> source.pipe() == source
>>> source.pipe(f) == f(source)
>>> source.pipe(g, f) == f(g(source))
>>> source.pipe(h, g, f) == f(g(h(source)))
```

#### run()

Runs the source synchronously. Subscribes to the observable source, then blocks and waits for it to either complete or error. Returns the last value emitted, or throws an exception if any error occurred.

**Returns:**

*   `Any` – The last element emitted from the observable.

**Raises:**

*   `SequenceContainsNoElementsError` – if observable completes (on_completed) without any values being emitted.
*   `Exception` – raises exception if any error (on_error) occurred.

**Examples:**

```
>>> result = run(source)
```

#### \_\_await\_\_()

Awaits the given observable.

**Returns:**

*   `Generator`[`Any`, `None`, `TypeVar`(`_T_out`, covariant=True)] – The last item of the observable sequence.

#### \_\_add\_\_(*other*)

Pythonic version of `concat`.

**Parameters:**

*   `other` (`Observable`[`TypeVar`(`_T_out`, covariant=True)]) – The second observable sequence in the concatenation.

**Returns:**

*   `Observable`[`TypeVar`(`_T_out`, covariant=True)] – Concatenated observable sequence.

**Example:**

```
>>> zs = xs + ys
```

#### \_\_iadd\_\_(*other*)

Pythonic use of `concat`.

**Parameters:**

*   `other` (`Observable`[`TypeVar`(`_T_out`, covariant=True)]) – The second observable sequence in the concatenation.

**Returns:**

*   `Observable`[`_T_out`] – Concatenated observable sequence.

**Example:**

```
>>> xs += ys
```

#### \_\_getitem\_\_(*key*)

Pythonic version of `slice`. Slices the given observable using Python slice notation (`start`, `stop`, `step`). It is a wrapper around the operators `skip`, `skip_last`, `take`, `take_last`, and `filter`.

**Parameters:**

*   `key` (`Union`[`slice`, `int`]) – Slice object.

**Returns:**

*   `Observable`[`TypeVar`(`_T_out`, covariant=True)] – Sliced observable sequence.

**Raises:**

*   `TypeError` – If key is not of type `int` or `slice`.

**Examples:**

```
>>> result = source[1:10]
>>> result = source[1:-2]
>>> result = source[1:-1:2]
```

### class reactivex.Observer(*on_next=None*, *on_error=None*, *on_completed=None*)

Base class for implementations of the Observer class. This base class enforces the grammar of observers where OnError and OnCompleted are terminal messages.

#### \_\_init\_\_(*on_next=None*, *on_error=None*, *on_completed=None*)

#### on_next(*value*)

Notify the observer of a new element in the sequence.

**Returns:**

*   `None`

#### on_error(*error*)

Notify the observer that an exception has occurred.

**Parameters:**

*   `error` (`Exception`) – The error that occurred.

**Returns:**

*   `None`

#### on_completed()

Notifies the observer of the end of the sequence.

**Returns:**

*   `None`

#### dispose()

Disposes the observer, causing it to transition to the stopped state.

**Returns:**

*   `None`

#### to_notifier()

Creates a notification callback from an observer. Returns the action that forwards its input notification to the underlying observer.

**Returns:**

*   `Callable`[[[`Notification`[`TypeVar`(`_T_in`, contravariant=True)]], `None`]]

#### as_observer()

Hides the identity of an observer. Returns an observer that hides the identity of the specified observer.

**Returns:**

*   `ObserverBase`[`TypeVar`(`_T_in`, contravariant=True)]

### reactivex.return_value(*value*, *scheduler=None*)

Returns an observable sequence that contains a single element, using the specified scheduler to send out observer messages. There is an alias called 'just'.

**Parameters:**

*   `value` (`TypeVar`(`_T`)) – Single element in the resulting observable sequence.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler instance to send the termination call on.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence containing the single specified element.

**Examples:**

```
>>> res = reactivex.return_value(42)
>>> res = reactivex.return_value(42, timeout_scheduler)
```

### reactivex.pipe(*\_\_value*, *\*fns*)

Functional pipe (|>) - Allows the use of function argument on the left side of the function.

**Returns:**

*   `Any`

**Example:**

```
>>> pipe(x, fn) == __fn(x)  # Same as x |> fn
>>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
```

### reactivex.range(*start*, *stop=None*, *step=None*, *scheduler=None*)

Generates an observable sequence of integral numbers within a specified range, using the specified scheduler to send out observer messages.

**Parameters:**

*   `start` (`int`) – The value of the first integer in the sequence.
*   `stop` (`Optional`[`int`]) – [Optional] Generate number up to (exclusive) the stop value. Default is `sys.maxsize`.
*   `step` (`Optional`[`int`]) – [Optional] The step to be used (default is 1).
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] The scheduler to schedule the values on. If not specified, the default is to use an instance of `CurrentThreadScheduler`.

**Returns:**

*   `Observable`[`int`] – An observable sequence that contains a range of sequential integral numbers.

**Examples:**

```
>>> res = reactivex.range(10)
>>> res = reactivex.range(0, 10)
>>> res = reactivex.range(0, 10, 1)
```

### reactivex.repeat_value(*value*, *repeat_count=None*)

Generates an observable sequence that repeats the given element the specified number of times.

**Parameters:**

*   `value` (`TypeVar`(`_T`)) – Element to repeat.
*   `repeat_count` (`Optional`[`int`]) – [Optional] Number of times to repeat the element. If not specified, repeats indefinitely.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence that repeats the given element the specified number of times.

**Examples:**

```
>>> res = reactivex.repeat_value(42)
>>> res = reactivex.repeat_value(42, 4)
```

### class reactivex.Subject

Represents an object that is both an observable sequence as well as an observer. Each notification is broadcasted to all subscribed observers.

#### \_\_init\_\_()

Creates an observable sequence object from the specified subscription function.

**Parameters:**

*   `subscribe` (Optional) – Subscription function.

#### on_next(*value*)

Notifies all subscribed observers with the value.

**Parameters:**

*   `value` (`TypeVar`(`_T`)) – The value to send to all subscribed observers.

**Returns:**

*   `None`

#### on_error(*error*)

Notifies all subscribed observers with the exception.

**Parameters:**

*   `error` (`Exception`) – The exception to send to all subscribed observers.

**Returns:**

*   `None`

#### on_completed()

Notifies all subscribed observers of the end of the sequence.

**Returns:**

*   `None`

#### dispose()

Unsubscribe all observers and release resources.

**Returns:**

*   `None`

### reactivex.start(*func*, *scheduler=None*)

Invokes the specified function asynchronously on the specified scheduler, surfacing the result through an observable sequence. The function is called immediately, not during the subscription of the resulting sequence. Multiple subscriptions to the resulting sequence can observe the function’s result.

**Parameters:**

*   `func` (`Callable`[[], `TypeVar`(`_T`)]) – Function to run asynchronously.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler to run the function on. If not specified, defaults to an instance of `TimeoutScheduler`.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence exposing the function’s result value, or an exception.

**Example:**

```
>>> res = reactivex.start(lambda: pprint('hello'))
>>> res = reactivex.start(lambda: pprint('hello'), rx.Scheduler.timeout)
```

### reactivex.start_async(*function_async*)

Invokes the asynchronous function, surfacing the result through an observable sequence.

**Parameters:**

*   `function_async` – Asynchronous function which returns a `Future` to run.

**Returns:**

*   An observable sequence exposing the function’s result value, or an exception.

### reactivex.throw(*exception*, *scheduler=None*)

Returns an observable sequence that terminates with an exception, using the specified scheduler to send out the single OnError message.

**Parameters:**

*   `exception` (`Union`[`str`, `Exception`]) – An object used for the sequence’s termination.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler to schedule the error notification on. If not specified, the default is to use an instance of `ImmediateScheduler`.

**Returns:**

*   `Observable`[`Any`] – The observable sequence that terminates exceptionally with the specified exception object.

**Example:**

```
>>> res = reactivex.throw(Exception('Error'))
```

### reactivex.timer(*duetime*, *period=None*, *scheduler=None*)

Returns an observable sequence that produces a value after `duetime` has elapsed and then after each `period`.

**Parameters:**

*   `duetime` (`Union`[`datetime`, `timedelta`, `float`]) – Absolute (specified as a datetime object) or relative time (specified as a float denoting seconds or an instance of timedelta) at which to produce the first value.
*   `period` (`Union`[`timedelta`, `float`, `None`]) – [Optional] Period to produce subsequent values (specified as a float denoting seconds or an instance of timedelta). If not specified, the resulting timer is not recurring.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler to run the timer on. If not specified, the default is to use an instance of `TimeoutScheduler`.

**Returns:**

*   `Observable`[`int`] – An observable sequence that produces a value after due time has elapsed and then each period.

**Examples:**

```
>>> res = reactivex.timer(datetime(...))
>>> res = reactivex.timer(datetime(...), 0.1)
>>> res = reactivex.timer(5.0)
>>> res = reactivex.timer(5.0, 1.0)
```

### reactivex.to_async(*func*, *scheduler=None*)

Converts the function into an asynchronous function. Each invocation of the resulting asynchronous function causes an invocation of the original synchronous function on the specified scheduler.

**Parameters:**

*   `func` (`Callable`[`...`, `TypeVar`(`_T`)]) – Function to convert to an asynchronous function.
*   `scheduler` (`Optional`[`SchedulerBase`]) – [Optional] Scheduler to run the function on. If not specified, defaults to an instance of `TimeoutScheduler`.

**Returns:**

*   `Callable`[`...`, [`Observable`[`TypeVar`(`_T`)]]] – Asynchronous function.

**Examples:**

```
>>> res = reactivex.to_async(lambda x, y: x + y)(4, 3)
>>> res = reactivex.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
>>> res = reactivex.to_async(lambda x: log.debug(x), Scheduler.timeout)('hello')
```

### reactivex.using(*resource_factory*, *observable_factory*)

Constructs an observable sequence that depends on a resource object, whose lifetime is tied to the resulting observable sequence’s lifetime.

**Parameters:**

*   `resource_factory` (`Callable`[[], `DisposableBase`]) – Factory function to obtain a resource object.
*   `observable_factory` (`Callable`[[`DisposableBase`], [`Observable`[`TypeVar`(`_T`)]]]) – Factory function to obtain an observable sequence that depends on the obtained resource.

**Returns:**

*   `Observable`[`TypeVar`(`_T`)] – An observable sequence whose lifetime controls the lifetime of the dependent resource object.

**Example:**

```
>>> res = reactivex.using(lambda: AsyncSubject(), lambda: s: s)
```

### reactivex.with_latest_from(*\*sources*)

Merges the specified observable sequences into one observable sequence by creating a `tuple` only when the first observable sequence produces an element.

**Parameters:**

*   `sources` (`Observable`[`Any`]) – Sequence of observables.

**Returns:**

*   `Observable`[`Tuple`[`Any`, `...`]] – An observable sequence containing the result of combining elements of the sources into a `tuple`.

**Examples:**

```
>>> obs = rx.with_latest_from(obs1)
>>> obs = rx.with_latest_from([obs1, obs2, obs3])
```

### reactivex.zip(*\*args*)

Merges the specified observable sequences into one observable sequence by creating a `tuple` whenever all of the observable sequences have produced an element at a corresponding index.

**Parameters:**

*   `args` (`Observable`[`Any`]) – Observable sources to zip.

**Returns:**

*   `Observable`[`Tuple`[`Any`, `...`]] – An observable sequence containing the result of combining elements of the sources as a `tuple`.

**Example:**

```
>>> res = rx.zip(obs1, obs2)
```
