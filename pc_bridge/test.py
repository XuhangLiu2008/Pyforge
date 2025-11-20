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