# Performance Benchmark

This document compares the performance of different graph backends and shortest-path algorithms used in the library.

## Benchmark Setup

- Number of routing queries: **1000**
- Graph dataset: A random connection of different locations worldwide
  - 1000 relations with origin and destination
  - Basic request
- Machine:
  - CPU: Intel i5 dual core 2,7 GHz
  - RAM: 16GB
- Python version: 3.11
- Benchmark mode: sequential execution
-  *Below result is the average of 3 runs*

---

## Tested Configurations

| Backend    | Algorithm | Time (1000 queries) | Avg/query |
|------------|------------|----------------------|------------|
| NetworkX   | Dijkstra   | 33.0 sec             | 33 ms      |
| NetworkX   | A*         | 15.0 sec             | 15 ms      |
| igraph     | Dijkstra   | 8.5 sec              | 8.5 ms     |

---

## Performance Comparison

### Relative Speedup

Using NetworkX Dijkstra as baseline:

| Configuration        | Speedup |
|----------------------|----------|
| NetworkX Dijkstra    | 1x       |
| NetworkX A*          | 2.2x faster |
| igraph Dijkstra      | 3.9x faster |

---

## Chart

```text
Execution Time (lower is better)

NetworkX Dijkstra  | #############################  33s
NetworkX A*        | ###############                15s
igraph Dijkstra    | ########                       8.5s
```

---

## Why igraph is faster

### NetworkX
- Pure Python implementation
- Easier to debug
- More flexible API
- Slower for large graph traversal workloads

### A*
- Faster than Dijkstra when a good heuristic exists
- Reduces explored nodes
- Performance depends on heuristic quality
- Not available in igraph

### igraph
- Core implementation written in C
- Much lower overhead
- Better memory efficiency
- Ideal for large-scale shortest path computations

---

## Recommendation

Use:

- **NetworkX** → for prototyping/debugging
- **NetworkX A*** → when geographic heuristics exist
- **igraph** → for production workloads with high query volume

For workloads above ~10,000 routing requests, `igraph` is strongly recommended.

---

## Example Benchmark Script

```python
import time
import searoute as sr

def benchmark(func, cases, *args, **kwargs):
    start = time.time()

    for source, target in cases:
        func(source, target, *args, **kwargs)

    return time.time() - start


print("NetworkX Dijkstra:", benchmark(sr.searoute, test_cases))
print("NetworkX A*:", benchmark(sr.searoute, test_cases, algorithm = "astar"))
print("igraph Dijkstra:", benchmark(sr.searoute, test_cases, backend = "igrpah"))
```
