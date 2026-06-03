# Bolt's Journal

## CRITICAL LEARNINGS
* **Python Function Call Overhead in Recursive Loops:** In extremely hot recursive paths (like `BSPTreeTraverser._traverse`), calling a method (e.g. `self._add_sector_id()`) repeatedly introduces significant wrapper overhead. Completely inlining the logic (e.g., directly checking a boolean tracking array) and passing bound primitive methods (like `list.append`) directly as parameters eliminates Python function call wrapper overhead completely, yielding superior execution speedups (~33% reduction in execution time for synthetic traversal benchmarks).
