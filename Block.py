listA = ['a','a','a']
listB = ['b','b','b','b']
listC = ['c','c','c']
listD = ['d','d','d']

list_ = [listA, listB, listC]

for target in list_:
    print(target)

list_b = listA + listB
print(list_b)

listoflists = []
a_list = []
for i in range(0,10):
    a_list.append(i)
    if len(a_list)>3:
        a_list.remove(a_list[0])
        listoflists.append((list(a_list), a_list[0]))
print(listoflists)


def funExplorer(listZ,listY):
    listN = listZ + listY
    return listN

listH = [1,2,3]
listR = funExplorer(listH,listH)
print (listR)