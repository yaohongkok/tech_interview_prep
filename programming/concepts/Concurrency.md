# 1) Concurrency & Thread Safety

### 1. Process vs. Thread

- **Process:** An executing instance of a program. It has its own dedicated memory space (Heap). Processes are independent; if one crashes, the others usually keep running.

- **Thread:** A "lightweight" unit of execution within a process. Multiple threads share the same memory space of their parent process but have their own Stack and Program Counter.

Program counter holds the memory address of the next instruction to be fetched and executed by the CPU. Each thread has its own PC because multiple threads might be executing different parts of the same program code at once. Used to help OS to switch between threads so that it can run and stop threads.

Thread stack is a private range of memory allocated specifically for that thread's function calls and local variables. Also, stack stores the value of the program counter (the return address) before jumping to a function.

**Shared memory:** OS resource (like files, network connection & signals), heap data (like global variable or dynamic allocated memory) & code section

**Private memory:** Program counter, register (for CPU usage) & stack (function call & local variables)

---

### 2. Concurrency vs. Parallelism

These terms are often used interchangeably, but they describe different behaviors:

- **Concurrency:** Handling many things at once. It's about structure. On a single-core CPU, threads "interleave" (switch back and forth rapidly), giving the illusion of simultaneous work.
  - **When to Use:** It usually used to make IO logic non-blocking. For example: waiting for network call to return.
  - **Random behavior:** Yes, due to scheduler and other threads.
  - **Context Switching:** Yes. Switch between threads consumes CPU seconds.

- **Parallelism:** Doing many things at once. It's about execution. This requires multi-core hardware where different threads run on different physical cores at the exact same millisecond.
  - **When to Use:** To speed up calculations by using more cores, e.g. processing of large array.
  - **Random behavior:** Less likely. Results and time to completion are more consistent.
  - **Context Switching:** No (at least). Parallel threads just execute their own logic and rarely wait for results from the other CPU.

---

## 3. The "Gotchas": Common Challenges

Sharing memory is efficient, but it's also dangerous. When two threads try to modify the same data at the same time, chaos ensues.

### Race Conditions

This happens when the outcome depends on the unpredictable timing of thread execution. Outcome becomes non-deterministic.

**Example:** Thread A reads a balance of $100. Thread B reads $100. Thread A adds $10. Thread B adds $20. They both write back. Instead of $130, the final balance might be $110 or $120 because they overrode each other.

**How to avoid:**

1. Mutex
2. Atomic operations (only one thread can read or write in a single step)
3. Make shared data immutable, i.e. shared data cannot be changed by thread
4. Pass global variable into local variable
5. Message passing (i.e. Go or Rust)

### Deadlocks

A "Mexican Standoff" for software. Thread 1 holds Resource A and waits for Resource B. Thread 2 holds Resource B and waits for Resource A. Neither can move, and the program freezes.

Deadlock occurs due to the locking of resource that is never released. It can be due to introducing ways to handle race conditions.

**When deadlock occurs:**

- Database deadlock (2 threads/process updating similar rows)
- Resource deadlock (2 threads/processes accessing 2 hardware resources)
- Network deadlock (2 routers waiting for each other)
- Mutex locking a variable while waiting for another locked variable
- Semaphores

**How to prevent deadlock:**

1. **Lock Ordering.** When acquiring more than 1 lock, locks must be obtained in a pre-determined order. For example, two locks may have IDs. Those IDs must be sorted first and then the "smaller" lock ID is obtained.
2. **Lock Timeout** – can still induce locking if both threads have similar timeouts. Results in livelock. One way to handle is to have 'jitter' in timeout. Some advise to use exponential backoff.
3. **`tryLock` method** – try to obtain lock. It won't wait indefinitely if a lock is not obtained. It will return false.
4. **Resource hierarchy** – Organize resources into levels and only allow a process to request resources at a higher level than those it currently holds.

---

## 4. Synchronization Tools

To prevent the chaos mentioned above, we use synchronization primitives:

- **Mutex (Mutual Exclusion):** A lock that ensures only one thread can access a resource at a time.
- **Semaphore:** A signaling mechanism. Mainly used for throttling. A "counting semaphore" can allow a specific number of threads (e.g., allowing only 5 concurrent database connections).
- **Atomic Operations:** Low-level operations that are guaranteed to complete in a single step without interruption, preventing race conditions without the overhead of a full lock.

**Mutex Go example:**

```go
package main

import (
	"fmt"
	"sync"
)

type SafeCounter struct {
	mu    sync.Mutex
	value int
}

func (c *SafeCounter) Increment(wg *sync.WaitGroup) {
	defer wg.Done()
	// Without Mutex, the counter will not get to 1000.
	c.mu.Lock()
	c.value++
	c.mu.Unlock()
}

func main() {
	counter := SafeCounter{}
	var wg sync.WaitGroup
	numGoroutines := 1000
	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go counter.Increment(&wg)
	}
	// Wait for all goroutines to finish.
	wg.Wait()
	fmt.Printf("Final Counter Value: %d\n", counter.value)
}
```

**Semaphore Go example:**

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	// This acts as a semaphore allowing only 3 concurrent workers.
	semaphore := make(chan struct{}, 3)

	var wg sync.WaitGroup
	for i := 1; i <= 10; i++ {
		wg.Add(1)

		go func(id int) {
			defer wg.Done()
			// If 3 values are already in there, this blocks.
			semaphore <- struct{}{}

			fmt.Printf("Worker %d: Started (Active workers: %d)\n", id, len(semaphore))
			time.Sleep(2 * time.Second) // Simulate a heavy task

			// RELEASE: Pull the value out to free up a slot for someone else.
			<-semaphore
			fmt.Printf("Worker %d: Done\n", id)
		}(i)
	}

	wg.Wait()
	fmt.Println("All workers finished.")
}
```

**Go atomic example:**

```go
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

func main() {
	// 1. Declare an atomic integer.
	// This is guaranteed to be thread-safe without locks.
	var counter atomic.Int64
	var wg sync.WaitGroup
	numGoroutines := 1000
	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func() {
			defer wg.Done()

			// 2. Perform an atomic increment.
			// Hardware ensures this happens as a single indivisible step.
			counter.Add(1)
		}()
	}
	wg.Wait()

	// 3. Perform an atomic load to read the final value.
	fmt.Printf("Final Atomic Counter: %d\n", counter.Load())
}
```

---

## 5. Modern Best Practices

In recent years, the industry has shifted away from manual thread management toward higher-level abstractions:

- **Thread Pools:** Instead of spawning a new thread for every task (which is expensive), you maintain a "pool" of standing threads and assign tasks to them as they become free.
- **Immutability:** If data can't be changed, you don't need to lock it. Functional programming patterns have made multi-threading much safer.
- **Async/Await:** While often single-threaded (like in JavaScript), this model allows for "non-blocking" code, which solves many of the same responsiveness problems as multi-threading without the memory overhead.
