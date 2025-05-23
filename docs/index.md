<!-- https://rxpy.readthedocs.io/en/latest/ -->
ReactiveX for Python (RxPY) is a library designed for composing asynchronous and event-based programs. It leverages observable collections and pipable query operators within Python.

The documentation covers the following key areas:

*   **Installation**: Instructions for setting up RxPY.
*   **Rationale**: Explains the reasoning and philosophy behind RxPY.
*   **Get Started**: Provides an introduction to using the library, including:
    *   Operators and Chaining
    *   Creating Custom Operators
    *   Concurrency management
*   **Testing**: Guidance on testing RxPY applications, covering:
    *   Basic examples
    *   Testing custom operators
    *   Using timelines
    *   An alternative using marbles
    *   Testing observable factories
    *   Testing error scenarios
    *   Testing subscriptions, multiple observables, and hot observables
*   **Migration v4 & v3**: Important information for users migrating from previous versions, detailing changes such as:
    *   Pipe-based operator chaining
    *   Removal of the result mapper
    *   Scheduler parameter in the `create` operator
    *   Removal of list of observables
    *   Blocking observable behavior
    *   Back-pressure considerations
    *   Time units (now in seconds)
    *   Package renaming
*   **Operators**: A comprehensive section detailing various types of operators:
    *   Creating Observables
    *   Transforming Observables
    *   Filtering Observables
    *   Combining Observables
    *   Error Handling
    *   Utility Operators
    *   Conditional and Boolean Operators
    *   Mathematical and Aggregate Operators
    *   Connectable Observable Operators
*   **Additional Reading**: Resources for further learning.
*   **Reference**: Detailed API reference for core components:
    *   Observable Factory
    *   Observable
    *   Subject
    *   Scheduler
    *   Operators
    *   Typing
*   **Contributing**: Guidelines for contributing to the RxPY project.
*   **The MIT License**: Licensing information for the library.
