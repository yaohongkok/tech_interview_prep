# Two Pointers & Sliding Window Cheat Sheet

## 1. Two Pointers Technique

Basically, there are 2 flavors:

### i. Pointers Moving in Opposite Directions
* **Setup:** You start one pointer at the beginning (`left = 0`) and one at the end (`right = len - 1`).
* **Movement:** You move them toward each other based on a condition.
* **Best for:** Sorted arrays, reversing strings, or finding pairs.
* **Classic Problems:** *Two Sum II (Sorted)*, *Valid Palindrome*.

### ii. Slow & Fast Pointers
* **Movement:** Both pointers move in the same direction, but at different speeds.
* **Best for:** Linked List cycles or finding the middle element of a list.
* **Classic Problems:** *Linked List Cycle detection*.

---

## 2. Sliding Window Technique

There are 2 main approaches:

### I. Fixed-Size Window
* **Concept:** The distance between the left and right pointers remains constant.
* **The Logic:** As you move the window forward, you "add" the new element on the right and "subtract" the element that fell off on the left.
* **Classic Problems:** *Maximum sum of a subarray of size K*.

### II. Dynamic-Size (Variable) Window
* **Concept:** The window expands or shrinks based on constraints.
    1.  **Expand:** Move the right pointer to include elements until the condition is met (or broken).
    2.  **Shrink:** Move the left pointer to find the smallest valid window or to make the window valid again.
* **Key Insight:** The hardest part of a sliding window problem is identifying exactly when to move the left pointer.
* **Tip:** Ask yourself: *"What specific event makes my current window 'invalid'?"* As soon as that happens, start incrementing `left`.
* **Classic Problems:** *Longest Substring Without Repeating Characters*.

### Window Helpers
You often need a "helper" to keep track of what’s inside your window:
1.  **Hash Maps / Sets:** To track frequencies of characters or check for duplicates.
2.  **Running Sum / Variable:** To track the current window's total.

---

## 3. Complexity Analysis

* **Time Complexity:** Usually `O(n)`. Even though there is a nested loop (the `while` loop for shrinking), each pointer only travels the length of the array once.
* **Space Complexity:** `O(1)` if you only use pointers, or `O(k)` (where `k` is the size of the character set) if you use a Hash Map.
