# SQL Interview Preparation Guide

A comprehensive reference covering core SQL concepts and commonly asked interview questions with detailed answers.

---

## Part 1: Core SQL Concepts

### 1. Data Definition Language (DDL)

DDL statements define and modify the structure of database objects.

- `CREATE` — creates a new table, index, view, or database
- `ALTER` — modifies an existing database object (add/drop columns, rename, etc.)
- `DROP` — permanently removes a database object
- `TRUNCATE` — removes all rows from a table without logging individual row deletions

```sql
CREATE TABLE employees (
    id        INT PRIMARY KEY AUTO_INCREMENT,
    name      VARCHAR(100) NOT NULL,
    dept_id   INT,
    salary    DECIMAL(10, 2),
    hire_date DATE
);
```

---

### 2. Data Manipulation Language (DML)

DML statements read and modify data.

| Statement  | Purpose                                      |
|------------|----------------------------------------------|
| `SELECT`   | Query and retrieve rows                      |
| `INSERT`   | Add new rows                                 |
| `UPDATE`   | Modify existing rows                         |
| `DELETE`   | Remove specific rows                         |

---

### 3. Filtering and Sorting

```sql
SELECT name, salary
FROM   employees
WHERE  salary > 50000
  AND  dept_id IN (1, 3, 5)
ORDER BY salary DESC
LIMIT 10;
```

Key clauses:

- `WHERE` — filters rows before aggregation
- `HAVING` — filters groups after `GROUP BY`
- `ORDER BY` — sorts the result set (ASC / DESC)
- `LIMIT` / `TOP` / `FETCH FIRST` — restricts the number of rows returned

---

### 4. Aggregate Functions

Aggregate functions compute a single value from a set of rows.

| Function    | Description                            |
|-------------|----------------------------------------|
| `COUNT()`   | Number of non-NULL values              |
| `SUM()`     | Total of a numeric column              |
| `AVG()`     | Arithmetic mean                        |
| `MIN()`     | Smallest value                         |
| `MAX()`     | Largest value                          |

```sql
SELECT dept_id,
       COUNT(*)        AS headcount,
       AVG(salary)     AS avg_salary,
       MAX(salary)     AS top_salary
FROM   employees
GROUP BY dept_id
HAVING COUNT(*) > 5;
```

---

### 5. JOINs

JOINs combine rows from two or more tables based on a related column.

```
Table A   Table B
  ┌───┐     ┌───┐
  │   │─────│   │   INNER JOIN  — rows matched in both
  │   │     │   │   LEFT JOIN   — all of A + matched B
  └───┘     └───┘   RIGHT JOIN  — matched A + all of B
                    FULL JOIN   — all rows from both
```

```sql
-- INNER JOIN: only employees with a matching department
SELECT e.name, d.dept_name
FROM   employees e
INNER JOIN departments d ON e.dept_id = d.id;

-- LEFT JOIN: all employees, even those without a department
SELECT e.name, d.dept_name
FROM   employees e
LEFT JOIN departments d ON e.dept_id = d.id;
```

**CROSS JOIN** produces a Cartesian product (every row in A paired with every row in B).  
**SELF JOIN** joins a table to itself, useful for hierarchical data (e.g., employee → manager).

---

### 6. Subqueries

A subquery is a query nested inside another query.

```sql
-- Scalar subquery: returns a single value
SELECT name
FROM   employees
WHERE  salary > (SELECT AVG(salary) FROM employees);

-- Correlated subquery: references the outer query
SELECT e.name
FROM   employees e
WHERE  salary = (
    SELECT MAX(salary)
    FROM   employees
    WHERE  dept_id = e.dept_id
);
```

---

### 7. Window Functions

Window functions perform calculations across a set of rows related to the current row without collapsing rows like `GROUP BY` does.

```sql
SELECT name,
       dept_id,
       salary,
       RANK()        OVER (PARTITION BY dept_id ORDER BY salary DESC) AS dept_rank,
       ROW_NUMBER()  OVER (ORDER BY hire_date)                        AS row_num,
       LAG(salary)   OVER (PARTITION BY dept_id ORDER BY hire_date)   AS prev_salary,
       SUM(salary)   OVER (PARTITION BY dept_id)                      AS dept_total
FROM   employees;
```

Common window functions:

| Function              | Use case                                            |
|-----------------------|-----------------------------------------------------|
| `ROW_NUMBER()`        | Unique sequential number per partition              |
| `RANK()`              | Rank with gaps for ties                             |
| `DENSE_RANK()`        | Rank without gaps for ties                          |
| `LEAD()` / `LAG()`   | Access next / previous row value                    |
| `NTILE(n)`            | Divide rows into n equal buckets                    |
| `SUM() OVER ()`       | Running or partitioned totals                       |

---

### 8. Common Table Expressions (CTEs)

CTEs improve readability and allow recursive queries.

```sql
-- Non-recursive CTE
WITH high_earners AS (
    SELECT id, name, salary
    FROM   employees
    WHERE  salary > 80000
)
SELECT *
FROM   high_earners
ORDER BY salary DESC;

-- Recursive CTE (org chart traversal)
WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 0 AS depth
    FROM   employees
    WHERE  manager_id IS NULL       -- root node

    UNION ALL

    SELECT e.id, e.name, e.manager_id, ot.depth + 1
    FROM   employees e
    JOIN   org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree;
```

---

### 9. Indexes

Indexes speed up reads at the cost of slightly slower writes and additional storage.

- **B-Tree index** — default type; efficient for equality, range, and sort operations
- **Hash index** — fast equality lookups; does not support ranges
- **Composite index** — index on multiple columns; column order matters
- **Covering index** — index that includes all columns needed by a query (avoids table lookup)

```sql
CREATE INDEX idx_dept_salary ON employees (dept_id, salary);
```

> **Interview tip:** Know when indexes help (high-cardinality columns, frequent WHERE/JOIN/ORDER BY) and when they hurt (low-cardinality columns, write-heavy tables).

---

### 10. Transactions and ACID Properties

| Property      | Meaning                                                         |
|---------------|-----------------------------------------------------------------|
| **Atomicity** | All operations succeed or all are rolled back                   |
| **Consistency** | Data moves from one valid state to another                    |
| **Isolation** | Concurrent transactions don't interfere with each other         |
| **Durability** | Committed changes survive system failures                      |

```sql
BEGIN;
    UPDATE accounts SET balance = balance - 500 WHERE id = 1;
    UPDATE accounts SET balance = balance + 500 WHERE id = 2;
COMMIT;  -- or ROLLBACK on error
```

**Isolation levels** (weakest → strongest):
`READ UNCOMMITTED` → `READ COMMITTED` → `REPEATABLE READ` → `SERIALIZABLE`

---

### 11. Keys and Constraints

| Constraint      | Purpose                                                           |
|-----------------|-------------------------------------------------------------------|
| `PRIMARY KEY`   | Uniquely identifies each row; implicitly NOT NULL + UNIQUE        |
| `FOREIGN KEY`   | Enforces referential integrity between tables                     |
| `UNIQUE`        | Ensures all values in a column (or column set) are distinct       |
| `NOT NULL`      | Prevents NULL values                                              |
| `CHECK`         | Validates data against a boolean expression                       |
| `DEFAULT`       | Supplies a value when none is provided                            |

---

### 12. Views

A view is a stored query that acts like a virtual table.

```sql
CREATE VIEW v_dept_summary AS
SELECT d.dept_name,
       COUNT(e.id)   AS headcount,
       AVG(e.salary) AS avg_salary
FROM   departments d
LEFT JOIN employees e ON d.id = e.dept_id
GROUP BY d.dept_name;
```

- **Regular views** — always reflect current data; no data is stored
- **Materialized views** — result is cached on disk; must be refreshed

---

## Part 2: Popular SQL Interview Questions & Answers

---

### Q1. What is the difference between `DELETE`, `TRUNCATE`, and `DROP`?

| Command    | Removes         | WHERE clause? | Rollback? | Resets auto-increment? | Logs individual rows? |
|------------|-----------------|---------------|-----------|------------------------|-----------------------|
| `DELETE`   | Specific rows   | ✅            | ✅        | ❌                     | ✅                    |
| `TRUNCATE` | All rows        | ❌            | ❌ (most) | ✅                     | ❌                    |
| `DROP`     | Entire table    | ❌            | ❌        | N/A                    | ❌                    |

Use `DELETE` when you need conditional removal or rollback capability. Use `TRUNCATE` for a fast reset of a table. Use `DROP` to remove the table entirely.

---

### Q2. What is the difference between `WHERE` and `HAVING`?

- `WHERE` filters **individual rows** before any grouping occurs.
- `HAVING` filters **grouped results** after `GROUP BY` has been applied.

```sql
-- WHERE filters rows; HAVING filters groups
SELECT dept_id, AVG(salary) AS avg_salary
FROM   employees
WHERE  hire_date >= '2020-01-01'    -- applied before grouping
GROUP BY dept_id
HAVING AVG(salary) > 60000;        -- applied after grouping
```

---

### Q3. Find the second-highest salary.

```sql
-- Method 1: Using OFFSET
SELECT DISTINCT salary
FROM   employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Method 2: Subquery
SELECT MAX(salary)
FROM   employees
WHERE  salary < (SELECT MAX(salary) FROM employees);

-- Method 3: DENSE_RANK (generalises to Nth highest)
SELECT salary
FROM (
    SELECT salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM   employees
) ranked
WHERE rnk = 2
LIMIT 1;
```

---

### Q4. Find duplicate rows in a table.

```sql
-- Find emails that appear more than once
SELECT email, COUNT(*) AS occurrences
FROM   users
GROUP BY email
HAVING COUNT(*) > 1;

-- Return all columns for the duplicate rows
SELECT *
FROM   users
WHERE  email IN (
    SELECT email
    FROM   users
    GROUP BY email
    HAVING COUNT(*) > 1
);
```

---

### Q5. What are the different types of JOINs?

| JOIN Type    | Returns                                                              |
|--------------|----------------------------------------------------------------------|
| `INNER JOIN` | Only rows with matching values in **both** tables                    |
| `LEFT JOIN`  | All rows from the **left** table; NULLs for unmatched right rows     |
| `RIGHT JOIN` | All rows from the **right** table; NULLs for unmatched left rows     |
| `FULL JOIN`  | All rows from **both** tables; NULLs where no match exists           |
| `CROSS JOIN` | Every combination of rows from both tables (Cartesian product)       |
| `SELF JOIN`  | Joins a table to itself; useful for hierarchies or comparisons       |

---

### Q6. Retrieve employees who earn more than their department's average salary.

```sql
SELECT e.name, e.salary, e.dept_id
FROM   employees e
JOIN (
    SELECT dept_id, AVG(salary) AS avg_sal
    FROM   employees
    GROUP BY dept_id
) dept_avg ON e.dept_id = dept_avg.dept_id
WHERE  e.salary > dept_avg.avg_sal;
```

---

### Q7. What is a self join? Give an example.

A self join joins a table to itself. It is commonly used to compare rows within the same table or navigate hierarchies.

```sql
-- List each employee alongside their manager's name
SELECT e.name   AS employee,
       m.name   AS manager
FROM   employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

---

### Q8. Find customers who have never placed an order.

```sql
-- Method 1: LEFT JOIN + NULL check
SELECT c.id, c.name
FROM   customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE  o.id IS NULL;

-- Method 2: NOT EXISTS
SELECT id, name
FROM   customers c
WHERE  NOT EXISTS (
    SELECT 1 FROM orders WHERE customer_id = c.id
);

-- Method 3: NOT IN (avoid if orders.customer_id can be NULL)
SELECT id, name
FROM   customers
WHERE  id NOT IN (SELECT customer_id FROM orders);
```

---

### Q9. What is the difference between `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()`?

Given salaries: 90k, 80k, 80k, 70k

| Function       | Row 1 | Row 2 | Row 3 | Row 4 |
|----------------|-------|-------|-------|-------|
| `ROW_NUMBER()` | 1     | 2     | 3     | 4     |
| `RANK()`       | 1     | 2     | 2     | 4     |
| `DENSE_RANK()` | 1     | 2     | 2     | 3     |

- `ROW_NUMBER()` — always unique; ties broken arbitrarily
- `RANK()` — ties share a rank; next rank skips numbers
- `DENSE_RANK()` — ties share a rank; next rank is consecutive

---

### Q10. Write a query to find the running total of sales by date.

```sql
SELECT order_date,
       daily_revenue,
       SUM(daily_revenue) OVER (ORDER BY order_date
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                               ) AS running_total
FROM (
    SELECT order_date, SUM(amount) AS daily_revenue
    FROM   orders
    GROUP BY order_date
) daily;
```

---

### Q11. What is the difference between a clustered and non-clustered index?

| Feature              | Clustered Index                              | Non-Clustered Index                           |
|----------------------|----------------------------------------------|-----------------------------------------------|
| Storage              | Table rows stored in index order on disk     | Separate structure that points to row data    |
| Count per table      | Only **one** (the physical sort order)       | Many allowed                                  |
| Speed (exact lookup) | Very fast — data is right there              | Slightly slower — follows pointer to row      |
| Default in SQL Server| `PRIMARY KEY` creates one automatically      | Created explicitly with `CREATE INDEX`        |

---

### Q12. How would you delete duplicate rows while keeping one?

```sql
-- Keep the row with the lowest id for each email
DELETE FROM users
WHERE id NOT IN (
    SELECT MIN(id)
    FROM   users
    GROUP BY email
);

-- PostgreSQL / modern SQL: using CTE + ROW_NUMBER
WITH duplicates AS (
    SELECT id,
           ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
    FROM   users
)
DELETE FROM users
WHERE id IN (SELECT id FROM duplicates WHERE rn > 1);
```

---

### Q13. Explain `COALESCE` and `NULLIF`.

```sql
-- COALESCE returns the first non-NULL argument
SELECT COALESCE(phone, mobile, 'N/A') AS contact FROM users;

-- NULLIF returns NULL if both arguments are equal (avoids divide-by-zero)
SELECT total_sales / NULLIF(num_transactions, 0) AS avg_sale FROM summary;
```

---

### Q14. What is query execution order in SQL?

SQL clauses are evaluated in this order (not the order they are written):

```
1. FROM / JOIN      — identify source tables and join them
2. WHERE            — filter individual rows
3. GROUP BY         — group the filtered rows
4. HAVING           — filter groups
5. SELECT           — compute output columns / aliases
6. DISTINCT         — remove duplicate result rows
7. ORDER BY         — sort the result
8. LIMIT / OFFSET   — restrict rows returned
```

> **Interview tip:** This is why you cannot use a `SELECT` alias in a `WHERE` clause — `WHERE` is evaluated before `SELECT`.

---

### Q15. What is normalization? Explain 1NF, 2NF, and 3NF.

**Normalization** organises a database to reduce redundancy and improve data integrity.

| Normal Form | Rule                                                                                          |
|-------------|-----------------------------------------------------------------------------------------------|
| **1NF**     | Each column holds atomic (indivisible) values; no repeating groups                            |
| **2NF**     | Meets 1NF + every non-key column is fully dependent on the **entire** primary key             |
| **3NF**     | Meets 2NF + no non-key column is transitively dependent on another non-key column             |

**Denormalization** intentionally introduces redundancy for read performance (common in data warehouses and analytics).

---

### Q16. Pivot rows into columns.

```sql
-- Monthly sales per product using conditional aggregation
SELECT product_id,
       SUM(CASE WHEN MONTH(order_date) = 1 THEN amount ELSE 0 END) AS jan,
       SUM(CASE WHEN MONTH(order_date) = 2 THEN amount ELSE 0 END) AS feb,
       SUM(CASE WHEN MONTH(order_date) = 3 THEN amount ELSE 0 END) AS mar
FROM   orders
GROUP BY product_id;
```

---

### Q17. How do you optimise a slow query?

1. **EXPLAIN / EXPLAIN ANALYZE** — inspect the execution plan to find table scans or nested loops
2. **Add indexes** on columns used in `WHERE`, `JOIN ON`, `ORDER BY`, or `GROUP BY`
3. **Use covering indexes** to avoid returning to the base table
4. **Rewrite correlated subqueries** as JOINs or CTEs
5. **Avoid `SELECT *`** — retrieve only the columns you need
6. **Filter early** — push `WHERE` conditions as close to the data source as possible
7. **Partition large tables** to reduce scan size
8. **Update statistics** so the query planner makes accurate cost estimates
9. **Avoid functions on indexed columns** in `WHERE` — they prevent index usage

```sql
-- Bad: function on indexed column disables the index
WHERE YEAR(hire_date) = 2022

-- Good: range condition uses the index
WHERE hire_date BETWEEN '2022-01-01' AND '2022-12-31'
```

---

*Good luck with your interview!*