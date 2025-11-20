import pcbridge

print("--- List 1 Operations ---")
# Append and Prepend
pcbridge.list1.append(1)
pcbridge.list1.append(2)
pcbridge.list1.prepend(0)
print(f"List 1: {pcbridge.list1}")

# Length
print(f"Length of list1: {len(pcbridge.list1)}")

# Indexing
print(f"First element: {pcbridge.list1[0]}")
print(f"Last element: {pcbridge.list1[-1]}")

# Modification
pcbridge.list1[1] = 100
print(f"Modified list1: {pcbridge.list1}")

# Deletion
del pcbridge.list1[1]
pcbridge.list1.remove(0) # Remove value 0
print(f"After deletion: {pcbridge.list1}")

# Iteration
print("Iterating list1:")
for v in pcbridge.list1:
    print(v)

print("\n--- List 2 & 3 ---")
pcbridge.list2.append(10)
pcbridge.list3.prepend(-5)
print(f"List 2: {pcbridge.list2}")
print(f"List 3: {pcbridge.list3}")