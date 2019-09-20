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
import tkinter as tk
import tkinter.filedialog as fdialog
import getpass
import os
import errno

# Usuario por default
user = getpass.getuser()

select = 'select'
workflow = 'n usp_'

function = 'ufn_'
equal = '='
objectid_ = 'object_id'
join = 'join'
between = 'between'
over = 'over'
group = 'group'
coma = ','

lineComment = '--'
blockCommentOpen = '/*'
blockCommentClose = '*/'

# constantes

space = ' '

go = 'go'
use = 'use'
if_ = 'if'
exists = 'exists'
from_ = 'from'
sysobjects = 'sysobjects'
and_ = 'and'
type_ = 'type'
drop = 'drop'
procedure = 'procedure'

create = 'create'
usp = 'usp_'
exec_ = 'exec'
grant = 'grant'
execute = 'execute'

beg = 0

datos = 'datos'
generales = 'generales'
parametros= 'parametros'
control = 'control'
version = 'version'
historial = 'historial'
autor = 'autor'
fecha = 'fecha'

database = 'bdoperaciones'

class Window(Frame):

    # Inicialización
    def __init__(self, master):
        # Parametros para mi clase Frame
        Frame.__init__(self, master)
        # Referenciamos
        self.master = master
        # corremos
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

    # Funcion para abrir un doc
    def openFile(self):

        self.lista.delete(0, END)

        # obtenemos el archivo
        filepath = fdialog.askopenfilename(initialdir="C:/Users/%s" % user,
                                           filetypes=(
                                               ("SQL File", "*.sql"), ("All Files", "*.*")),
                                           title="Selección de Archivo")

        switchCommentOn = 'N'
        flagBlockBD = 'N'
        listBlockBD = [use, database]
        listBlockHeader = [if_, exists, from_, sysobjects, objectid_, and_, type_, drop, procedure]
        listBlockBody = [create, procedure]
        listBlockFoot = [grant, execute]

        listBlockMerge = [listBlockHeader,listBlockBody,listBlockFoot]

        dic = {}
        dicBlock = {}
#        dicParameters = {}
        dicBlockDescriptions = {}

#        listObjects = []
        listConstants = [use, if_, exists, from_, sysobjects, objectid_, and_, type_, drop, procedure, create, grant, execute]
        listStatements = [usp]
#        listParameters = ['@']
        listDescriptions = [datos, generales, parametros, control, version, historial, autor, fecha]
        listBlock = []
        conjBlockBD = set(listBlockBD)
        conjBlockHeader = set(listBlockHeader)
        conjBlockBody = set(listBlockBody)
        conjBlockFoot = set(listBlockFoot)

#        listBlockParameters = []
        listBlockDescriptions = []

        try:
            # con el nombre del archivo
            with open(filepath) as fp:
                # obtenemos la primera linea
                line = fp.readline()
                cnt = 1

                # mientras exista una linea
                while line:
                    # damos formato estandar a la linea reemplazando )([].' por un espacio
                    line = line.lower().replace(')', ' ').replace('(', ' ').replace('[', ' ').replace(
                        ']', ' ').replace('.', ' ').replace("'", ' ').replace("\n", ' ').replace("\t", ' ')

                    strippedLine = line.strip()

                    if strippedLine == "":
                        line = fp.readline()
                        cnt += 1
                        continue

                    if strippedLine == go:

                        conjBlock = set(listBlock)

                        if conjBlock == conjBlockBD:
                            flagBlockBD = 'S'
                            print(conjBlock)
                        elif conjBlockHeader.issubset(conjBlock):
                            print(conjBlock)
                        elif conjBlockBody.issubset(conjBlock):
                            print(conjBlock)
                        elif conjBlockFoot.issubset(conjBlock):
                            print(conjBlock)


                        #print (listBlockDescriptions)
                        
                        listBlock.clear()  # limpiamos la lista por bloque
                        #listBlockParameters.clear()
                        #listBlockDescriptions.clear()

                    else:

                        indexBlockComentOpen = line.find(blockCommentOpen, beg)

                        if indexBlockComentOpen >= 0 or switchCommentOn == 'S':
                            indexBlockComentClose = line.find(blockCommentClose, beg)
                            if indexBlockComentClose >= 0:
                                switchCommentOn = 'N'
                            else:
                                for const in listDescriptions:
                                    startPosition = line.find(const, beg)
                                    while startPosition >= 0:
                                        endPosition = line.find(space, startPosition)
                                        object_ = line[startPosition: endPosition]
                                        if object_ in listDescriptions:
                                            # listObjects.append(object_)
                                            if object_ in listBlockDescriptions:
                                                dicBlockDescriptions[object_] += 1
                                            else:
                                                dicBlockDescriptions[object_] = 1
                                                listBlockDescriptions.append(object_)

                                        startPosition = line.find(const, endPosition + 1)

                                switchCommentOn = 'S'
                        
                        if flagBlockBD == 'N':
                            for const in listBlockBD:
                                startPosition = line.find(const, beg)
                                while startPosition >= 0:
                                    endPosition = line.find(space, startPosition)
                                    object_ = line[startPosition: endPosition]
                                    if object_ in listBlockBD:
                                        # listObjects.append(object_)
                                        if object_ in listBlock:
                                            dicBlock[object_] += 1
                                        else:
                                            dicBlock[object_] = 1
                                            listBlock.append(object_)     

                                    startPosition = line.find(const, endPosition + 1)
                            
                            line = fp.readline()
                            continue
                        
                        for target in listBlockMerge:
                            listFusion = target + listStatements

                            for const in listFusion:
                                startPosition = line.find(const, beg)
                                while startPosition >= 0:
                                    endPosition = line.find(space, startPosition)
                                    object_ = line[startPosition: endPosition]
                                    
                                    if object_ in target or const in listStatements:
                                        if object_ in listBlock:
                                            dicBlock[object_] += 1
                                        else:
                                            dicBlock[object_] = 1
                                            listBlock.append(object_)
                                    
                                    startPosition = line.find(const, endPosition + 1)


#                        for par in listParameters:
#                            startPosition = line.find(par)
#                            while startPosition >= 0:
#                                endPosition = line.find(space, startPosition)
#                                object_ = line[startPosition: endPosition]
#                                # listObjects.append(object_)
#                                if object_ in listBlockParameters:
#                                    dicParameters[object_] += 1
#                                else:
#                                    dicParameters[object_] = 1
#                                    listBlockParameters.append(object_)
#
#                                startPosition = line.find(par, endPosition + 1)

                    # siguiente linea
                    line = fp.readline()
                    cnt += 1

        except OSError as e:
            if e.errno == errno.ENOENT:
                messagebox.showwarning("Warning", "File not found / File not selected")


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
