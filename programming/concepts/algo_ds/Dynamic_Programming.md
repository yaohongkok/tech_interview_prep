# Dynamic Programming (DP) Notes

## 1. Fundamentals

DP is **recursion + remembering answers**. A problem can be solved with DP when it has both:

* **Optimal Substructure:** The best answer to the whole problem is built from the best answers to smaller sub-problems.
  * *Example:* If the shortest path A → C goes through B, then its A → B part must also be the shortest A → B path.
* **Overlapping Sub-problems:** The same sub-problem is needed again and again.
  * *Example:* Naive Fibonacci computes `fib(3)` many times when computing `fib(6)`. Storing it once turns $O(2^n)$ into $O(n)$.

> If sub-problems **do not** overlap (e.g., merge sort), it's plain divide & conquer, not DP.
> If one local choice is always safe, it's **Greedy** (see [Optimization_and_Greedy.md](Optimization_and_Greedy.md)). DP is what you use when you must **try every choice** and keep the best.

### Two Ways to Implement
| | Top-down (Memoization) | Bottom-up (Tabulation) |
|---|---|---|
| Style | Recursive function + cache | Loop filling a table |
| Order | Computed on demand | You must pick an order where dependencies are filled first |
| Pros | Easy to write straight from the equation; only visits needed states | No recursion limit; easy to space-optimize |
| Cons | Recursion depth / stack overflow | Must reason about loop order |

```python
from functools import lru_cache

# Top-down
@lru_cache(maxsize=None)
def V(state):
    if is_base(state):
        return base_value(state)
    return max(reward(state, a) + V(next_state(state, a)) for a in actions(state))

# Bottom-up
dp = [base] * (N + 1)
for state in order_where_dependencies_come_first:
    dp[state] = max(reward(state, a) + dp[next_state(state, a)] for a in actions(state))
```

**Complexity rule of thumb:** `Time = (# of states) × (# of choices per state)`, `Space = # of states` (often reducible).

---

## 2. The Bellman Equation

Every DP solution is a **Bellman equation** (a.k.a. recurrence / transition function). Richard Bellman coined both the term "dynamic programming" and the **Principle of Optimality**:

> *Whatever the first decision is, the remaining decisions must be optimal for the state that first decision leads to.*

That sentence is literally the equation.

### 2.1 General Form (deterministic, the one used in coding interviews)

$$
\boxed{V(s) = \underset{a \in A(s)}{\text{opt}} \Big[ r(s, a) \oplus V\big(f(s, a)\big) \Big]}
\qquad\text{with}\qquad V(s_{\text{base}}) = \text{known}
$$

### 2.2 What Each Term Means

| Term | Name | Plain English | Question to ask yourself |
|---|---|---|---|
| $s$ | **State** | A snapshot of "where am I in the problem". Usually indices / remaining capacity / flags. | *What is the minimum info I need to finish the problem from here?* |
| $V(s)$ | **Value function** (`dp[s]`) | The **best answer for the sub-problem** described by $s$. | *In one sentence, what does `dp[i]` mean?* (Write it down! Most bugs come from a fuzzy definition.) |
| $A(s)$ | **Action / choice set** | The legal decisions available at $s$. | *What can I do right now?* (take/skip, which coin, which edge, match/delete/insert…) |
| $r(s, a)$ | **Immediate reward / cost** | What you gain or pay **for this one step only**. | *How much does this single decision contribute?* (often `+1`, `+value[i]`, `+weight`, or `0`) |
| $f(s, a)$ | **Transition** (next state, $s'$) | The smaller sub-problem you land in after making choice $a$. | *After this choice, what problem is left?* |
| $V(f(s,a))$ | **Value-to-go** / "future" | The best you can do on the **rest**. You *trust* that it's already solved (that's the recursion leap of faith). | *Has this been computed before I need it?* |
| $\oplus$ | **Combine** | How the step's contribution joins the rest. Usually `+`; sometimes `×` or nothing. | |
| $\text{opt}$ | **Aggregator** | How you pick among choices: `max`, `min`, `sum` (counting), `or` (feasibility). | *Am I maximizing, minimizing, counting, or checking possibility?* |
| $V(s_{\text{base}})$ | **Base case / boundary** | Answers to the tiniest sub-problems, known without recursion. Use $\pm\infty$ for "impossible". | *What's the answer for empty / zero / first element?* |
| Final answer | **Goal state** | Which $V(\cdot)$ you return. Usually `dp[n]` but sometimes `max(dp)`. | *Is the answer one cell or the best over all cells?* |

### 2.3 The Aggregator Changes the Problem Type

The same skeleton covers four families just by swapping $\text{opt}$ and $\oplus$:

| Problem type | $\text{opt}$ | $\oplus$ | "Impossible" value | Example |
|---|---|---|---|---|
| Maximize | `max` | `+` | $-\infty$ | House Robber, Knapsack |
| Minimize | `min` | `+` | $+\infty$ | Coin Change, Edit Distance, Shortest Path |
| Count ways | `sum` ($\Sigma$) | `×` (or nothing) | `0` | Climbing Stairs, Unique Paths |
| Feasibility | `any` (OR) | `and` | `False` | Word Break, Partition Equal Subset Sum |

### 2.4 Where It Comes From: The "Full" Bellman Equation (RL / MDP)

In reinforcement learning / control, you'll see:

$$
V(s) = \max_{a} \Big[ R(s,a) + \gamma \sum_{s'} P(s' \mid s, a)\, V(s') \Big]
$$

| Extra term | Meaning | In algorithm DP |
|---|---|---|
| $\gamma$ (discount, 0–1) | Future rewards are worth less than immediate ones | Always $\gamma = 1$, so it disappears |
| $P(s' \mid s,a)$ | Probability that action $a$ lands you in $s'$ (randomness) | Transitions are deterministic: one $s'$ with probability 1, so the sum collapses to $V(f(s,a))$ |

So interview DP is just the RL Bellman equation with **no discount and no randomness**.

### 2.5 Direction: "Value-to-go" vs "Value-so-far"

A frequent source of confusion: two equally valid ways to define the state.

* **Backward / value-to-go (classic Bellman):** `dp[i]` = best answer for the **suffix** starting at `i`. Transitions point to *larger* `i`. Answer is `dp[0]`.
* **Forward / value-so-far (most LeetCode solutions):** `dp[i]` = best answer for the **prefix** ending at / up to `i`. Transitions point to *smaller* `i`. Answer is `dp[n]`.

Both are the same idea; "the rest of the problem" is just to the right or to the left. Pick one and be consistent. The examples below mostly use the forward version because that's what you'll see in interview solutions.

---

## 3. Recipe: Turning a Problem into a Bellman Equation

1. **Define the state** in words: "`dp[i]` = the max money robbing houses `0..i`".
   * The state must be **Markov**: knowing $s$ alone is enough to solve the rest; *how* you got there must not matter. If it matters, add it to the state (e.g., a `holding` flag, an item index).
2. **List choices** at that state (usually about the *last* or *first* element).
3. **For each choice**, write the immediate reward $r$ and the next state $f$.
4. **Pick the aggregator** (`max` / `min` / `sum` / `or`).
5. **Base cases** (including impossible states with $\pm\infty$).
6. **Evaluation order** so that every $V(f(s,a))$ is computed before $V(s)$.
7. **Where's the answer?** `dp[n]`, `dp[0]`, or `max(dp)`.
8. **Optimize space** if each row depends only on the previous one or two.

---

## 4. Worked Examples: Mapping Each Term

### Math Index vs Code Index (read this first)
A state index `i` can mean one of two different things, and that decides whether `i = 0` in the equation is the same as index `0` in code:

| Kind | `i` means | `i = 0` means | `i`-th element in code | dp array size | Used by |
|---|---|---|---|---|---|
| **Element index** | position of an actual element | the **first element** `nums[0]` | `nums[i]` (same as code) | `n` | House Robber, LIS, Stock |
| **Length / count index** | "the first `i` elements" (prefix `a[:i]`) | the **empty prefix**, which is the base case | `a[i-1]` (**shifted by one**) | `n + 1` | Knapsack, LCS, Edit Distance |
| **Quantity** | a number, not a position (step #, amount, capacity) | the quantity zero | n/a, no input array is indexed by it | `max + 1` | Climbing Stairs, Coin Change, Knapsack's `c` |

* Math subscripts like $a_i$, $v_i$, $w_i$ are conventionally **1-based** ("the $i$-th item"), so in 0-based code they become `a[i-1]`, `v[i-1]`, `w[i-1]`.
* Why use the length index at all? The extra slot `dp[0]` stores the "empty" base case, so the recurrence never reads a negative index.
* **Python trap:** if the equation mentions $V(-1)$, never write `dp[-1]`. Python silently returns the **last** element instead of raising an error.

Each subsection below ends its table with an **Indexing** note.

### 4.1 Climbing Stairs (LC 70) — *Counting*
> You can climb 1 or 2 steps at a time. How many distinct ways to reach step $n$?

$$
V(i) = \sum_{k \in \{1, 2\}} V(i - k) = V(i-1) + V(i-2), \qquad V(0) = 1,\; V(1) = 1
$$

| Term | Here |
|---|---|
| $s$ | `i` = the step you're standing on |
| $V(s)$ | number of distinct ways to reach step `i` |
| $A(s)$ | "my last move was a 1-step" or "my last move was a 2-step" |
| $r(s,a)$ | none (counting; each path contributes ×1) |
| $f(s,a)$ | `i-1` or `i-2` |
| $\text{opt}$ | **sum**: different last moves give *disjoint* sets of paths, so you add them |
| Base | `V(0) = 1` (one way to stand still: the empty path), `V(1) = 1` |
| Answer | `V(n)` |

> **Indexing: same as code (quantity).** `i` is a step number, and step `0` is the ground, not the first stair. Allocate `dp = [0] * (n + 1)` so that `dp[i]` is $V(i)$, from `dp[0]` (ground) to `dp[n]` (top). There's no input array, so there's no offset.

> Why `V(0) = 1` and not 0? It's the number of ways to "do nothing", which is exactly one. If it were 0, every count would collapse to 0.

### 4.2 House Robber (LC 198) — *Maximize, take/skip*
> Houses in a row with `nums[i]` money. Can't rob two adjacent houses. Max money?

$$
V(i) = \max\Big(\underbrace{ V(i-1) }_{\text{skip house } i}, \underbrace{ \text{nums}[i] + V(i-2) }_{\text{rob house } i}\Big), \qquad V(-1) = V(-2) = 0
$$

| Term | Here |
|---|---|
| $s$ | `i` = we've considered houses `0..i` |
| $V(s)$ | max money obtainable from houses `0..i` |
| $A(s)$ | {skip `i`, rob `i`} |
| $r(s,a)$ | skip → `0`; rob → `nums[i]` |
| $f(s,a)$ | skip → `i-1`; rob → `i-2` (robbing `i` **forbids** `i-1`, so we jump over it) |
| $\text{opt}$ | `max` |
| Base | no houses → 0 |
| Answer | `V(n-1)` |

> **Indexing: same as code (element index), except for the base cases.** `i` is the 0-based house index, so `nums[i]` in the equation is `nums[i]` in code, and `i = 0` is the first house. But $V(-1)$ and $V(-2)$ are **not** real array cells (don't write `dp[-1]` in Python!). Two ways to handle them:
> * Keep two rolling variables for them (the snippet below), or
> * Shift to a **length index**: `dp[k]` = best from the first `k` houses, with `dp[0] = 0`, `dp[1] = nums[0]`, `dp[k] = max(dp[k-1], nums[k-1] + dp[k-2])`, and answer `dp[n]`. Here $V(i)$ = `dp[i+1]`.

> The transition $f$ is where the **constraint** lives. "No adjacent houses" is encoded by jumping to `i-2` instead of `i-1`.

```python
prev2, prev1 = 0, 0          # V(i-2), V(i-1)
for x in nums:
    prev2, prev1 = prev1, max(prev1, x + prev2)
return prev1
```

### 4.3 Coin Change (LC 322) — *Minimize, unbounded choices*
> Min number of coins to make `amount`. Infinite supply of each coin.

$$
V(x) = \min_{c \,\in\, \text{coins},\; c \le x} \Big[ 1 + V(x - c) \Big], \qquad V(0) = 0,\;\; V(x<0) = +\infty
$$

| Term | Here |
|---|---|
| $s$ | `x` = remaining amount to make |
| $V(s)$ | fewest coins to make exactly `x` |
| $A(s)$ | which coin to use **last** (any coin with value ≤ `x`) |
| $r(s,a)$ | `1` — this coin costs one coin |
| $f(s,a)$ | `x - c` |
| $\text{opt}$ | `min` |
| Base | `V(0) = 0`; unreachable amounts stay `∞` |
| Answer | `V(amount)` or `-1` if `∞` |

> **Indexing: same as code (quantity).** `x` is an amount of money, not a position, so `dp[x]` is $V(x)$ with `dp` of size `amount + 1`. The base case $V(x<0) = \infty$ is **never stored**; the guard `if c <= x` in the code plays that role. The coin loop `for c in coins` iterates values, so coin positions in the array don't matter.

> The `1 +` is the **immediate cost** $r$. People sometimes forget it, or put it in the wrong place; ask "what did *this* decision cost me?" → one coin.

```python
INF = float('inf')
dp = [0] + [INF] * amount
for x in range(1, amount + 1):
    for c in coins:
        if c <= x:
            dp[x] = min(dp[x], 1 + dp[x - c])
return dp[amount] if dp[amount] != INF else -1
```

### 4.4 0/1 Knapsack — *Why the state needs 2 dimensions*
> Items with weight `w[i]` and value `v[i]`, bag capacity `W`, each item used at most once.

$$
V(i, c) = \max\Big(\underbrace{V(i-1,\, c)}_{\text{skip item } i},\;\; \underbrace{v_i + V(i-1,\, c - w_i)}_{\text{take item } i,\ \text{only if } w_i \le c}\Big), \qquad V(0, c) = 0
$$

| Term | Here |
|---|---|
| $s$ | `(i, c)` = considering the first `i` items with remaining capacity `c` |
| $V(s)$ | max value using items `1..i` within capacity `c` |
| $A(s)$ | {skip item `i`, take item `i` (if it fits)} |
| $r(s,a)$ | skip → `0`; take → $v_i$ (code: `v[i-1]`) |
| $f(s,a)$ | skip → `(i-1, c)`; take → `(i-1, c - w_i)` (code: `c - w[i-1]`) |
| $\text{opt}$ | `max` |
| Base | no items → 0 value |
| Answer | `V(n, W)` |

> **Indexing: shifted by one for `i` (length index), same as code for `c` (quantity).** `i` counts how many items have been considered, so `i = 0` means **no items** (the base row), not the first item. Item $i$ in the math is item `i-1` in 0-based code. Allocate `(n + 1) × (W + 1)`.
>
> ```python
> n = len(v)
> dp = [[0] * (W + 1) for _ in range(n + 1)]    # row 0 = no items
> for i in range(1, n + 1):
>     wi, vi = w[i - 1], v[i - 1]               # math item i == code item i-1
>     for c in range(W + 1):
>         dp[i][c] = dp[i - 1][c]               # skip
>         if wi <= c:
>             dp[i][c] = max(dp[i][c], vi + dp[i - 1][c - wi])  # take
> return dp[n][W]
> ```

> **Why isn't capacity alone enough as the state?** Because "can I still use item 3?" depends on history. That violates the Markov requirement, so we add `i` to the state. Moving to `i-1` after each decision guarantees each item is decided exactly once.
>
> **Contrast with Coin Change (unbounded):** there, after using a coin you can use it *again*, so there's no "item index" in the state.
>
> **Space-optimized loop direction:** with a 1-D array, iterate `c` **downward** for 0/1 knapsack (so `dp[c - w]` is still the *previous* row's value), and **upward** for unbounded knapsack (so you can reuse the item).

### 4.5 Longest Common Subsequence (LC 1143) — *Two-sequence DP*
> Given two strings `a` and `b`, return the length of their longest common subsequence: a sequence of characters that appears in both strings in the same order, but not necessarily contiguously. E.g., `a = "abcde"`, `b = "ace"` → `3` (`"ace"`).

$$
V(i, j) =
\begin{cases}
1 + V(i-1,\, j-1) & \text{if } a_i = b_j \\[4pt]
\max\big(V(i-1,\, j),\; V(i,\, j-1)\big) & \text{otherwise}
\end{cases}
\qquad V(0, \cdot) = V(\cdot, 0) = 0
$$

| Term | Here |
|---|---|
| $s$ | `(i, j)` = prefixes `a[:i]` and `b[:j]` |
| $V(s)$ | LCS length of those two prefixes |
| $A(s)$ | if last chars match → use the match; else → drop last char of `a` **or** drop last char of `b` |
| $r(s,a)$ | match → `1`; drop → `0` |
| $f(s,a)$ | match → `(i-1, j-1)`; drop a → `(i-1, j)`; drop b → `(i, j-1)` |
| $\text{opt}$ | `max` |
| Base | empty string → LCS 0 |
| Answer | `V(len(a), len(b))` |

> **Indexing: shifted by one (length index).** `i` and `j` are prefix **lengths**: `(i, j)` means `a[:i]` and `b[:j]`. So `i = 0` is the empty string (the base row), and the math character $a_i$ is `a[i-1]` in code. Allocate `(len(a) + 1) × (len(b) + 1)`; row 0 and column 0 are the all-zero base cases.
>
> ```python
> m, n = len(a), len(b)
> dp = [[0] * (n + 1) for _ in range(m + 1)]
> for i in range(1, m + 1):
>     for j in range(1, n + 1):
>         if a[i - 1] == b[j - 1]:              # math a_i == b_j
>             dp[i][j] = 1 + dp[i - 1][j - 1]
>         else:
>             dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
> return dp[m][n]
> ```

> Notice the **action set depends on the state** ($A(s)$): whether "match" is available depends on `a[i] == b[j]`. That's why the equation has cases.

### 4.6 Edit Distance (LC 72) — *Minimize, three actions*
> Given strings `a` and `b`, return the minimum number of single-character operations (insert, delete, or replace) needed to turn `a` into `b`. E.g., `a = "horse"`, `b = "ros"` → `3` (horse → rorse → rose → ros).

$$
V(i, j) = \min
\begin{cases}
1 + V(i-1,\, j) & \text{delete } a_i \\
1 + V(i,\, j-1) & \text{insert } b_j \\
[a_i \ne b_j] + V(i-1,\, j-1) & \text{replace (free if equal)}
\end{cases}
\qquad V(i, 0) = i,\;\; V(0, j) = j
$$

| Term | Here |
|---|---|
| $s$ | `(i, j)` = turn `a[:i]` into `b[:j]` |
| $V(s)$ | min edits to do that |
| $A(s)$ | {delete, insert, replace/keep} |
| $r(s,a)$ | `1` per edit; `0` if chars already equal (Iverson bracket $[a_i \ne b_j]$ is 1 if true, else 0) |
| $f(s,a)$ | `(i-1,j)`, `(i,j-1)`, `(i-1,j-1)` |
| $\text{opt}$ | `min` |
| Base | turning a string into empty = delete all (`i`); empty into a string = insert all (`j`) |
| Answer | `V(len(a), len(b))` |

> **Indexing: shifted by one (length index), same as LCS.** `(i, j)` are prefix lengths, $a_i$ is `a[i-1]`, and the replace cost is `int(a[i-1] != b[j-1])`. The base cases live in the extra row and column: `dp[i][0] = i` and `dp[0][j] = j`. That's exactly why `V(i, 0) = i` makes sense: turning a length-`i` prefix into the empty string takes `i` deletes.

> Base cases here are **not** zero. Always ask: "what's the true answer for the smallest version?"

### 4.7 Longest Increasing Subsequence (LC 300) — *Answer is not one cell*
> Given an integer array `a`, return the length of the longest strictly increasing subsequence (elements kept in original order, not necessarily contiguous). E.g., `[10, 9, 2, 5, 3, 7, 101, 18]` → `4` (`[2, 3, 7, 101]`).

$$
V(i) = 1 + \max_{\,j < i,\; a_j < a_i} V(j) \quad (\text{max over empty set} = 0), \qquad \text{Answer} = \max_i V(i)
$$

| Term | Here |
|---|---|
| $s$ | `i` |
| $V(s)$ | length of the longest increasing subsequence **ending exactly at** `i` |
| $A(s)$ | which earlier index `j` to attach to (must have `a[j] < a[i]`), or start fresh |
| $r(s,a)$ | `1` (the element `a[i]` itself) |
| $f(s,a)$ | `j` |
| $\text{opt}$ | `max` |
| Base | every element alone is length 1 |
| Answer | **`max(dp)`**, not `dp[n-1]`, because the best subsequence can end anywhere |

> **Indexing: same as code (element index).** `i` is the 0-based position of a real element, so $a_i$ = `a[i]` and $V(i)$ = `dp[i]`, with `dp = [1] * n`. `i = 0` is the first element, and its value `1` is a real answer, not an "empty" base case. There's no extra slot because "ending exactly at `i`" requires an actual element at `i`.

> The phrase "**ending exactly at** `i`" is what makes the transition possible (we need to know the last element to check `a[j] < a[i]`). It's also why the answer needs a `max` over all states.

### 4.8 Shortest Path / Bellman–Ford — *The original Bellman equation*
> Given a directed graph with weighted edges `w(u, v)` (weights may be negative, but no negative cycles) and a `source` node, find the minimum total weight of a path from `source` to every other node.

$$
d(v) = \min_{(u,\,v) \in E} \Big[\, d(u) + w(u, v) \,\Big], \qquad d(\text{source}) = 0
$$

| Term | Here |
|---|---|
| $s$ | node `v` |
| $V(s)$ | `d(v)`: shortest distance from source to `v` |
| $A(s)$ | which incoming edge `(u, v)` you arrived by |
| $r(s,a)$ | edge weight `w(u, v)` |
| $f(s,a)$ | `u` (the previous node) |
| $\text{opt}$ | `min` |
| Base | `d(source) = 0`, others start at `∞` |
| Answer | `d(target)` |

> **Indexing: same as code (node id).** The state is a node label, not a position in a sequence, so `dist[v]` is $d(v)$ with no shift. The only thing to watch is the input format: if nodes are labelled `1..n`, allocate `n + 1` slots and ignore `dist[0]`. Don't subtract 1 from the labels inside the recurrence.

> On a graph with cycles there's no obvious "smaller first" order, so Bellman–Ford just **relaxes all edges $|V|-1$ times** until the equation holds everywhere (that's *value iteration* in RL terms). Dijkstra solves the same equation faster when weights are non-negative by processing nodes in order of distance.

### 4.9 Stock with Cooldown (LC 309) — *State machine: multiple value functions*
> Buy/sell a stock; after selling you must rest one day.

When the history matters (am I holding a stock? did I just sell?), split $V$ into one function per "mode":

$$
\begin{aligned}
\text{hold}(i) &= \max\big(\text{hold}(i-1),\;\; \text{rest}(i-1) - p_i\big) \\
\text{sold}(i) &= \text{hold}(i-1) + p_i \\
\text{rest}(i) &= \max\big(\text{rest}(i-1),\;\; \text{sold}(i-1)\big)
\end{aligned}
$$

Base: `hold(0) = -p[0]`, `sold(0) = -∞`, `rest(0) = 0`. Answer: `max(sold(n-1), rest(n-1))`.

| Term | Here |
|---|---|
| $s$ | `(i, mode)` where mode ∈ {hold, sold, rest} |
| $V(s)$ | max profit at end of day `i` while in that mode |
| $A(s)$ | depends on mode: from rest → buy or wait; from hold → sell or wait; sold → must rest |
| $r(s,a)$ | buy → `-p[i]`; sell → `+p[i]`; wait → `0` |
| $f(s,a)$ | previous day's mode that legally leads here |
| $\text{opt}$ | `max` |

> **Indexing: same as code (element index).** `i` is the 0-based day, so $p_i$ = `prices[i]` and `i = 0` is the **first trading day**, not an "empty" state. That's why the base case `hold(0) = -prices[0]` refers to a real price. Arrays `hold`, `sold`, `rest` all have size `n`.

> A **negative** reward is normal: buying costs money now, which pays off when the future term includes a sale.

---

## 5. Cheat Sheet

Array accesses below are written as 0-based **code**. Knapsack, LCS and Edit Distance use length indices, so their `dp` has an extra row/column.

| Problem | State $s$ | $V(s)$ means | Choices | $r(s,a)$ | $f(s,a)$ | opt |
|---|---|---|---|---|---|---|
| Climbing Stairs | `i` | # ways to reach `i` | last step 1 or 2 | — | `i-1`, `i-2` | Σ |
| House Robber | `i` | max $ from `0..i` | skip / rob | `0` / `nums[i]` | `i-1` / `i-2` | max |
| Coin Change | `x` | min coins for `x` | last coin `c` | `1` | `x-c` | min |
| 0/1 Knapsack | `(i, c)` | max value, first `i` items, cap `c` | skip / take | `0` / `v[i-1]` | `(i-1,c)` / `(i-1,c-w[i-1])` | max |
| LCS | `(i, j)` | LCS of prefixes | match / drop a / drop b | `1` / `0` / `0` | diag / up / left | max |
| Edit Distance | `(i, j)` | min edits | del / ins / rep | `1` / `1` / `[≠]` | up / left / diag | min |
| LIS | `i` | LIS ending at `i` | previous `j` | `1` | `j` | max (answer = `max(dp)`) |
| Shortest Path | `v` | dist to `v` | incoming edge | `w(u,v)` | `u` | min |

---

## 6. Common Pitfalls

* **Fuzzy state definition.** "`dp[i]` is about index i" is not a definition. Write the full sentence, including *up to* vs *ending at*.
* **State is missing information** (not Markov). If you find yourself needing "what did I pick before?", add it to the state.
* **Forgetting the immediate reward** (`1 +`, `+ nums[i]`) or adding it twice.
* **Wrong base case.** Counting problems usually need `dp[0] = 1`; min problems need `∞` for impossible; max problems need `-∞`.
* **Wrong loop order.** In bottom-up, every `dp[f(s,a)]` must be filled before `dp[s]`.
* **0/1 vs unbounded knapsack** loop direction when space-optimizing (down vs up).
* **Returning `dp[n]` when the answer is `max(dp)`** (LIS, max subarray, longest valid parentheses).
* **Counting permutations vs combinations** (Coin Change II): putting the coin loop *outside* the amount loop counts combinations; inside counts ordered sequences.
