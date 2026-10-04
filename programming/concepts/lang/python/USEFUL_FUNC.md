# Useful Python Functions for Interviews

## Strings

```python
s.split(",")            # -> list; s.split() splits on any whitespace
",".join(words)         # list of str -> str
s.strip()               # also lstrip / rstrip
s[::-1]                 # reverse
s.isalnum(), s.isdigit(), s.isalpha()
s.lower(), s.upper()
s.find("x")             # index or -1 (s.index raises ValueError)
s.startswith("ab"), s.endswith("yz")
ord("a"), chr(97)       # char <-> int
ord(c) - ord("a")       # letter -> 0..25
f"{x:.2f}", f"{n:05d}", f"{n:b}"   # 2dp, zero-pad, binary
```

## Lists

```python
a.append(x); a.pop(); a.pop(0)      # pop(0) is O(n) -> use deque
a.insert(i, x); a.remove(x)         # both O(n)
a[::-1], a[i:j], a[-k:]             # slices copy
a.sort(key=lambda x: (-x[1], x[0])) # in place; desc by [1], asc by [0]
sorted(a, reverse=True)             # returns new list
[[0] * cols for _ in range(rows)]   # 2D grid (NOT [[0]*c]*r)
[x for x in a if x > 0]             # filter
sum(a), min(a), max(a), max(a, key=len)
max(a, default=0)                   # safe on empty
```

## Iteration helpers

```python
for i, x in enumerate(a, start=1): ...
for x, y in zip(a, b): ...
for x, y in zip(a, a[1:]): ...      # adjacent pairs
for i in range(n - 1, -1, -1): ...  # reverse index
any(x < 0 for x in a), all(...)
list(map(int, "1 2 3".split()))
rows = list(zip(*matrix))           # transpose
```

## Dict / Set

```python
d.get(k, 0)
d.setdefault(k, []).append(v)
for k, v in d.items(): ...
sorted(d.items(), key=lambda kv: kv[1], reverse=True)
max(d, key=d.get)                   # key with largest value
d.pop(k, None)                      # delete without KeyError

s.add(x); s.discard(x)              # discard never raises
a & b, a | b, a - b, a ^ b          # intersect, union, diff, symdiff
seen = set(); frozenset(s)          # frozenset is hashable
```

## collections

```python
from collections import Counter, defaultdict, deque, OrderedDict

c = Counter(a)
c.most_common(k)                    # [(item, count), ...]
c1 == c2                            # anagram check
c1 - c2                             # keeps positive counts only

g = defaultdict(list); g[u].append(v)
cnt = defaultdict(int); cnt[x] += 1

q = deque([start])                  # O(1) both ends
q.append(x); q.appendleft(x); q.pop(); q.popleft()
deque(maxlen=k)                     # sliding window of last k

od = OrderedDict()                  # LRU cache
od.move_to_end(k); od.popitem(last=False)
```

## heapq (min-heap)

```python
import heapq

heapq.heapify(a)                    # O(n), in place
heapq.heappush(h, x); heapq.heappop(h); h[0]   # peek
heapq.heappush(h, -x)               # max-heap: negate
heapq.heappush(h, (dist, node))     # tuples compare by first item
heapq.nlargest(k, a); heapq.nsmallest(k, a, key=f)
```

## bisect (sorted lists)

```python
import bisect

bisect.bisect_left(a, x)    # first index with a[i] >= x
bisect.bisect_right(a, x)   # first index with a[i] >  x
bisect.insort(a, x)         # insert keeping order, O(n)
```

## itertools / functools

```python
from itertools import permutations, combinations, product, accumulate, groupby
from functools import lru_cache, reduce, cmp_to_key

permutations(a, 2); combinations(a, 2); product("01", repeat=3)
list(accumulate(a))                 # prefix sums
[(k, len(list(g))) for k, g in groupby("aaabb")]   # run-length

@lru_cache(maxsize=None)            # memoize; args must be hashable
def dp(i, j): ...

sorted(a, key=cmp_to_key(lambda x, y: -1 if x + y > y + x else 1))
```

## Math / numbers

```python
float("inf"), float("-inf")
a // b, a % b, divmod(a, b)         # // floors toward -inf
int(a / b)                          # truncate toward zero
abs(x), pow(b, e, mod), round(x, 2)
import math
math.gcd(a, b), math.lcm(a, b), math.isqrt(n), math.ceil(x)
int("101", 2), bin(5), hex(255)
x & 1, x >> 1, x << 1, x ^ y, x & (x - 1)   # last one clears lowest set bit
bin(x).count("1")                   # popcount
```

## Common patterns

```python
# BFS on a grid
q, seen = deque([(r0, c0, 0)]), {(r0, c0)}
while q:
    r, c, d = q.popleft()
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in seen:
            seen.add((nr, nc)); q.append((nr, nc, d + 1))

# Binary search
lo, hi = 0, len(a) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if a[mid] == target: return mid
    if a[mid] < target: lo = mid + 1
    else: hi = mid - 1

# Sliding window
left = 0
for right, x in enumerate(a):
    window[x] += 1
    while invalid(window):
        window[a[left]] -= 1; left += 1
    best = max(best, right - left + 1)

# Dijkstra
dist, h = {src: 0}, [(0, src)]
while h:
    d, u = heapq.heappop(h)
    if d > dist.get(u, float("inf")): continue
    for v, w in g[u]:
        if d + w < dist.get(v, float("inf")):
            dist[v] = d + w; heapq.heappush(h, (d + w, v))
```

## Files / logs (SRE rounds)

```python
import re, sys, json
from datetime import datetime

with open(path) as f:
    for line in f:                  # streams, constant memory
        parts = line.rstrip("\n").split()

m = re.search(r"(\d+\.\d+\.\d+\.\d+).*\" (\d{3}) ", line)
if m: ip, status = m.group(1), int(m.group(2))
re.findall(r"\d+", s); re.sub(r"\s+", " ", s)

datetime.strptime("2026-10-04 12:30:00", "%Y-%m-%d %H:%M:%S")
(t2 - t1).total_seconds()
json.loads(line); json.dumps(obj, indent=2)
for line in sys.stdin: ...
```

## Gotchas

- `def f(x, acc=[])` shares `acc` across calls; use `acc=None`.
- `a.sort()` returns `None`; `sorted(a)` returns the list.
- `b = a` aliases; use `a[:]` or `copy.deepcopy(a)` for nested.
- Recursion limit is ~1000: `sys.setrecursionlimit(10**6)`.
- Don't mutate a list/dict while iterating over it; iterate a copy.
