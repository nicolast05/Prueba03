#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""App como herramienta de revisión de scripts consolidados para QAI"""

# Importaciones
##from tkinter import *

from tkinter import Frame
from tkinter import Menu
from tkinter import Scrollbar
from tkinter import VERTICAL
from tkinter import RIGHT
from tkinter import Y
from tkinter import Listbox
from tkinter import NONE
from tkinter import BOTH
from tkinter import messagebox
from tkinter import END
#from tkinter import Treeview
import tkinter as tk
import tkinter.filedialog as fdialog
import getpass
import os
import errno
from typing import Set
import unicodedata

# Usuario por default
user = getpass.getuser()

""" select = 'select'
workflow = 'n usp_'
function = 'ufn_'
equal = '='
join = 'join'
between = 'between'
over = 'over'
group = 'group'
coma = ',' """

# constantes para omitir busqueda
lineComment = '--'
blockCommentOpen = '/*'
blockCommentClose = '*/'
exec_ = 'exec'

# constante usada en funcion que procesa lineas
space = ' '

# constante que indica cierre de un bloque
go = 'go'

# constantes usadas en bloque de BD
use = 'use'
database = 'bdoperaciones'

# constantes usadas en bloque de Header
if_ = 'if'
exists = 'exists'
from_ = 'from'
sysobjects = 'sysobjects'
objectid_ = 'object_id'
and_ = 'and'
type_ = 'type'
drop = 'drop'
procedure = 'procedure'

# constantes usadas en bloque de Body
create = 'create'
as_ = 'as'

# constantes usadas en bloque de Foot
grant = 'grant'
execute = 'execute'
reader = '_datareader'
writer = '_datawriter'
sqlbi = '_sqlbi'

# constantes usadas en bloque de extendedproperty
addextendedproperty = 'sp_addextendedproperty'
workflow = 'workflow'
schema = 'schema'

# constantes principales de busqueda
usp = 'usp_'

# constantes en subbloque contenido en descripcion
datos = 'datos'
generales = 'generales'
parametros= 'parametros'
control = 'control'
version = 'version'
historial = 'historial'
autor = 'autor'
fecha = 'fecha'
descripcion = 'descripcion'

# constantes principales de busqueda en sub bloques
arroba = '@'
dospuntos = ':'
punto = '.'

# listas para bloques
listBlockBD = [use, database]
listBlockHeader = [if_, exists, from_, sysobjects, objectid_, and_, type_, drop, procedure]
listBlockBody = [create, procedure]
listBlockFootReader = [grant, execute, reader]
listBlockFootWriter = [grant, execute, writer]
listBlockFootSQLBI = [grant, execute, sqlbi]
listBlockExtendedProperty = [addextendedproperty, workflow, schema]

# lista de constantes para identificar variables
listMainConstants = [usp]

# listas para procesar información
listConstants =  list(set(listBlockHeader + listBlockBody + listBlockFootReader + listBlockFootWriter + listBlockFootSQLBI + listBlockExtendedProperty))

# conjuntos para bloques
conjBlockBD = set(listBlockBD)
conjBlockHead = set(listBlockHeader)
conjBlockBody = set(listBlockBody)
conjBlockFootReader = set(listBlockFootReader)
conjBlockFootWriter = set(listBlockFootWriter)
conjBlockFootSQLBI = set(listBlockFootSQLBI)
conjBlockExtendedProperty = set(listBlockExtendedProperty)

# conjunto para procesar información
conjConstants = set(listConstants)

# listas para sub bloques
listSubBlockDatosGenerales = [datos, generales, descripcion]
listSubBlockParametros = [parametros]
listSubBlocControlVersion = [control, version, historial, autor, fecha, descripcion]

# lista para procesar informacion de sub blqoues
listConstantsDescriptions = list(set(listSubBlockDatosGenerales + listSubBlockParametros + listSubBlocControlVersion))

# conjuntos para sub bloques
conjSubBlockDatosGenerales = set(listSubBlockDatosGenerales)
conjSubBlockParametros = set(listSubBlockParametros)
conjSubBlockControlVersion = set(listSubBlocControlVersion)

# conjunto para procesar información en sub bloques
conjConstantsDescriptions = set(listConstantsDescriptions)

conjSubBlock = set()
conjBlock = set()

class Window(Frame):

    # Inicialización
    def __init__(self, master):
        # Parametros para mi clase Frame
        Frame.__init__(self, master)
        # Referenciamos
        self.master = master
        # GUI Here
        self.init_window()

    def init_window(self):
        # Titulo de la ventana
        self.master.title("QA Tools")
        # Instanciamos un menu
        menu = Menu(self.master)
        # Referenciamos al widget
        self.master.config(menu=menu)
        # Agreamos submenus
        file = Menu(menu, tearoff=0)
        # Agregamos submenu Open
        file.add_command(label="Open", command=self.openFile)
        # Agregamos submenu exit
        file.add_command(label="Exit", command=self.client_exit)
        # menu File
        menu.add_cascade(label="File", menu=file)
        # Scrollbar
        self.scrollbar = Scrollbar(self.master, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Lista
        self.lista = Listbox(self.master, font=("Helvetica", 8), borderwidth=0, activestyle=NONE, yscrollcommand=self.scrollbar.set)
        self.lista.pack(fill=BOTH, expand=1)
        self.scrollbar.config(command=self.lista.yview)
        

    # Funcion para cerrar la app
    def client_exit(self):

        self.master.destroy()

    # Funcion para abrir un doc sql y procesar su contenido
    def openFile(self):

        # limpiamos contenido de la lista como interfaz
        self.lista.delete(0, END)

        # obtenemos el archivo
        filepath = fdialog.askopenfilename(initialdir="C:/Users/%s" % user,
                                           filetypes=(
                                               ("SQL File", "*.sql"), ("All Files", "*.*")),
                                           title="Selección de Archivo")

        # Switch que indica si estamos en contenido de comentario en bloque -- N : no ; S : si 
        switchCommentOn = 'N'
        # Switch que indica si estamos en contenido de As -- N : no ; S : si 
        switchAsOn = 'N'
        # Flag para inicializar bloque de BD 
        flagBlockBD = ''
        # Flag para inicializar bloque estandar
        flagBlockES = ''
        # Contador de bloques
        countBlock = 1
        # Contador de lineas de contenido
        countLine = 0
        countObject = 0
        
        # Lista de Listas para procesar
        listOfLists = [listConstants,listMainConstants]

        # Diccionario temporal por bloque para procesar contenido
        dicTempBlock = {}

        dicTempVersions = {}
        dicTempDescriptionVersions = {}

        dicReport = {}
        dicTempDescriptions = {}
        listTempDescriptionParametersFull = []
        listTempDescriptionVersionsFull = []
        listTempDescriptionVersions = []
        
        listTempParameters = []
        listTempDescriptionParameters = []

        listTempVersions = []
        listTempDescriptionVersions = []

        lastVersion = ''

        try:
            # con el nombre del archivo
            with open(filepath, encoding='latin-1', mode='r', errors='ignore') as fp:
                # obtenemos la primera linea
                line = fp.readline()
                
                # mientras exista una linea
                while line:
                    # damos formato estandar a la linea reemplazando )([].'\n\t' por un espacio
                    line = line.lower().replace(')', ' ').replace('(', ' ').replace('[', ' ').replace(
                        ']', ' ').replace('.', ' ').replace("'", ' ').replace("\n", ' ').replace("\t", ' ')

                    # quitamos acentos
                    line = stripAccents(line)

                    # eliminamos espacios en blanco a la izq y der
                    strippedLine = line.strip()

                    # si la linea de contenido es vacía, leemos la siguiente linea
                    if strippedLine == "":
                        line = fp.readline()
                        countLine += 1
                        continue
                    
                    # si la linea de contenido sin espacios es igual a la constante go
                    if strippedLine == go:
                        
                        # inicializamos la variable para observaciones
                        observation = ''

                        # obtenemos el contenido del diccionario temporal por bloque y lo seteamos como conjunto
                        conjTempBlock = set(dicTempBlock.keys())

                        # validamos si el contenido de algun conjunto bloque esta dentro de nuestro contenido
                        if conjBlockBD.issubset(conjTempBlock):
                            flagBlockBD = 'BD'
                            """ print(conjTempBlock) """
                        elif conjBlockHead.issubset(conjTempBlock):
                            flagBlockES = 'Head'
                            countObject = 2
                            """ print(conjTempBlock) """
                        elif conjBlockBody.issubset(conjTempBlock):
                            flagBlockES = 'Body'
                            countObject = 1
                            """ print(conjTempBlock) """
                        elif conjBlockFootReader.issubset(conjTempBlock):
                            flagBlockES = 'FootReader'
                            countObject = 1
                            """ print(conjTempBlock) """
                        elif conjBlockFootWriter.issubset(conjTempBlock):
                            flagBlockES = 'FootWriter'
                            countObject = 1
                            """ print(conjTempBlock) """
                        elif conjBlockFootSQLBI.issubset(conjTempBlock):
                            flagBlockES = 'FootSQLBI'
                            countObject = 1
                            """ print(conjTempBlock) """
                        elif conjBlockExtendedProperty.issubset(conjTempBlock):
                            flagBlockES = 'ExtendedProperty'
                            countObject = 1
                            """ print(conjTempBlock) """
                        else:
                            # al no tener ningun conjunto bloque en nuestro contenido, indicamos observacion
                            flagBlockES = ''
                            observation = "Bloque incompleto o nulo" 
                            
                        # si el contador de bloque es 1 validaremos el bloque de BD
                        if countBlock == 1:
                            # si el flag de bloque BD es vacio agregamos a la observacion e insertamos en lista
                            if flagBlockBD == '':
                                observation += " (Bloque BD) " 
                                self.lista.insert(END, observation + 'linea: ' + str(countLine))
                                self.lista.itemconfigure(END, fg="#ff0000")
                                break
                            # caso contrario insertamos datos de bloque BD
                            else:
                                self.lista.insert(END, ' '.join(map(str, conjTempBlock)))
                                self.lista.itemconfigure(END, fg="#00aa00")
                        # si el contador de bloque mayor a 1 validaremos el bloque estandar     
                        else:
                            # si el flag de bloque ES es vacio indicamos como observacion el detalle  
                            if flagBlockES == '':
                                observation += " (Bloque Estandar) " 
                                self.lista.insert(END, observation + 'linea: ' + str(countLine))
                                self.lista.itemconfigure(END, fg="#ff0000")
                            # caso contrario a nuestro contenido le quitamos todas las constantes para quedarnos con la variable
                            else:
                                conjTempBlock = conjTempBlock - conjConstants   

                                # si tenemos 0 dato
                                if len(conjTempBlock) == 0:
                                    # insertamos la observación
                                    observation = "Procedimiento no identificado en "
                                    self.lista.insert(END, observation + flagBlockES + 'linea: ' + str(countLine))
                                    self.lista.itemconfigure(END, fg="#ff0000")
                                # si tenemos 1 dato
                                elif len(conjTempBlock) == 1:
                                    # si no existe alguna observación
                                    if observation == "":
                                        # insertamos variable de bloque ES
                                        self.lista.insert(END,' '.join(map(str, conjTempBlock)) + ' : '+ flagBlockES)
                                        self.lista.itemconfigure(END, fg="#00aa00")
                                    # aca podemos validar si ya existe un bloque con el mismo procedimiento en la lista de interfaz
                                    else:
                                        # insertamos la observación
                                        self.lista.insert(END, observation + 'linea: ' + str(countLine))
                                        self.lista.itemconfigure(END, fg="#ff0000")
                                # si tenemos 2 datos o más
                                else:
                                    observation = "Procedimientos multiples en "
                                    self.lista.insert(END, observation + flagBlockES + 'linea: ' + str(countLine))
                                    self.lista.itemconfigure(END, fg="#ff0000")

                                if flagBlockES == 'Body':
                                    conjTempDescriptionParameters = set (listTempDescriptionParameters) 
                                    conjTempParameters = set (listTempParameters)

                                    if conjTempDescriptionParameters.issubset(conjTempParameters):
                                        self.lista.insert(END,' '.join(map(str, conjTempBlock)) + ' : '+ flagBlockES + ' Confirmación variables en parámetros')
                                        self.lista.itemconfigure(END, fg="#00aa00")
                                    else:
                                        self.lista.insert(END,'Inconsistencia en parámetros')
                                        self.lista.itemconfigure(END, fg="#ff0000")

                                    listTempDescriptionVersions = list(dicTempDescriptionVersions.keys())
                                    listTempVersions = list(dicTempVersions.keys())
                                    
                                    if len(listTempDescriptionVersions) == 0:
                                        lastVersion = "vacio"
                                    elif len(listTempDescriptionVersions) == 1:
                                        lastVersion = listTempDescriptionVersions[0]
                                    else:
                                        lastVersion = listTempDescriptionVersions[len(listTempDescriptionVersions) - 1]
                                        
                                    if lastVersion != '1 0':
                                        str_match = [s for s in listTempVersions if lastVersion in s]
                                        if len(str_match) > 0:
                                            # insertamos variable de bloque ES
                                            self.lista.insert(END,' '.join(map(str, conjTempBlock)) + ' : '+ flagBlockES + ' Confirmación en versión')
                                            self.lista.itemconfigure(END, fg="#00aa00")
                                        else:
                                            self.lista.insert(END, 'No se encuentra versión')
                                            self.lista.itemconfigure(END, fg="#ff0000")    
                                    else:
                                        # insertamos variable de bloque ES
                                        self.lista.insert(END,'Confirmación versión inicial')
                                        self.lista.itemconfigure(END, fg="#00aa00")

                        # limpiamos el diccionario temporal por bloque y sumamos 1 al contador de bloques
                        dicTempBlock.clear()
                        dicTempVersions.clear()

                        listTempParameters.clear()
                        listTempDescriptionParameters.clear()

                        listTempVersions.clear()
                        listTempDescriptionVersions.clear()

                        countBlock += 1

                        lastVersion = ''
                        switchAsOn = 'N'
                    
                    else:
                        # si el flag de bloque BD es vacio y estamos en el primer bloque
                        if countBlock == 1:
                            dicTempBlock = processLineFromListToDic(line,listBlockBD,dicTempBlock)
                            # leemos siguiente linea
                            line = fp.readline()
                            countLine += 1
                            continue

                        else:

                            if switchAsOn == 'N':

                                for listTarget in listOfLists:
                                    dicTempBlock = processLineFromListToDic(line,listTarget,dicTempBlock)

                                conjBlock = set(dicTempBlock.keys())

                            ## si los elementos de body ya se encuentran en linea
                            if conjBlockBody.issubset(conjBlock) and switchAsOn == 'S':
                                
                                #busco version
                                dicTempVersions = processLineFromConstToDic_SearchVersions(line,lineComment,dicTempVersions)

                            else:
                            
                                if conjBlockBody.issubset(conjBlock):
                                    #busco parametros
                                    listTempParameters = processLineFromConstToListSuffix(line,arroba,listTempParameters)
                                    #busco version
                                    dicTempVersions = processLineFromConstToDic_SearchVersions(line,lineComment,dicTempVersions)
                                    
                                #Descripcion
                                else:
                                    #
                                    indexLineComent = line.find(lineComment, 0)
                                    indexBlockComentOpen = line.find(blockCommentOpen, 0)
                                    indexExec = strippedLine.find(exec_, 0)
                                    indexBlockAsOpen = strippedLine.find(as_, 0)

                                    if indexBlockAsOpen > 0:
                                        indexPrefixAs = strippedLine.find(' ', indexBlockAsOpen - 1, indexBlockAsOpen)
                                        indexSufixAs = strippedLine.find(' ', indexBlockAsOpen + 1, indexBlockAsOpen)

                                        if len(strippedLine) == indexPrefixAs + 3:
                                            indexSufixAs = 0

                                    elif indexBlockAsOpen == 0:
                                        indexPrefixAs = 0
                                        indexSufixAs = 0

                                    
                                    if indexLineComent >= 0:

                                        if indexLineComent != 0:
                                            #busco parametros
                                            listTempParameters = processLineFromConstToListSuffix(line,arroba,listTempParameters)
                                            
                                        #busco version
                                        dicTempVersions = processLineFromConstToDic_SearchVersions(line,lineComment,dicTempVersions)
                                        line = fp.readline()
                                        countLine += 1
                                        continue
                                    elif indexExec == 0 and switchAsOn == 'S':
                                        
                                        #busco version
                                        dicTempVersions = processLineFromConstToDic_SearchVersions(line,lineComment,dicTempVersions)
                                        line = fp.readline()
                                        countLine += 1
                                        continue
                                    
                                    elif indexBlockComentOpen >= 0 or switchCommentOn == 'S':
                                        indexBlockComentClose = line.find(blockCommentClose, 0)
                                        conjSubBlock = set(dicTempDescriptions.keys())
                                        if indexBlockComentClose >= 0:
                                            if len(listTempDescriptionVersionsFull) == 0:
                                                lastVersion = "vacio"
                                            elif len(listTempDescriptionVersionsFull) == 1:
                                                lastVersion = listTempDescriptionVersionsFull[0]
                                            else:
                                                lastVersion = listTempDescriptionVersionsFull[len(listTempDescriptionVersionsFull) - 1]
                                            #comentamos ultimaversion full
                                            """ self.lista.insert(END, lastVersion)
                                            self.lista.itemconfigure(END, fg="#00aa00") """

                                            dicTempDescriptions.clear() 
                                            listTempDescriptionParametersFull.clear()#parametros :
                                            listTempDescriptionVersionsFull.clear()#lista de versiones
                                            switchCommentOn = 'N'
                                        else:
                                            dicTempDescriptions = processLineFromListToDic(line,listConstantsDescriptions,dicTempDescriptions)
                                            
                                            if conjConstantsDescriptions.issubset(conjSubBlock):
                                                # buscamos versiones en sub bloque descripciones
                                                listTempDescriptionVersionsFull = processLineFromConstToListboth(line,space,listTempDescriptionVersionsFull)
                                                dicTempDescriptionVersions = processLineFromConstToDic_ExtractVersions(line,space,dicTempDescriptionVersions)
                                                
                                            else:
                                                # buscamos parametros en sub bloque descripciones
                                                listTempDescriptionParametersFull = processLineFromConstToListboth(line,dospuntos,listTempDescriptionParametersFull)
                                                listTempDescriptionParameters = processLineFromConstToListSuffix(line,arroba,listTempDescriptionParameters)

                                            switchCommentOn = 'S'
                                    
                                    elif (indexBlockAsOpen >= 0 or switchAsOn == 'S') and (indexPrefixAs >= 0 and indexSufixAs >= 0):
                                        
                                        if switchAsOn == 'N':
                                            for listTarget in listOfLists:
                                                dicTempBlock = processLineFromListToDic(line,listTarget,dicTempBlock)  
                                            #busco parametros
                                            listTempParameters = processLineFromConstToListSuffix(line,arroba,listTempParameters)
                                            
                                        #busco version
                                        dicTempVersions = processLineFromConstToDic_SearchVersions(line,lineComment,dicTempVersions)
                                        
                                        if indexBlockAsOpen > 0 and indexPrefixAs >= 0 and indexSufixAs >= 0:
                                            switchAsOn = 'S'

                                        

                                    else:
                                        
                                        """ conjBlock = set(dicTempBlock.keys())
                                        if conjBlockBody.issubset(conjBlock):
                                            #busco version
                                            dicTempVersions = processLineFromConstToDic_SearchVersions(line,lineComment,dicTempVersions)
                                        else:

                                            for listTarget in listOfLists:
                                                dicTempBlock = processLineFromListToDic(line,listTarget,dicTempBlock)

                                        conjBlock = set(dicTempBlock.keys())
                                        if switchAsOn == 'N' and conjBlockBody.issubset(conjBlock):
                                            #busco parametros
                                            listTempParameters = processLineFromConstToListSuffix(line,arroba,listTempParameters)
                                        """

                                        switchAsOn = 'N'
                            
                    # siguiente linea
                    line = fp.readline()
                    countLine += 1

        except OSError as e:
            if e.errno == errno.ENOENT:
                messagebox.showwarning("Warning", "File not found / File not selected")
        except UnicodeDecodeError:
            print ("invalid utf-8")


def processLineFromConstToDic_ExtractVersions(line,const,dicResult):
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

def processLineFromConstToDic_SearchVersions(line,const,dicResult):
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

    return dicResult



def processLineFromListToDic(line,listMain,dicResult):
    #hacemos un bucle de busqueda por cada elemento de la lista que ingresa
    for const in listMain:
        startPosition = line.find(const, 0)
        while startPosition >= 0:
            endPosition = line.find(space, startPosition)
            object_ = line[startPosition: endPosition]                                    
            if object_ in listMain or const in listMainConstants:
                if object_ in dicResult.keys():
                    dicResult[object_] += 1
                else:
                    dicResult[object_] = 1                           
            startPosition = line.find(const, endPosition + 1)

    return dicResult

def processLineFromConstToListboth(line,const,listResult):
    #hacemos una busqueda de la constante que ingresa
    startPosition = line.find(const, 0)
    if startPosition >= 0:
        endPosition = len(line)-1
        objectsufijo_ = line[startPosition + 1 : endPosition].strip()
        if startPosition == 1:
            objectprefijo_ = line[0 : startPosition]
        else:
            objectprefijo_ = line[0 : startPosition - 1].strip()
        object_ = objectprefijo_ + const + objectsufijo_
        object_ = " ".join(object_.split())
        listResult.append(object_)

    return listResult

def processLineFromConstToListSuffix(line,const,listResult):
    #hacemos una busqueda de la constante que ingresa
    line = line.replace(':',' ')
    startPosition = line.find(const, 0)
    """ if startPosition >= 0:
        endPosition = line.find(space, startPosition)
        objectsufijo_ = line[startPosition + 1 : endPosition].strip()
        if startPosition == 1:
            objectprefijo_ = line[0 : startPosition]
        else:
            objectprefijo_ = line[0 : startPosition - 1].strip()
        object_ = const + objectsufijo_
        object_ = " ".join(object_.split())
        listResult.append(object_) """

    while startPosition >= 0:
        endPosition = line.find(space, startPosition)
        objectsufijo_ = line[startPosition + 1 : endPosition].strip()
        if startPosition == 1:
            objectprefijo_ = line[0 : startPosition]
        else:
            objectprefijo_ = line[0 : startPosition - 1].strip()
        object_ = const + objectsufijo_
        object_ = " ".join(object_.split())
        listResult.append(object_)
        startPosition = line.find(const, endPosition + 1)

    return listResult

def processLineFromConstToListPrefix(line,const,listResult):
    #hacemos una busqueda de la constante que ingresa
    startPosition = line.find(const, 0)
    if startPosition >= 0:
        endPosition = len(line)-1
        objectsufijo_ = line[startPosition + 1 : endPosition].strip()
        if startPosition == 1:
            objectprefijo_ = line[0 : startPosition]
        else:
            objectprefijo_ = line[0 : startPosition - 1].strip()
        object_ = objectprefijo_ + const
        object_ = " ".join(object_.split())
        listResult.append(object_)

    return listResult

def stripAccents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def main():
    root = tk.Tk()
    root.iconbitmap('kms.ico')
    root.geometry("400x300+300+300")
    app = Window(root)
    root.mainloop()


if __name__ == '__main__':
    main()

# Developer mode
# if not os.path.isfile(filepath):
##            messagebox.showinfo("Info", "You must to choose a file")
# if storeObject == 'usp_plantillametodoensayemuestraqc_select':
##                                print (line)
##            items = self.listbox.get(0, tk.END)
# except Exception as inst:
##            messagebox.showinfo("Info", inst)
