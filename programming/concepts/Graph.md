# Graph Traversal & Distributed Systems Notes

## Basic Info
### Directed Acyclic Graph (DAG)
* **Directed**: Edges must have a specific direction.
* **Acyclic**: There can be no cycles. If A depends on B, B depends on C, and C depends on A, there is no valid starting point, and a sort is impossible.

---

## Graph Storage Methods
> **Lead Note:** At the Lead level, you shouldn't just code these; you should explain their memory implications. You must be able to justify why you chose one storage method over another based on the density of the graph and the operations required.

### 1. Adjacency List
* **Overview**: The industry standard for sparse graphs. It saves space $O(V + E)$ and is efficient for finding neighbors. Represented using a map of lists.
* **Memory Complexity**: $O(V + E)$
* **Best Used For**: 
    * Sparse graphs (most real-world graphs are sparse)
    * Optimizing memory space
    * Fast lookups & insertions

### 2. Adjacency Matrix
* **Overview**: Ideal for dense graphs or when you need to check if an edge exists between two nodes in $O(1)$ time. Represented as `edgeMatrix[nodeIdx1][nodeIdx2]` where values denote existence (yes/no) or an edge weight.
* **Memory Complexity**: $O(V^2)$
* **Best Used For**:
    * Dense graphs
    * Frequent edge lookups
    * Weighted graphs
    * Matrix Math / Spectral Graph Theory

### 3. Object-Oriented (Node/Edge Objects)
* **Overview**: Common in real-world software where nodes carry heavy metadata.
* **Best Used For**:
    * Complex metadata structures (e.g., User profiles, Infrastructure nodes)
    * Graphs too massive for a single machine requiring a distributed system
    * Scenarios needing direct business logic invocations from the graph elements

---

## Core Graph Algorithms
> **Lead Note:** Lead roles often involve cost optimization and resource routing.

### Breadth-First Search (BFS)
* **Use Case**: Finding the shortest path in unweighted graphs.
* **System Detail**: Mind the memory bottleneck. BFS stores an entire "level" of nodes in the queue, which can grow exponentially in wide graphs.

### Depth-First Search (DFS)
* **Use Case**: Exhaustive search, pathfinding, and cycle detection.
* **System Detail**: Be mindful of stack overflow on extremely deep graphs. Always consider an iterative approach using an explicit stack for production-grade code.

### Dijkstra’s Algorithm
* **Use Case**: Finding the shortest path in a weighted graph (with non-negative weights).
* **System Detail**: Understand the critical role of the Priority Queue ($O(E \log V)$).

### Topological Sort (Kahn’s Algorithm)
* **Use Case**: Essential for modeling dependencies (e.g., build systems, task scheduling, or data pipelines).
* **Definition**: If there is a path from Node A to Node B, Node A must appear anywhere to the left of Node B in your final list (they do not need to be adjacent).

#### DFS Approach
1.  **Visit**: Start at an unvisited node and explore its neighbors recursively.
2.  **Stack**: Once a node has no more unvisited neighbors (it is "finished"), push it onto a stack.
3.  **Output**: After visiting all nodes, pop contents from the stack one by one to get the topological sort.

#### BFS Approach (Kahn's Algorithm)
1.  **Calculate In-degree**: Count the number of incoming edges for every vertex.
2.  **Initialize Queue**: Add all vertices with an in-degree of 0 (nodes with no dependencies) to a queue.
3.  **Process**:
    * Remove a vertex from the queue and add it to the sorted list.
    * For each of its neighbors, decrease their in-degree by 1.
    * If a neighbor's in-degree drops to 0, add it to the queue.
4.  **Cycle Check**: If the final sorted list does not contain all vertices, the graph contains a cycle.

### Advanced Groupings
* **Union-Find (Disjoint Set Union)**: Extremely efficient for checking connectivity and finding Minimum Spanning Trees (Kruskal’s).
* **Strongly Connected Components (SCCs)**: Useful for analyzing social networks or web crawls to find clusters where every node is reachable from every other node.

---

## Real-World Problem Transformation
> **Lead Note:** This is where Lead candidates distinguish themselves. You should be able to transform a vague problem into a graph problem.

### Dependency Resolution
* *Vague Problem:* "How do we ensure Service A starts after Service B?"
* *Graph Mapping:* Topological Sort / DAG.

### Network Flow (Max-Flow Min-Cut)
* *Vague Problem:* "How much data/water/cars can we push through this network of pipes from point A to point B?"
* *Graph Mapping:* Ford-Fulkerson method.
* **Ford-Fulkerson Steps**:
    1.  Start with zero flow on all edges.
    2.  **Find an "Augmenting Path"**: Look for any path from Source to Sink that has "residual capacity" (space left).
    3.  **Identify the Bottleneck**: Find the edge in that path with the smallest remaining capacity (e.g., 5 units).
    4.  **Augment the Flow**: Add those bottleneck units to every edge along that path.
    5.  **Repeat**: Keep searching for paths. When no more paths from Source to Sink exist, Max-Flow is reached.
* **The Max-Flow Min-Cut Theorem**: A "Cut" is a partition slicing the graph into Source and Sink halves. The capacity of a cut is the sum of all edge capacities crossing from the Source side to the Sink side. **Theorem:** The value of the Maximum Flow is exactly equal to the capacity of the Minimum Cut.
* **Applications**: Internet Routing, Logistics & Supply Chain, Airline Scheduling & Image Segmentation.

### Recommendation Engines
* *Graph Mapping:* Bipartite Graph & Random Walk with Restart.
* **Bipartite Graph**: Vertices are divided into two disjoint, independent sets ($U$ and $V$) such that every edge connects a vertex in $U$ to one in $V$. No two nodes within the same set are connected.
* **Properties**: A graph is bipartite if and only if it contains no odd-length cycles. The adjacency matrix structure can be decomposed as:
    $$\begin{bmatrix} 0 & B \\ B^T & 0 \end{bmatrix}$$
* **How to recommend**: Random Walk with Restart. Start at User A $\rightarrow$ move to an Item they liked $\rightarrow$ move to User B who also liked that item $\rightarrow$ move to a new Item liked by User B.

### Graph Neural Networks (GNNs)
* **Core Operation**: Graph Convolution Network’s main operation is Neighborhood Aggregation (or Message Passing).
* **The Gist**: Aggregate feature vectors from neighboring nodes. The graph structure itself is part of the model.

### Fraud Detection
* **The Gist**: Identifying cycles or unusually dense subgraphs in transaction logs. Cycles and dense clusters are usually strong patterns for fraud. Graphs represent relationships beautifully and allow fast traversal.
* **Identification Techniques**:
    * Identify super nodes (nodes with an unusually high number of edges).
    * Detect synthetic identities (multiple distinct nodes connecting to the same IP address).
    * Ring & loop detections for money laundering tracking.
    * Community detection via Louvain or Label Propagation.

---

## System Architecture & Scale
> **Lead Note:** Since you are likely interviewing for a role involving large-scale systems, consider how graphs behave when they don't fit on a single machine.

### Graph Databases vs. Relational
* **When to use Neo4j or AWS Neptune over PostgreSQL**: Use graph databases when the relationship/join depth is deep and highly unpredictable.

### Partitioning (Sharding)
* **The "Giant Component" Problem**: How do you split a graph across multiple servers without creating too many slow "cross-server" edges?
* **Strategies**:
    * **Vertex Cut**: Good for graphs containing prominent "super nodes".
    * **Edge Cut**: Good for uniform graphs where nodes share a balanced number of edges.
    * **Hash-Based Partitioning**: Very fast and doesn't require knowing layout properties ahead of time.
    * **Geographic/Spatial Partitioning**: Grouped by physical locations.
    * **Label Partitioning / METIS**: Excellent for social or transactional graphs.

### Caching
* Representing graphs in **Redis** using hashes, sets, and sorted sets to manage real-time social feeds or session permissions efficiently.

---

## Potential Interview Coding Questions

### Graph Problems
* Shortest path in a grid
* Detecting cycles in dependency graphs
* "Number of Islands" variations

### Tree & List Problems
* Linked List Cycle
* Swapping Nodes in a Linked List
* Validate Binary Search Tree
* Maximum Difference Between Node and Ancestor