<!-- https://rxpy.readthedocs.io/en/latest/reference_operators.html -->
<!-- 22113 -->
This document summarizes the `reactivex.operators` module, which provides a rich set of operators for composing observable sequences. These operators transform, combine, and filter data streams, enabling complex asynchronous programming patterns.

### `reactivex.operators.all(predicate)`

Determines whether all elements of an observable sequence satisfy a condition.

*   **Parameters**:
    *   `predicate` (`Callable[[_T], bool]`): A function to test each element for a condition.
*   **Returns**: `Callable[[Observable[_T]], Observable[bool]]`
    An operator function that takes an observable source and returns an observable sequence containing a single boolean element, indicating whether all elements in the source sequence pass the test in the specified predicate.
*   **Example**:
    ```
    >>> op = all(lambda value: value.length > 3)
    ```

### `reactivex.operators.amb(right_source)`

Propagates the observable sequence that reacts first.

*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that surfaces any of the given sequences, whichever reacted first.
*   **Example**:
    ```
    >>> op = amb(ys)
    ```

### `reactivex.operators.as_observable()`

Hides the identity of an observable sequence.

*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that hides the identity of the source sequence.

### `reactivex.operators.average(key_mapper=None)`

Computes the average of an observable sequence of values. Values can be directly from the sequence or obtained by invoking a transform function on each element.

*   **Parameters**:
    *   `key_mapper` (`Optional[Callable[[_T], float]]`): \[Optional] A transform function to apply to each element.
*   **Returns**: `Callable[[Observable[_T]], Observable[float]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element with the average of the sequence of values.
*   **Examples**:
    ```
    >>> op = average()
    >>> op = average(lambda x: x.value)
    ```

### `reactivex.operators.buffer(boundaries)`

Projects each element of an observable sequence into zero or more buffers.

*   **Parameters**:
    *   `boundaries` (`Observable[Any]`): Observable sequence whose elements denote the creation and completion of buffers.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    A function that takes an observable source and returns an observable sequence of buffers.
*   **Examples**:
    ```
    >>> res = buffer(reactivex.interval(1.0))
    ```

### `reactivex.operators.buffer_when(closing_mapper)`

Projects each element of an observable sequence into zero or more buffers. A buffer is started when the previous one is closed, resulting in non-overlapping buffers. The buffer is closed when one item is emitted or when the observable completes.

*   **Parameters**:
    *   `closing_mapper` (`Callable[[], Observable[Any]]`): A function invoked to define the closing of each produced buffer.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    A function that takes an observable source and returns an observable sequence of windows.
*   **Examples**:
    ```
    >>> res = buffer_when(lambda: reactivex.timer(0.5))
    ```

### `reactivex.operators.buffer_toggle(openings, closing_mapper)`

Projects each element of an observable sequence into zero or more buffers.

*   **Parameters**:
    *   `openings` (`Observable[Any]`): Observable sequence whose elements denote the creation of buffers.
    *   `closing_mapper` (`Callable[[Any], Observable[Any]]`): A function invoked to define the closing of each produced buffer. The value from the `openings` Observable that initiated the associated buffer is provided as an argument to this function. The buffer is closed when one item is emitted or when the observable completes.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    A function that takes an observable source and returns an observable sequence of windows.
*   **Example**:
    ```
    >>> res = buffer_toggle(reactivex.interval(0.5), lambda i: reactivex.timer(i))
    ```

### `reactivex.operators.buffer_with_count(count, skip=None)`

Projects each element of an observable sequence into zero or more buffers which are produced based on element count information.

*   **Parameters**:
    *   `count` (`int`): Length of each buffer.
    *   `skip` (`Optional[int]`): \[Optional] Number of elements to skip between creation of consecutive buffers. If not provided, defaults to `count`.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    A function that takes an observable source and returns an observable sequence of buffers.
*   **Examples**:
    ```
    >>> res = buffer_with_count(10)(xs)
    >>> res = buffer_with_count(10, 1)(xs)
    ```

### `reactivex.operators.buffer_with_time(timespan, timeshift=None, scheduler=None)`

Projects each element of an observable sequence into zero or more buffers which are produced based on timing information.

*   **Parameters**:
    *   `timespan` (`Union[timedelta, float]`): Length of each buffer (specified as a float denoting seconds or an instance of `timedelta`).
    *   `timeshift` (`Union[timedelta, float, None]`): \[Optional] Interval between creation of consecutive buffers (specified as a float denoting seconds or an instance of `timedelta`). If not specified, `timeshift` will be the same as `timespan`, resulting in non-overlapping adjacent buffers.
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] Scheduler to run the timer on. If not specified, the timeout scheduler is used.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    An operator function that takes an observable source and returns an observable sequence of buffers.
*   **Examples**:
    ```
    >>> # non-overlapping segments of 1 second
    >>> res = buffer_with_time(1.0)
    >>> # segments of 1 second with time shift 0.5 seconds
    >>> res = buffer_with_time(1.0, 0.5)
    ```

### `reactivex.operators.buffer_with_time_or_count(timespan, count, scheduler=None)`

Projects each element of an observable sequence into a buffer that is completed when either it’s full or a given amount of time has elapsed.

*   **Parameters**:
    *   `timespan` (`Union[timedelta, float]`): Maximum time length of a buffer.
    *   `count` (`int`): Maximum element count of a buffer.
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] Scheduler to run buffering timers on. If not specified, the timeout scheduler is used.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    An operator function that takes an observable source and returns an observable sequence of buffers.
*   **Examples**:
    ```
    >>> # 5s or 50 items in an array
    >>> res = source._buffer_with_time_or_count(5.0, 50)
    >>> # 5s or 50 items in an array
    >>> res = source._buffer_with_time_or_count(5.0, 50, Scheduler.timeout)
    ```

### `reactivex.operators.catch(handler)`

Continues an observable sequence that is terminated by an exception with the next observable sequence.

*   **Parameters**:
    *   `handler` (`Union[Observable[_T], Callable[[Exception, Observable[_T]], Observable[_T]]]`): Second observable sequence used to produce results when an error occurred in the first sequence, or an exception handler function that returns an observable sequence given the error and source observable that occurred in the first sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A function taking an observable source and returns an observable sequence containing the first sequence’s elements, followed by the elements of the handler sequence in case an exception occurred.
*   **Examples**:
    ```
    >>> op = catch(ys)
    >>> op = catch(lambda ex, src: ys(ex))
    ```

### `reactivex.operators.combine_latest(*others)`

Merges the specified observable sequences into one observable sequence by creating a tuple whenever any of the observable sequences produces an element.

*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence containing the result of combining elements of the sources into a tuple.
*   **Examples**:
    ```
    >>> obs = combine_latest(other)
    >>> obs = combine_latest(obs1, obs2, obs3)
    ```

### `reactivex.operators.concat(*sources)`

Concatenates all the observable sequences.

*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes one or more observable sources and returns an observable sequence that contains the elements of each given sequence, in sequential order.
*   **Examples**:
    ```
    >>> op = concat(xs, ys, zs)
    ```

### `reactivex.operators.contains(value, comparer=None)`

Determines whether an observable sequence contains a specified element with an optional equality comparer.

*   **Parameters**:
    *   `value` (`_T`): The value to locate in the source sequence.
    *   `comparer` (`Optional[Callable[[_T, _T], bool]]`): \[Optional] An equality comparer to compare elements.
*   **Returns**: `Callable[[Observable[_T]], Observable[bool]]`
    A function that takes a source observable that returns an observable sequence containing a single element determining whether the source sequence contains an element that has the specified value.
*   **Examples**:
    ```
    >>> op = contains(42)
    >>> op = contains({ "value": 42 }, lambda x, y: x["value"] == y["value"])
    ```

### `reactivex.operators.count(predicate=None)`

Returns an observable sequence containing a value that represents how many elements in the specified observable sequence satisfy a condition if provided, else the count of items.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): A function to test each element for a condition.
*   **Returns**: `Callable[[Observable[_T]], Observable[int]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element with a number that represents how many elements in the input sequence satisfy the condition in the predicate function if provided, else the count of items in the sequence.
*   **Examples**:
    ```
    >>> op = count()
    >>> op = count(lambda x: x > 3)
    ```

### `reactivex.operators.debounce(duetime, scheduler=None)`

Ignores values from an observable sequence which are followed by another value before `duetime`.

*   **Parameters**:
    *   `duetime` (`Union[timedelta, float]`): Duration of the throttle period for each value (specified as a float denoting seconds or an instance of `timedelta`).
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to debounce values on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes the source observable and returns the debounced observable sequence.
*   **Example**:
    ```
    >>> res = debounce(5.0) # 5 seconds
    ```

### `reactivex.operators.throttle_with_timeout(duetime, scheduler=None)`

Alias for `debounce`. Ignores values from an observable sequence which are followed by another value before `duetime`.

*   **Parameters**:
    *   `duetime` (`Union[timedelta, float]`): Duration of the throttle period for each value (specified as a float denoting seconds or an instance of `timedelta`).
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to debounce values on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes the source observable and returns the debounced observable sequence.
*   **Example**:
    ```
    >>> res = debounce(5.0) # 5 seconds
    ```

### `reactivex.operators.default_if_empty(default_value=None)`

Returns the elements of the specified sequence or the specified value in a singleton sequence if the sequence is empty.

*   **Parameters**:
    *   `default_value` (`Optional[Any]`): The value to return if the sequence is empty. If not provided, this defaults to `None`.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence that contains the specified default value if the source is empty, otherwise, the elements of the source.
*   **Examples**:
    ```
    >>> res = obs = default_if_empty()
    >>> obs = default_if_empty(False)
    ```

### `reactivex.operators.delay_subscription(duetime, scheduler=None)`

Time shifts the observable sequence by delaying the subscription.

*   **Parameters**:
    *   `duetime` (`Union[datetime, timedelta, float]`): Absolute or relative time to perform the subscription at.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to delay subscription on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A function that takes a source observable and returns a time-shifted observable sequence.
*   **Example**:
    ```
    >>> res = delay_subscription(5.0) # 5s
    ```

### `reactivex.operators.delay_with_mapper(subscription_delay=None, delay_duration_mapper=None)`

Time shifts the observable sequence based on a subscription delay and a delay mapper function for each element.

*   **Parameters**:
    *   `subscription_delay` (`Union[Observable[Any], Callable[[Any], Observable[Any]], None]`): \[Optional] Sequence indicating the delay for the subscription to the source.
    *   `delay_duration_mapper` (`Optional[Callable[[_T], Observable[Any]]]`): \[Optional] Selector function to retrieve a sequence indicating the delay for each given element.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A function that takes an observable source and returns a time-shifted observable sequence.
*   **Examples**:
    ```
    >>> # with mapper only
    >>> res = source.delay_with_mapper(lambda x: reactivex.timer(5.0))
    >>> # with delay and mapper
    >>> res = source.delay_with_mapper(
        reactivex.timer(2.0), lambda x: reactivex.timer(x)
    )
    ```

### `reactivex.operators.dematerialize()`

Dematerializes the explicit notification values of an observable sequence as implicit notifications.

*   **Returns**: `Callable[[Observable[Notification[_T]]], Observable[_T]]`
    An observable sequence exhibiting the behavior corresponding to the source sequence’s notification values.

### `reactivex.operators.delay(duetime, scheduler=None)`

Time shifts the observable sequence by `duetime`. The relative time intervals between the values are preserved.

*   **Parameters**:
    *   `duetime` (`Union[timedelta, float]`): Relative time, specified as a float denoting seconds or an instance of `timedelta`, by which to shift the observable sequence.
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] Scheduler to run the delay timers on. If not specified, the timeout scheduler is used.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A partially applied operator function that takes the source observable and returns a time-shifted sequence.
*   **Examples**:
    ```
    >>> res = delay(timedelta(seconds=10))
    >>> res = delay(5.0)
    ```

### `reactivex.operators.distinct(key_mapper=None, comparer=None)`

Returns an observable sequence that contains only distinct elements according to the `key_mapper` and the `comparer`.

*   **Important**: Usage of this operator should be considered carefully due to the maintenance of an internal lookup structure which can grow large.
*   **Parameters**:
    *   `key_mapper` (`Optional[Callable[[_T], _TKey]]`): \[Optional] A function to compute the comparison key for each element.
    *   `comparer` (`Optional[Callable[[_TKey, _TKey], bool]]`): \[Optional] Used to compare items in the collection.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence only containing the distinct elements, based on a computed key value, from the source sequence.
*   **Examples**:
    ```
    >>> res = obs = xs.distinct()
    >>> obs = xs.distinct(lambda x: x.id)
    >>> obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)
    ```

### `reactivex.operators.distinct_until_changed(key_mapper=None, comparer=None)`

Returns an observable sequence that contains only distinct contiguous elements according to the `key_mapper` and the `comparer`.

*   **Parameters**:
    *   `key_mapper` (`Optional[Callable[[_T], _TKey]]`): \[Optional] A function to compute the comparison key for each element. If not provided, it projects the value.
    *   `comparer` (`Optional[Callable[[_TKey, _TKey], bool]]`): \[Optional] Equality comparer for computed key values. If not provided, defaults to an equality comparer function.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence only containing the distinct contiguous elements, based on a computed key value, from the source sequence.
*   **Examples**:
    ```
    >>> op = distinct_until_changed();
    >>> op = distinct_until_changed(lambda x: x.id)
    >>> op = distinct_until_changed(lambda x: x.id, lambda x, y: x == y)
    ```

### `reactivex.operators.do(observer)`

Invokes an action for each element in the observable sequence and invokes an action on graceful or exceptional termination of the observable sequence. This method can be used for debugging, logging, etc. of query behavior by intercepting the message stream to run arbitrary actions for messages on the pipeline.

*   **Parameters**:
    *   `observer` (`ObserverBase[_T]`): Observer.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes the source observable and returns the source sequence with the side-effecting behavior applied.
*   **Example**:
    ```
    >>> do(observer)
    ```

### `reactivex.operators.do_action(on_next=None, on_error=None, on_completed=None)`

Invokes an action for each element in the observable sequence and invokes an action on graceful or exceptional termination of the observable sequence. This method can be used for debugging, logging, etc. of query behavior by intercepting the message stream to run arbitrary actions for messages on the pipeline.

*   **Parameters**:
    *   `on_next` (`Optional[Callable[[_T], None]]`): \[Optional] Action to invoke for each element in the observable sequence.
    *   `on_error` (`Optional[Callable[[Exception], None]]`): \[Optional] Action to invoke on exceptional termination of the observable sequence.
    *   `on_completed` (`Optional[Callable[[], None]]`): \[Optional] Action to invoke on graceful termination of the observable sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes the source observable and returns the source sequence with the side-effecting behavior applied.
*   **Examples**:
    ```
    >>> do_action(send)
    >>> do_action(on_next, on_error)
    >>> do_action(on_next, on_error, on_completed)
    ```

### `reactivex.operators.do_while(condition)`

Repeats source as long as condition holds, emulating a do-while loop.

*   **Parameters**:
    *   `condition` (`Callable[[Observable[_T]], bool]`): The condition which determines if the source will be repeated.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An observable sequence which is repeated as long as the condition holds.

### `reactivex.operators.element_at(index)`

Returns the element at a specified index in a sequence.

*   **Parameters**:
    *   `index` (`int`): The zero-based index of the element to retrieve.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that produces the element at the specified position in the source sequence.
*   **Example**:
    ```
    >>> res = source.element_at(5)
    ```

### `reactivex.operators.element_at_or_default(index, default_value=None)`

Returns the element at a specified index in a sequence or a default value if the index is out of range.

*   **Parameters**:
    *   `index` (`int`): The zero-based index of the element to retrieve.
    *   `default_value` (`Optional[_T]`): \[Optional] The default value if the index is outside the bounds of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A function that takes an observable source and returns an observable sequence that produces the element at the specified position in the source sequence, or a default value if the index is outside the bounds of the source sequence.
*   **Example**:
    ```
    >>> res = source.element_at_or_default(5)
    >>> res = source.element_at_or_default(5, 0)
    ```

### `reactivex.operators.exclusive()`

Performs an exclusive waiting for the first observable to finish before subscribing to another observable. Observables that come in between subscriptions will be dropped.

*   **Returns**: `Callable[[Observable[Observable[_T]]], Observable[_T]]`
    An exclusive observable with only the results that happen when subscribed.

### `reactivex.operators.expand(mapper)`

Expands an observable sequence by recursively invoking `mapper`.

*   **Parameters**:
    *   `mapper` (`Callable[[_T], Observable[_T]]`): Mapper function to invoke for each produced element, resulting in another sequence to which the mapper will be invoked recursively again.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An observable sequence containing all the elements produced by the recursive expansion.

### `reactivex.operators.filter(predicate)`

Filters the elements of an observable sequence based on a predicate.

*   **Parameters**:
    *   `predicate` (`Callable[[_T], bool]`): A function to test each source element for a condition.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains elements from the input sequence that satisfy the condition.
*   **Example**:
    ```
    >>> op = filter(lambda value: value < 10)
    ```

### `reactivex.operators.filter_indexed(predicate_indexed=None)`

Filters the elements of an observable sequence based on a predicate by incorporating the element’s index.

*   **Parameters**:
    *   `predicate` (`Callable[[_T, int], bool]`): A function to test each source element for a condition; the second parameter of the function represents the index of the source element.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains elements from the input sequence that satisfy the condition.
*   **Example**:
    ```
    >>> op = filter_indexed(lambda value, index: (value + index) < 10)
    ```

### `reactivex.operators.finally_action(action)`

Invokes a specified action after the source observable sequence terminates gracefully or exceptionally.

*   **Parameters**:
    *   `action` (`Callable[[], None]`): Action to invoke after the source observable sequence terminates.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence with the action-invoking termination behavior applied.
*   **Example**:
    ```
    >>> res = finally_action(lambda: print('sequence ended')
    ```

### `reactivex.operators.find(predicate)`

Searches for an element that matches the conditions defined by the specified predicate, and returns the first occurrence within the entire Observable sequence.

*   **Parameters**:
    *   `predicate` (`Callable[[_T, int, Observable[_T]], bool]`): The predicate that defines the conditions of the element to search for.
*   **Returns**: `Callable[[Observable[_T]], Observable[Optional[_T]]]`
    An operator function that takes an observable source and returns an observable sequence with the first element that matches the conditions defined by the specified predicate, if found, otherwise, `None`.

### `reactivex.operators.find_index(predicate)`

Searches for an element that matches the conditions defined by the specified predicate, and returns an Observable sequence with the zero-based index of the first occurrence within the entire Observable sequence.

*   **Parameters**:
    *   `predicate` (`Callable[[_T, int, Observable[_T]], bool]`): The predicate that defines the conditions of the element to search for.
*   **Returns**: `Callable[[Observable[_T]], Observable[Optional[int]]]`
    An operator function that takes an observable source and returns an observable sequence with the zero-based index of the first occurrence of an element that matches the conditions defined by match, if found; otherwise, -1.

### `reactivex.operators.first(predicate=None)`

Returns the first element of an observable sequence that satisfies the condition in the predicate if present, else the first item in the sequence.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): \[Optional] A predicate function to evaluate for elements in the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A function that takes an observable source and returns an observable sequence containing the first element in the observable sequence that satisfies the condition in the predicate if provided, else the first item in the sequence.
*   **Examples**:
    ```
    >>> res = res = first()
    >>> res = res = first(lambda x: x > 3)
    ```

### `reactivex.operators.first_or_default(predicate=None, default_value=None)`

Returns the first element of an observable sequence that satisfies the condition in the predicate, or a default value if no such element exists.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): \[Optional] A predicate function to evaluate for elements in the source sequence.
    *   `default_value` (`Optional[_T]`): \[Optional] The default value if no such element exists. If not specified, defaults to `None`.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A function that takes an observable source and returns an observable sequence containing the first element in the observable sequence that satisfies the condition in the predicate, or a default value if no such element exists.
*   **Examples**:
    ```
    >>> res = first_or_default()
    >>> res = first_or_default(lambda x: x > 3)
    >>> res = first_or_default(lambda x: x > 3, 0)
    >>> res = first_or_default(None, 0)
    ```

### `reactivex.operators.flat_map(mapper=None)`

Projects each element of an observable sequence to an observable sequence and merges the resulting observable sequences into one observable sequence. Alternatively, projects each element of the source observable sequence to another observable sequence and merges the resulting observable sequences into one observable sequence.

*   **Parameters**:
    *   `mapper` (`Optional[Any]`): A transform function to apply to each element or an observable sequence to project each element from the source sequence onto.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes a source observable and returns an observable sequence whose elements are the result of invoking the one-to-many transform function on each element of the input sequence.
*   **Example**:
    ```
    >>> flat_map(lambda x: Observable.range(0, x))
    ```
    Or:
    ```
    >>> flat_map(Observable.of(1, 2, 3))
    ```

### `reactivex.operators.flat_map_indexed(mapper_indexed=None)`

Projects each element of an observable sequence to an observable sequence and merges the resulting observable sequences into one observable sequence, incorporating the element's index. Alternatively, projects each element of the source observable sequence to another observable sequence and merges the resulting observable sequences into one observable sequence.

*   **Parameters**:
    *   `mapper_indexed` (`Optional[Any]`): \[Optional] A transform function to apply to each element or an observable sequence to project each element from the source sequence onto.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence whose elements are the result of invoking the one-to-many transform function on each element of the input sequence.
*   **Example**:
    ```
    >>> source.flat_map_indexed(lambda x, i: Observable.range(0, x))
    ```
    Or:
    ```
    >>> source.flat_map_indexed(Observable.of(1, 2, 3))
    ```

### `reactivex.operators.flat_map_latest(mapper)`

Projects each element of an observable sequence into a new sequence of observable sequences by incorporating the element’s index and then transforms an observable sequence of observable sequences into an observable sequence producing values only from the most recent observable sequence.

*   **Parameters**:
    *   `mapper` (`Callable[[_T, int], Observable[Any]]`): A transform function to apply to each source element. The second parameter of the function represents the index of the source element.
*   **Returns**: `Callable[[Observable[_T]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence whose elements are the result of invoking the transform function on each element of source producing an observable of Observable sequences and that at any point in time produces the elements of the most recent inner observable sequence that has been received.

### `reactivex.operators.fork_join(*others)`

Waits for observables to complete and then combine last values they emitted into a tuple.

*   **Important**: Whenever any of the observables completes without emitting any value, the result sequence will complete at that moment as well.
*   **Returns**: `Callable[[Observable[Any]], Observable[Tuple[Any, ...]]]`
    An operator function that takes an observable source and returns an observable sequence containing the result of combining the last element from each source in the given sequence.
*   **Examples**:
    ```
    >>> res = fork_join(obs1)
    >>> res = fork_join(obs1, obs2, obs3)
    ```

### `reactivex.operators.group_by(key_mapper, element_mapper=None, subject_mapper=None)`

Groups the elements of an observable sequence according to a specified key mapper function and selects the resulting elements by using a specified function.

*   **Parameters**:
    *   `key_mapper` (`Callable[[_T], _TKey]`): A function to extract the key for each element.
    *   `element_mapper` (`Optional[Callable[[_T], _TValue]]`): \[Optional] A function to map each source element to an element in an observable group.
    *   `subject_mapper` (`Optional[Callable[[], Subject[_TValue]]]`): A function that returns a subject used to initiate a grouped observable. Default mapper returns a `Subject` object.
*   **Returns**: `Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]`
    An operator function that takes an observable source and returns a sequence of observable groups, each of which corresponds to a unique key value, containing all elements that share that same key value.
*   **Examples**:
    ```
    >>> group_by(lambda x: x.id)
    >>> group_by(lambda x: x.id, lambda x: x.name)
    >>> group_by(lambda x: x.id, lambda x: x.name, lambda: ReplaySubject())
    ```

### `reactivex.operators.group_by_until(key_mapper, element_mapper, duration_mapper, subject_mapper=None)`

Groups the elements of an observable sequence according to a specified key mapper function. A duration mapper function is used to control the lifetime of groups. When a group expires, it receives an `OnCompleted` notification. When a new element with the same key value as a reclaimed group occurs, the group will be reborn with a new lifetime request.

*   **Parameters**:
    *   `key_mapper` (`Callable[[_T], _TKey]`): A function to extract the key for each element.
    *   `element_mapper` (`Optional[Callable[[_T], _TValue]]`): A function to map each source element to an element in an observable group.
    *   `duration_mapper` (`Callable[[GroupedObservable[_TKey, _TValue]], Observable[Any]]`): A function to signal the expiration of a group.
    *   `subject_mapper` (`Optional[Callable[[], Subject[_TValue]]]`): A function that returns a subject used to initiate a grouped observable. Default mapper returns a `Subject` object.
*   **Returns**: `Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]`
    An operator function that takes an observable source and returns a sequence of observable groups, each of which corresponds to a unique key value, containing all elements that share that same key value. If a group’s lifetime expires, a new group with the same key value can be created once an element with such a key value is encountered.
*   **Examples**:
    ```
    >>> group_by_until(lambda x: x.id, None, lambda : reactivex.never())
    >>> group_by_until(
        lambda x: x.id, lambda x: x.name, lambda grp: reactivex.never()
    )
    >>> group_by_until(
        lambda x: x.id,
        lambda x: x.name,
        lambda grp: reactivex.never(),
        lambda: ReplaySubject()
    )
    ```

### `reactivex.operators.group_join(right, left_duration_mapper, right_duration_mapper)`

Correlates the elements of two sequences based on overlapping durations, and groups the results.

*   **Parameters**:
    *   `right` (`Observable[_TRight]`): The right observable sequence to join elements for.
    *   `left_duration_mapper` (`Callable[[_TLeft], Observable[Any]]`): A function to select the duration (expressed as an observable sequence) of each element of the left observable sequence, used to determine overlap.
    *   `right_duration_mapper` (`Callable[[_TRight], Observable[Any]]`): A function to select the duration (expressed as an observable sequence) of each element of the right observable sequence, used to determine overlap.
*   **Returns**: `Callable[[Observable[_TLeft]], Observable[Tuple[_TLeft, Observable[_TRight]]]]`
    An operator function that takes an observable source and returns an observable sequence that contains elements combined into a tuple from source elements that have an overlapping duration.

### `reactivex.operators.ignore_elements()`

Ignores all elements in an observable sequence leaving only the termination messages.

*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an empty observable sequence that signals termination, successful or exceptional, of the source sequence.

### `reactivex.operators.is_empty()`

Determines whether an observable sequence is empty.

*   **Returns**: `Callable[[Observable[Any]], Observable[bool]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element determining whether the source sequence is empty.

### `reactivex.operators.join(right, left_duration_mapper, right_duration_mapper)`

Correlates the elements of two sequences based on overlapping durations.

*   **Parameters**:
    *   `right` (`Observable[_T2]`): The right observable sequence to join elements for.
    *   `left_duration_mapper` (`Callable[[Any], Observable[Any]]`): A function to select the duration (expressed as an observable sequence) of each element of the left observable sequence, used to determine overlap.
    *   `right_duration_mapper` (`Callable[[Any], Observable[Any]]`): A function to select the duration (expressed as an observable sequence) of each element of the right observable sequence, used to determine overlap.
*   **Returns**: `Callable[[Observable[_T1]], Observable[Tuple[_T1, _T2]]]`
    An operator function that takes an observable source and returns an observable sequence that contains elements combined into a tuple from source elements that have an overlapping duration.

### `reactivex.operators.last(predicate=None)`

Returns the last element of an observable sequence that satisfies the condition in the predicate if specified, else the last element.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): \[Optional] A predicate function to evaluate for elements in the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the last element in the observable sequence that satisfies the condition in the predicate.
*   **Examples**:
    ```
    >>> op = last()
    >>> op = last(lambda x: x > 3)
    ```

### `reactivex.operators.last_or_default(default_value=None, predicate=None)`

Returns the last element of an observable sequence that satisfies the condition in the predicate, or a default value if no such element exists.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): \[Optional] A predicate function to evaluate for elements in the source sequence.
    *   `default_value` (`Optional[Any]`): \[Optional] The default value if no such element exists. If not specified, defaults to `None`.
*   **Returns**: `Callable[[Observable[_T]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence containing the last element in the observable sequence that satisfies the condition in the predicate, or a default value if no such element exists.
*   **Examples**:
    ```
    >>> res = last_or_default()
    >>> res = last_or_default(lambda x: x > 3)
    >>> res = last_or_default(lambda x: x > 3, 0)
    >>> res = last_or_default(None, 0)
    ```

### `reactivex.operators.map(mapper=None)`

Projects each element of an observable sequence into a new form.

*   **Parameters**:
    *   `mapper` (`Optional[Callable[[_T1], _T2]]`): A transform function to apply to each source element.
*   **Returns**: `Callable[[Observable[_T1]], Observable[_T2]]`
    A partially applied operator function that takes an observable source and returns an observable sequence whose elements are the result of invoking the transform function on each element of the source.
*   **Example**:
    ```
    >>> map(lambda value: value * 10)
    ```

### `reactivex.operators.map_indexed(mapper_indexed=None)`

Projects each element of an observable sequence into a new form by incorporating the element’s index.

*   **Parameters**:
    *   `mapper_indexed` (`Optional[Callable[[_T1, int], _T2]]`): A transform function to apply to each source element. The second parameter of the function represents the index of the source element.
*   **Returns**: `Callable[[Observable[_T1]], Observable[_T2]]`
    A partially applied operator function that takes an observable source and returns an observable sequence whose elements are the result of invoking the transform function on each element of the source.
*   **Example**:
    ```
    >>> ret = map_indexed(lambda value, index: value * value + index)
    ```

### `reactivex.operators.materialize()`

Materializes the implicit notifications of an observable sequence as explicit notification values.

*   **Returns**: `Callable[[Observable[_T]], Observable[Notification[_T]]]`
    An operator function that takes an observable source and returns an observable sequence containing the materialized notification values from the source sequence.

### `reactivex.operators.max(comparer=None)`

Returns the maximum value in an observable sequence according to the specified comparer.

*   **Parameters**:
    *   `comparer` (`Optional[Callable[[_T, _T], bool]]`): \[Optional] Comparer used to compare elements.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A partially applied operator function that takes an observable source and returns an observable sequence containing a single element with the maximum element in the source sequence.
*   **Examples**:
    ```
    >>> op = max()
    >>> op = max(lambda x, y:  x.value - y.value)
    ```

### `reactivex.operators.max_by(key_mapper, comparer=None)`

Returns the elements in an observable sequence with the maximum key value according to the specified comparer.

*   **Parameters**:
    *   `key_mapper` (`Callable[[_T], _TKey]`): Key mapper function.
    *   `comparer` (`Optional[Callable[[_TKey, _TKey], bool]]`): \[Optional] Comparer used to compare key values.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    A partially applied operator function that takes an observable source and returns an observable sequence containing a list of zero or more elements that have a maximum key value.
*   **Examples**:
    ```
    >>> res = max_by(lambda x: x.value)
    >>> res = max_by(lambda x: x.value, lambda x, y: x - y)
    ```

### `reactivex.operators.merge(*sources, max_concurrent=None)`

Merges an observable sequence of observable sequences into an observable sequence, limiting the number of concurrent subscriptions to inner sequences. Or merges two observable sequences into a single observable sequence.

*   **Parameters**:
    *   `max_concurrent` (`Optional[int]`): \[Optional] Maximum number of inner observable sequences being subscribed to concurrently or the second observable sequence.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns the observable sequence that merges the elements of the inner sequences.
*   **Examples**:
    ```
    >>> op = merge(max_concurrent=1)
    >>> op = merge(other_source)
    ```

### `reactivex.operators.merge_all()`

Merges an observable sequence of observable sequences into an observable sequence.

*   **Returns**: `Callable[[Observable[Observable[_T]]], Observable[_T]]`
    A partially applied operator function that takes an observable source and returns the observable sequence that merges the elements of the inner sequences.

### `reactivex.operators.min(comparer=None)`

Returns the minimum element in an observable sequence according to the optional comparer, else a default greater than/less than check.

*   **Parameters**:
    *   `comparer` (`Optional[Callable[[_T, _T], bool]]`): \[Optional] Comparer used to compare elements.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element with the minimum element in the source sequence.
*   **Examples**:
    ```
    >>> res = source.min()
    >>> res = source.min(lambda x, y: x.value - y.value)
    ```

### `reactivex.operators.min_by(key_mapper, comparer=None)`

Returns the elements in an observable sequence with the minimum key value according to the specified comparer.

*   **Parameters**:
    *   `key_mapper` (`Callable[[_T], _TKey]`): Key mapper function.
    *   `comparer` (`Optional[Callable[[_TKey, _TKey], bool]]`): \[Optional] Comparer used to compare key values.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    An operator function that takes an observable source and returns an observable sequence containing a list of zero or more elements that have a minimum key value.
*   **Examples**:
    ```
    >>> res = min_by(lambda x: x.value)
    >>> res = min_by(lambda x: x.value, lambda x, y: x - y)
    ```

### `reactivex.operators.multicast(subject=None, *, subject_factory=None, mapper=None)`

Multicasts the source sequence notifications through an instantiated subject into all uses of the sequence within a mapper function. Each subscription to the resulting sequence causes a separate multicast invocation, exposing the sequence resulting from the mapper function’s invocation. For specializations with fixed subject types, see `Publish`, `PublishLast`, and `Replay`.

*   **Parameters**:
    *   `subject_factory` (`Optional[Callable[[Optional[SchedulerBase]], SubjectBase[_T]]]`): Factory function to create an intermediate subject through which the source sequence’s elements will be multicast to the mapper function.
    *   `subject` (`Optional[SubjectBase[_T]]`): Subject to push source elements into.
    *   `mapper` (`Optional[Callable[[Observable[_T]], Observable[_T2]]]`): \[Optional] Mapper function which can use the multicasted source sequence subject to the policies enforced by the created subject. Specified only if `subject_factory` is a factory function.
*   **Returns**: `Callable[[Observable[_T]], Union[Observable[_T2], ConnectableObservable[_T]]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements of a sequence produced by multicasting the source sequence within a mapper function.
*   **Examples**:
    ```
    >>> res = multicast(observable)
    >>> res = multicast(
        subject_factory=lambda scheduler: Subject(), mapper=lambda x: x
    )
    ```

### `reactivex.operators.observe_on(scheduler)`

Wraps the source sequence in order to run its observer callbacks on the specified scheduler.

*   **Important**: This only invokes observer callbacks on a scheduler. In case the subscription and/or unsubscription actions have side-effects that require to be run on a scheduler, use `subscribe_on`.
*   **Parameters**:
    *   `scheduler` (`SchedulerBase`): Scheduler to notify observers on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns the source sequence whose observations happen on the specified scheduler.

### `reactivex.operators.on_error_resume_next(second)`

Continues an observable sequence that is terminated normally or by an exception with the next observable sequence.

*   **Parameters**:
    *   `second` (`Observable[_T]`): Second observable sequence used to produce results after the first sequence terminates.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An observable sequence that concatenates the first and second sequence, even if the first sequence terminates exceptionally.

### `reactivex.operators.pairwise()`

Returns a new observable that triggers on the second and subsequent triggerings of the input observable. The Nth triggering of the input observable passes the arguments from the N-1th and Nth triggering as a pair. The argument passed to the N-1th triggering is held in hidden internal state until the Nth triggering occurs.

*   **Returns**: `Callable[[Observable[_T]], Observable[Tuple[_T, _T]]]`
    An operator function that takes an observable source and returns an observable that triggers on successive pairs of observations from the input observable as an array.

### `reactivex.operators.partition(predicate)`

Returns two observables which partition the observations of the source by the given function. The first will trigger observations for those values for which the predicate returns true. The second will trigger observations for those values where the predicate returns false. The predicate is executed once for each subscribed observer. Both also propagate all error observations arising from the source and each completes when the source completes.

*   **Parameters**:
    *   `predicate` (`Callable[[_T], bool]`): The function to determine which output Observable will trigger a particular observation.
*   **Returns**: `Callable[[Observable[_T]], List[Observable[_T]]]`
    An operator function that takes an observable source and returns a list of observables. The first triggers when the predicate returns `True`, and the second triggers when the predicate returns `False`.

### `reactivex.operators.partition_indexed(predicate_indexed)`

Returns two observables which partition the observations of the source by the given function, incorporating the element's index. The first will trigger observations for those values for which the predicate returns true. The second will trigger observations for those values where the predicate returns false. The predicate is executed once for each subscribed observer. Both also propagate all error observations arising from the source and each completes when the source completes.

*   **Parameters**:
    *   `predicate` (`Callable[[_T, int], bool]`): The function to determine which output Observable will trigger a particular observation.
*   **Returns**: `Callable[[Observable[_T]], List[Observable[_T]]]`
    A list of observables. The first triggers when the predicate returns `True`, and the second triggers when the predicate returns `False`.

### `reactivex.operators.pluck(key)`

Retrieves the value of a specified key using dict-like access (as in `element[key]`) from all elements in the Observable sequence. To pluck an attribute of each element, use `pluck_attr`.

*   **Parameters**:
    *   `key` (`_TKey`): The key to pluck.
*   **Returns**: `Callable[[Observable[Dict[_TKey, _TValue]]], Observable[_TValue]]`
    An operator function that takes an observable source and returns a new observable sequence of key values.

### `reactivex.operators.pluck_attr(prop)`

Retrieves the value of a specified property (using `getattr`) from all elements in the Observable sequence. To pluck values using dict-like access (as in `element[key]`) on each element, use `pluck`.

*   **Parameters**:
    *   `property` (`str`): The property to pluck.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns a new observable sequence of property values.

### `reactivex.operators.publish(mapper=None)`

Returns an observable sequence that is the result of invoking the mapper on a connectable observable sequence that shares a single subscription to the underlying sequence. This operator is a specialization of `Multicast` using a regular `Subject`.

*   **Parameters**:
    *   `mapper` (`Optional[Callable[[Observable[_T1]], Observable[_T2]]]`): \[Optional] Selector function which can use the multicasted source sequence as many times as needed, without causing multiple subscriptions to the source sequence. Subscribers to the given source will receive all notifications of the source from the time of the subscription on.
*   **Returns**: `Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements of a sequence produced by multicasting the source sequence within a mapper function.
*   **Example**:
    ```
    >>> res = publish()
    >>> res = publish(lambda x: x)
    ```

### `reactivex.operators.publish_value(initial_value, mapper=None)`

Returns an observable sequence that is the result of invoking the mapper on a connectable observable sequence that shares a single subscription to the underlying sequence and starts with `initial_value`. This operator is a specialization of `Multicast` using a `BehaviorSubject`.

*   **Parameters**:
    *   `initial_value` (`_T1`): Initial value received by observers upon subscription.
    *   `mapper` (`Optional[Callable[[Observable[_T1]], Observable[_T2]]]`): \[Optional] Optional mapper function which can use the multicasted source sequence as many times as needed, without causing multiple subscriptions to the source sequence. Subscribers to the given source will immediately receive the initial value, followed by all notifications of the source from the time of the subscription on.
*   **Returns**: `Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements of a sequence produced by multicasting the source sequence within a mapper function.
*   **Examples**:
    ```
    >>> res = source.publish_value(42)
    >>> res = source.publish_value(42, lambda x: x.map(lambda y: y * y))
    ```

### `reactivex.operators.reduce(accumulator, seed=<class 'reactivex.internal.utils.NotSet'>)`

Applies an accumulator function over an observable sequence, returning the result of the aggregation as a single element in the result sequence. The specified seed value is used as the initial accumulator value. For aggregation behavior with incremental intermediate results, see `scan`.

*   **Parameters**:
    *   `accumulator` (`Callable[[_TState, _T], _TState]`): An accumulator function to be invoked on each element.
    *   `seed` (`Union[_TState, Type[NotSet]]`): Optional initial accumulator value.
*   **Returns**: `Callable[[Observable[_T]], Observable[Any]]`
    A partially applied operator function that takes an observable source and returns an observable sequence containing a single element with the final accumulator value.
*   **Examples**:
    ```
    >>> res = reduce(lambda acc, x: acc + x)
    >>> res = reduce(lambda acc, x: acc + x, 0)
    ```

### `reactivex.operators.ref_count()`

Returns an observable sequence that stays connected to the source as long as there is at least one subscription to the observable sequence.

*   **Returns**: `Callable[[ConnectableObservable[_T]], Observable[_T]]`

### `reactivex.operators.repeat(repeat_count=None)`

Repeats the observable sequence a specified number of times. If the repeat count is not specified, the sequence repeats indefinitely.

*   **Parameters**:
    *   `repeat_count` (`Optional[int]`): Number of times to repeat the sequence. If not provided, repeats the sequence indefinitely.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence producing the elements of the given sequence repeatedly.
*   **Examples**:
    ```
    >>> repeated = repeat()
    >>> repeated = repeat(42)
    ```

### `reactivex.operators.replay(buffer_size=None, window=None, *, mapper=None, scheduler=None)`

Returns an observable sequence that is the result of invoking the mapper on a connectable observable sequence that shares a single subscription to the underlying sequence replaying notifications subject to a maximum time length for the replay buffer. This operator is a specialization of `Multicast` using a `ReplaySubject`.

*   **Parameters**:
    *   `mapper` (`Optional[Callable[[Observable[_T1]], Observable[_T2]]]`): \[Optional] Selector function which can use the multicasted source sequence as many times as needed, without causing multiple subscriptions to the source sequence. Subscribers to the given source will receive all the notifications of the source subject to the specified replay buffer trimming policy.
    *   `buffer_size` (`Optional[int]`): \[Optional] Maximum element count of the replay buffer.
    *   `window` (`Union[timedelta, float, None]`): \[Optional] Maximum time length of the replay buffer.
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] Scheduler the observers are invoked on.
*   **Returns**: `Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements of a sequence produced by multicasting the source sequence within a mapper function.
*   **Examples**:
    ```
    >>> res = replay(buffer_size=3)
    >>> res = replay(buffer_size=3, window=0.5)
    >>> res = replay(None, 3, 0.5)
    >>> res = replay(lambda x: x.take(6).repeat(), 3, 0.5)
    ```

### `reactivex.operators.retry(retry_count=None)`

Repeats the source observable sequence the specified number of times or until it successfully terminates. If the retry count is not specified, it retries indefinitely.

*   **Parameters**:
    *   `retry_count` (`Optional[int]`): \[Optional] Number of times to retry the sequence. If not provided, retry the sequence indefinitely.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An observable sequence producing the elements of the given sequence repeatedly until it terminates successfully.
*   **Examples**:
    ```
    >>> retried = retry()
    >>> retried = retry(42)
    ```

### `reactivex.operators.sample(sampler, scheduler=None)`

Samples the observable sequence at each interval.

*   **Parameters**:
    *   `sampler` (`Union[timedelta, float, Observable[Any]]`): Observable used to sample the source observable **or** time interval at which to sample (specified as a float denoting seconds or an instance of `timedelta`).
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to use only when a time interval is given.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns a sampled observable sequence.
*   **Examples**:
    ```
    >>> res = sample(sample_observable) # Sampler tick sequence
    >>> res = sample(5.0) # 5 seconds
    ```

### `reactivex.operators.scan(accumulator, seed=<class 'reactivex.internal.utils.NotSet'>)`

Applies an accumulator function over an observable sequence and returns each intermediate result. The optional seed value is used as the initial accumulator value. For aggregation behavior with no intermediate results, see `aggregate()` or `Observable()`.

*   **Parameters**:
    *   `accumulator` (`Callable[[_TState, _T], _TState]`): An accumulator function to be invoked on each element.
    *   `seed` (`Union[_TState, Type[NotSet]]`): \[Optional] The initial accumulator value.
*   **Returns**: `Callable[[Observable[_T]], Observable[_TState]]`
    A partially applied operator function that takes an observable source and returns an observable sequence containing the accumulated values.
*   **Examples**:
    ```
    >>> scanned = source.scan(lambda acc, x: acc + x)
    >>> scanned = source.scan(lambda acc, x: acc + x, 0)
    ```

### `reactivex.operators.sequence_equal(second, comparer=None)`

Determines whether two sequences are equal by comparing the elements pairwise using a specified equality comparer.

*   **Parameters**:
    *   `second` (`Union[Observable[_T], Iterable[_T]]`): Second observable sequence or iterable to compare.
    *   `comparer` (`Optional[Callable[[_T, _T], bool]]`): \[Optional] Comparer used to compare elements of both sequences. No guarantees on order of comparer arguments.
*   **Returns**: `Callable[[Observable[_T]], Observable[bool]]`
    An operator function that takes an observable source and returns an observable sequence that contains a single element which indicates whether both sequences are of equal length and their corresponding elements are equal according to the specified equality comparer.
*   **Examples**:
    ```
    >>> res = sequence_equal([1,2,3])
    >>> res = sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
    >>> res = sequence_equal(reactivex.return_value(42))
    >>> res = sequence_equal(
        reactivex.return_value({ "value": 42 }), lambda x, y: x.value == y.value)
    ```

### `reactivex.operators.share()`

Shares a single subscription among multiple observers. This is an alias for a composed `publish()` and `ref_count()`.

*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns a new Observable that multicasts (shares) the original Observable. As long as there is at least one Subscriber this Observable will be subscribed and emitting data. When all subscribers have unsubscribed it will unsubscribe from the source Observable.

### `reactivex.operators.single(predicate=None)`

Returns the only element of an observable sequence that satisfies the condition in the optional predicate, and reports an exception if there is not exactly one element in the observable sequence.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): \[Optional] A predicate function to evaluate for elements in the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the single element in the observable sequence that satisfies the condition in the predicate.
*   **Example**:
    ```
    >>> res = single()
    >>> res = single(lambda x: x == 42)
    ```

### `reactivex.operators.single_or_default(predicate=None, default_value=None)`

Returns the only element of an observable sequence that matches the predicate, or a default value if no such element exists. This method reports an exception if there is more than one element in the observable sequence.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): \[Optional] A predicate function to evaluate for elements in the source sequence.
    *   `default_value` (`Optional[Any]`): \[Optional] The default value if the index is outside the bounds of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the single element in the observable sequence that satisfies the condition in the predicate, or a default value if no such element exists.
*   **Examples**:
    ```
    >>> res = single_or_default()
    >>> res = single_or_default(lambda x: x == 42)
    >>> res = single_or_default(lambda x: x == 42, 0)
    >>> res = single_or_default(None, 0)
    ```

### `reactivex.operators.skip(count)`

Bypasses a specified number of elements in an observable sequence and then returns the remaining elements.

*   **Parameters**:
    *   `count` (`int`): The number of elements to skip before returning the remaining elements.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements that occur after the specified index in the input sequence.
*   **Example**:
    ```
    >>> op = skip(5)
    ```

### `reactivex.operators.skip_last(count)`

Bypasses a specified number of elements at the end of an observable sequence.

*   **Important**: This operator accumulates a queue with a length enough to store the first `count` elements. As more elements are received, elements are taken from the front of the queue and produced on the result sequence. This causes elements to be delayed.
*   **Parameters**:
    *   `count` (`int`): Number of elements to bypass at the end of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the source sequence elements except for the bypassed ones at the end.

### `reactivex.operators.skip_last_with_time(duration, scheduler=None)`

Skips elements for the specified duration from the end of the observable source sequence.

*   **Important**: This operator accumulates a queue with a length enough to store elements received during the initial duration window. As more elements are received, elements older than the specified duration are taken from the queue and produced on the result sequence. This causes elements to be delayed with duration.
*   **Parameters**:
    *   `duration` (`Union[timedelta, float]`): Duration for skipping elements from the end of the sequence.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to use for time handling.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An observable sequence with the elements skipped during the specified duration from the end of the source sequence.
*   **Example**:
    ```
    >>> res = skip_last_with_time(5.0)
    ```

### `reactivex.operators.skip_until(other)`

Returns the values from the source observable sequence only after the other observable sequence produces a value.

*   **Parameters**:
    *   `other` (`Observable[Any]`): The observable sequence that triggers propagation of elements of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the elements of the source sequence starting from the point the other sequence triggered propagation.

### `reactivex.operators.skip_until_with_time(start_time, scheduler=None)`

Skips elements from the observable source sequence until the specified start time.

*   **Important**: Errors produced by the source sequence are always forwarded to the result sequence, even if the error occurs before the start time.
*   **Parameters**:
    *   `start_time` (`Union[datetime, timedelta, float]`): Time to start taking elements from the source sequence. If this value is less than or equal to `datetime.utcnow()`, no elements will be skipped.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to delay subscription on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence with the elements skipped until the specified start time.
*   **Examples**:
    ```
    >>> res = skip_until_with_time(datetime())
    >>> res = skip_until_with_time(5.0)
    ```

### `reactivex.operators.skip_while(predicate)`

Bypasses elements in an observable sequence as long as a specified condition is true and then returns the remaining elements. The element’s index is used in the logic of the predicate function.

*   **Parameters**:
    *   `predicate` (`Callable[[_T], bool]`): A function to test each element for a condition; the second parameter of the function represents the index of the source element.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements from the input sequence starting at the first element in the linear series that does not pass the test specified by predicate.
*   **Example**:
    ```
    >>> skip_while(lambda value: value < 10)
    ```

### `reactivex.operators.skip_while_indexed(predicate)`

Bypasses elements in an observable sequence as long as a specified condition is true and then returns the remaining elements. The element’s index is used in the logic of the predicate function.

*   **Parameters**:
    *   `predicate` (`Callable[[_T, int], bool]`): A function to test each element for a condition; the second parameter of the function represents the index of the source element.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements from the input sequence starting at the first element in the linear series that does not pass the test specified by predicate.
*   **Example**:
    ```
    >>> skip_while(lambda value, index: value < 10 or index < 10)
    ```

### `reactivex.operators.skip_with_time(duration, scheduler=None)`

Skips elements for the specified duration from the start of the observable source sequence.

*   **Important**: Specifying a zero value for duration doesn’t guarantee no elements will be dropped from the start of the source sequence. This is a side-effect of the asynchrony introduced by the scheduler, where the action that causes callbacks from the source sequence to be forwarded may not execute immediately, despite the zero due time. Errors produced by the source sequence are always forwarded to the result sequence, even if the error occurs before the duration.
*   **Parameters**:
    *   `duration` (`Union[timedelta, float]`): Duration for skipping elements from the start of the sequence.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to use for time handling.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence with the elements skipped during the specified duration from the start of the source sequence.

### `reactivex.operators.slice(start=None, stop=None, step=None)`

Slices the given observable. It is basically a wrapper around the operators `skip`, `skip_last`, `take`, `take_last` and `filter`.

*   **Parameters**:
    *   `start` (`Optional[int]`): First element to take or skip last.
    *   `stop` (`Optional[int]`): Last element to take or skip last.
    *   `step` (`Optional[int]`): Takes every step element. Must be larger than zero.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns a sliced observable sequence.
*   **Examples**:
    ```
    >>> result = source.slice(1, 10)
    >>> result = source.slice(1, -2)
    >>> result = source.slice(1, -1, 2)
    ```

### `reactivex.operators.some(predicate=None)`

Determines whether some element of an observable sequence satisfies a condition if present, else if some items are in the sequence.

*   **Parameters**:
    *   `predicate` (`Optional[Callable[[_T], bool]]`): A function to test each element for a condition.
*   **Returns**: `Callable[[Observable[_T]], Observable[bool]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element determining whether some elements in the source sequence pass the test in the specified predicate if given, else if some items are in the sequence.
*   **Examples**:
    ```
    >>> result = source.some()
    >>> result = source.some(lambda x: x > 3)
    ```

### `reactivex.operators.starmap(mapper=None)`

Unpacks arguments grouped as tuple elements of an observable sequence and return an observable sequence of values by invoking the mapper function with star applied unpacked elements as positional arguments. Use instead of `map()` when the arguments to the mapper are grouped as tuples and the mapper function takes multiple arguments.

*   **Parameters**:
    *   `mapper` (`Optional[Callable[..., Any]]`): A transform function to invoke with unpacked elements as arguments.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence containing the results of invoking the mapper function with unpacked elements of the source.
*   **Example**:
    ```
    >>> starmap(lambda x, y: x + y)
    ```

### `reactivex.operators.starmap_indexed(mapper=None)`

Variant of `starmap()` which accepts an indexed mapper.

*   **Parameters**:
    *   `mapper` (`Optional[Callable[..., Any]]`): A transform function to invoke with unpacked elements as arguments.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence containing the results of invoking the indexed mapper function with unpacked elements of the source.
*   **Example**:
    ```
    >>> starmap_indexed(lambda x, y, i: x + y + i)
    ```

### `reactivex.operators.start_with(*args)`

Prepends a sequence of values to an observable sequence.

*   **Parameters**:
    *   `*args` (`_T`): Values to prepend.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes a source observable and returns the source sequence prepended with the specified values.
*   **Example**:
    ```
    >>> start_with(1, 2, 3)
    ```

### `reactivex.operators.subscribe_on(scheduler)`

Subscribes on the specified scheduler. Wraps the source sequence in order to run its subscription and unsubscription logic on the specified scheduler.

*   **Important**: This operation is not commonly used; see the remarks section for more information on the distinction between `subscribe_on` and `observe_on`. This only performs the side-effects of subscription and unsubscription on the specified scheduler. In order to invoke observer callbacks on a scheduler, use `observe_on`.
*   **Parameters**:
    *   `scheduler` (`SchedulerBase`): Scheduler to perform subscription and unsubscription actions on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns the source sequence whose subscriptions and un-subscriptions happen on the specified scheduler.

### `reactivex.operators.sum(key_mapper=None)`

Computes the sum of a sequence of values that are obtained by invoking an optional transform function on each element of the input sequence, else if not specified computes the sum on each item in the sequence.

*   **Parameters**:
    *   `key_mapper` (`Optional[Callable[[Any], float]]`): \[Optional] A transform function to apply to each element.
*   **Returns**: `Callable[[Observable[Any]], Observable[float]]`
    An operator function that takes a source observable and returns an observable sequence containing a single element with the sum of the values in the source sequence.
*   **Examples**:
    ```
    >>> res = sum()
    >>> res = sum(lambda x: x.value)
    ```

### `reactivex.operators.switch_latest()`

Transforms an observable sequence of observable sequences into an observable sequence producing values only from the most recent observable sequence.

*   **Returns**: `Callable[[Observable[Observable[_T]]], Observable[_T]]`
    A partially applied operator function that takes an observable source and returns the observable sequence that at any point in time produces the elements of the most recent inner observable sequence that has been received.

### `reactivex.operators.take(count)`

Returns a specified number of contiguous elements from the start of an observable sequence.

*   **Parameters**:
    *   `count` (`int`): The number of elements to return.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains the specified number of elements from the start of the input sequence.
*   **Example**:
    ```
    >>> op = take(5)
    ```

### `reactivex.operators.take_last(count)`

Returns a specified number of contiguous elements from the end of an observable sequence.

*   **Important**: This operator accumulates a buffer with a length enough to store `count` elements. Upon completion of the source sequence, this buffer is drained on the result sequence. This causes the elements to be delayed.
*   **Parameters**:
    *   `count` (`int`): Number of elements to take from the end of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the specified number of elements from the end of the source sequence.
*   **Example**:
    ```
    >>> res = take_last(5)
    ```

### `reactivex.operators.take_last_buffer(count)`

Returns an array with the specified number of contiguous elements from the end of an observable sequence.

*   **Important**: This operator accumulates a buffer with a length enough to store `count` elements. Upon completion of the source sequence, this buffer is drained on the result sequence. This causes the elements to be delayed.
*   **Parameters**:
    *   `count` (`int`): Number of elements to take from the end of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    An operator function that takes an observable source and returns an observable sequence containing a single list with the specified number of elements from the end of the source sequence.
*   **Example**:
    ```
    >>> res = source.take_last(5)
    ```

### `reactivex.operators.take_last_with_time(duration, scheduler=None)`

Returns elements within the specified duration from the end of the observable source sequence.

*   **Important**: This operator accumulates a queue with a length enough to store elements received during the initial duration window. As more elements are received, elements older than the specified duration are taken from the queue and produced on the result sequence. This causes elements to be delayed with duration.
*   **Parameters**:
    *   `duration` (`Union[timedelta, float]`): Duration for taking elements from the end of the sequence.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to use for time handling.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence with the elements taken during the specified duration from the end of the source sequence.
*   **Example**:
    ```
    >>> res = take_last_with_time(5.0)
    ```

### `reactivex.operators.take_until(other)`

Returns the values from the source observable sequence until the other observable sequence produces a value.

*   **Parameters**:
    *   `other` (`Observable[Any]`): Observable sequence that terminates propagation of elements of the source sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence containing the elements of the source sequence up to the point the other sequence interrupted further propagation.

### `reactivex.operators.take_until_with_time(end_time, scheduler=None)`

Takes elements for the specified duration until the specified end time, using the specified scheduler to run timers.

*   **Parameters**:
    *   `end_time` (`Union[datetime, timedelta, float]`): Time to stop taking elements from the source sequence. If this value is less than or equal to `datetime.utcnow()`, the result stream will complete immediately.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to run the timer on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence with the elements taken until the specified end time.
*   **Examples**:
    ```
    >>> res = take_until_with_time(dt, [optional scheduler])
    >>> res = take_until_with_time(5.0, [optional scheduler])
    ```

### `reactivex.operators.take_while(predicate, inclusive=False)`

Returns elements from an observable sequence as long as a specified condition is true.

*   **Parameters**:
    *   `predicate` (`Callable[[_T], bool]`): A function to test each element for a condition.
    *   `inclusive` (`bool`): \[Optional] When set to `True` the value that caused the predicate function to return `False` will also be emitted. If not specified, defaults to `False`.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence that contains the elements from the input sequence that occur before the element at which the test no longer passes.
*   **Example**:
    ```
    >>> take_while(lambda value: value < 10)
    ```

### `reactivex.operators.take_while_indexed(predicate, inclusive=False)`

Returns elements from an observable sequence as long as a specified condition is true. The element’s index is used in the logic of the predicate function.

*   **Parameters**:
    *   `predicate` (`Callable[[_T, int], bool]`): A function to test each element for a condition; the second parameter of the function represents the index of the source element.
    *   `inclusive` (`bool`): \[Optional] When set to `True` the value that caused the predicate function to return `False` will also be emitted. If not specified, defaults to `False`.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An observable sequence that contains the elements from the input sequence that occur before the element at which the test no longer passes.
*   **Example**:
    ```
    >>> take_while_indexed(lambda value, index: value < 10 or index < 10)
    ```

### `reactivex.operators.take_with_time(duration, scheduler=None)`

Takes elements for the specified duration from the start of the observable source sequence.

*   **Important**: This operator accumulates a queue with a length enough to store elements received during the initial duration window. As more elements are received, elements older than the specified duration are taken from the queue and produced on the result sequence. This causes elements to be delayed with duration.
*   **Parameters**:
    *   `duration` (`Union[timedelta, float]`): Duration for taking elements from the start of the sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence with the elements taken during the specified duration from the start of the source sequence.
*   **Example**:
    ```
    >>> res = take_with_time(5.0)
    ```

### `reactivex.operators.throttle_first(window_duration, scheduler=None)`

Returns an Observable that emits only the first item emitted by the source Observable during sequential time windows of a specified duration.

*   **Parameters**:
    *   `window_duration` (`Union[timedelta, float]`): Time to wait before emitting another item after emitting the last item.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to use for time handling.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable that performs the throttle operation.

### `reactivex.operators.throttle_with_mapper(throttle_duration_mapper)`

Ignores values from an observable sequence which are followed by another value within a computed throttle duration.

*   **Parameters**:
    *   `throttle_duration_mapper` (`Callable[[Any], Observable[Any]]`): Mapper function to retrieve an observable sequence indicating the throttle duration for each given element.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    A partially applied operator function that takes an observable source and returns the throttled observable sequence.
*   **Example**:
    ```
    >>> op = throttle_with_mapper(lambda x: reactivex.timer(x+x))
    ```

### `reactivex.operators.timestamp(scheduler=None)`

Records the timestamp for each value in an observable sequence. Produces objects with attributes `value` and `timestamp`, where `value` is the original value.

*   **Parameters**:
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] The scheduler used to run the the input sequence on.
*   **Returns**: `Callable[[Observable[_T]], Observable[Timestamp[_T]]]`
    A partially applied operator function that takes an observable source and returns an observable sequence with timestamp information on values.
*   **Examples**:
    ```
    >>> timestamp()
    ```

### `reactivex.operators.timeout(duetime, other=None, scheduler=None)`

Returns the source observable sequence or the other observable sequence if `duetime` elapses.

*   **Parameters**:
    *   `duetime` (`Union[datetime, timedelta, float]`): Absolute (specified as a `datetime` object) or relative time (specified as a float denoting seconds or an instance of `timedelta`) when a timeout occurs.
    *   `other` (`Optional[Observable[_T]]`): Sequence to return in case of a timeout. If not specified, a timeout error throwing sequence will be used.
    *   `scheduler` (`Optional[SchedulerBase]`): Scheduler to run the timer on.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns the source sequence switching to the other sequence in case of a timeout.
*   **Examples**:
    ```
    >>> res = timeout(5.0)
    >>> res = timeout(datetime(), return_value(42))
    >>> res = timeout(5.0, return_value(42))
    ```

### `reactivex.operators.timeout_with_mapper(first_timeout=None, timeout_duration_mapper=None, other=None)`

Returns the source observable sequence, switching to the other observable sequence if a timeout is signaled.

*   **Parameters**:
    *   `first_timeout` (`Optional[Observable[Any]]`): \[Optional] Observable sequence that represents the timeout for the first element. If not provided, this defaults to `reactivex.never()`.
    *   `timeout_duration_mapper` (`Optional[Callable[[_T], Observable[Any]]]`): \[Optional] Selector to retrieve an observable sequence that represents the timeout between the current element and the next element.
    *   `other` (`Optional[Observable[_T]]`): \[Optional] Sequence to return in case of a timeout. If not provided, this is set to `reactivex.throw()`.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns the source sequence switching to the other sequence in case of a timeout.
*   **Examples**:
    ```
    >>> res = timeout_with_mapper(reactivex.timer(0.5))
    >>> res = timeout_with_mapper(
        reactivex.timer(0.5), lambda x: reactivex.timer(0.2)
    )
    >>> res = timeout_with_mapper(
        reactivex.timer(0.5),
        lambda x: reactivex.timer(0.2),
        reactivex.return_value(42)
    )
    ```

### `reactivex.operators.time_interval(scheduler=None)`

Records the time interval between consecutive values in an observable sequence.

*   **Parameters**:
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] Scheduler to run the timer on.
*   **Returns**: `Callable[[Observable[_T]], Observable[TimeInterval[_T]]]`
    An operator function that takes an observable source and returns an observable sequence with time interval information on values.
*   **Examples**:
    ```
    >>> res = time_interval()
    ```

### `reactivex.operators.to_dict(key_mapper, element_mapper=None)`

Converts the observable sequence to a dictionary.

*   **Parameters**:
    *   `key_mapper` (`Callable[[_T], _TKey]`): A function which produces the key for the dictionary.
    *   `element_mapper` (`Optional[Callable[[_T], _TValue]]`): \[Optional] An optional function which produces the element for the dictionary. If not present, defaults to the value from the observable sequence.
*   **Returns**: `Callable[[Observable[_T]], Observable[Dict[_TKey, _TValue]]]`
    An operator function that takes an observable source and returns an observable sequence with a single value of a dictionary containing the values from the observable sequence.

### `reactivex.operators.to_future(future_ctor=None)`

Converts an existing observable sequence to a Future.

*   **Parameters**:
    *   `future_ctor` (`Optional[Callable[..., Future]]`): \[Optional] The constructor of the future.
*   **Returns**: `Callable[[Observable[_T]], Future[_T]]`
    An operator function that takes an observable source and returns a future with the last value from the observable sequence.
*   **Example**:
    ```
    op = to_future(asyncio.Future);
    ```

### `reactivex.operators.to_iterable()`

Creates an iterable from an observable sequence. There is also an alias called `to_list`.

*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element with an iterable containing all the elements of the source sequence.

### `reactivex.operators.to_list()`

Creates an iterable from an observable sequence. This is an alias for `to_iterable`.

*   **Returns**: `Callable[[Observable[_T]], Observable[List[_T]]]`
    An operator function that takes an observable source and returns an observable sequence containing a single element with an iterable containing all the elements of the source sequence.

### `reactivex.operators.to_marbles(timespan=0.1, scheduler=None)`

Convert an observable sequence into a marble diagram string.

*   **Parameters**:
    *   `timespan` (`Union[timedelta, float]`): \[Optional] Duration of each character in seconds. If not specified, defaults to 0.1s.
    *   `scheduler` (`Optional[SchedulerBase]`): \[Optional] The scheduler used to run the input sequence on.
*   **Returns**: `Callable[[Observable[Any]], Observable[str]]`
    Observable stream.

### `reactivex.operators.to_set()`

Converts the observable sequence to a set.

*   **Returns**: `Callable[[Observable[_T]], Observable[Set[_T]]]`
    An operator function that takes an observable source and returns an observable sequence with a single value of a set containing the values from the observable sequence.

### `reactivex.operators.while_do(condition)`

Repeats source as long as condition holds, emulating a while loop.

*   **Parameters**:
    *   `condition` (`Callable[[Observable[_T]], bool]`): The condition which determines if the source will be repeated.
*   **Returns**: `Callable[[Observable[_T]], Observable[_T]]`
    An operator function that takes an observable source and returns an observable sequence which is repeated as long as the condition holds.

### `reactivex.operators.window(boundaries)`

Projects each element of an observable sequence into zero or more windows.

*   **Parameters**:
    *   `boundaries` (`Observable[Any]`): Observable sequence whose elements denote the creation and completion of non-overlapping windows.
*   **Returns**: `Callable[[Observable[_T]], Observable[Observable[_T]]]`
    An operator function that takes an observable source and returns an observable sequence of windows.
*   **Examples**:
    ```
    >>> res = window(reactivex.interval(1.0))
    ```

### `reactivex.operators.window_when(closing_mapper)`

Projects each element of an observable sequence into zero or more windows.

*   **Parameters**:
    *   `closing_mapper` (`Callable[[], Observable[Any]]`): A function invoked to define the closing of each produced window. It defines the boundaries of the produced windows (a window is started when the previous one is closed, resulting in non-overlapping windows).
*   **Returns**: `Callable[[Observable[_T]], Observable[Observable[_T]]]`
    An operator function that takes an observable source and returns an observable sequence of windows.
*   **Examples**:
    ```
    >>> res = window(lambda: reactivex.timer(0.5))
    ```

### `reactivex.operators.window_toggle(openings, closing_mapper)`

Projects each element of an observable sequence into zero or more windows.

*   **Parameters**:
    *   `openings` (`Observable[Any]`): Observable sequence whose elements denote the creation of windows.
    *   `closing_mapper` (`Callable[[Any], Observable[Any]]`): A function invoked to define the closing of each produced window. Value from `openings` Observable that initiated the associated window is provided as argument to the function.
*   **Returns**: `Callable[[Observable[_T]], Observable[Observable[_T]]]`
    An operator function that takes an observable source and returns an observable sequence of windows.
*   **Example**:
    ```
    >>> res = window(reactivex.interval(0.5), lambda i: reactivex.timer(i))
    ```

### `reactivex.operators.window_with_count(count, skip=None)`

Projects each element of an observable sequence into zero or more windows which are produced based on element count information.

*   **Parameters**:
    *   `count` (`int`): Length of each window.
    *   `skip` (`Optional[int]`): \[Optional] Number of elements to skip between creation of consecutive windows. If not specified, defaults to the `count`.
*   **Returns**: `Callable[[Observable[_T]], Observable[Observable[_T]]]`
    An observable sequence of windows.
*   **Examples**:
    ```
    >>> window_with_count(10)
    >>> window_with_count(10, 1)
    ```

### `reactivex.operators.with_latest_from(*sources)`

Merges the specified observable sequences into one observable sequence by creating a tuple only when the first observable sequence produces an element. The observables can be passed either as separate arguments or as a list.

*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence containing the result of combining elements of the sources into a tuple.
*   **Examples**:
    ```
    >>> op = with_latest_from(obs1)
    >>> op = with_latest_from([obs1, obs2, obs3])
    ```

### `reactivex.operators.zip(*args)`

Merges the specified observable sequences into one observable sequence by creating a tuple whenever all of the observable sequences have produced an element at a corresponding index.

*   **Parameters**:
    *   `args` (`Observable[Any]`): Observable sources to zip.
*   **Returns**: `Callable[[Observable[Any]], Observable[Any]]`
    An operator function that takes an observable source and returns an observable sequence containing the result of combining elements of the sources as a tuple.
*   **Example**:
    ```
    >>> res = zip(obs1, obs2)
    ```

### `reactivex.operators.zip_with_list(second)`

Merges the specified observable sequence and list into one observable sequence by creating a tuple whenever all of the observable sequences have produced an element at a corresponding index.

*   **Parameters**:
    *   `second` (`Iterable[_T2]`): Iterable to zip with the source observable.
*   **Returns**: `Callable[[Observable[_T1]], Observable[Tuple[_T1, _T2]]]`
    An operator function that takes an observable source and returns an observable sequence containing the result of combining elements of the sources as a tuple.
*   **Example**:
    ```
    >>> res = zip([1,2,3])
    ```

### `reactivex.operators.zip_with_iterable(second)`

Merges the specified observable sequence and list into one observable sequence by creating a tuple whenever all of the observable sequences have produced an element at a corresponding index. This is an alias for `zip_with_list`.

*   **Parameters**:
    *   `second` (`Iterable[_T2]`): Iterable to zip with the source observable.
*   **Returns**: `Callable[[Observable[_T1]], Observable[Tuple[_T1, _T2]]]`
    An operator function that takes an observable source and returns an observable sequence containing the result of combining elements of the sources as a tuple.
*   **Example**:
    ```
    >>> res = zip([1,2,3])
    ```
