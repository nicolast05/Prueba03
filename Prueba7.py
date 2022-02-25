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


""" datos = 'datos'
generales = 'generales'
parametros= 'parametros'
control = 'control'
version = 'version'
historial = 'historial'
autor = 'autor'
fecha = 'fecha' """

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
""" listWithoutDuplicates =  list(set(listBlockHeader + listBlockBody + listBlockFootReader + listBlockFootWriter + listBlockFootSQLBI))
listConstants = [use, if_, exists, from_, sysobjects, objectid_, and_, type_, drop, procedure, create, as_, grant, execute, reader, writer, sqlbi] """
listConstants =  list(set(listBlockHeader + listBlockBody + listBlockFootReader + listBlockFootWriter + listBlockFootSQLBI))

""" listDescriptions = [datos, generales, parametros, control, version, historial, autor, fecha] """

# conjuntos para bloques
conjBlockBD = set(listBlockBD)
conjBlockHeader = set(listBlockHeader)
conjBlockBody = set(listBlockBody)
conjBlockFootReader = set(listBlockFootReader)
conjBlockFootWriter = set(listBlockFootWriter)
conjBlockFootSQLBI = set(listBlockFootSQLBI)

# conjunto para procesar información
conjConstants = set(listConstants)

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
        countBlock = 0
        # Contador de lineas de contenido
        countLine = 0
        countObject = 0
        
        listOfLists = [listConstants,listMainConstants]

        dicBlock = {}
        dicReport = {}
        dicBlockDescriptions = {}


        

        listBlockDescriptions = []

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

                    strippedLine = line.strip()

                    if strippedLine == "":
                        line = fp.readline()
                        countLine += 1
                        continue

                    if flagBlockBD == '' and countBlock >= 1:
                        break

                    if strippedLine == go:

                        observation = ''
                        conjBlock = set(dicBlock.keys())

                        if conjBlockBD.issubset(conjBlock):
                            flagBlockBD = 'BD'
                            print(conjBlock)
                        elif conjBlockHeader.issubset(conjBlock):
                            flagBlockES = 'H'
                            countObject = 2
                            print(conjBlock)
                        elif conjBlockBody.issubset(conjBlock):
                            flagBlockES = 'B'
                            countObject = 1
                            print(conjBlock)
                        elif conjBlockFootReader.issubset(conjBlock):
                            flagBlockES = 'FR'
                            countObject = 1
                            print(conjBlock)
                        elif conjBlockFootWriter.issubset(conjBlock):
                            flagBlockES = 'FW'
                            countObject = 1
                            print(conjBlock)
                        elif conjBlockFootSQLBI.issubset(conjBlock):
                            flagBlockES = 'FS'
                            countObject = 1
                            print(conjBlock)
                        else:
                            observation = "Bloque incompleto "
                            flagBlockES = ''

                        if countBlock == 0:
                            if flagBlockBD == '':
                                observation += "(Bloque BD) "
                            else:
                                self.lista.insert(END, ' '.join(map(str, conjBlock)))
                                self.lista.itemconfigure(END, fg="#00aa00")
                            
                        else:    
                            if flagBlockES == '':
                                observation += "(Bloque Estandar) "
                            else:
                                conjBlock = conjBlock - conjConstants   

                            if len(conjBlock) == 1:
                                if observation == "":
                                    self.lista.insert(END, ' '.join(map(str, conjBlock)))
                                    self.lista.itemconfigure(END, fg="#00aa00")

                                else:
                                    self.lista.insert(END, observation)
                                    self.lista.itemconfigure(END, fg="#ff0000")

                            elif len(conjBlock) == 0:
                                self.lista.insert(END, observation)
                                self.lista.itemconfigure(END, fg="#ff0000")

                            else:
                                self.lista.insert(END, observation)
                                self.lista.itemconfigure(END, fg="#ff0000")

                        dicBlock.clear()  
                        #dicBlockDescriptions.clear()
                        #print(dicReport)
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

                        if indexLineComent >= 0:
                            line = fp.readline()
                            countLine += 1
                            continue
                        elif indexBlockComentOpen >= 0 or switchCommentOn == 'S':
                            indexBlockComentClose = line.find(blockCommentClose, 0)
                            if indexBlockComentClose >= 0:
                                switchCommentOn = 'N'
                            else:
                                #dicBlockDescriptions = processLine(line,listDescriptions,dicBlockDescriptions)
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
