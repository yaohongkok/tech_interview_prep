# Java Interview Preparation Guide

A comprehensive reference covering core Java concepts and common interview questions with detailed answers.

---

## Part 1: Core Java Concepts

### 1. Object-Oriented Programming (OOP)

Java is built around four fundamental OOP principles:

**Encapsulation** — Bundling data (fields) and behavior (methods) into a class, and restricting direct access using access modifiers (`private`, `protected`, `public`). Getters and setters expose controlled access.

**Inheritance** — A class (`child`) can extend another class (`parent`) to reuse and override its behavior. Java supports single inheritance for classes but multiple inheritance via interfaces.

**Polymorphism** — The ability for a single interface or method to take on different forms. Achieved through method overriding (runtime) and method overloading (compile-time).

**Abstraction** — Hiding implementation details and exposing only what is necessary, using `abstract` classes or `interface`.

---

### 2. Java Memory Model

| Area | Description |
|------|-------------|
| **Heap** | Where objects are stored. Shared across threads. Managed by the Garbage Collector. |
| **Stack** | Stores method call frames and local variables. Each thread has its own stack. |
| **Method Area / Metaspace** | Stores class-level data, static fields, and method bytecode. |
| **PC Register** | Tracks the current instruction being executed per thread. |

**Garbage Collection (GC)** automatically reclaims heap memory from objects that are no longer reachable. Common GC algorithms include Serial, Parallel, G1, and ZGC.

---

### 3. Java Data Types

**Primitive types:** `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`

**Reference types:** Objects, arrays, strings, and any instance of a class.

Key distinction: primitives are stored by value; reference types store a memory address (pointer) to the actual object on the heap.

---

### 4. Collections Framework

The Java Collections Framework provides data structures for storing and manipulating groups of objects.

**Interfaces and common implementations:**

| Interface | Common Implementations | Characteristics |
|-----------|----------------------|-----------------|
| `List` | `ArrayList`, `LinkedList` | Ordered, allows duplicates |
| `Set` | `HashSet`, `LinkedHashSet`, `TreeSet` | No duplicates |
| `Map` | `HashMap`, `LinkedHashMap`, `TreeMap` | Key-value pairs, no duplicate keys |
| `Queue` | `LinkedList`, `PriorityQueue`, `ArrayDeque` | FIFO ordering |

**Big-O for HashMap:** average O(1) for `get`/`put`; O(n) worst case (hash collisions). Uses `hashCode()` and `equals()` together.

---

### 5. Concurrency and Multithreading

- A **Thread** is a lightweight unit of execution. Threads share the heap but have their own stack.
- **`synchronized`** keyword ensures mutual exclusion on a block or method.
- **`volatile`** ensures visibility of changes to a variable across threads (no caching in CPU registers).
- **`java.util.concurrent`** package provides higher-level abstractions: `ExecutorService`, `CountDownLatch`, `Semaphore`, `ConcurrentHashMap`, `BlockingQueue`, etc.
- **Deadlock** occurs when two or more threads are waiting for each other's locks indefinitely.

---

### 6. Exception Handling

Java exceptions are split into two categories:

- **Checked exceptions** — Must be declared or caught (e.g., `IOException`, `SQLException`). Subclass of `Exception`.
- **Unchecked exceptions** — Runtime exceptions that don't need to be declared (e.g., `NullPointerException`, `ArrayIndexOutOfBoundsException`). Subclass of `RuntimeException`.
- **Errors** — Serious JVM-level failures not meant to be caught (e.g., `OutOfMemoryError`, `StackOverflowError`).

Use `try-catch-finally` for handling. The `finally` block always executes regardless of whether an exception was thrown.

---

### 7. Generics

Generics allow classes and methods to operate on parameterized types, providing compile-time type safety.

```java
List<String> names = new ArrayList<>();
names.add("Alice");
String name = names.get(0); // No casting needed
```

Wildcards:
- `? extends T` — upper bounded (read-only, covariant)
- `? super T` — lower bounded (write-safe, contravariant)
- `?` — unbounded wildcard

---

### 8. Functional Programming and Streams (Java 8+)

**Lambda expressions** provide a concise way to implement functional interfaces (interfaces with a single abstract method).

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.stream()
     .filter(n -> n.startsWith("A"))
     .map(String::toUpperCase)
     .forEach(System.out::println);
```

**Key functional interfaces:** `Predicate<T>`, `Function<T, R>`, `Consumer<T>`, `Supplier<T>`, `BiFunction<T, U, R>`

**Optional** — A container object used to represent nullable values and avoid `NullPointerException`.

---

### 9. String Handling

- `String` is **immutable** in Java — every modification creates a new object.
- `StringBuilder` is mutable and not thread-safe; preferred for single-threaded string manipulation.
- `StringBuffer` is mutable and thread-safe (synchronized), but slower.
- String literals are stored in the **String Pool** (part of the heap since Java 7).

---

### 10. Design Patterns

Common patterns frequently tested in interviews:

| Pattern | Type | Purpose |
|---------|------|---------|
| Singleton | Creational | Ensure only one instance of a class exists |
| Factory Method | Creational | Delegate object creation to subclasses |
| Builder | Creational | Construct complex objects step by step |
| Observer | Behavioral | Notify dependents when state changes |
| Strategy | Behavioral | Swap algorithms at runtime |
| Decorator | Structural | Add behavior to objects dynamically |

---

## Part 2: Popular Java Interview Questions & Answers

---

### Q1. What is the difference between `==` and `.equals()` in Java?

`==` compares **references** (memory addresses) for objects, or **values** for primitives.

`.equals()` compares **logical equality** — what the objects represent. For `String`, `Integer`, and other wrapper classes, `.equals()` is overridden to compare content.

```java
String a = new String("hello");
String b = new String("hello");
System.out.println(a == b);       // false (different objects)
System.out.println(a.equals(b));  // true  (same content)
```

---

### Q2. What is the difference between an abstract class and an interface?

| Feature | Abstract Class | Interface |
|---------|---------------|-----------|
| Instantiation | Cannot be instantiated | Cannot be instantiated |
| Methods | Can have abstract and concrete methods | All methods abstract by default (Java 8+ allows `default` and `static`) |
| Fields | Can have instance fields | Only `public static final` constants |
| Inheritance | Single inheritance only | A class can implement multiple interfaces |
| Constructor | Can have constructors | Cannot have constructors |

Use an **abstract class** when sharing common state or behavior among closely related classes. Use an **interface** to define a contract that unrelated classes can implement.

---

### Q3. What is the Java Memory Model and how does garbage collection work?

The JVM manages memory in several regions. The **heap** stores all objects and is shared across threads. The **stack** is per-thread and stores local variables and call frames. The **Metaspace** (formerly PermGen) stores class metadata.

Garbage collection automatically reclaims heap memory from objects with no live references. The GC uses a **generational** approach:

1. **Young Generation** (Eden + Survivor spaces) — New objects are created here. Minor GC is frequent and fast.
2. **Old Generation (Tenured)** — Objects that survive multiple GC cycles are promoted here. Major GC is less frequent but slower.
3. **GC Roots** — GC starts from roots (stack references, static fields) and marks all reachable objects. Unreachable objects are collected.

Modern GC algorithms (G1, ZGC, Shenandoah) aim for low pause times and are suitable for large heap sizes.

---

### Q4. Explain the concept of `final`, `finally`, and `finalize`.

- **`final`** — A keyword. Applied to a variable (value cannot change), method (cannot be overridden), or class (cannot be subclassed).
- **`finally`** — A block in a `try-catch-finally` statement that always executes, whether or not an exception occurs. Used for cleanup (closing resources).
- **`finalize()`** — A deprecated method in `Object` that the GC used to call before reclaiming an object. Unreliable and discouraged; use `try-with-resources` or explicit cleanup instead.

---

### Q5. What is the difference between `ArrayList` and `LinkedList`?

| Feature | `ArrayList` | `LinkedList` |
|---------|------------|--------------|
| Internal structure | Dynamic array | Doubly-linked list of nodes |
| Random access | O(1) | O(n) |
| Insert/delete at middle | O(n) (shift elements) | O(1) (if node reference known) |
| Memory overhead | Lower | Higher (stores prev/next pointers) |
| Best use case | Frequent reads | Frequent insertions/deletions |

---

### Q6. What is a `HashMap` and how does it work internally?

`HashMap` stores key-value pairs using a hash table. Internally it maintains an array of **buckets**.

When you call `put(key, value)`:
1. `key.hashCode()` is computed and the hash is mapped to a bucket index.
2. If the bucket is empty, the entry is stored there.
3. If there's a collision (two keys map to the same bucket), Java uses a **linked list** (or a balanced tree for 8+ entries in a bucket, since Java 8) to chain entries.
4. `equals()` is used to distinguish keys within the same bucket.

Default initial capacity is 16, with a load factor of 0.75. When 75% full, the map **rehashes** (doubles capacity and redistributes entries).

**Note:** `HashMap` is not thread-safe. Use `ConcurrentHashMap` for concurrent access.

---

### Q7. What is the difference between `String`, `StringBuilder`, and `StringBuffer`?

- **`String`** — Immutable. Each concatenation creates a new object. Thread-safe by virtue of immutability. Stored in the String Pool when using literals.
- **`StringBuilder`** — Mutable, not thread-safe. Best choice for single-threaded string building (e.g., in loops).
- **`StringBuffer`** — Mutable, thread-safe (synchronized methods). Slower than `StringBuilder`. Use when multiple threads share the same buffer.

```java
// Prefer StringBuilder for performance in loops
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) sb.append(i);
String result = sb.toString();
```

---

### Q8. What are Java 8 streams and when should you use them?

Streams provide a declarative, functional-style API for processing sequences of elements. They do not store data — they transform or consume it from a source (collection, array, I/O channel).

Key characteristics:
- **Lazy** — Intermediate operations (like `filter`, `map`) are not executed until a terminal operation (like `collect`, `forEach`, `reduce`) is invoked.
- **Non-reusable** — A stream can only be consumed once.
- **Parallelizable** — Use `parallelStream()` to process elements concurrently.

Use streams when you need to filter, map, sort, or aggregate data in a concise, readable way. Avoid them when you need indexed access, mutation of external state, or complex branching logic.

---

### Q9. What is the Singleton pattern and how do you implement it thread-safely?

The Singleton pattern ensures only one instance of a class is created throughout the application lifecycle.

**Thread-safe implementation using initialization-on-demand holder:**

```java
public class Singleton {
    private Singleton() {} // private constructor

    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

This is lazy (created on first access), thread-safe (class loading is thread-safe), and avoids synchronization overhead. Alternatively, using `enum` is the simplest thread-safe singleton approach.

---

### Q10. What is the difference between `Comparable` and `Comparator`?

| | `Comparable` | `Comparator` |
|--|-------------|--------------|
| Package | `java.lang` | `java.util` |
| Method | `compareTo(T o)` | `compare(T o1, T o2)` |
| Implementation | Implemented by the class itself | Implemented externally |
| Use case | Natural ordering (e.g., alphabetical for strings) | Custom or alternate orderings |
| Modifies class | Yes | No |

```java
// Comparable — natural order
class Employee implements Comparable<Employee> {
    public int compareTo(Employee other) {
        return this.name.compareTo(other.name);
    }
}

// Comparator — custom order (by salary)
Comparator<Employee> bySalary = (a, b) -> Double.compare(a.salary, b.salary);
employees.sort(bySalary);
```

---

### Q11. What is a deadlock and how do you prevent it?

(Learn more at `programming/concepts/algo_ds/Concurrency.md`)

A **deadlock** occurs when two or more threads are waiting for each other to release locks, causing all of them to block indefinitely.

Classic scenario:
- Thread A holds Lock 1, waits for Lock 2.
- Thread B holds Lock 2, waits for Lock 1.

Prevention strategies:
1. **Lock ordering** — Always acquire locks in the same fixed order across all threads.
2. **Lock timeout** — Use `tryLock(timeout)` from `java.util.concurrent.locks.Lock` to fail gracefully if a lock is unavailable.
3. **Avoid nested locking** — Minimize holding multiple locks simultaneously.
4. **Use higher-level concurrency utilities** — `java.util.concurrent` classes like `ConcurrentHashMap`, `Semaphore`, and `ExecutorService` reduce the need for manual locking.

---

### Q12. What is the difference between `checked` and `unchecked` exceptions?

**Checked exceptions** are verified by the compiler. If a method can throw one, it must either catch it or declare it with `throws`. They represent recoverable conditions (e.g., file not found, network timeout).

**Unchecked exceptions** (subclasses of `RuntimeException`) are not checked at compile time. They represent programming errors (e.g., null pointer dereference, array index out of bounds) that typically should not be caught but fixed.

```java
// Checked — must be handled
try {
    FileReader fr = new FileReader("file.txt"); // throws IOException
} catch (IOException e) {
    e.printStackTrace();
}

// Unchecked — no obligation to catch
int[] arr = new int[5];
arr[10] = 1; // throws ArrayIndexOutOfBoundsException at runtime
```

---

### Q13. What is method overloading vs method overriding?

**Overloading** — Same method name, different parameter list (type, count, or order). Resolved at **compile time** (static polymorphism).

**Overriding** — A subclass provides its own implementation of a method inherited from a superclass. The method signature must match. Resolved at **runtime** (dynamic polymorphism).

```java
// Overloading
int add(int a, int b) { return a + b; }
double add(double a, double b) { return a + b; }

// Overriding
class Animal { void speak() { System.out.println("..."); } }
class Dog extends Animal {
    @Override
    void speak() { System.out.println("Woof"); }
}
```

---

### Q14. What is `volatile` and when should you use it?

The `volatile` keyword guarantees that reads and writes to a variable are always done directly from/to main memory, preventing CPU or JVM caching optimizations that could cause threads to see stale values.

Use `volatile` when:
- A variable is read and written by multiple threads.
- You only need visibility (not atomicity for compound operations like `count++`).

For compound atomic operations, use `AtomicInteger`, `AtomicLong`, etc. from `java.util.concurrent.atomic`, or use `synchronized`.

---

### Q15. How does `HashMap` differ from `Hashtable` and `ConcurrentHashMap`?

| Feature | `HashMap` | `Hashtable` | `ConcurrentHashMap` |
|---------|-----------|-------------|---------------------|
| Thread safety | Not thread-safe | Thread-safe (full sync) | Thread-safe (segment locking) |
| Null keys/values | Allows one null key, multiple null values | No null keys or values | No null keys or values |
| Performance | Fastest (single-threaded) | Slowest (coarse lock) | Best for concurrent access |
| Legacy | No | Yes (Java 1.0) | No (Java 5+) |
| Iteration | Fail-fast iterator | Fail-safe enumeration | Weakly consistent iterator |

For new concurrent code, always prefer `ConcurrentHashMap` over `Hashtable`.

---

*This guide covers the most critical topics for Java interviews. Practice coding each concept hands-on, and review the Java documentation for any areas where you want deeper understanding.*