# pcbridge Python Extension Usage

This document explains how to build and use the `pcbridge` C++ extension from Python.

## 1. Build and install

From the `pc_bridge` directory:

```bash
cd pc_bridge
python3 setup.py build_ext --inplace
```

This compiles `test.cpp` and creates the `pcbridge` Python extension module in the same directory.

Ensure your environment has the dependencies listed in `requirements.txt` (notably `pybind11`).

## 2. Module contents

The `pcbridge` module exposes:

- Class `Node`: internal list node (read-only fields).
- Class `DoublyList`: a doubly linked list of integers.
- Three global list instances:
  - `pcbridge.list1`
  - `pcbridge.list2`
  - `pcbridge.list3`

### 2.1 `Node`

```python
node.value  # int (read-only)
node.prev   # previous Node or None (read-only)
node.next   # next Node or None (read-only)
```

Nodes are managed internally by `DoublyList`; you normally do not create or free them directly.

### 2.2 `DoublyList`

Constructor and methods:

```python
lst = pcbridge.DoublyList(initial_value: int)

lst.append(value: int)      # add at the tail
lst.prepend(value: int)     # add at the head
lst.remove(node: pcbridge.Node)  # remove a specific node

lst.sum_forward()  # sum from head to tail
lst.sum_backward() # sum from tail to head

lst.head  # first Node in the list (read-only)
lst.tail  # last Node in the list (read-only)
```

`DoublyList` is iterable from head to tail, yielding integer values:

```python
for value in lst:
    print(value)
```

## 3. Using the three global lists

Three pre-created global lists are available:

- `pcbridge.list1`
- `pcbridge.list2`
- `pcbridge.list3`

These are `DoublyList` instances initialized with a single element `0`. You can operate on them like any other `DoublyList`.

Example:

```python
import pcbridge

pcbridge.list1.append(1)
pcbridge.list1.append(2)

pcbridge.list2.append(10)
pcbridge.list3.prepend(-5)

for v in pcbridge.list1:
    print("list1:", v)

for v in pcbridge.list2:
    print("list2:", v)

for v in pcbridge.list3:
    print("list3:", v)
```

All three lists share the same internal node pool. Removing nodes from one list may free capacity for others, but each list maintains its own head/tail and node links.

## 4. Notes and limitations

- The linked lists store **integers only**.
- There is a fixed internal pool of 1024 nodes shared by all lists; if the pool is exhausted, new appends/prepends will fail internally.
- `Node` pointers (`prev`/`next`) are only valid while the list and underlying node remain allocated; do not store them across processes or expect them to be stable after heavy modifications.

## 5. Minimal quick-start

```bash
cd pc_bridge
python3 setup.py build_ext --inplace
python3 test.py
```

`test.py` demonstrates use of `list1`, `list2`, and `list3` and prints their contents.