#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata






u = 'abcdé'
print(ord(u[-1]))

space = ' '

def processLineFromConstToDic(line,const,dicResult):
    #hacemos un bucle de busqueda por cada elemento de la lista que ingresa
    line = line.strip()
    startPosition = line.find(const, 0)
    if startPosition >= 0:
        endPosition = line.find(space, startPosition + len(const))
        newline = line[endPosition:len(line)]
        newendPosition = newline.find(space, 0)
        object_ = line[0: endPosition + newendPosition]                                    
        if any(chr.isdigit() for chr in object_):
            if object_ in dicResult.keys():
                dicResult[object_] += 1
            else:
                dicResult[object_] = 1                   

    return dicResult

""" def processLineFromConstToDic(line,const,dicResult):
    #hacemos un bucle de busqueda por cada elemento de la lista que ingresa
    
    startPosition = line.find(const, 0)
    if startPosition >= 0:
        endPosition = len(line)
        object_ = line[startPosition: endPosition].strip()                                    
        if any(chr.isdigit() for chr in object_):
            if object_ in dicResult.keys():
                dicResult[object_] += 1
            else:
                dicResult[object_] = 1                   

    return dicResult """

dicTempVersion = {}
dicTempVersion = processLineFromConstToDic(',CtdDecimalesCalculo --28 85 ET','--',dicTempVersion)

""" listA = ['a','a','a']
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
print(listoflists) """


""" def funExplorer(listZ,listY):
    listN = listZ + listY
    return listN """

""" listH = [1,2,3]
listR = funExplorer(listH,listH)
print (listR) """


""" def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn') """
                

""" stri = 'definición  '

var = strip_accents(stri)
print(var) """


