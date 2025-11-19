import pcbridge

lst = pcbridge.DoublyList(10)

lst.append(20)
lst.append(30)
lst.prepend(5)

for value in lst:
    print(value)