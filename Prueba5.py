"""App como herramienta de revisión de scripts consolidados para QAI"""

#Importaciones
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

#Usuario por default
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

##constantes

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
""" on = 'on '
to = 'to ' """
        
class Window(Frame):
  
    #Inicialización
    def __init__(self, master):
        #Parametros para mi clase Frame
        Frame.__init__(self, master)   
        #Referenciamos             
        self.master = master
        #corremos
        self.init_window()
        
    def init_window(self):
        #Titulo de la ventana
        self.master.title("QA Tools")
        #Instanciamos un menu
        menu = Menu(self.master)
        #Referenciamos al widget
        self.master.config(menu=menu)
        #Agreamos submenus
        file = Menu(menu, tearoff = 0)
        #Agregamos submenu Open
        file.add_command(label="Open", command=self.openFile)
        #Agregamos submenu exit
        file.add_command(label="Exit", command=self.client_exit)
        #menu File
        menu.add_cascade(label="File", menu=file)
        ##Scrollbar
        self.scrollbar = Scrollbar(self.master, orient=VERTICAL)  
        self.scrollbar.pack( side = RIGHT, fill = Y )
        ##Lista                
        self.lista = Listbox(self.master, font=("Helvetica", 8), borderwidth=0, activestyle=NONE, yscrollcommand = self.scrollbar.set)     
        self.lista.pack(fill=BOTH, expand=1)      
        self.scrollbar.config( command = self.lista.yview )

    #Funcion para cerrar la app
    def client_exit(self):
        
        self.master.destroy()

    #Funcion para abrir un doc   
    def openFile(self):

        self.lista.delete(0,END)
        
        ##obtenemos el archivo
        filepath = fdialog.askopenfilename(initialdir="C:/Users/%s" % user,
                               filetypes =(("SQL File", "*.sql"),("All Files","*.*")),
                               title = "Selección de Archivo")

        switchCommentOn = 'N'
        listBlockBD = [use]
        listBlockHeader = [if_,exists,from_,sysobjects,objectid_,and_,type_,drop,procedure]
        listBlockBody = [create,procedure]
        listBlockFoot = [grant,execute]
        dic = {}
        dicwords = {}

        listObjects = []
        listConstants = [use,if_,exists,from_,sysobjects,objectid_,and_,type_,drop,procedure,create,grant,execute]
        listVariables = [usp]
        listBlock = []
        conjBlockBD=set(listBlockBD)
        conjBlockHeader=set(listBlockHeader)
        conjBlockBody=set(listBlockBody)
        conjBlockFoot=set(listBlockFoot)

        try:
            ##con el nombre del archivo
            with open(filepath) as fp:
                ##obtenemos la primera linea
                line = fp.readline()
                cnt = 1
                
                ##mientras exista una linea
                while line:
                    ##damos formato estandar a la linea reemplazando )([].' por un espacio
                    line = line.lower().replace(')',' ').replace('(',' ').replace('[',' ').replace(']',' ').replace('.',' ').replace("'",' ')

                    switchBlockOn = 'S'
                    listObjects.clear()

                    if line.strip() == "":
                        line = fp.readline()
                        cnt += 1
                        continue
                    
                    startPosition = line.find(go)
                    
                    if startPosition >= 0:
                        endPosition = line.find(go[len(go) - 1])
                        object_     = line[startPosition: endPosition + 1]
                        if object_ == go:

                            conjBlock = set(listBlock)
                            
                            if conjBlock == conjBlockBD:
                                print(conjBlock)
                                
                            elif conjBlockHeader.issubset(conjBlock):
                                print(conjBlock)
                                """ print(dic) """
                            elif conjBlockBody.issubset(conjBlock):
                                print(conjBlock)
                                """ print(dic) """
                            elif conjBlockFoot.issubset(conjBlock):
                                print(conjBlock)
                                """ print(dic) """

                            switchBlockOn = 'N'
                            listBlock.clear()

                    else:
                        for const in listConstants:
                            startPosition = line.find(const)
                            
                            if startPosition >= 0:
                                endPosition = line.find(space,startPosition)
                                object_     = line[startPosition: endPosition]
                                if object_ in listConstants:
                                    listObjects.append(object_)
                                #elif const == store:
                                #    listObjects.append(object_)

                        for var in listVariables:
                            startPosition = line.find(var)
                                        
                            if startPosition >= 0:
                                endPosition = line.find(space,startPosition)
                                object_     = line[startPosition: endPosition]
                                listObjects.append(object_)
                            
                    """ print (listObjects) """

                    if switchBlockOn == 'S':
                        for targetObj in listObjects:

                            if targetObj in listBlock:
                                dic[targetObj] += 1
                            else:
                                dic[targetObj] = 1
                                listBlock.append(targetObj)

                    ##siguiente linea        
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

## Developer mode
##        if not os.path.isfile(filepath):
##            messagebox.showinfo("Info", "You must to choose a file")
##                            if storeObject == 'usp_plantillametodoensayemuestraqc_select':
##                                print (line)
##            items = self.listbox.get(0, tk.END)      
##        except Exception as inst:
##            messagebox.showinfo("Info", inst)
