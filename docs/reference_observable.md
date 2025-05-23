<!-- https://rxpy.readthedocs.io/en/latest/reference_observable.html -->
<!-- 1655 -->
# Observable

*class* `reactivex.Observable`(*subscribe=None*)

Observable base class. Represents a push-style collection, which you can [`pipe`](reference_observable_factory.html#reactivex.pipe "reactivex.pipe") into [`operators`](reference_operators.html#module-reactivex.operators "reactivex.operators").

### `__init__`(*subscribe=None*)

Creates an observable sequence object from the specified subscription function.

**Parameters**:

*   **subscribe** (`Optional`[`Callable`[[`ObserverBase`[`TypeVar`(`_T_out`, covariant=True)], `Optional`[`SchedulerBase`]], `DisposableBase`]]) – [Optional] Subscription function

### `subscribe`(*on\_next=None*, *on\_error=None*, *on\_completed=None*, *\**, *scheduler=None*)

Subscribe an observer to the observable sequence.

You may subscribe using an observer or callbacks, not both; if the first argument is an instance of `Observer` or if it has a (callable) attribute named `on_next`, then any callback arguments will be ignored.

**Examples**:

```
>>> source.subscribe()
>>> source.subscribe(observer)
>>> source.subscribe(observer, scheduler=scheduler)
>>> source.subscribe(on_next)
>>> source.subscribe(on_next, on_error)
>>> source.subscribe(on_next, on_error, on_completed)
>>> source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)

```

**Parameters**:

*   **observer** – [Optional] The object that is to receive notifications.
*   **on\_error** (`Optional`[`Callable`[[`Exception`], `None`]]) – [Optional] Action to invoke upon exceptional termination of the observable sequence.
*   **on\_completed** (`Optional`[`Callable`[[], `None`]]) – [Optional] Action to invoke upon graceful termination of the observable sequence.
*   **on\_next** (`Union`[`ObserverBase`[`TypeVar`(`_T_out`, covariant=True)], `Callable`[[`TypeVar`(`_T_out`, covariant=True)], `None`], `None`]) – [Optional] Action to invoke for each element in the observable sequence.
*   **scheduler** (`Optional`[`SchedulerBase`]) – [Optional] The default scheduler to use for this subscription.

**Return type**:
`DisposableBase`

**Returns**:
Disposable object representing an observer’s subscription to the observable sequence.

### `pipe`(*\*operators*)

Compose multiple operators left to right.

Composes zero or more operators into a functional composition. The operators are composed from left to right. A composition of zero operators gives back the original source.

**Examples**:

```
>>> source.pipe() == source
>>> source.pipe(f) == f(source)
>>> source.pipe(g, f) == f(g(source))
>>> source.pipe(h, g, f) == f(g(h(source)))

```

**Parameters**:

*   **operators** (`Callable`[[`Any`], `Any`]) – Sequence of operators.

**Return type**:
`Any`

**Returns**:
The composed observable.

### `run`()

Run source synchronously.

Subscribes to the observable source. Then blocks and waits for the observable source to either complete or error. Returns the last value emitted, or throws exception if any error occurred.

**Examples**:

```
>>> result = run(source)

```

**Raises**:

*   **SequenceContainsNoElementsError** – if observable completes (on\_completed) without any values being emitted.
*   **Exception** – raises exception if any error (on\_error) occurred.

**Return type**:
`Any`

**Returns**:
The last element emitted from the observable.

### `__await__`()

Awaits the given observable.

**Return type**:
`Generator`[`Any`, `None`, `TypeVar`(`_T_out`, covariant=True)]

**Returns**:
The last item of the observable sequence.

### `__add__`(*other*)

Pythonic version of [`concat`](reference_observable_factory.html#reactivex.concat "reactivex.concat").

**Example**:

```
>>> zs = xs + ys

```

**Parameters**:

*   **other** ([`Observable`](reference_observable_factory.html#reactivex.Observable "reactivex.observable.observable.Observable")[`TypeVar`(`_T_out`, covariant=True)]) – The second observable sequence in the concatenation.

**Return type**:
[`Observable`](reference_observable_factory.html#reactivex.Observable "reactivex.observable.observable.Observable")[`TypeVar`(`_T_out`, covariant=True)]

**Returns**:
Concatenated observable sequence.

### `__iadd__`(*other*)

Pythonic use of [`concat`](reference_observable_factory.html#reactivex.concat "reactivex.concat").

**Example**:

```
>>> xs += ys

```

**Parameters**:

*   **other** ([`Observable`](reference_observable_factory.html#reactivex.Observable "reactivex.observable.observable.Observable")[`TypeVar`(`_T_out`, covariant=True)]) – The second observable sequence in the concatenation.

**Return type**:
[Observable](reference_observable_factory.html#reactivex.Observable "reactivex.Observable")[\_T\_out]

**Returns**:
Concatenated observable sequence.

### `__getitem__`(*key*)

Pythonic version of [`slice`](reference_operators.html#reactivex.operators.slice "reactivex.operators.slice").

Slices the given observable using Python slice notation. The arguments to slice are start, stop and step given within brackets `[]` and separated by the colons `:`.

It is basically a wrapper around the operators [`skip`](reference_operators.html#reactivex.operators.skip "reactivex.operators.skip"), [`skip_last`](reference_operators.html#reactivex.operators.skip_last "reactivex.operators.skip_last"), [`take`](reference_operators.html#reactivex.operators.take "reactivex.operators.take"), [`take_last`](reference_operators.html#reactivex.operators.take_last "reactivex.operators.take_last") and [`filter`](reference_operators.html#reactivex.operators.filter "reactivex.operators.filter").

The following diagram helps you remember how slices works with streams. Positive numbers are relative to the start of the events, while negative numbers are relative to the end (close) of the stream.

```
 r---e---a---c---t---i---v---e---!
 0   1   2   3   4   5   6   7   8
-8  -7  -6  -5  -4  -3  -2  -1   0

```

**Examples**:

```
>>> result = source[1:10]
>>> result = source[1:-2]
>>> result = source[1:-1:2]

```

**Parameters**:

*   **key** (`Union`[`slice`, `int`]) – Slice object

**Return type**:
[`Observable`](reference_observable_factory.html#reactivex.Observable "reactivex.observable.observable.Observable")[`TypeVar`(`_T_out`, covariant=True)]

**Returns**:
Sliced observable sequence.

**Raises**:

*   **TypeError** – If key is not of type `int` or `slice`
