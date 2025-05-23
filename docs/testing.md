<!-- https://rxpy.readthedocs.io/en/latest/testing.html#testing-subscriptions-multiple-observables-hot-observables -->
<!-- 2897 -->
The `reactivex.testing` module provides tools for creating tests for custom observables, operators, and subscriptions, and for understanding the behavior of existing operators.

### Basic Example

Tests can be created using `TestScheduler` to simulate time and `ReactiveTest` to define observable events.

**Key Components:**

*   **`TestScheduler()`**: Creates a virtual time scheduler.
*   **`scheduler.create_hot_observable(*messages)`**: Defines a hot observable that emits predefined messages at specific virtual times.
    *   **`ReactiveTest.on_next(time, value)`**: Represents an `on_next` notification at a given `time` with a `value`.
*   **`scheduler.start(create_function, created=100, subscribed=200, disposed=1000)`**: Triggers the subscription to the observable returned by `create_function` and records all emissions.
    *   **`create_function`**: A callable that returns the observable to be tested.
    *   **`created` (default: 100)**: Virtual time when the observable is created (i.e., `create_function` is called).
    *   **`subscribed` (default: 200)**: Virtual time when the subscription occurs.
    *   **`disposed` (default: 1000)**: Virtual time when the subscription is disposed.
*   **`results.messages`**: A list of `ReactiveTest` notifications (e.g., `on_next`, `on_completed`, `on_error`) recorded during the test.

**Timeline Considerations for `scheduler.start`:**

The `scheduler.start` method operates on a virtual timeline with default timestamps:
*   **`created` [100]**: When the observable factory function is called.
*   **`subscribed` [200]**: When the subscription to the observable occurs.
*   **`disposed` [1000]**: When the subscription is disposed.

**Gotchas when modifying these values:**
*   Do not use `0` as values for `created` or `subscribed`.
*   If `subscribed` is set lower than `100`, `created` must also be adjusted accordingly, otherwise no events will be observed.

```
# This assumes that you are using pytest but unittest or others would work just as well
# Import the testing tools
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex import operators

def test_double():
    # Create a scheduler
    scheduler = TestScheduler()
    # Define one or more source
    source = scheduler.create_hot_observable(
        ReactiveTest.on_next(250, 3),
        ReactiveTest.on_next(350, 5),
    )

    # Define how the observable/operator is used on the source
    def create():
        return source.pipe(operators.map(lambda x: 2 * x))

    # trigger subscription and record emissions
    results = scheduler.start(create)

    # check the messages and potentially subscriptions
    assert results.messages == [
        ReactiveTest.on_next(250, 6),
        ReactiveTest.on_next(350, 10),
    ]

```

### Testing a Custom Operator

Custom operators, whether composed of existing operators or implemented with full control, can be tested using the same `TestScheduler` and `ReactiveTest` mechanisms.

### An Alternative Using Marbles

The `reactivex.testing.marbles` module provides a simplified flow for testing using marble diagrams.

**Key Components:**

*   **`marbles_testing()`**: A context manager that provides `start`, `cold`, `hot`, and `exp` functions.
    *   **`cold('marble_string')`**: Creates a cold observable from a marble string.
    *   **`hot('marble_string')`**: Creates a hot observable from a marble string.
    *   **`exp('marble_string', lookup_dict)`**: Creates an expected marble string for assertion, optionally using a `lookup_dict` for values.
    *   **`start(observable)`**: Starts the observable directly (without a `create` function) and returns the results.

**Limitation:** This method does not currently allow for testing subscriptions.

```
def test_start_with():
    from reactivex.testing.marbles import marbles_testing
    with marbles_testing() as (start, cold, hot, exp):
        source = cold('------1-2-3-|')
        outcome = exp('a-----1-2-3-|', {"a": None})  # can use lookups if needed
        obs = source.pipe(
            operators.start_with(None)
        )
        # Note that start accepts the observable directly,
        # without the need for a "create" function
        results = start(obs)

        assert results == outcome

```

### Testing an Observable Factory

Observables created directly from `reactivex.Observable` can also be tested. This includes scenarios involving `Disposable` objects.

```
def test_my_observable_factory():
    from reactivex.disposable import Disposable, CompositeDisposable
    a = 42
    def factory(observer: Observer, scheduler=None):
        def increment():
            nonlocal a
            a += 1
        sub = Disposable(action=increment)
        return CompositeDisposable(
            sub,
            reactivex.timer(20, scheduler=scheduler).subscribe(observer)
        )

    scheduler = TestScheduler()
    result = scheduler.start(lambda: Observable(factory))
    assert result.messages == [
        on_next(220, 0),
        on_completed(220)
    ]
    assert a == 43  # shows that our Disposable's action was as expected

```

### Testing Errors

Error cases can be tested by asserting against `ReactiveTest.on_error` notifications. Individual notification details can be inspected.

**Notification Properties:**

*   **`notification.time`**: The virtual time of the notification.
*   **`notification.value.kind`**: The type of notification ('N' for `on_next`, 'E' for `on_error`, 'C' for `on_completed`).
*   **`notification.value.value`**: The value emitted for `on_next` notifications.
*   **`notification.value.exception`**: The exception object for `on_error` notifications.

```
def test_in_sequence_or_throw_error():
    scheduler = TestScheduler()
    source = reactivex.from_marbles('--1-4-3-', timespan=50, scheduler=scheduler)
    result = scheduler.start(lambda: source.pipe(
        in_sequence_or_throw(),
    ), created=1, subscribed=30)

    assert result.messages == [
        on_next(30+100, 1),
        on_error(230, ValueError('Sequence error'))
    ]
    # At times it's better not to test the exact exception,
    # maybe its message changes with time or other reasons
    # We can test a specific notification's details as follows:
    first_notification, error_notification = result.messages
    assert first_notification.time == 130
    assert error_notification.time == 230
    assert first_notification.value.kind == 'N'  # Notification
    assert error_notification.value.kind == 'E'  # E for errors
    assert first_notification.value.value == 1
    assert type(error_notification.value.exception) == ValueError  # look at .exception for errors

```

### Testing Subscriptions, Multiple Observables, Hot Observables

`scheduler.start` is limited to a single subscription. For testing scenarios involving multiple subscriptions, or explicit control over subscription timing, additional tools are available.

**Key Components:**

*   **`scheduler.create_observer()`**: Creates a test observer to manually subscribe to observables and record messages.
*   **`scheduler.schedule_relative(time, action)`**: Schedules an `action` to be executed at a `time` relative to the scheduler's current virtual time.
*   **`Subscription(start_time, end_time)`**: A class used to represent and assert the start and end times of subscriptions on source observables. An infinite subscription is represented as `Subscription(start_time)`.
*   **`scheduler.create_cold_observable()`**: Creates a cold observable for testing.
*   **`scheduler.create_hot_observable()`**: Creates a hot observable for testing.
*   **`operators.to_marbles(timespan=..., scheduler=...)`**: An operator that converts an observable's emissions into a marble string, useful for assertions.

```
def test_multiple():
    scheduler = TestScheduler()
    source = reactivex.from_marbles('-1-4-3-|', timespan=50, scheduler=scheduler)
    odd, even = source.pipe(
        operators.partition(lambda x: x % 2),
    )
    steven = scheduler.create_observer()
    todd = scheduler.create_observer()

    even.subscribe(steven)
    odd.subscribe(todd)

    # Note! Since the subscription is not created within
    # `scheduler.start` below, the usual `subscribed` delay of t=200
    # is not in effect. The subscriptions therefore occur at t=0
    scheduler.start()

    assert steven.messages == [
        on_next(150, 4),
        on_completed(350)
    ]
    assert todd.messages == [
        on_next(50, 1),
        on_next(250, 3),
        on_completed(350)
    ]

```

```
from reactivex.testing.subscription import Subscription
def test_subscriptions():
    scheduler = TestScheduler()
    source = scheduler.create_cold_observable()  # "infinite"
    subs = []
    shared = source.pipe(
        operators.share()
    )
    # Creating our story:
    # first sub is set to occur at t=200; this creates a sub on source
    scheduler.schedule_relative(200, lambda *_: subs.append(shared.subscribe(scheduler=scheduler)))
    # second sub does not create a new sub on source, due to the `share` operator
    scheduler.schedule_relative(300, lambda *_: subs.append(shared.subscribe(scheduler=scheduler)))
    # second sub ends
    scheduler.schedule_relative(500, lambda *_: subs[1].dispose())
    # first sub ends… and since there is no sub remaining, the only sub on source should be disposed too
    scheduler.schedule_relative(600, lambda *_: subs[0].dispose())
    # no existing sub on source, therefore this will create a new one
    # we never dispose of it; we will test that infinite sub in the assertions
    scheduler.schedule_relative(900, lambda *_: subs.append(shared.subscribe(scheduler=scheduler)))

    scheduler.start()
    # Check that the submissions on the source are as expected
    assert source.subscriptions == [
        Subscription(200, 600), # only one sub from 200 to 600
        Subscription(900),  # represents an infinite subscription
    ]

```

```
def test_hot():
    scheduler = TestScheduler()
    # hot starts at 0 but sub starts at 200 so we'll miss 190
    source = scheduler.create_hot_observable(
        on_next(190, 5),
        on_next(300, 42),
        on_completed(500)
    )
    result = scheduler.start(lambda: source.pipe(
        operators.to_marbles(timespan=20, scheduler=scheduler)
    ))

    message = result.messages[0]
    # the subscription starts at 200;
    # since `source` is a hot observable, the notification @190 will not be caught
    # the next notification is at 300 ticks,
    # which, on our subscription, will show at 100 ticks (300-200 from subscription delay)
    # or 5 "-" each representing 20 ticks (timespan=20 in `to_marbles`).
    # Then the "42" notification is received
    # and then nothing for another 200 ticks, which is equal to 10 "-", before complete
    assert message.value.value == '-----(42)----------|'

```
