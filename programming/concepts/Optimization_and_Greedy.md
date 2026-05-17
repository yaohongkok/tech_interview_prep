# Optimization & Greedy Engineering Notes

## 1. Fundamentals of Greedy Approaches
* **The Lead's Core Skill:** For a lead, the most important concept isn't how to write a for loop; it's knowing if a problem is provably solvable with a greedy approach.
* **Greedy Choice Property:** Can you make a locally optimal choice (the best move right now) and have it lead to a globally optimal solution? You take the "best" option available.
* **Proving Optimality:** Prove optimality via Contradiction or Induction.
  * *Contradiction proof:* Assume there is an optimal solution that didn't pick the greedy choice, and then prove that substituting the greedy choice makes the solution just as good or better.
* **Mathematical Identities for Optimization:**
  * In general: $\max(x + y) \le \max(x) + \max(y)$
  * When $x$ and $y$ are independent (not related at all): $\max(x + y) = \max(x) + \max(y)$ (Can be proved by upper bound analysis and showing the bound is attainable, e.g., $x \le \max(x)$ & $y \le \max(y)$).
  * Another useful identity: $\max(x - y) = \max(x) - \min(y)$
* **Optimal Substructure:** Can the problem be broken down into smaller versions of itself? It should be recursive. 
  * *Example:* If you are finding the shortest path from City A to City C, and that path passes through City B, then the portion of the path from A to B must also be the shortest possible path between those two cities.
* **Identifying Greedy-Choice Failure:** A lead perspective requires being able to identify when a greedy choice fails. 
  * Using greedy logic on a non-greedy problem results in buggy, sub-optimal production code.
  * *The Knapsack Example:* The 0/1 Knapsack Problem cannot be solved greedily, while the Fractional Knapsack can.
    * **Fractional Knapsack:** Always take the item with the highest Value per KG first. You can always fill the remaining space with the next best thing; the local best choice never blocks a better global outcome.
    * **0/1 Knapsack:** You have a bag that holds 10kg, but the items are solid (e.g., a laptop, a gold bar, a heavy book). You either take it or you don't. Suppose Item A is 6kg ($100), Item B is 5kg ($60), and Item C is 5kg ($60). 
      * *Greedy Choice:* Takes Item A (highest value/kg). Bag has 4kg left and can't fit B or C. Total: $100.
      * *Global Optimum:* Take Item B and Item C. Total: $120.

## 2. Practical Applications of Greedy Algorithms
Lots of optimization problems are NP-hard. Solving via Greedy is the hope to get to suboptimal results.

### 1. Scheduling & Resource Allocation
* **Interval Scheduling:** If you have multiple tasks competing for a single resource, the goal is to complete the maximum number of tasks. 
  * The "greedy" choice here is to always pick the task that finishes earliest, leaving the maximum amount of time available for subsequent tasks.
* **Task Scheduling with Deadlines:** Unlike interval scheduling, every task here has a specific deadline and an associated penalty or profit. You prioritize tasks that minimize "lateness" or maximize total profit, often by sorting tasks by their deadlines and filling slots from the latest possible time backward.

### 2. Graph Optimization
* **Minimum Spanning Trees (MST):** Connect all nodes in a graph with the minimum total edge weight, ensuring no cycles.
  * *Prim's Algorithm:* Starts from a single node and "grows" the tree by adding the cheapest edge connected to the current tree. It is excellent for dense graphs.
  * *Kruskal's Algorithm:* Treats every node as an individual tree and merges them by adding the shortest available edges across the entire graph. It is often preferred for sparse graphs.
* **Dijkstra’s Algorithm:** This finds the quickest route from point A to point B. It maintains a "tentative" distance to every node and constantly updates those distances as it finds shorter paths. This is the logic behind OSPF (Open Shortest Path First) routing protocols.

### 3. Data Compression
* **Huffman Coding:** A "lossless" compression technique that makes modern web traffic and file storage manageable.
  * *Prefix Property:* Ensures that no code is a prefix of another (e.g., if 'A' is 01, no other character starts with 01). This allows a stream of bits to be decoded uniquely without needing spaces or delimiters.
  * *System Impact:* Understanding this is vital for optimizing Serialization Protocols (like Protocol Buffers or Avro). When you reduce the size of the payload at the algorithmic level, you directly reduce network latency and egress costs.

## 3. Advanced Optimization Techniques & Analysis
In lead-level engineering, you often deal with NP-hard problems where an exact solution is computationally impossible at scale.

* **Approximation Algorithms:** Knowing when to use a greedy approach to get a "good" solution quickly (e.g., the Set Cover problem).
  * Has an approximation ratio of $\ln(n)$.
  * $\ln(n)$ complexity is great for NP-hard problems.
* **Competitive Analysis:** Understanding how much worse your greedy solution is compared to the optimal one (the approximation ratio).
* **Local Search:** Improving a greedy starting point by making small, incremental changes (e.g., Hill Climbing or Simulated Annealing).
* **Complexity & Constraints:** Optimization is often a battle against time and space complexity.
  * *Bottleneck Analysis:* Identifying whether the sorting step (often $O(n \log n)$) or the selection step is the primary constraint in your optimization pipeline.
  * *Linear Programming (LP):* Modeling constraints and objectives using tools like the Simplex algorithm.
* **Amortized Analysis:** Understanding the cost of operations over time, especially when using auxiliary data structures like Priority Queues or Disjoint Set Unions (DSU) to power greedy choices.
  * The goal is to make an expensive operation occur less frequently.
  * *Example:* Kruskal's algorithm uses a DSU, a special type of data structure that has a search complexity of $O(lpha(n))$, where $lpha$ is the inverse Ackermann function. It performs amortization for the search; basically, it sorts it once to make future searches faster.

## 4. Dynamic Programming (DP) vs. Greedy
* **When to use DP:** Recognizing when sub-problems overlap and require memoization because a greedy choice would be short-sighted.
* **Cost Functions:** Defining what "optimal" actually means for the business (e.g., is it minimizing latency, maximizing throughput, or reducing cloud egress costs?).
* **The Core DP Concept:** If you are calculating the same state multiple times, you should store the result. This turns exponential time complexity $O(2^n)$ into polynomial complexity $O(n)$ by ensuring each unique state is computed exactly once.

### Memoization vs. Tabulation
Choosing between these two is often a matter of language constraints (recursion depth) and memory patterns.
* **Memoization:** A recursive approach that caches results in a lookup table (usually a hash map or array). It only computes the states necessary to reach the answer.
* **Tabulation:** An iterative approach that fills a table (matrix or array) starting from the base cases. 
  * *Pro-Tip:* Tabulation is generally faster in production environments because it avoids the overhead of recursive function calls and offers better cache locality.

### DP Architecture
* **State Design:** This is the most difficult part of DP design. You must define what "state" represents the minimum information needed to make a future decision.
  * *The State:* Usually represented as `DP[i][j]`, representing the optimal value at index `i` given a constraint `j` (like remaining capacity or time).
* **The Transition Equation:** The logic that connects the current state to previous ones.
  * *Example:* `DP[i] = min(DP[i-1], DP[i-2]) + cost[i]`
* **Space Optimization:** In many DP problems, you only need the results from the previous row or step to compute the current one.
  * *The Strategy:* Instead of an $O(N^2)$ matrix, you can often use two rows (or even a single array) to reduce space complexity to $O(N)$.
  * *Example:* In the Knapsack problem or Edit Distance, you typically only reference `DP[i-1]`.
  * As a lead, you should always push for space-optimized DP if the full history isn't required for reconstruction.
* **Bitmask DP:** When an optimization problem involves "all possible subsets" or "all possible permutations" (like the Traveling Salesperson Problem), a standard array isn't enough.
  * *The Concept:* Use an integer's binary representation to represent a set of items or visited nodes.
  * *Constraint:* This is usually reserved for small input sizes (typically $N < 20$) because the complexity is $O(2^n \cdot n^2)$.
* **Reconstruction:** Often, the business doesn't just want the value of the optimization (e.g., "The max profit is $500"), they want the steps taken to get there. This involves "backtracking" through your DP table from the final result to the base case to identify which choices were made.

## 5. Reference Questions
1. Meeting Rooms II
2. (Basic Greedy) Minimum Number of Food Buckets to Feed Hamsters
3. Kadane Algorithm for Maximum Subarray problem
4. Task Scheduling
