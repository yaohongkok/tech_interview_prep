# Python Concepts

## Data Model & Types

- Everything is an object, including functions, classes and modules; variables are names bound to objects, not boxes holding values.
- **Mutable**: `list`, `dict`, `set`, `bytearray`. **Immutable**: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`.
- `==` compares value (`__eq__`); `is` compares identity. Use `is` only for `None`, `True`, `False`.
- Arguments are passed by object reference: mutating a passed-in list affects the caller, rebinding the name does not.
- Mutable default arguments (`def f(x=[])`) are evaluated once at definition time and shared across calls. Use `None` as the default.
- Dict keys and set members must be hashable: `__hash__` must be consistent with `__eq__` and stable over the object's lifetime.
- Shallow copy (`copy.copy`, `list[:]`) duplicates the container only; `copy.deepcopy` duplicates nested objects too.
- Truthiness: `0`, `""`, `[]`, `{}`, `None` are falsy. Prefer `if x is None` when an empty value is valid.

## Built-in Data Structures

- `list`: dynamic array. Append and index are O(1); insert or pop at the front is O(n).
- `dict`: hash table, average O(1) lookup, preserves insertion order (3.7+).
- `set`: hash table of unique items, O(1) membership; supports `|`, `&`, `-`, `^`.
- `tuple`: immutable sequence, hashable if its contents are; use for fixed records and dict keys.
- `collections`: `deque` (O(1) at both ends), `defaultdict`, `Counter`, `OrderedDict`, `namedtuple`.
- `heapq`: min-heap on a plain list; negate values for a max-heap.
- Sorting is Timsort: stable, O(n log n). `sorted()` returns a new list, `list.sort()` sorts in place; both take `key=`.

## Functions & Scope

- Name resolution follows **LEGB**: Local, Enclosing, Global, Built-in.
- `global` and `nonlocal` are needed to rebind (not to read) names in outer scopes.
- Functions are first-class: pass them around, store them, return them.
- **Closures** capture variables, not values. Lambdas created in a loop all see the final loop value unless bound via a default argument.
- `*args` collects positional arguments, `**kwargs` collects keyword arguments; `/` and `*` in a signature mark positional-only and keyword-only parameters.
- **Decorators** are functions that take a function and return a replacement; `@functools.wraps` preserves the original name and docstring.

## Iteration

- An **iterable** implements `__iter__`; an **iterator** also implements `__next__` and raises `StopIteration` when done.
- **Generators** (`yield`) produce values lazily and keep state between calls, giving constant memory for large or infinite streams.
- Generator expressions `(x for x in xs)` are lazy; list comprehensions `[x for x in xs]` are eager.
- Iterators are single-pass: once exhausted they stay empty.
- Modifying a list or dict while iterating over it leads to skipped items or a `RuntimeError`; iterate over a copy.

## Object-Oriented Python

- Instance, class and static methods: `self`, `@classmethod` with `cls` (alternative constructors), `@staticmethod` (no implicit argument).
- Class attributes are shared by all instances; a mutable class attribute is a common source of bugs.
- **Dunder methods** hook into language features: `__repr__`, `__str__`, `__eq__`, `__hash__`, `__lt__`, `__len__`, `__getitem__`, `__contains__`, `__call__`, `__enter__` / `__exit__`.
- Defining `__eq__` without `__hash__` makes the class unhashable.
- Multiple inheritance is resolved by the **MRO** (C3 linearisation); `super()` follows the MRO, not just the parent.
- `@property` exposes computed attributes with getter/setter control and no API change.
- Duck typing: behaviour matters, not declared type. Formalise with `abc.ABC` or `typing.Protocol`.
- `@dataclass` generates `__init__`, `__repr__` and `__eq__`; `frozen=True` makes instances immutable and hashable.
- `__slots__` removes the per-instance `__dict__`, saving memory for many small objects.

## Errors & Resource Handling

- `try / except / else / finally`: `else` runs only if no exception was raised, `finally` always runs.
- Catch specific exceptions; a bare `except:` also swallows `KeyboardInterrupt` and `SystemExit`.
- EAFP ("easier to ask forgiveness than permission") is idiomatic over pre-checking (LBYL).
- `raise NewError(...) from err` preserves the original cause in the traceback.
- **Context managers** (`with`) guarantee cleanup; implement with `__enter__` / `__exit__` or `@contextlib.contextmanager`.

## Memory & Execution Model

- Source is compiled to bytecode, then interpreted by the CPython VM.
- Memory is managed by **reference counting**, plus a generational garbage collector that handles reference cycles.
- Small integers and some strings are interned, so `is` may appear to work on them; never rely on it.
- `if __name__ == "__main__":` separates script entry from import-time behaviour.
- A module is executed once on first import and cached in `sys.modules`; circular imports fail on partially initialised modules.

## Concurrency & Parallelism

- The **GIL** lets only one thread execute Python bytecode at a time in standard CPython.
- **Threads** (`threading`): good for I/O-bound work, since the GIL is released while waiting on I/O; no speed-up for CPU-bound code.
- **Processes** (`multiprocessing`): true parallelism for CPU-bound work, at the cost of process start-up and pickling data between processes.
- **asyncio**: single-threaded cooperative concurrency. `await` yields control to the event loop; a blocking call stalls everything.
- The GIL does not make code thread-safe: compound operations like `x += 1` still need a `Lock`. `queue.Queue` is thread-safe.

## Typing & Tooling

- Type hints are not enforced at runtime; checkers such as `mypy` or `pyright` verify them statically.
- Common forms: `list[int]`, `dict[str, int]`, `X | None`, `Callable`, `TypeVar`, `Protocol`, `Literal`.
- Isolate dependencies per project with virtual environments (`venv`, `uv`, `poetry`); pin versions in a lock file.

## Idioms & Performance

- Prefer comprehensions, unpacking (`a, b = b, a`, `first, *rest = xs`), f-strings and `pathlib` over manual equivalents.
- Build strings with `"".join(parts)`; repeated `+=` in a loop is O(n²).
- Test membership against a `set` or `dict`, not a `list`.
- Profile before optimising: `timeit` for snippets, `cProfile` for programs.
