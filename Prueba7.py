"""App como herramienta de revisión de scripts consolidados para QAI"""

# Importaciones
##from tkinter import *
from ast import If
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
listBlockBody = [create, procedure, as_]
listBlockFootReader = [grant, execute, reader]
listBlockFootWriter = [grant, execute, writer]
listBlockFootSQLBI = [grant, execute, sqlbi]

# lista de constantes principales
listMainConstants = [usp]

# listas para procesar información
listConstants =  list(set(listBlockHeader + listBlockBody + listBlockFootReader + listBlockFootWriter + listBlockFootSQLBI))

# conjuntos para bloques
conjBlockBD = set(listBlockBD)
conjBlockHead = set(listBlockHeader)
conjBlockBody = set(listBlockBody)
conjBlockFootReader = set(listBlockFootReader)
conjBlockFootWriter = set(listBlockFootWriter)
conjBlockFootSQLBI = set(listBlockFootSQLBI)

# conjunto para procesar información
conjConstants = set(listConstants)

# listas para sub bloques
listSubBlockDatosGenerales = [datos, generales, descripcion]
listSubBlockParametros = [parametros]
listSubBlocControlVersion = [control, version, historial, autor, fecha, descripcion]

# lista de constantes principales en sub bloques
#listMainConstantsDescription = [arroba, dospuntos, punto]
listMainConstantsDescription = [dospuntos]

# lista para procesar informacion de sub blqoues
listConstantsDescription = list(set(listSubBlockDatosGenerales + listSubBlockParametros + listSubBlocControlVersion))

# conjuntos para sub bloques
conjSubBlockDatosGenerales = set(listSubBlockDatosGenerales)
conjSubBlockParametros = set(listSubBlockParametros)
conjSubBlockControlVersion = set(listSubBlocControlVersion)

# conjunto para procesar información en sub bloques
conjConstantsDescription = set(listConstantsDescription)

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

        # Diccionario temporal para procesar contenido
        dicBlock = {}

        dicReport = {}
        dicTempLineDescriptions = {}
        ListTempLineDescriptions = []

        try:
            # con el nombre del archivo
            with open(filepath) as fp:
                # obtenemos la primera linea
                line = fp.readline()
                
                # mientras exista una linea
                while line:
                    # damos formato estandar a la linea reemplazando )([].' por un espacio
                    line = line.lower().replace(')', ' ').replace('(', ' ').replace('[', ' ').replace(
                        ']', ' ').replace('.', ' ').replace("'", ' ').replace("\n", ' ').replace("\t", ' ')

                    # eliminamos espacios en blanco
                    strippedLine = line.strip()

                    # si la linea de contenido es vacía, leemos la siguiente linea
                    if strippedLine == "":
                        line = fp.readline()
                        countLine += 1
                        continue
                    
                    # si no tenemos bloque de BD y ya pasamos el primer bloque
                    if flagBlockBD == '' and countBlock >= 2:
                        break

                    # si la linea de contenido sin espacios es igual a la constante go
                    if strippedLine == go:
                        
                        # inicializamos la variable para observaciones
                        observation = ''

                        # obtenemos el contenido del diccionario temporal y lo seteamos como conjunto
                        conjBlock = set(dicBlock.keys())

                        # validamos si el contenido de algun bloque esta dentro de nuestro contenido
                        if conjBlockBD.issubset(conjBlock):
                            flagBlockBD = 'BD'
                            print(conjBlock)
                        elif conjBlockHead.issubset(conjBlock):
                            flagBlockES = 'Head'
                            countObject = 2
                            print(conjBlock)
                        elif conjBlockBody.issubset(conjBlock):
                            flagBlockES = 'Body'
                            countObject = 1
                            print(conjBlock)
                        elif conjBlockFootReader.issubset(conjBlock):
                            flagBlockES = 'FootReader'
                            countObject = 1
                            print(conjBlock)
                        elif conjBlockFootWriter.issubset(conjBlock):
                            flagBlockES = 'FootWriter'
                            countObject = 1
                            print(conjBlock)
                        elif conjBlockFootSQLBI.issubset(conjBlock):
                            flagBlockES = 'FootSQLBI'
                            countObject = 1
                            print(conjBlock)
                        else:
                            observation = "Bloque incompleto " 
                            flagBlockES = ''

                        # si el contador de bloque es 1 validaremos el bloque de BD
                        if countBlock == 1:
                            if flagBlockBD == '':
                                observation += "(Bloque BD) " 
                            else:
                                self.lista.insert(END, ' '.join(map(str, conjBlock)))
                                self.lista.itemconfigure(END, fg="#00aa00")

                        # si el contador de bloque mayor a 1 validaremos el bloque estandar     
                        else:    
                            if flagBlockES == '':
                                observation += "(Bloque Estandar) " 
                            else:
                                conjBlock = conjBlock - conjConstants   

                            if len(conjBlock) == 1:
                                if observation == "":
                                    self.lista.insert(END,' '.join(map(str, conjBlock)))
                                    self.lista.itemconfigure(END, fg="#00aa00")

                                else:
                                    self.lista.insert(END, observation + 'linea: ' + str(countLine))
                                    self.lista.itemconfigure(END, fg="#ff0000")

                            elif len(conjBlock) == 0:
                                self.lista.insert(END, observation + 'linea: ' + str(countLine))
                                self.lista.itemconfigure(END, fg="#ff0000")

                            else:
                                self.lista.insert(END, observation + 'linea: ' + str(countLine))
                                self.lista.itemconfigure(END, fg="#ff0000")

                        # limpiamos el diccionario temporal y sumamos 1 al contador de bloques
                        dicBlock.clear()  
                        countBlock += 1

                    elif flagBlockBD == '':
                            dicBlock = processLine(line,listBlockBD,dicBlock)
                            line = fp.readline()
                            countLine += 1
                            continue

                    else:
                        
                        indexLineComent = line.find(lineComment, 0)
                        indexBlockComentOpen = line.find(blockCommentOpen, 0)
                        indexExec = strippedLine.find(exec_, 0)

                        if indexLineComent >= 0 and switchCommentOn == 'N':
                            line = fp.readline()
                            countLine += 1
                            continue
                        elif indexBlockComentOpen >= 0 or switchCommentOn == 'S':
                            indexBlockComentClose = line.find(blockCommentClose, 0)
                            if indexBlockComentClose >= 0:
                                conjSubBlock = set(dicTempLineDescriptions.keys())
                                
                                switchCommentOn = 'N'
                            else:
                                dicTempLineDescriptions = processLine(line,listConstantsDescription,dicTempLineDescriptions)
                                
                                if conjConstantsDescription.issubset(set(dicTempLineDescriptions.keys())):
                                    #buscamos versiones
                                    ListTempLineDescriptions = processLineBloqueComentariosVersion(line,space,ListTempLineDescriptions)
                                else:
                                    ListTempLineDescriptions = processLineBloqueComentarios(line,listMainConstantsDescription,ListTempLineDescriptions)

                                switchCommentOn = 'S'
                        elif indexExec == 0:
                            line = fp.readline()
                            countLine += 1
                            continue
                        else:
                            for listTarget in listOfLists:
                                dicBlock = processLine(line,listTarget,dicBlock)
                            
                    # siguiente linea
                    line = fp.readline()
                    countLine += 1

        except OSError as e:
            if e.errno == errno.ENOENT:
                messagebox.showwarning("Warning", "File not found / File not selected")

def processLine(line,listMain,dicResult):
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

def processLineBloqueComentarios(line,listMain,listResult):
    #hacemos un bucle de busqueda por cada elemento de la lista que ingresa
    for const in listMain:
        startPosition = line.find(const, 0)
        if startPosition >= 0:
            endPosition = len(line)-1
            objectsufijo_ = line[startPosition + 1 : endPosition].strip()
            objectprefijo_ = line[0 : startPosition - 1].strip()
            object_ = objectprefijo_ + const + objectsufijo_
            listResult.append(object_)
        """ while startPosition >= 0:
            endPosition = line.find(space, startPosition)
            object_ = line[startPosition: endPosition]                                    
            if object_ in listMain or const in listMainConstants:
                if object_ in dicResult.keys():
                    dicResult[object_] += 1
                else:
                    dicResult[object_] = 1                           
            startPosition = line.find(const, endPosition + 1) """

    return listResult

def processLineBloqueComentariosVersion(line,const,listResult):
    #hacemos un bucle de busqueda por cada elemento de la lista que ingresa
    
    startPosition = line.find(const, 0)
    if startPosition >= 0:
        endPosition = len(line)-1
        objectsufijo_ = line[startPosition + 1 : endPosition].strip()
        if startPosition == 1:
            objectprefijo_ = line[0 : startPosition]
        else:
            objectprefijo_ = line[0 : startPosition - 1].strip()
        object_ = objectprefijo_ + punto + objectsufijo_
        object_ = " ".join(object_.split())
        startPosition = object_.find(const, 0)
        listResult.append(object_)
        """ while startPosition >= 0:
            endPosition = line.find(space, startPosition)
            object_ = line[startPosition: endPosition]                                    
            if object_ in listMain or const in listMainConstants:
                if object_ in dicResult.keys():
                    dicResult[object_] += 1
                else:
                    dicResult[object_] = 1                           
            startPosition = line.find(const, endPosition + 1) """

    return listResult
#def deleteAccent(lineText):
    #s = ''.join((c for c in unicodedata.normalize('NFD',lineText) if unicodedata.category(c) != 'Mn'))
    #return s

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
