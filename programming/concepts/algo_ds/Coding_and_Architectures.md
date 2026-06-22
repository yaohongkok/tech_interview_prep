# Coding & Architectures

## Clean Code
* **Self-Documenting Logic:** Use intention-revealing names. In a system with many moving parts, `processTransaction()` is better than `handle()`.
* **Small, Atomic Functions:** Each function should do one thing. This is critical for distributed logic where a single function might involve a database hit, a cache update, and an external API call.
* **Graceful Exit & Fail-Fast:** Clean code handles edge cases (like a timeout or a 503 Service Unavailable) immediately rather than letting null values propagate through the system.
* **Testability:** If code isn't modular, it isn't testable. Leads emphasize Unit Tests for logic and Integration Tests for boundaries.
* **Observability Hooks:** Maintainable code includes "hooks" for logging, metrics, and tracing. If a module is a "black box" that doesn't emit logs, it is not maintainable.

## SOLID Principles
* **Single Responsibility (SRP):** A module (class, function, package) should only have one responsibility. *Why?* Maintainability, less complex, easier testing, reusable.
* **Open/Closed (OCP):** Entity should be open for extension, closed for modification. New features should ideally be added via extension (through polymorphism) and avoid changing the source code directly.
  * *Polymorphism:* Many forms. Different object types can be treated as one interface. *Why?* Maintainability, faster development, prevent bugs, better architecture.
* **Liskov Substitution (LSP):** Superclass should be replaceable with objects of its subclasses without affecting the program's correctness. *Why?* Prevents broken functionality, reusability, maintainability & logical inheritance.
* **Interface Segregation (ISP):** No code should be forced to depend on methods it does not use. It promotes breaking down large, "fat" interfaces into smaller, specific ones, ensuring implementing classes only handle relevant methods. *Why?* Code modularity, flexibility, and maintainability.
* **Dependency Inversion (DIP):** Depend on abstractions. Your business logic shouldn't depend on a specific database driver; both should depend on a storage interface. *Why?* Decoupling, independent development, flexibility, easier testing.

## Design Patterns
* **Strategy Pattern:** Enables selecting an algorithm at runtime. Instead of implementing a single algorithm directly, code receives runtime instructions as to which in a family of algorithms to use. Strategy lets the algorithm vary independently from clients that use it.
* **Factory Pattern:** Useful for creating complex objects, like different types of database connections based on configuration.
* **Observer/Pub-Sub:** Crucial for distributed systems where one event (like a "User Created" event) needs to trigger actions in multiple other modules or services. Class S subscribe to the results from Class P.
* **Decorator/Middleware:** Used to wrap core logic with "cross-cutting concerns" like authentication, logging, or rate limiting without cluttering the main business function. Add more functionality before or after a function call.

## Architectural Patterns
This is how you structure the "folders and files" to separate the concerns of a distributed application.

### Layered (N-Tier) Architecture
A software design pattern that organizes code into horizontal layers, each with a specific responsibility.
* *Example:* Model-View-Controller (3-tier), Domain Driven Design (DDD)
* *Common Layered Architecture (DDD):*
  * **Presentation:** UI or result format
  * **App/Service Layer:** Bridge to business layer, i.e. http endpoint handling logic
  * **Domain/Business Layer:** Business logic, rules or constraints
  * **Infrastructure:** DB or data

### Hexagonal (Ports and Adapters)
The core logic sits in the center, and "Adapters" (HTTP, Database, Message Queues) connect to it via "Ports" (Interfaces). This is the gold standard for modern distributed services.
* **Domain (center):** Core business logic. E.g. product model & business logic.
* **Ports (interface to the center):** Exposes interfaces to the center. Two types - inbound ports & outbound ports.
* **Adapters:** Concrete implementations to the ports. Can be database implementation, REST or even UIs.

### Clean Architecture
An evolution of Hexagonal that strictly enforces that dependencies only point inwards toward the business rules.

![The Clean Architecture](https://raw.githubusercontent.com/mapping-the-commons/resources/main/clean_architecture.png)

---

## Practical Implementation Exercises
1. Design a **Rate Limiter**.
2. Design an **LRU Cache**.
3. Write a function to **transfer money between two accounts**. How do you ensure this is atomic and safe from 'race conditions'?
