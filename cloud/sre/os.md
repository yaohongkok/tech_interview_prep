# OS & SRE Interview Preparation Guide

---

## Part 1: Core OS Concepts for SRE Interviews

### 1.1 Processes and Threads

**Processes** are independent programs with their own memory space, file descriptors, and system resources. The OS manages them via a Process Control Block (PCB) that stores state, PID, registers, and memory mappings.

**Threads** are lightweight units of execution that share the same memory space within a process. They allow concurrency within a single process but introduce risks like race conditions and deadlocks.

Key distinctions:
- **Context switching** between processes is expensive (full memory map swap); between threads it's cheaper (shared address space).
- **Fork vs. exec**: `fork()` creates a copy-on-write clone of the parent process; `exec()` replaces the process image with a new program.
- **Zombie processes**: A process that has finished executing but hasn't been reaped by its parent via `wait()`. They hold a PID and PCB entry.
- **Orphan processes**: A child whose parent has died; adopted by `init`/`systemd` (PID 1).

---

### 1.2 CPU Scheduling

The kernel scheduler decides which process/thread runs on which CPU core and for how long.

**Scheduling algorithms:**
- **Round Robin (RR)**: Each process gets a fixed time slice (quantum); preempted if not done.
- **Completely Fair Scheduler (CFS)**: Linux's default. Tracks "virtual runtime" per task and always runs the task with the smallest vruntime.
- **Priority-based / Real-time (SCHED_FIFO, SCHED_RR)**: Used for latency-sensitive workloads.

**Key metrics:** CPU utilization, throughput, turnaround time, waiting time, response time.

**Load average** represents the average number of processes in a runnable or uninterruptible sleep state over 1, 5, and 15 minutes. On a single-core machine, a load of 1.0 means full utilization.

---

### 1.3 Memory Management

The OS abstracts physical RAM through **virtual memory**, giving each process the illusion of its own address space.

**Key concepts:**
- **Paging**: Virtual memory is divided into fixed-size pages; physical memory into frames. The kernel maintains a **page table** mapping virtual pages to physical frames.
- **Page faults**: Occur when a process accesses a page not in physical memory. The kernel fetches it from disk (swap).
- **Swap space**: Disk area used as overflow for RAM. Excessive swapping (thrashing) degrades performance severely.
- **Memory segments**: Stack (local variables, grows downward), Heap (dynamic allocations, grows upward), BSS (uninitialized globals), Data (initialized globals), Text (code).
- **OOM Killer**: When the system runs out of memory, the Linux OOM killer selects and kills a process based on `oom_score`.

**Tools:** `free -h`, `vmstat`, `/proc/meminfo`, `smem`, `pmap <pid>`

---

### 1.4 File Systems

The filesystem abstracts persistent storage into a hierarchy of files and directories.

**Core concepts:**
- **Inodes**: Data structures storing file metadata (permissions, owner, timestamps, block pointers) — everything *except* the filename.
- **Hard links vs. soft links**: Hard links share the same inode; soft (symbolic) links are pointers to a path.
- **VFS (Virtual File System)**: A kernel abstraction layer allowing different filesystems (ext4, xfs, tmpfs, nfs) to be used through a unified API.
- **Journaling**: Filesystems like ext4 and xfs maintain a journal to recover from crashes without full fsck scans.
- **Mount namespaces**: Allow different processes to see different filesystem trees (used heavily in containers).

**Common filesystems:** ext4 (general purpose), xfs (large files/parallel I/O), tmpfs (RAM-backed), btrfs (snapshots, COW), overlayfs (containers).

---

### 1.5 I/O and Storage

**I/O models:**
- **Blocking I/O**: The process waits until the I/O completes.
- **Non-blocking I/O**: Returns immediately; the process polls for completion.
- **Asynchronous I/O (AIO)**: The kernel notifies the process when I/O is done (`epoll`, `io_uring`).
- **Memory-mapped I/O (mmap)**: Maps a file into the process's address space for direct access.

**Disk I/O scheduling:** The kernel uses I/O schedulers (CFQ, deadline, none/mq-deadline for NVMe) to reorder and batch disk requests for efficiency.

**Key metrics:** IOPS, throughput (MB/s), latency, `iowait` (CPU time spent waiting for I/O).

**Tools:** `iostat -x`, `iotop`, `blktrace`, `fio` (benchmarking)

---

### 1.6 Networking (OS Perspective)

**TCP/IP stack layers** are implemented in the kernel. SREs regularly deal with:
- **Socket buffers** (send/receive buffers) — tunable via `sysctl net.core.rmem_max` etc.
- **TIME_WAIT**: A TCP connection state that lingers for 2×MSL after close. Under high connection rates, exhausted ports cause `EADDRINUSE`.
- **SYN backlog**: Queue of half-open TCP connections. SYN floods can fill this (`net.ipv4.tcp_max_syn_backlog`).
- **TCP keepalive**: Detects dead connections by sending probes after an idle period.
- **Congestion control algorithms**: Cubic (default Linux), BBR (throughput-optimized).

**Kernel tuning levers for networking:** `sysctl`, `/proc/sys/net/`, `ss`, `netstat`, `tc` (traffic control).

---

### 1.7 Signals and IPC

**Signals** are asynchronous notifications sent to processes. Common ones:
| Signal | Number | Default Action |
|--------|--------|----------------|
| SIGHUP | 1 | Reload config (convention) |
| SIGINT | 2 | Interrupt (Ctrl+C) |
| SIGKILL | 9 | Kill (cannot be caught/ignored) |
| SIGTERM | 15 | Graceful termination request |
| SIGSEGV | 11 | Segmentation fault |
| SIGCHLD | 17 | Child process state changed |

**Inter-Process Communication (IPC):**
- **Pipes / named pipes (FIFOs)**: Unidirectional byte streams.
- **Unix domain sockets**: Bidirectional, faster than TCP for local communication.
- **Shared memory (SHM)**: Fastest IPC; requires explicit synchronization.
- **Message queues**: Kernel-managed queues of typed messages.
- **Semaphores / mutexes**: Synchronization primitives to prevent race conditions.

---

### 1.8 Kernel, System Calls, and Namespaces

**System calls** are the interface between user space and kernel space. Common ones for SREs: `read`, `write`, `open`, `close`, `fork`, `execve`, `mmap`, `brk`, `socket`, `connect`, `epoll_wait`, `clone`.

**`strace`** traces system calls made by a process — invaluable for debugging.

**Linux Namespaces** (foundation of containers):
| Namespace | Isolates |
|-----------|----------|
| pid | Process IDs |
| net | Network interfaces, routing |
| mnt | Mount points |
| uts | Hostname, domain name |
| ipc | SysV IPC, POSIX MQ |
| user | UIDs and GIDs |
| cgroup | Cgroup root |

**cgroups (Control Groups)**: Limit and account for resource usage (CPU, memory, I/O, network) per group of processes. Used by Docker, Kubernetes, and systemd.

---

### 1.9 Observability and Performance Tools

A mental map of tools by resource:

| Resource | Tools |
|----------|-------|
| CPU | `top`, `htop`, `mpstat`, `perf`, `flame graphs` |
| Memory | `free`, `vmstat`, `smem`, `/proc/meminfo` |
| Disk I/O | `iostat`, `iotop`, `dstat`, `blktrace` |
| Network | `ss`, `netstat`, `iftop`, `tcpdump`, `wireshark` |
| System calls | `strace`, `ltrace` |
| Kernel events | `perf`, `eBPF/bpftrace`, `ftrace` |
| All-in-one | `dstat`, `glances`, `sar` |

**USE Method** (Brendan Gregg): For every resource, check **Utilization**, **Saturation**, and **Errors**.

---

### 1.10 Reliability Concepts

These bridge pure OS knowledge into SRE practice:

- **SLI / SLO / SLA**: Service Level Indicators (metrics), Objectives (targets), Agreements (contractual commitments).
- **Error budget**: `1 - SLO` expressed as allowed downtime or error rate. Guides release velocity decisions.
- **Toil**: Repetitive, manual, automatable operational work. SRE teams aim to keep toil under 50% of work time.
- **Blast radius**: The scope of impact from a failure. Limiting blast radius via isolation (namespaces, separate clusters, canary deployments) is a key SRE practice.
- **MTTR vs. MTBF**: Mean Time To Repair vs. Mean Time Between Failures. SREs optimize heavily for fast detection and recovery.

---

## Part 2: Popular OS/SRE Interview Questions and Answers

---

### Process & Thread Management

**Q1: What is the difference between a process and a thread?**

A process is an independent execution unit with its own virtual address space, file descriptors, and system resources. Threads live within a process and share its address space, making communication between threads fast but requiring careful synchronization to avoid data corruption. Context-switching between processes is costlier than between threads because the kernel must swap memory mappings. From an SRE perspective, multithreaded applications can be harder to debug (race conditions, deadlocks) but typically have lower latency for concurrent workloads than forking new processes.

---

**Q2: What happens when you run `fork()` followed by `exec()`?**

`fork()` creates a child process as a near-exact copy of the parent. Linux uses **copy-on-write (COW)** — physical memory pages are shared until one process writes to them, at which point a private copy is made. `exec()` then replaces the child's address space with a new program image. This `fork-exec` pattern is how shells launch commands: `fork()` creates the child, the child calls `exec()` to load the binary, and the parent `wait()`s for completion.

---

**Q3: How would you find and kill a zombie process?**

Zombie processes have already exited but haven't been reaped by their parent. You can identify them with:
```bash
ps aux | grep 'Z'
```
You **cannot** kill a zombie directly (it's already dead). The fix is to kill or signal the **parent** process so it calls `wait()`:
```bash
kill -SIGCHLD <parent_pid>
# or if that doesn't work:
kill -9 <parent_pid>
```
If the parent is PID 1 (systemd), zombies are automatically reaped.

---

**Q4: What is a deadlock and how can it be prevented?**

A deadlock occurs when two or more processes are each waiting for a resource held by another, forming a circular wait. The four **Coffman conditions** must all hold for deadlock to occur: mutual exclusion, hold-and-wait, no preemption, and circular wait.

Prevention strategies:
- **Lock ordering**: Always acquire locks in a consistent global order.
- **Lock timeouts**: Use `trylock` with a timeout and back off on failure.
- **Resource allocation graphs**: Detect cycles at design time.
- **Avoid hold-and-wait**: Acquire all needed locks at once.

---

### Memory Management

**Q5: What is a page fault and what are the different types?**

A page fault is a hardware exception raised when a process accesses a virtual address that isn't currently mapped to a physical frame. Types:
- **Minor (soft) page fault**: The page exists in memory but isn't mapped in the page table (e.g., shared library already loaded by another process). Cheap — no disk I/O.
- **Major (hard) page fault**: The page must be loaded from disk (swap or file). Expensive — causes I/O latency.
- **Invalid page fault (segfault)**: The address is not mapped at all or permissions are violated. Results in SIGSEGV.

You can monitor page faults with `perf stat`, `/proc/<pid>/stat`, or `ps -o majflt,minflt`.

---

**Q6: What causes memory leaks and how do you diagnose them?**

A memory leak occurs when a program allocates heap memory and never frees it, causing RSS (resident set size) to grow unboundedly over time.

Diagnosis steps:
1. Watch RSS growth over time: `watch -n5 'ps -o pid,rss,comm -p <pid>'`
2. Use `/proc/<pid>/smaps` or `pmap -x <pid>` to see memory segments.
3. For C/C++ programs: `valgrind --leak-check=full` or `AddressSanitizer`.
4. For Go: `pprof` heap profiles.
5. For Java: heap dumps, VisualVM, or async-profiler.

---

**Q7: What is the OOM killer and how does it decide which process to kill?**

When the kernel cannot satisfy a memory allocation and swap is exhausted, the **OOM (Out-Of-Memory) killer** is invoked. It selects a victim process based on `oom_score`, calculated from:
- Memory usage (RSS + swap)
- Process uptime (newer processes score higher)
- Whether the process has `CAP_SYS_ADMIN` (scores lower)
- The `oom_score_adj` value (range -1000 to 1000, tunable per process)

To protect critical processes, set:
```bash
echo -1000 > /proc/<pid>/oom_score_adj
```
To prefer killing a process, set it to 1000. Check OOM events in `/var/log/kern.log` or `dmesg | grep -i oom`.

---

### File Systems and I/O

**Q8: What is the difference between a hard link and a symbolic link?**

A **hard link** is a directory entry that points directly to an inode. Multiple hard links can point to the same inode; the file data is only deleted when the last hard link is removed (inode link count drops to 0). Hard links cannot span filesystems and cannot link to directories.

A **symbolic (soft) link** is a special file containing a path string to another file or directory. If the target is deleted, the symlink becomes dangling. Symlinks can cross filesystems and can point to directories.

```bash
ln file hard_link       # hard link
ln -s file soft_link    # symbolic link
stat file               # shows inode and link count
```

---

**Q9: A disk is full but `df -h` shows space available. What could be wrong?**

This classic mismatch has several causes:

1. **Deleted files held open by processes**: A file deleted while a process still holds an open file descriptor is not freed until the process closes it. `df` shows the inode as deleted but the blocks are still consumed. Fix: `lsof | grep deleted` and restart or restart the process holding the file.
2. **Inode exhaustion**: You've run out of inodes even though disk blocks are available. Check with `df -i`. Common on filesystems with millions of tiny files.
3. **Reserved blocks**: ext4 reserves ~5% of blocks for root by default. `tune2fs -m 1 /dev/sdX` reduces the reservation.
4. **Bind mounts or overlayfs**: Apparent space is on a different underlying device.

---

**Q10: Explain the difference between buffered and direct I/O.**

**Buffered (cached) I/O** goes through the kernel's **page cache**. Reads may be served from cache; writes are written to cache first and flushed to disk asynchronously by the kernel's writeback threads. This is fast for repeated reads and batches small writes.

**Direct I/O** (`O_DIRECT` flag) bypasses the page cache, transferring data directly between user buffers and the storage device. It requires aligned buffers and access sizes matching the block size. Databases like PostgreSQL and MySQL often use direct I/O to implement their own caching layer and avoid double-buffering.

Trade-off: Buffered I/O is simpler and usually faster for general workloads; direct I/O gives more predictable latency and lets applications control caching.

---

### Networking

**Q11: What is TIME_WAIT and why is it a problem at scale?**

`TIME_WAIT` is a TCP state that a connection enters after actively closing it. It persists for **2 × MSL** (Maximum Segment Lifetime, typically 60 seconds on Linux = 120 seconds total). Its purpose is to ensure that delayed packets from the old connection don't corrupt a new connection using the same 4-tuple (src IP, src port, dst IP, dst port).

At high connection rates (e.g., a service making many short-lived outbound HTTP requests), the ephemeral port range (typically 32768–60999) can be exhausted by TIME_WAIT sockets, causing `EADDRINUSE` or connection failures.

Mitigations:
- Enable `net.ipv4.tcp_tw_reuse=1` (allows reuse for outbound connections with timestamps).
- Expand ephemeral port range: `net.ipv4.ip_local_port_range = 1024 65535`.
- Use persistent connections (HTTP keep-alive, connection pools).
- `net.ipv4.tcp_fin_timeout` controls FIN_WAIT_2 timeout (not TIME_WAIT directly).

---

**Q12: How does the Linux kernel handle a large number of concurrent connections?**

The key bottleneck is the **I/O notification mechanism**:
- Old approach: `select`/`poll` — O(n) scan of all file descriptors per call. Doesn't scale past thousands of connections.
- Modern approach: **`epoll`** — O(1) notification for ready events. The kernel maintains a set of watched fds and notifies only on state changes.

Beyond epoll, at very high scale:
- **SO_REUSEPORT**: Allows multiple sockets to bind to the same port; the kernel distributes connections across them (useful for multi-threaded servers).
- **TCP offload / DPDK**: Bypass the kernel network stack entirely for ultra-low latency.
- **`io_uring`**: Modern kernel AIO interface that further reduces syscall overhead.

Tuning levers: `net.core.somaxconn`, `net.ipv4.tcp_max_syn_backlog`, `ulimit -n` (open file descriptors), `net.core.netdev_max_backlog`.

---

**Q13: Walk me through what happens when you type `curl https://example.com`.**

1. **DNS resolution**: The system resolver checks `/etc/hosts`, then queries the configured DNS server for `example.com`'s A/AAAA record.
2. **TCP connection**: curl opens a socket and initiates a 3-way handshake (SYN → SYN-ACK → ACK) with the resolved IP on port 443.
3. **TLS handshake**: Client sends ClientHello (supported cipher suites, TLS version). Server responds with its certificate and ServerHello. Keys are exchanged (ECDHE), and both sides derive session keys. Application data now flows encrypted.
4. **HTTP request**: curl sends an HTTP/1.1 or HTTP/2 GET request over the TLS session.
5. **Server response**: The server responds with headers and body; curl writes output to stdout.
6. **Teardown**: TCP FIN/FIN-ACK closes the connection; both sides enter TIME_WAIT briefly.

From an SRE perspective, each step has failure modes: DNS NXDOMAIN, TCP RST, TLS cert errors, HTTP 4xx/5xx, and each has distinct debugging tools (`dig`, `tcpdump`, `openssl s_client`, `curl -v`).

---

### Observability and Debugging

**Q14: A service is slow. Walk me through your debugging approach.**

Use the **USE method** (Utilization, Saturation, Errors) and a top-down approach:

1. **Check symptoms first**: Is it high latency, low throughput, or errors? Check dashboards, logs, and error rates.
2. **CPU**: `top`/`htop` — is CPU pegged? `perf top` or flame graphs to find hot code paths. Check `iowait` (high iowait = I/O bound).
3. **Memory**: `free -h` — is there swap usage? Are there page faults? Check for OOM kills in `dmesg`.
4. **Disk I/O**: `iostat -x 1` — look at `%util`, `await` (average I/O latency), `r/s`, `w/s`. `iotop` to identify the offending process.
5. **Network**: `ss -s` for connection states. Are there many TIME_WAIT or CLOSE_WAIT? `tcpdump` to inspect packet-level behavior. Check for packet drops with `netstat -s`.
6. **Application level**: Check thread pool saturation, connection pool exhaustion, GC pauses, lock contention. Review application metrics and distributed traces.
7. **Kernel/syscalls**: `strace -p <pid>` to see what syscalls the process is blocked on.

---

**Q15: How do you diagnose high CPU usage on a Linux server?**

```bash
# 1. Identify the offending process
top -c              # interactive; press P to sort by CPU
ps aux --sort=-%cpu | head -20

# 2. Identify which threads/functions are hot
top -H -p <pid>     # per-thread CPU usage
perf top -p <pid>   # live sampling of functions

# 3. Generate a flame graph for deep analysis
perf record -F 99 -p <pid> -g -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# 4. Check if it's kernel or user CPU
vmstat 1            # 'us' = user, 'sy' = system/kernel, 'wa' = iowait
```

Common causes: CPU-bound computation, spin locks, excessive GC, tight retry loops, or a runaway process.

---

**Q16: What is `strace` and when would you use it?**

`strace` intercepts and records system calls made by a process. It's invaluable for:
- **Debugging startup failures**: What files is a process trying to open and failing?
- **Finding missing libraries or configs**: `strace -e trace=open,openat,read ./binary`
- **Understanding I/O patterns**: Which files is the process reading/writing?
- **Diagnosing hangs**: What syscall is the process blocking on?

```bash
strace -p <pid>                    # attach to running process
strace -tt -T -p <pid>            # with timestamps and per-call duration
strace -e trace=network -p <pid>  # only network syscalls
strace -f ./program               # follow child processes (fork)
```

Caution: `strace` adds significant overhead (~2-10x slowdown) due to ptrace. Use it briefly in production or in a test environment.

---

### Containers and Virtualization

**Q17: How do containers differ from virtual machines?**

| | Virtual Machine | Container |
|---|---|---|
| Isolation unit | Full OS + hypervisor | Linux namespaces + cgroups |
| Boot time | Minutes | Milliseconds |
| Overhead | High (separate kernel per VM) | Low (shared host kernel) |
| Security boundary | Strong (hardware-level) | Weaker (kernel is shared) |
| Portability | Moderate | High |

Containers use Linux **namespaces** for isolation (PID, net, mnt, uts, ipc, user) and **cgroups** for resource limits. They share the host kernel, which is why a container escape vulnerability affects the host. VMs use hardware virtualization (Intel VT-x / AMD-V) to run entirely separate kernels.

---

**Q18: What are cgroups and how are they used by Kubernetes?**

**cgroups (Control Groups)** are a Linux kernel feature that limits, accounts for, and isolates resource usage (CPU, memory, disk I/O, network) for groups of processes.

Kubernetes uses cgroups to enforce:
- **CPU limits**: Implemented via `cpu.cfs_period_us` and `cpu.cfs_quota_us` (CFS bandwidth controller). A pod throttled to 500m CPU gets 50ms of CPU per 100ms period.
- **Memory limits**: Set via `memory.limit_in_bytes`. Exceeding it triggers the OOM killer within the cgroup.
- **QoS classes**: `Guaranteed` (requests == limits), `Burstable` (requests < limits), `BestEffort` (no requests/limits). The kubelet uses these to decide eviction order under memory pressure.

Understanding cgroup v1 vs. v2 differences (unified hierarchy in v2) is increasingly important for modern Kubernetes clusters.

---

### SRE Principles

**Q19: What is an error budget and how do you use it?**

An error budget is the allowed amount of unreliability derived from your SLO. If your availability SLO is 99.9%, your monthly error budget is `0.1% × 43,200 minutes ≈ 43 minutes` of downtime.

How it's used:
- **When budget is healthy**: Teams can move fast, deploy frequently, and take risks.
- **When budget is depleted**: Feature releases slow or freeze; engineering focuses on reliability improvements.
- **Policy enforcement**: The error budget makes reliability a shared engineering problem, not just an ops problem — it creates accountability across product and SRE teams.

The error budget removes the adversarial dynamic between development (wanting to ship) and operations (wanting stability) by giving both a shared, quantitative objective.

---

**Q20: How would you design a runbook for a common on-call scenario (e.g., high memory usage)?**

A good runbook follows this structure:

**Alert**: `MemoryUsageHigh` — Pod memory usage > 90% of limit for > 5 minutes.

**Impact**: Risk of OOM kill; possible service degradation or restart loop.

**Step 1 — Verify**
```bash
kubectl top pods -n <namespace>
kubectl describe pod <pod> | grep -A5 OOMKilled
```

**Step 2 — Diagnose**
```bash
# Check heap if JVM
kubectl exec <pod> -- jcmd 1 VM.native_memory
# Check RSS breakdown
kubectl exec <pod> -- cat /proc/1/status | grep VmRSS
```

**Step 3 — Mitigate**
- If a leak: restart pod (`kubectl rollout restart deployment/<name>`) to buy time.
- If legitimate growth: temporarily increase memory limit via Helm values or HPA.
- If recurring: scale horizontally and file a ticket for code-level investigation.

**Step 4 — Escalate if**: OOM kills are happening faster than restarts can keep up, or if the memory growth is anomalous vs. historical traffic.

**Follow-up**: File a ticket to add heap profiling, review recent deploys for memory regressions, and consider setting up memory alerting at 70% for earlier warning.

---
