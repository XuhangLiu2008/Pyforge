# pcbridge Python Extension Usage

This document explains how to build and use the `pcbridge` C++ extension from Python.

## 1. Build and install

From the `pc_bridge` directory:

```bash
cd pc_bridge
pip install .
```

This compiles `test.cpp` and installs the `pcbridge` Python extension module.

Ensure your environment has `pybind11` installed.

## 2. Module contents

The `pcbridge` module exposes:

- Class `Node`: internal list node.
- Class `DoublyList`: a doubly linked list of integers.
- Three global list instances:
  - `pcbridge.list1`
  - `pcbridge.list2`
  - `pcbridge.list3`

### 2.1 `Node`

```python
node.value  # int (read/write)
node.prev   # previous Node or None (read-only)
node.next   # next Node or None (read-only)
```

Nodes are managed internally by `DoublyList`.

### 2.2 `DoublyList`

Constructor and methods:

```python
lst = pcbridge.DoublyList()           # empty list
lst = pcbridge.DoublyList(val: int)   # list with one element

lst.append(value: int)      # add at the tail
lst.prepend(value: int)     # add at the head
lst.clear()                 # remove all nodes
lst.remove(value: int)      # remove first occurrence of value
lst.remove_node(node)       # remove a specific node (unsafe if not in list)

lst.sum_forward()  # sum from head to tail
lst.sum_backward() # sum from tail to head

lst.head  # first Node in the list (read-only)
lst.tail  # last Node in the list (read-only)
lst.size  # number of elements (read-only)
```

### 2.3 Pythonic Features

`DoublyList` supports standard Python list operations:

```python
# Length
n = len(lst)

# Indexing (0-based, supports negative indices)
val = lst[0]
lst[1] = 99

# Deletion
del lst[2]

# Iteration
for value in lst:
    print(value)

# String representation
print(lst)  # Output: DoublyList([1, 2, 3])
```

## 3. Using the three global lists

Three pre-created global lists are available:

- `pcbridge.list1`
- `pcbridge.list2`
- `pcbridge.list3`

These are initialized as empty `DoublyList` instances.

## 4. Implementation Notes

- The linked lists store **integers only**.
- Memory is dynamically allocated (no fixed pool limit).
- Indexing is O(N) as it traverses the list.
- `Node` pointers (`prev`/`next`) are only valid while the list and underlying node remain allocated; do not store them across processes or expect them to be stable after heavy modifications.

## 5. Minimal quick-start

```bash
cd pc_bridge
python3 setup.py build_ext --inplace
python3 test.py
```

`test.py` demonstrates use of `list1`, `list2`, and `list3` and prints their contents.

## 6. Internal implementation details

### 6.1 Memory model and node pool

The C++ side defines a fixed-size pool of `Node` objects:

- `static const int POOL_SIZE = 1024;`
- `static Node node_pool[POOL_SIZE];`
- `static bool node_used[POOL_SIZE] = {false};`

New nodes are acquired via `alloc_node(int v)`, which linearly scans `node_used` for a free slot, marks it as used, initializes the corresponding `node_pool[i]`, and returns a pointer. Nodes are returned to the pool with `free_node(Node* n)`, which computes the index from the pointer and sets the corresponding `node_used` entry back to `false`.

All `DoublyList` instances (including `list1`, `list2`, `list3`, and any lists you create from Python) share this global pool. The maximum total number of simultaneously alive nodes across all lists is therefore `POOL_SIZE` (1024).

### 6.2 List structure and invariants

Each `DoublyList` holds two pointers:

- `head`: first `Node` in the list
- `tail`: last `Node` in the list

The list maintains classic doubly linked list invariants:

- Starting from `head` and following `next` pointers eventually reaches `tail` (or `nullptr` for a degenerate list).
- Starting from `tail` and following `prev` pointers eventually reaches `head`.
- For every node `n` in a list:
    - If `n->prev` is not `nullptr`, then `n->prev->next == n`.
    - If `n->next` is not `nullptr`, then `n->next->prev == n`.

The constructor `DoublyList(int v)` allocates a single node from the pool and sets both `head` and `tail` to point to it. `append(int v)` and `prepend(int v)` allocate new nodes and update `head`, `tail`, and neighbor links accordingly. `remove(Node* node)` re-links neighbors (or `head`/`tail` when removing at the ends) and then calls `free_node(node)` to make the slot reusable.

### 6.3 Pybind11 binding behavior

The bindings are defined in `test.cpp` using `PYBIND11_MODULE(pcbridge, m)`:

- `Node` is exposed with three read-only attributes: `value`, `prev`, `next`.
- `DoublyList` is exposed with:
    - Constructor `DoublyList(int v)`.
    - Methods `append`, `prepend`, `remove`, `sum_forward`, `sum_backward`.
    - Read-only attributes `head` and `tail`.
- Iteration is provided by binding `__iter__` to a C++ iterator range using `py::make_iterator(self.begin(), self.end())` plus `py::keep_alive<0, 1>()`. The keep-alive policy ensures the `DoublyList` Python object stays alive for as long as the iterator exists.

Three global `DoublyList` instances are defined in the C++ translation unit:

```cpp
static DoublyList list1(0);
static DoublyList list2(0);
static DoublyList list3(0);

m.attr("list1") = &list1;
m.attr("list2") = &list2;
m.attr("list3") = &list3;
```

From Python, `pcbridge.list1`, `pcbridge.list2`, and `pcbridge.list3` behave like ordinary `DoublyList` objects, but their lifetime is tied to the module (they are global statics created when the module is loaded and destroyed when the process exits).

### 6.4 Example: walking via Node pointers

In addition to iterating over integer values, you can traverse using the underlying `Node` objects through `head` and `next`:

```python
import pcbridge

lst = pcbridge.DoublyList(1)
lst.append(2)
lst.append(3)

node = lst.head
while node is not None:
        print("value:", node.value)
        node = node.next
```

Be careful when modifying the list (e.g., calling `remove`) while holding onto `Node` references: once a node is removed, its slot may be reused for another node, and the old pointer should be considered invalid.