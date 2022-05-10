
"""
Autor:  Daniel Araya

Fecha de creación:  8 de Mayo, 2022

Descripción:    Administrador de Base de Datos  (Tkinter)

    - Trabaja con bases de datos MySql. 
    - Crea/Conecta bases de datos.
    - Crea tablas, índices, procedimientos almacenados, vistas y triggers.
    - Genera sentencias SQL (select, insert, update y delete).
    - Ejecuta sentencias SQL con la opción "SQL".

Requisitos: 
    
    - Instalar MySql
    - Modificar constantes 'HOST', 'USER' Y 'PASSWORD'
    - Instalar librería mysql para Python (pip install mysql)
    - Instalar librería mysql.connector para Python (pip install mysql.connector)
    - Instalar librería pyautogui (pip install pyautogui)
    - Instalar librería pyperclip (pip install pyperclip)

"""

import time
import tkinter as tk
from functools import partialmethod
from tkinter import END, messagebox, scrolledtext, ttk
from tkinter.font import Font
import mysql.connector as mysql
import pyautogui  # Mejora calidad programa
from idlelib.tooltip import Hovertip
from pyperclip import copy, paste

root = tk.Tk()
root.title("Administrador de Bases de Datos")
root.resizable(False,False)
root.geometry("970x900")

NOMBRE_APP = "Administrador de Base de Datos"

HOST = "HOST"
USER = "USER"
PASSWORD = "PASSWORD"

CREAR = "CREAR"
CONECTAR = "CONECTAR"

MSG_ATENCION = "Atención"
MSG_CAMPOS_INCOMPLETOS = "Por favor complete todos los campos."
MSG_SELECCIONE_TABLA = "Por favor seleccione una tabla."
MSG_ERROR = "Ha ocurrido un error:\n{}"
MSG_SIN_CONEXION = "No se ha establecido conexión con ninguna base de datos.\nPresione 'BBDD' para crear o establecer conexión con una base de datos."

style = ttk.Style()

style.configure("TMenubutton",font=("Helvetica",15))
Fuente = Font(family="Helvetica",size=13)

root.option_add("*TCombobox*Listbox*Font", Fuente)

style.configure(
"mystyle.Treeview",
font=("Helvetica",12),
rowheight=45
)

style.configure(
"mystyle.Treeview.Heading",
font=("Helvetica",12,"bold")
)

style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky':'nswe'})])

class Widgets():

    def __init__(self):

        self.CerrarIMG = tk.PhotoImage(file="Imagenes\Cerrar.png")
        self.SimularIMG = tk.PhotoImage(file="Imagenes\SimularConsulta.png")
        self.OrderByIMG = tk.PhotoImage(file="Imagenes\OrderBy.png")
        self.PantallaCompletaIMG = tk.PhotoImage(file="Imagenes\PantallaCompleta.png")

        self.LabelEstadoConexion = tk.Label(root,text="Conéctate o crea una BD...",font=("Helvetica",13),fg="grey")
        self.LabelEstadoConexion.pack()

        self.BBDDmenubutton = ttk.Menubutton(root,text="BBDD")
        self.BBDDmenu = tk.Menu(self.BBDDmenubutton,font=("Helvetica",12),tearoff=0)

        self.BBDDmenu.add_command(label="Conectar",command=bd.IniciarConectar)
        self.BBDDmenu.add_command(label="Crear",command=bd.IniciarCrear)
        self.BBDDmenu.add_command(label="Cerrar",state="disabled",command=bd.Cerrar)
        self.BBDDmenu.add_separator()
        self.BBDDmenu.add_command(label="Salir",command=bd.Salir)
        self.BBDDmenubutton.configure(menu=self.BBDDmenu)
        self.BBDDmenubutton.place(x=0,y=0)

        tk.Button(root,text="SELECT",font=("Helvetica",16),width=17,cursor="hand2",border=0,bg="white",command=Select).place(x=47,y=675)
        tk.Button(root,text="CREATE",font=("Helvetica",16),width=17,cursor="hand2",border=0,bg="white",command=Create).place(x=344,y=675)
        tk.Button(root,text="UPDATE",font=("Helvetica",16),width=17,cursor="hand2",border=0,bg="white",command=Update).place(x=641,y=675)
        tk.Button(root,text="INSERT",font=("Helvetica",16),width=17,cursor="hand2",border=0,bg="white",command=Insert).place(x=47,y=768)
        tk.Button(root,text="DELETE",font=("Helvetica",16),width=17,cursor="hand2",border=0,bg="white",command=Delete).place(x=344,y=768)
        tk.Button(root,text="SQL",font=("Helvetica",16),width=17,cursor="hand2",border=0,bg="white",command=Sql).place(x=641,y=768)

class BD():

    def __IniciarBD(self,comando):

        comando = comando

        self.Conexion = mysql.connect(host=HOST,user=USER,password=PASSWORD,database="App")
        self.Cursor = self.Conexion.cursor()

        widgets.BBDDmenubutton.config(state="disabled")
        
        self.FrameConectarCrear = tk.Frame(root,height=350,width=500,highlightbackground="grey",highlightthickness=1)
        self.FrameConectarCrear.pack(pady=115)
        self.FrameConectarCrear.pack_propagate(False)

        tk.Button(self.FrameConectarCrear,image=widgets.CerrarIMG,border=0,cursor="hand2",command=lambda:[widgets.BBDDmenubutton.config(state="normal"),self.FrameConectarCrear.destroy()]).pack(side="right",anchor="n",padx=3,pady=3)

        tk.Label(self.FrameConectarCrear, text="Nombre:",font=("Helvetica",13)).place(x=120,y=65)
        self.NombreBD = tk.Entry(self.FrameConectarCrear,font=("Helvetica",13))
        self.NombreBD.place(x=118,y=115)
        self.NombreBD.focus()
        self.NombreBD.bind("<Return>",self.__Conectar if comando == CONECTAR else self.__Crear)

        tk.Button(self.FrameConectarCrear,text=comando,font=("Helvetica",15),width=15,cursor="hand2",border=0,bg="white",command=lambda:self.__Conectar(None) if comando == CONECTAR else self.__Crear(None)).place(x=130,y=230)

    def __Conectar(self,event):
        
        self.nombre = self.NombreBD.get()

        if len(self.nombre) == 0:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

        else:

            try:
                self.Conexion = mysql.connect(host=HOST,user=USER,password=PASSWORD,database=self.nombre)
                self.Cursor = self.Conexion.cursor()

                widgets.LabelEstadoConexion.config(text=f"Conexión establecida - {self.nombre}")
                widgets.BBDDmenubutton.config(state="normal")
                widgets.BBDDmenu.entryconfig(index="Conectar", state="disabled")
                widgets.BBDDmenu.entryconfig(index="Crear", state="disabled")
                widgets.BBDDmenu.entryconfig(index="Cerrar", state="normal")
                self.EstadoConexion = True

                self.FrameConectarCrear.destroy()
                
                messagebox.showinfo(NOMBRE_APP,"Conexión establecida con éxito.")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))
        
    def __Crear(self,event):

        self.nombre = self.NombreBD.get() 

        if len(self.nombre) == 0:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

        else:

            try:
                self.Cursor.execute("CREATE DATABASE {}".format(self.nombre))
                self.Conexion = mysql.connect(host=HOST,user=USER,password=PASSWORD,database=self.nombre)
                self.Cursor = self.Conexion.cursor()

                widgets.LabelEstadoConexion.config(text=f"Conexión establecida - {self.nombre}")
                widgets.BBDDmenubutton.config(state="normal")
                widgets.BBDDmenu.entryconfig(index="Conectar", state="disabled")
                widgets.BBDDmenu.entryconfig(index="Crear", state="disabled")
                widgets.BBDDmenu.entryconfig(index="Cerrar", state="normal")
                self.EstadoConexion = True

                self.FrameConectarCrear.destroy()
                
                messagebox.showinfo(NOMBRE_APP,f"BD '{self.nombre}' creada con éxito.")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

    def Cerrar(self):

        widgets.LabelEstadoConexion.config(text="Conéctate o crea una BD...")
        widgets.BBDDmenu.entryconfig(index="Cerrar",state="disabled")
        widgets.BBDDmenu.entryconfig(index="Conectar",state="normal")
        widgets.BBDDmenu.entryconfig(index="Crear",state="normal")
        self.Conexion.close()
        self.EstadoConexion = False

        root.geometry("970x900")

        for i in root.winfo_children()[8:]:i.destroy()

    def Salir(self):

        VarSalir = messagebox.askyesno(NOMBRE_APP,"¿Desea salir de la aplicación?")

        if VarSalir:
            root.destroy()

            try:
                self.Conexion.close()
            except AttributeError:
                pass

    IniciarConectar = partialmethod(__IniciarBD,CONECTAR)
    IniciarCrear = partialmethod(__IniciarBD,CREAR)

# SELECT

class Select():

    def __init__(self):
        
        if not bd.EstadoConexion:

            messagebox.showinfo(MSG_ATENCION,MSG_SIN_CONEXION)

        else:

            self.__IniciarSelect()

    def __IniciarSelect(self):

        self.NumFilas = 1
        self.yCanvas = 233
        self.IntVarCondiciones = tk.IntVar()
        self.yCondiciones = 323
        self.yCondicionesLabel = 278
        self.VarOrderBy = ""

        self.MainFrame = tk.Frame(root,height=840,width=925)
        self.MainFrame.place(x=20,y=37)
        self.MainFrame.pack_propagate(False)
        
        self.Canvas = tk.Canvas(self.MainFrame,width=595,height=390,highlightthickness=0)
        self.Canvas.place(x=50,y=233)
        self.Canvas.pack_propagate(False)
        self.FrameFilas = tk.Frame(self.Canvas,height=30,width=574)
        self.yScrollBarFilas = tk.Scrollbar(self.Canvas,orient="vertical",command=self.Canvas.yview)
        self.Canvas.create_window((0,0),window=self.FrameFilas,anchor="nw")
        self.Canvas.bind("<Configure>",lambda event:self.Canvas.config(scrollregion=self.Canvas.bbox("all")))

        bd.Cursor.execute("SHOW TABLES")
        
        tk.Label(self.MainFrame,text="SELECT",font=("Helvetica",15),border=0,width=8,pady=40).pack()
        tk.Label(self.MainFrame,text="Tabla:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Columna(s):",font=("Helvetica",14)).place(x=50,y=185)
        self.CondicionesLabel = tk.Label(self.MainFrame,text="Condiciones:",font=("Helvetica",14))
        self.CondicionesLabel.place(x=50,y=278)
        self.NumFilasLabel = tk.Label(self.MainFrame,text=self.NumFilas,font=("Helvetica",14),justify="center")
        self.NumFilasLabel.place(x=225,y=183)
        self.Tabla = ttk.Combobox(self.MainFrame,font=("Helvetica",14),values=[i for i in bd.Cursor],width=31,state="readonly")
        self.Tabla.place(x=194,y=125)
        self.MenosBoton = tk.Button(self.MainFrame,text="<",font=("Helvetica",14),border=0,state="disabled",command=self.__Menos)
        self.MenosBoton.place(x=188,y=180)
        self.MasBoton = tk.Button(self.MainFrame,text=">",font=("Helvetica",14),border=0,command=self.__Mas)
        self.MasBoton.place(x=250,y=180)
        ttk.Combobox(self.FrameFilas,font=("Helvetica",14),width=42,state="readonly").pack()
        self.Condiciones = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),width=57,height=12,undo=True)
        self.CheckButtonCondiciones = tk.Checkbutton(self.MainFrame,variable=self.IntVarCondiciones,onvalue=1,offvalue=0,command=self.__MostrarCondiciones)
        self.CheckButtonCondiciones.place(x=200,y=278)
        self.FrameBordeOrderBy = tk.Frame(self.MainFrame,highlightbackground="grey")
        self.FrameBordeOrderBy.place(x=250,y=272)
        tk.Button(self.FrameBordeOrderBy,image=widgets.OrderByIMG,border=0,command=self.__FuncOrderBy).pack(ipadx=7,ipady=7)

        self.Tabla.bind("<<ComboboxSelected>>",self.__ActualizarValuesFilas)
        self.FrameFilas.winfo_children()[0].bind("<<ComboboxSelected>>",self.__ActualizarNumFilas)
        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__EjecutarSelect())
        root.bind("<Control-E>",lambda event:self.__EjecutarSelect())
        self.Condiciones.bind("<space>",lambda event:self.Condiciones.edit_separator())
        self.Condiciones.bind("<Control-y>",lambda event:exec("try:self.Condiciones.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.Condiciones.bind("<Control-Y>",lambda event:exec("try:self.Condiciones.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.Condiciones.bind("<Control-c>",lambda event:copy(self.Condiciones.selection_get() if self.Condiciones.tag_ranges("sel") else ""))
        self.Condiciones.bind("<Control-C>",lambda event:copy(self.Condiciones.selection_get() if self.Condiciones.tag_ranges("sel") else ""))
        self.Condiciones.bind("<Control-v>",lambda event:paste())
        self.Condiciones.bind("<Control-V>",lambda event:paste())
        self.Condiciones.bind("<Control-l>",lambda event:self.Condiciones.delete("1.0","end-1c"))
        self.Condiciones.bind("<Control-L>",lambda event:self.Condiciones.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="EJECUTAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__EjecutarSelect).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=lambda:[self.MainFrame.destroy(),root.geometry("970x900")]).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__Limpiar).place(x=600,y=700)

    def __MostrarCondiciones(self):

        if self.IntVarCondiciones.get() == 1:

            self.Condiciones.place(x=50,y=self.yCondiciones)
            self.Condiciones.focus()

            self.Canvas.config(height=131)

            self.yCanvas = 224 if self.NumFilas >= 4 else 233 - (self.NumFilas-1)*3
            self.Canvas.place(y=self.yCanvas)

            self.yCondicionesLabel = 362 if self.NumFilas >= 4 else 278 + (self.NumFilas-1)*28
            self.CondicionesLabel.place(y=self.yCondicionesLabel)

            self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)
            self.FrameBordeOrderBy.place(y=self.yCondicionesLabel-6)

            if self.NumFilas >= 4:
                self.yScrollBarFilas.pack(side="right",fill="y")
                self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)

        else:

            self.Condiciones.place_forget()
            self.Condiciones.delete("1.0","end-1c")

            self.yCanvas = 233
            self.yCondicionesLabel = 278 + (self.NumFilas-1)*33 if self.NumFilas <= 12 else 641
            self.Canvas.config(height=390)
            self.Canvas.place(y=self.yCanvas)
            self.CondicionesLabel.place(y=self.yCondicionesLabel)
            self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)
            self.FrameBordeOrderBy.place(y=self.yCondicionesLabel-6)

            if self.NumFilas >= 12:
                self.yScrollBarFilas.pack(side="right",fill="y")
                self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)
            else:
                self.yScrollBarFilas.pack_forget()
        
    def __Limpiar(self):

        self.Tabla.config(state="normal")
        self.Tabla.delete(0,END)
        self.Tabla.config(state="readonly")

        for i in self.FrameFilas.winfo_children():
            i.config(values=[])
            i.config(state="normal")
            i.delete(0,END)
            i.config(state="readonly")

        self.Condiciones.delete("1.0","end-1c")

        self.MasBoton.config(state="normal")
        self.FrameBordeOrderBy.config(highlightthickness=0)
        self.VarOrderBy = ""

    def __FuncOrderBy(self):

        if len(self.Tabla.get()) == 0:

            messagebox.showinfo(MSG_ATENCION,MSG_SELECCIONE_TABLA)

        else:
            IntVarOrderBy = tk.IntVar()

            for i in self.MainFrame.winfo_children():
                if not isinstance(i,(tk.Frame,tk.Canvas)):
                    i.config(state="disabled")

            for i in self.FrameFilas.winfo_children():i.config(state="disabled")

            self.FrameOrderBy = tk.Frame(self.MainFrame,height=400,width=500,highlightbackground="grey",highlightthickness=1)
            self.FrameOrderBy.pack(pady=100)
            self.FrameOrderBy.pack_propagate(False)
            self.Condiciones.config(state="disabled")

            tk.Button(self.FrameOrderBy,text="CONFIRMAR",font=("Helvetica",15),command=lambda:FuncConfirmarOrderBy(),width=15,cursor="hand2",border=0,bg="white").pack(side="bottom",pady=60)
            tk.Label(self.FrameOrderBy, text="Ordenar por:",font=("Helvetica",13)).place(x=120,y=65)

            ColumnaOrderBy = ttk.Combobox(self.FrameOrderBy,font=("Helvetica",13),state="readonly",values=self.FilasValues[1:])
            ColumnaOrderBy.place(x=118,y=125)
            tk.Radiobutton(self.FrameOrderBy,text="Asc",font=("Helvetica",13),variable=IntVarOrderBy,value=1).place(x=118,y=195)
            tk.Radiobutton(self.FrameOrderBy,text="Desc",font=("Helvetica",13),variable=IntVarOrderBy,value=2).place(x=300,y=195)

            tk.Button(self.FrameOrderBy,image=widgets.CerrarIMG,cursor="hand2",border=0,command=lambda:FuncCerrarFrameOrderBy()).pack(side="top",anchor="e",pady=2,padx=2)

        def FuncCerrarFrameOrderBy():

            self.FrameOrderBy.destroy()
            self.Condiciones.config(state="normal")

            for i in self.MainFrame.winfo_children():
                
                if isinstance(i,(tk.Label,tk.Checkbutton,tk.Button)):
                    i.config(state="normal")

                elif isinstance(i,ttk.Combobox):
                    i.config(state="readonly")

                elif isinstance(i,tk.Frame):
                    for j in self.FrameFilas.winfo_children():
                        j.config(state="readonly")

        def FuncConfirmarOrderBy():

            CamposIncompletos = False

            if len(ColumnaOrderBy.get()) == 0:
                CamposIncompletos = True
            
            if IntVarOrderBy.get() == 1:
                self.VarOrderBy = f" ORDER BY {ColumnaOrderBy.get()} ASC"

            elif IntVarOrderBy.get() == 2:
                self.VarOrderBy = f" ORDER BY {ColumnaOrderBy.get()} DESC"

            else:
                CamposIncompletos = True

            if not CamposIncompletos:

                self.Condiciones.config(state="normal")
                self.FrameOrderBy.destroy()
                self.FrameBordeOrderBy.config(highlightthickness=1)

                for i in self.MainFrame.winfo_children():
                    
                    if isinstance(i,(tk.Label,tk.Checkbutton,tk.Button)):
                        i.config(state="normal")

                    elif isinstance(i,ttk.Combobox):
                        i.config(state="readonly")

                    elif isinstance(i,tk.Frame):
                        for j in self.FrameFilas.winfo_children():
                            j.config(state="readonly")
            else:
                messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

    def __Mas(self):

        if len(self.Tabla.get()) == 0:
            messagebox.showinfo(MSG_ATENCION,MSG_SELECCIONE_TABLA)
            
        else:
            if not self.FrameFilas.winfo_children()[0].get() == "*":

                if self.IntVarCondiciones.get() == 0:
                    
                    if self.NumFilas < 12:
                        self.yCondicionesLabel += 33

                    if self.NumFilas < 4:
                        self.yCondiciones += 26
                        self.Condiciones.config(height=self.Condiciones["height"]-1)
                else:
                    
                    if self.NumFilas < 4:
                        self.Condiciones.config(height=self.Condiciones["height"]-1)
                        self.yCondicionesLabel += 28
                        self.yCondiciones += 26
                        self.yCanvas -= 3

                self.MenosBoton.config(state="normal")

                self.FrameFilas.config(height=self.FrameFilas.winfo_height()+31)
                self.Canvas.config(scrollregion=self.Canvas.bbox("all"))

                self.NumFilas += 1
                self.NumFilasLabel.config(text=self.NumFilas)

                self.CondicionesLabel.place(y=self.yCondicionesLabel)
                self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)
                self.FrameBordeOrderBy.place(y=self.yCondicionesLabel-6)
                self.Canvas.place(y=self.yCanvas)

                ttk.Combobox(self.FrameFilas,font=("Helvetica",14),width=42,state="readonly",values=self.FilasValues).pack()

                self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-1].bind("<<ComboboxSelected>>",self.__ActualizarNumFilas)

                self.MasBoton.place(x=250+(len(str(self.NumFilas))-1)*15)

                if self.NumFilas == len(self.FilasValues)-1:self.MasBoton.config(state="disabled")

                if self.IntVarCondiciones.get() == 0:

                    if self.NumFilas == 12:
                        self.yScrollBarFilas.pack(side="right",fill="y")
                        self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)
                else:

                    if self.NumFilas == 4:
                        self.yScrollBarFilas.pack(side="right",fill="y")
                        self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)

                if self.IntVarCondiciones.get() == 1:self.Condiciones.place(y=self.yCondiciones)
                
            else:
                messagebox.showinfo(MSG_ATENCION,"Cambia el valor del campo para poder realizar esta acción.")

    def __Menos(self):

        if self.IntVarCondiciones.get() == 1:

            if self.NumFilas <= 4:
                self.Condiciones.config(height=self.Condiciones["height"]+1)
                self.yCondicionesLabel -= 28
                self.yCondiciones -= 26
                self.yCanvas += 3
        
        else:

            if self.NumFilas <= 12:
                self.yCondicionesLabel -= 33

            if self.NumFilas <= 4:
                self.Condiciones.config(height=self.Condiciones["height"]+1)
                self.yCondiciones -= 26

        self.MasBoton.config(state="normal")

        self.FrameFilas.config(height=self.FrameFilas.winfo_height()-31)
        self.Canvas.config(scrollregion=self.Canvas.bbox("all"))

        self.NumFilas -= 1
        self.NumFilasLabel.config(text=self.NumFilas)
        
        self.CondicionesLabel.place(y=self.yCondicionesLabel)
        self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)
        self.FrameBordeOrderBy.place(y=self.yCondicionesLabel-6)
        self.Canvas.place(y=self.yCanvas)

        self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-1].destroy()

        self.MasBoton.place(x=250+(len(str(self.NumFilas))-1)*15)

        if self.NumFilas == 1:self.MenosBoton.config(state="disabled")

        if self.IntVarCondiciones.get() == 1:

            if self.NumFilas == 3:self.yScrollBarFilas.pack_forget()

        else:

            if self.NumFilas == 11:self.yScrollBarFilas.pack_forget()

        if self.IntVarCondiciones.get() == 1:self.Condiciones.place(y=self.yCondiciones)

    def __EjecutarSelect(self):

        CamposIncompletos = False
        
        if len(self.Tabla.get()) == 0:CamposIncompletos = True
        
        for i in self.FrameFilas.winfo_children():
            if len(i.get()) == 0:CamposIncompletos = True

        if len(self.Condiciones.get("1.0","end-1c")) == 0 and self.IntVarCondiciones.get() == 1:CamposIncompletos = True

        if not CamposIncompletos:
            
            try:
                Tiempo = time.time()
                bd.Cursor.execute("SELECT {} FROM {}{}{};".format(
                                    # Columnas
                                    ", ".join([i.get() for i in self.FrameFilas.winfo_children()]),
                                    # Tabla
                                    self.Tabla.get(),
                                    # Condiciones
                                    ((" WHERE " + self.Condiciones.get("1.0","end-1c").strip(";") if not self.Condiciones.get("1.0","end-1c").upper().startswith("WHERE") else " " + self.Condiciones.get("1.0","end-1c").strip(";")) if self.IntVarCondiciones.get() == 1 else ""),
                                    # Order by
                                    self.VarOrderBy))
                                    
                self.ContenidoConsulta = bd.Cursor.fetchall()

                self.__MostrarConsulta()

                messagebox.showinfo(NOMBRE_APP,f"Consulta realizada con éxito:\n\n{bd.Cursor.statement}\n\nFilas encontradas: {len(self.ContenidoConsulta)}\n\nConsulta realizada en: {str(time.time()-Tiempo)[:5]} segundos.")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

    def __MostrarConsulta(self):

        for i in range(len(self.ContenidoConsulta)):
            self.ContenidoConsulta[i] = list(self.ContenidoConsulta[i])

            for j in self.ContenidoConsulta[i]:
                if j is None:
                    self.ContenidoConsulta[i][self.ContenidoConsulta[i].index(None)] = "NULL"

        ColumnasTreeView = []

        for i in bd.Cursor.description:ColumnasTreeView.append(i[0])

        tk.Frame(self.MainFrame,height=750,width=925,bg="white").place(x=0,y=30)
        self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1].pack_propagate(False)

        Treeview = ttk.Treeview(self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1],style="mystyle.Treeview",columns=ColumnasTreeView,height=16)
        Treeview.pack(side="left",pady=20)

        Treeview.column("#0",width=0,stretch="no")

        for i in range(len(ColumnasTreeView)):Treeview.column(i,width=250,minwidth=100,anchor="center")

        for i in range(len(ColumnasTreeView)):Treeview.heading(i,text=ColumnasTreeView[i])

        for i in range(len(self.ContenidoConsulta)):Treeview.insert("",END,values=self.ContenidoConsulta[i])

        yScrollBar = tk.Scrollbar(root,orient="vertical",command=Treeview.yview)
        yScrollBar.pack(side="right",fill="y")
        xScrollBar = tk.Scrollbar(root,orient="horizontal",command=Treeview.xview)
        xScrollBar.pack(side="bottom",fill="x")

        Treeview.config(yscrollcommand=yScrollBar.set)
        Treeview.config(xscrollcommand=xScrollBar.set)

        tk.Button(root,image=widgets.PantallaCompletaIMG,font=("Helvetica",20),border=0,cursor="hand2",command=lambda:PantallaCompleta()).place(x=838,y=825)

        VolverBoton = tk.Button(root,text="VOLVER",font=("Helvetica",14),border=0,cursor="hand2",bg="white",height=1,width=45,command=lambda:[
            
            self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1].destroy(),
            root.winfo_children()[len(root.winfo_children())-2].destroy(),
            self.MainFrame.config(width=925),
            VolverBoton.destroy(),
            yScrollBar.destroy(),
            xScrollBar.destroy(),
            root.geometry("970x900")
            
        ])

        VolverBoton.pack(side="bottom",pady=7)

        def PantallaCompleta():

            root.geometry("1250x900")

            self.MainFrame.config(width=1208)
            self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1].config(width=1207)

    def __ActualizarValuesFilas(self,event):

        bd.Cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.Tabla.get(),bd.nombre))
        self.FilasValues = bd.Cursor.fetchall()
        self.FilasValues.insert(0,"*")

        for i in self.FrameFilas.winfo_children()[1:]:i.destroy()

        for i in self.FrameFilas.winfo_children():
            i.config(values=self.FilasValues)
            i.config(state="normal")
            i.delete(0,END)
            i.config(state="readonly")

        self.NumFilas = 1
        self.NumFilasLabel.config(text=self.NumFilas)
        self.FrameFilas.config(height=30)

        self.MasBoton.config(state="disabled") if self.NumFilas == len(self.FilasValues)-1 else self.MasBoton.config(state="normal")

        self.MenosBoton.config(state="disabled")
        self.yCondicionesLabel = 278
        self.yCanvas = 233
        self.yCondiciones = 323
        self.Condiciones.config(height=12)
        self.FrameBordeOrderBy.place(y=self.yCondicionesLabel-6)
        self.MasBoton.place(x=250)
        self.Canvas.place(y=233)
        self.CondicionesLabel.place(y=278)
        self.CheckButtonCondiciones.place(y=278)
        self.yScrollBarFilas.pack_forget()
        if self.IntVarCondiciones.get() == 1:self.Condiciones.place(y=323)

    def __ActualizarNumFilas(self,event):

        for i in self.FrameFilas.winfo_children():
            if i.get() == "*":

                for i in self.FrameFilas.winfo_children()[1:]:i.destroy()

                self.FrameFilas.winfo_children()[0].set("*")

                self.NumFilas = 1
                self.NumFilasLabel.config(text=self.NumFilas)

                self.yCondicionesLabel = 278
                self.yCanvas = 233
                self.yCondiciones = 323

                self.FrameFilas.config(height=30)
                self.Condiciones.config(height=12)
                self.MenosBoton.config(state="disabled")
                self.FrameBordeOrderBy.place(y=self.yCondicionesLabel-6)
                self.MasBoton.place(x=250)
                self.Canvas.place(y=233)
                self.CondicionesLabel.place(y=278)
                self.CheckButtonCondiciones.place(y=278)
                if self.IntVarCondiciones.get() == 1:self.Condiciones.place(y=323)
                self.yScrollBarFilas.pack_forget()

                if len(self.FilasValues)-1 > 1:self.MasBoton.config(state="normal")

                self.Canvas.yview_moveto(0)
                
                break

# CREATE
        
class Create():

    def __init__(self):

        
        if not bd.EstadoConexion:

            messagebox.showinfo(MSG_ATENCION,MSG_SIN_CONEXION)
            
        else:

            self.__IniciarCreate()

            self.__IniciarCreateTabla()

    def __IniciarCreate(self):

        self.MainFrame = tk.Frame(root,height=846,width=948)
        self.MainFrame.place(x=20,y=37)
        self.MainFrame.pack_propagate(False)

        self.CREATEmenubutton = ttk.Menubutton(self.MainFrame)
        self.CREATEmenubutton.pack(pady=40)

        self.CREATEmenu = tk.Menu(self.CREATEmenubutton,tearoff=0,font=("Helvetica",12))
        self.CREATEmenu.add_command(label="Tabla",command=self.__IniciarCreateTabla)
        self.CREATEmenu.add_command(label="Trigger",command=self.__IniciarCreateTrigger)
        self.CREATEmenu.add_command(label="Indice",command=self.__IniciarCreateIndice)
        self.CREATEmenu.add_command(label="Vista",command=self.__IniciarCreateVista)
        self.CREATEmenu.add_command(label="Procedimiento",command=self.__IniciarCreateProcedimiento)
        self.CREATEmenubutton.configure(menu=self.CREATEmenu)

    #TABLA

    def __IniciarCreateTabla(self):

        for i in self.MainFrame.winfo_children()[1:]:i.destroy()

        self.CREATEmenubutton.config(text="TABLA")
        self.NumFilasTabla = 1
        self.RowTabla = 0
        self.ColumnTabla = 0

        self.CanvasTabla = tk.Canvas(self.MainFrame,width=820,highlightthickness=0)
        self.CanvasTabla.place(x=50,y=300)
        self.CanvasTabla.bind("<Configure>",lambda event:self.CanvasTabla.config(scrollregion=self.CanvasTabla.bbox("all")))

        self.FrameFilasTabla = tk.Frame(self.CanvasTabla,height=30,width=820)
        self.CanvasTabla.create_window((0,0),window=self.FrameFilasTabla,anchor="nw")

        tk.Label(self.MainFrame,text="Nombre Tabla:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Columna(s):                                              Tipo:",font=("Helvetica",14)).place(x=50,y=245)
        self.NumFilasLabelTabla = tk.Label(self.MainFrame,text=self.NumFilasTabla,font=("Helvetica",14),justify="center")
        self.NumFilasLabelTabla.place(x=225,y=245)
        self.yScrollBarTabla = tk.Scrollbar(self.MainFrame,orient="vertical",command=self.CanvasTabla.yview)
        self.yScrollBarTabla.pack(side="right",fill="y")
        self.CanvasTabla.config(yscrollcommand=self.yScrollBarTabla.set)
        self.NombreTabla = tk.Entry(self.MainFrame,font=("Helvetica",14),width=31)
        self.NombreTabla.place(x=50,y=185)
        self.NombreTabla.focus()
        self.MenosBotonTabla = tk.Button(self.MainFrame,text="<",font=("Helvetica",14),command=self.__MenosTabla,border=0,state="disabled")
        self.MenosBotonTabla.place(x=188,y=242)
        self.MasBotonTabla = tk.Button(self.MainFrame,text=">",font=("Helvetica",14),command=self.__MasTabla,border=0)
        self.MasBotonTabla.place(x=250,y=242)
        tk.Entry(self.FrameFilasTabla,font=("Helvetica",14),justify="center",width=32).grid(column=self.ColumnTabla,row=self.RowTabla)
        self.ColumnTabla += 1
        tk.Entry(self.FrameFilasTabla,font=("Helvetica",14),justify="center",width=32).grid(column=self.ColumnTabla,row=self.RowTabla)
        self.RowTabla += 1
        self.ColumnTabla = 0

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__CrearTabla())
        root.bind("<Control-E>",lambda event:self.__CrearTabla())

        tk.Button(self.MainFrame,text="CREAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__CrearTabla).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__LimpiarTabla).place(x=600,y=700)

    def __LimpiarTabla(self):

        self.NombreTabla.delete(0,END)
        for i in self.FrameFilasTabla.winfo_children():i.delete(0,END)

    def __MasTabla(self):

        self.MenosBotonTabla.config(state="normal")

        self.FrameFilasTabla.config(height=self.FrameFilasTabla.winfo_height()+33)
        self.CanvasTabla.config(scrollregion=self.CanvasTabla.bbox("all"))

        self.NumFilasTabla += 1
        self.NumFilasLabelTabla.config(text=self.NumFilasTabla)

        tk.Entry(self.FrameFilasTabla,font=("Helvetica",14),justify="center",width=32).grid(column=self.ColumnTabla,row=self.RowTabla)
        self.ColumnTabla += 1
        tk.Entry(self.FrameFilasTabla,font=("Helvetica",14),justify="center",width=32).grid(column=self.ColumnTabla,row=self.RowTabla)
        self.RowTabla += 1
        self.ColumnTabla = 0

        self.MasBotonTabla.place(x=250+(len(str(self.NumFilasTabla))-1)*15)

        if self.NumFilasTabla == 99:self.MasBotonTabla.config(state="disabled")
                
    def __MenosTabla(self):

        self.MasBotonTabla.config(state="normal")

        self.FrameFilasTabla.config(height=self.FrameFilasTabla.winfo_height()-33)
        self.CanvasTabla.config(scrollregion=self.CanvasTabla.bbox("all"))

        self.NumFilasTabla -= 1
        self.NumFilasLabelTabla.config(text=self.NumFilasTabla)

        for i in self.FrameFilasTabla.winfo_children()[len(self.FrameFilasTabla.winfo_children())-2:]:i.destroy()

        self.MasBotonTabla.place(x=250+(len(str(self.NumFilasTabla))-1)*15)

        if self.NumFilasTabla == 1:self.MenosBotonTabla.config(state="disabled")

    def __CrearTabla(self):

        ContenidoNombreTabla = self.NombreTabla.get()
        CamposIncompletos = False

        for i in self.FrameFilasTabla.winfo_children():
            if len(i.get()) == 0:
                CamposIncompletos = True
                break

        if len(ContenidoNombreTabla) == 0:CamposIncompletos = True

        if not CamposIncompletos:

            vals = ""
            lista = [i.get() + " " for i in self.FrameFilasTabla.winfo_children()]
            for i in range(0,len(lista),2):vals += lista[i] + lista[i+1] + ("," if not i+2 == len(lista) else "")

            try:
                bd.Cursor.execute("CREATE TABLE {} ({})".format(
                            # Nombre
                            self.NombreTabla.get(),
                            # Columnas
                            vals))

                self.MainFrame.destroy()

                messagebox.showinfo(NOMBRE_APP,f"Tabla '{ContenidoNombreTabla}' creada con éxito.")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)
    
    # TRIGGER

    def __IniciarCreateTrigger(self):
        
        for i in self.MainFrame.winfo_children()[1:]:i.destroy()

        self.CREATEmenubutton.config(text="TRIGGER")

        tk.Label(self.MainFrame,text="Nombre Trigger:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Tabla:",font=("Helvetica",14)).place(x=50,y=185)
        tk.Label(self.MainFrame,text="Momento:",font=("Helvetica",14)).place(x=50,y=245)
        tk.Label(self.MainFrame,text="Evento:",font=("Helvetica",14)).place(x=50,y=305)
        tk.Label(self.MainFrame,text="Instrucción:",font=("Helvetica",14)).place(x=50,y=365)
        self.NombreTrigger = tk.Entry(self.MainFrame,font=("Helvetica",14),width=31)
        self.NombreTrigger.place(x=260,y=125)
        self.NombreTrigger.focus()
        bd.Cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.tables WHERE TABLE_SCHEMA='{}' AND TABLE_TYPE='BASE TABLE'".format(bd.nombre))
        self.TablaTrigger = ttk.Combobox(self.MainFrame,values=[i for i in bd.Cursor],font=("Helvetica",13),state="readonly",width=32)
        self.TablaTrigger.place(x=260,y=185)
        self.Momento = ttk.Combobox(self.MainFrame,values=["After","Before"],font=("Helvetica",13),state="readonly",width=32)
        self.Momento.place(x=260,y=245)
        self.Evento = ttk.Combobox(self.MainFrame,values=["Insert","Update","Delete"],font=("Helvetica",13),state="readonly",width=32)
        self.Evento.place(x=260,y=305)
        self.InstruccionTrigger = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),height=10,width=45,undo=True)
        self.InstruccionTrigger.place(x=260,y=365)

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__CrearTrigger())
        root.bind("<Control-E>",lambda event:self.__CrearTrigger())
        self.InstruccionTrigger.bind("<space>",lambda event:self.InstruccionTrigger.edit_separator())
        self.InstruccionTrigger.bind("<Control-y>",lambda event:exec("try:self.InstruccionTrigger.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionTrigger.bind("<Control-Y>",lambda event:exec("try:self.InstruccionTrigger.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionTrigger.bind("<Control-c>",lambda event:copy(self.InstruccionTrigger.selection_get() if self.InstruccionTrigger.tag_ranges("sel") else ""))
        self.InstruccionTrigger.bind("<Control-C>",lambda event:copy(self.InstruccionTrigger.selection_get() if self.InstruccionTrigger.tag_ranges("sel") else ""))
        self.InstruccionTrigger.bind("<Control-v>",lambda event:paste())
        self.InstruccionTrigger.bind("<Control-V>",lambda event:paste())
        self.InstruccionTrigger.bind("<Control-l>",lambda event:self.InstruccionTrigger.delete("1.0","end-1c"))
        self.InstruccionTrigger.bind("<Control-L>",lambda event:self.InstruccionTrigger.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="CREAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__CrearTrigger).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=lambda:self.__LimpiarTrigger).place(x=600,y=700)

    def __LimpiarTrigger(self):

        self.NombreTrigger.delete(0,END)

        for i in self.MainFrame.winfo_children()[7:10]:
            i.config(state="normal")
            i.delete(0,END)
            i.config(state="readonly")

        self.InstruccionTrigger.delete("1.0","end-1c")

    def __CrearTrigger(self):

        ContenidoNombreTrigger = self.NombreTrigger.get()
        CamposIncompletos = False

        for i in self.MainFrame.winfo_children()[7:10]:
            if len(i.get()) == 0:
                CamposIncompletos = True
                break

        if len(self.InstruccionTrigger.get("1.0","end-1c")) == 0:CamposIncompletos = True

        if not CamposIncompletos:

            try:
                bd.Cursor.execute("CREATE TRIGGER {} {} {} ON {} FOR EACH ROW BEGIN {}; END;".format(
                                # Nombre
                                ContenidoNombreTrigger,
                                # Momento
                                self.Momento.get(),
                                # Evento
                                self.Evento.get(),
                                # Tabla
                                self.TablaTrigger.get(),
                                # Instruccion
                                self.InstruccionTrigger.get('1.0','end-1c').strip(";")))

                self.MainFrame.destroy()

                messagebox.showinfo(NOMBRE_APP,f"Trigger '{ContenidoNombreTrigger}' creado con éxito")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

    #INDICE

    def __IniciarCreateIndice(self):

        for i in self.MainFrame.winfo_children()[1:]:i.destroy()

        self.CREATEmenubutton.config(text="INDICE")
        self.NumFilasIndice = 1
        
        self.CanvasIndice = tk.Canvas(self.MainFrame,height=264,width=651,highlightthickness=0)
        self.CanvasIndice.place(x=50,y=360)

        self.yScrollBarIndice = tk.Scrollbar(self.MainFrame,orient="vertical",command=self.CanvasIndice.yview)
        self.yScrollBarIndice.pack(side="right",fill="y")
        self.CanvasIndice.config(yscrollcommand=self.yScrollBarIndice.set)
        self.CanvasIndice.bind("<Configure>",lambda event:self.CanvasIndice.config(scrollregion=self.CanvasIndice.bbox("all")))

        self.FrameFilasIndice = tk.Frame(self.CanvasIndice,height=30,width=651)
        self.CanvasIndice.create_window((0,0),window=self.FrameFilasIndice,anchor="nw")

        tk.Label(self.MainFrame,text="Columna(s):",font=("Helvetica",14)).place(x=50,y=305)
        tk.Label(self.MainFrame,text="Tipo:",font=("Helvetica",14)).place(x=50,y=245)
        tk.Label(self.MainFrame,text="Nombre Índice:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Tabla:",font=("Helvetica",14)).place(x=50,y=185)
        self.NumFilasLabelIndice = tk.Label(self.MainFrame,text=self.NumFilasIndice,font=("Helvetica",14))
        self.NumFilasLabelIndice.place(x=225,y=305)
        self.NombreIndice = tk.Entry(self.MainFrame,font=("Helvetica",14),width=34)
        self.NombreIndice.place(x=260,y=125)
        self.NombreIndice.focus()
        bd.Cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.tables WHERE TABLE_SCHEMA='{}' AND TABLE_TYPE='BASE TABLE'".format(bd.nombre))
        self.TablaIndice = ttk.Combobox(self.MainFrame,font=("Helvetica",14),values=[i for i in bd.Cursor],state="readonly",width=32)
        self.TablaIndice.place(x=260,y=185)
        self.Tipo = ttk.Combobox(self.MainFrame,font=("Helvetica",14),values=["Unique","Index","Primary"],state="readonly",width=32)
        self.Tipo.place(x=260,y=245)
        self.MenosBotonIndice = tk.Button(self.MainFrame,text="<",font=("Helvetica",14),command=self.__MenosIndice,border=0,state="disabled")
        self.MenosBotonIndice.place(x=188,y=302)
        self.MasBotonIndice = tk.Button(self.MainFrame,text=">",font=("Helvetica",14),command=self.__MasIndice,border=0)
        self.MasBotonIndice.place(x=250,y=302)
        ttk.Combobox(self.FrameFilasIndice,font=("Helvetica",14),state="readonly",width=48).pack()

        self.TablaIndice.bind("<<ComboboxSelected>>",self.__ActualizarValuesFilas)
        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__CrearIndice())
        root.bind("<Control-E>",lambda event:self.__CrearIndice())

        tk.Button(self.MainFrame,text="CREAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__CrearIndice).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__LimpiarIndice).place(x=600,y=700)

    def __LimpiarIndice(self):

        self.NombreIndice.delete(0,END)

        for i in self.FrameFilasIndice.winfo_children():
            i.config(values=[])
            i.config(state="normal")
            i.delete(0,END)
            i.config(state="readonly")

        for i in self.MainFrame.winfo_children()[9:11]:
            i.config(state="normal")
            i.delete(0,END)
            i.config(state="readonly")

        self.MasBotonIndice.config(state="normal")
            
    def __MasIndice(self):

        if len(self.TablaIndice.get()) == 0:
            messagebox.showinfo(MSG_ATENCION,MSG_SELECCIONE_TABLA)

        else:
            self.MenosBotonIndice.config(state="normal")

            self.FrameFilasIndice.config(height=self.FrameFilasIndice.winfo_height()+33)
            self.CanvasIndice.config(scrollregion=self.CanvasIndice.bbox("all"))

            self.NumFilasIndice += 1
            self.NumFilasLabelIndice.config(text=self.NumFilasIndice)
            
            ttk.Combobox(self.FrameFilasIndice,font=("Helvetica",14),state="readonly",width=48,values=self.FilasValues).pack()

            self.MasBotonIndice.place(x=250+(len(str(self.NumFilasIndice))-1)*15)

            if self.NumFilasIndice == len(self.FilasValues):self.MasBotonIndice.config(state="disabled")

    def __MenosIndice(self):

        self.MasBotonIndice.config(state="normal")
        self.FrameFilasIndice.config(height=self.FrameFilasIndice.winfo_height()-33)
        self.CanvasIndice.config(scrollregion=self.CanvasIndice.bbox("all"))
        self.NumFilasIndice -= 1
        self.NumFilasLabelIndice.config(text=self.NumFilasIndice)

        for i in self.FrameFilasIndice.winfo_children()[len(self.FrameFilasIndice.winfo_children())-1]:i.destroy()

        self.MasBotonIndice.place(x=250+(len(str(self.NumFilasIndice))-1)*15)

        if self.NumFilasIndice == 1:self.MenosBotonIndice.config(state="disabled")

    def __CrearIndice(self):

        ContenidoNombreIndice = self.NombreIndice.get()
        CamposIncompletos = False

        for i in self.MainFrame.winfo_children()[8:11]:
            if len(i.get()) == 0:CamposIncompletos = True

        for i in self.FrameFilasIndice.winfo_children():
            if len(i.get()) == 0:
                CamposIncompletos = True
                break

        if not CamposIncompletos:

            if self.Tipo.get() == "Unique":

                CrearIndiceConsulta = f"CREATE UNIQUE INDEX {ContenidoNombreIndice} ON {self.TablaIndice.get()} ({', '.join([i.get() for i in self.FrameFilasIndice.winfo_children()])})"

            if self.Tipo.get() == "Index":

                CrearIndiceConsulta = f"CREATE INDEX {ContenidoNombreIndice} ON {self.TablaIndice.get()} ({', '.join([i.get() for i in self.FrameFilasIndice.winfo_children()])})"

            if self.Tipo.get() == "Primary":

                CrearIndiceConsulta = f"ALTER TABLE {self.TablaIndice.get()} ADD PRIMARY KEY ({', '.join([i.get() for i in self.FrameFilasIndice.winfo_children()])})"

            try:
                bd.Cursor.execute(CrearIndiceConsulta)
                self.MainFrame.destroy()

                messagebox.showinfo(NOMBRE_APP,f"Índice '{ContenidoNombreIndice}' creado con éxito.")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else: 
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

    def __ActualizarValuesFilas(self,event):


        bd.Cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.TablaIndice.get(),bd.nombre))
        self.FilasValues = bd.Cursor.fetchall()

        for i in self.FrameFilasIndice.winfo_children()[1:]:i.destroy()

        for i in self.FrameFilasIndice.winfo_children():
            i.config(values=self.FilasValues)
            i.config(state="normal")
            i.delete(0,END)
            i.config(state="readonly")

        self.NumFilasIndice = 1
        self.NumFilasLabelIndice.config(text=self.NumFilasIndice)
        self.FrameFilasIndice.config(height=30)

        self.MasBotonIndice.config(state="disabled") if self.NumFilasIndice == len(self.FilasValues) else self.MasBotonIndice.config(state="normal")

        self.MenosBotonIndice.config(state="disabled")
        self.MasBotonIndice.place(x=250)
        self.CanvasIndice.yview_moveto(0)

    # VISTA

    def __IniciarCreateVista(self):

        for i in self.MainFrame.winfo_children()[1:]:i.destroy()

        self.CREATEmenubutton.config(text="VISTA")

        tk.Label(self.MainFrame,font=("Helvetica",14),text="Nombre Vista:").place(x=50,y=125)
        tk.Label(self.MainFrame,font=("Helvetica",14),text="Instrucción:").place(x=50,y=245)
        self.NombreVista = tk.Entry(self.MainFrame,font=("Helvetica",14),width=32)
        self.NombreVista.place(x=50,y=185)
        self.NombreVista.focus()
        self.InstruccionVista = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),height=12,width=57,undo=True)
        self.InstruccionVista.place(x=50,y=305)

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__CrearVista())
        root.bind("<Control-E>",lambda event:self.__CrearVista())
        self.InstruccionVista.bind("<space>",lambda event:self.InstruccionVista.edit_separator())
        self.InstruccionVista.bind("<Control-y>",lambda event:exec("try:self.InstruccionVista.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionVista.bind("<Control-Y>",lambda event:exec("try:self.InstruccionVista.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionVista.bind("<Control-c>",lambda event:copy(self.InstruccionVista.selection_get() if self.InstruccionVista.tag_ranges("sel") else ""))
        self.InstruccionVista.bind("<Control-C>",lambda event:copy(self.InstruccionVista.selection_get() if self.InstruccionVista.tag_ranges("sel") else ""))
        self.InstruccionVista.bind("<Control-v>",lambda event:paste())
        self.InstruccionVista.bind("<Control-V>",lambda event:paste())
        self.InstruccionVista.bind("<Control-l>",lambda event:self.InstruccionVista.delete("1.0","end-1c"))
        self.InstruccionVista.bind("<Control-L>",lambda event:self.InstruccionVista.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="CREAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__CrearVista).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__LimpiarVista).place(x=600,y=700)

    def __LimpiarVista(self):

        self.NombreVista.delete(0,END)
        self.InstruccionVista.delete("1.0","end-1c")

    def __CrearVista(self):

        ContenidoNombreVista = self.NombreVista.get()

        if (len(ContenidoNombreVista) == 0 or 
            len(self.InstruccionVista.get("1.0","end-1c")) == 0):

            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

        else:

            try:
                bd.Cursor.execute("CREATE VIEW {} AS {}".format(
                                # Nombre
                                ContenidoNombreVista,
                                # Instruccion
                                self.InstruccionVista.get('1.0','end-1c')))

                self.MainFrame.destroy()

                messagebox.showinfo(NOMBRE_APP,f"Vista '{ContenidoNombreVista}' creada con éxito.")

            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

    # PROCEDIMIENTO

    def __IniciarCreateProcedimiento(self):

        for i in self.MainFrame.winfo_children()[1:]:i.destroy()

        self.CREATEmenubutton.config(text="PROC")
        self.NumFilasProc = 0
        self.RowProc = 0
        self.ColumnProc = 0
        self.yInstruccionLabelPos = 245
        self.yInstruccionPos = 305

        self.CanvasProc = tk.Canvas(self.MainFrame,width=820,height=123,highlightthickness=0)
        self.CanvasProc.place(x=50,y=230)
        self.CanvasProc.bind("<Configure>",lambda event:self.CanvasProc.config(scrollregion=self.CanvasProc.bbox("all")))

        self.FrameFilasProc = tk.Frame(self.CanvasProc,height=0,width=820)
        self.CanvasProc.create_window((0,0),window=self.FrameFilasProc,anchor="nw")

        self.yScrollBarProc = tk.Scrollbar(self.MainFrame,orient="vertical",command=self.CanvasProc.yview)
        self.yScrollBarProc.pack(side="right",fill="y")
        self.CanvasProc.config(yscrollcommand=self.yScrollBarProc.set)
        tk.Label(self.MainFrame,font=("Helvetica",14),text="Nombre Procedimiento:").place(x=50,y=125)
        tk.Label(self.MainFrame,font=("Helvetica",14),text="Parametro(s):                                            Tipo:").place(x=50,y=185)
        self.NumFilasLabelProc = tk.Label(self.MainFrame,text=self.NumFilasProc,font=("Helvetica",14))
        self.NumFilasLabelProc.place(x=225,y=187)
        self.InstruccionProcLabel = tk.Label(self.MainFrame,font=("Helvetica",14),text="Instrucción:")
        self.InstruccionProcLabel.place(x=50,y=245)
        self.NombreProc = tk.Entry(self.MainFrame,font=("Helvetica",14),width=32)
        self.NombreProc.place(x=350,y=125)
        self.NombreProc.focus()
        self.MenosBotonProc = tk.Button(self.MainFrame,text="<",font=("Helvetica",14),border=0,state="disabled",command=self.__MenosProc)
        self.MenosBotonProc.place(x=188,y=184)
        self.MasBotonProc = tk.Button(self.MainFrame,text=">",font=("Helvetica",14),border=0,command=self.__MasProc)
        self.MasBotonProc.place(x=250,y=184)
        self.InstruccionProc = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),height=12,width=57,undo=True)
        self.InstruccionProc.place(x=50,y=305)

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__CrearProc())
        root.bind("<Control-E>",lambda event:self.__CrearProc())
        self.InstruccionProc.bind("<space>",lambda event:self.InstruccionProc.edit_separator())
        self.InstruccionProc.bind("<Control-y>",lambda event:exec("try:self.InstruccionProc.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionProc.bind("<Control-Y>",lambda event:exec("try:self.InstruccionProc.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionProc.bind("<Control-c>",lambda event:copy(self.InstruccionProc.selection_get() if self.InstruccionProc.tag_ranges("sel") else ""))
        self.InstruccionProc.bind("<Control-C>",lambda event:copy(self.InstruccionProc.selection_get() if self.InstruccionProc.tag_ranges("sel") else ""))
        self.InstruccionProc.bind("<Control-v>",lambda event:paste())
        self.InstruccionProc.bind("<Control-V>",lambda event:paste())
        self.InstruccionProc.bind("<Control-l>",lambda event:self.InstruccionProc.delete("1.0","end-1c"))
        self.InstruccionProc.bind("<Control-L>",lambda event:self.InstruccionProc.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="CREAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__CrearProc).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__LimpiarProc).place(x=600,y=700)

    def __LimpiarProc(self):

        self.NombreProc.delete(0,END)
        
        for i in self.FrameFilasProc.winfo_children():i.delete(0,END)

        self.InstruccionProc.delete("1.0","end-1c")

    def __MasProc(self):
        
        if self.NumFilasProc < 4:
            self.yInstruccionLabelPos += 29
            self.yInstruccionPos += 26

        self.MenosBotonProc.config(state="normal")

        self.NumFilasProc += 1
        self.NumFilasLabelProc.config(text=self.NumFilasProc)

        self.InstruccionProc.config(height=self.InstruccionProc["height"]-1)
        self.FrameFilasProc.config(height=self.FrameFilasProc.winfo_height()+32)
        self.CanvasProc.config(scrollregion=self.CanvasProc.bbox("all"))

        self.InstruccionProcLabel.place(y=self.yInstruccionLabelPos)
        self.InstruccionProc.place(y=self.yInstruccionPos)

        tk.Entry(self.FrameFilasProc,font=("Helvetica",14),justify="center",width=32).grid(column=self.ColumnProc,row=self.RowProc)
        self.ColumnProc += 1
        tk.Entry(self.FrameFilasProc,font=("Helvetica",14),justify="center",width=32).grid(column=self.ColumnProc,row=self.RowProc)
        self.RowProc += 1
        self.ColumnProc -= 1

        self.MasBotonProc.place(x=250+(len(str(self.NumFilasProc))-1)*15)

        if self.NumFilasProc == 99:self.MasBotonProc.config(state="disabled")

    def __MenosProc(self):

        if self.NumFilasProc <= 4:
            self.yInstruccionLabelPos -= 29
            self.yInstruccionPos -= 26
            
        self.MasBotonProc.config(state="normal")

        self.NumFilasProc -= 1
        self.NumFilasLabelProc.config(text=self.NumFilasProc)

        self.InstruccionProc.config(height=self.InstruccionProc["height"]+1)
        self.FrameFilasProc.config(height=self.FrameFilasProc.winfo_height()-32)
        self.CanvasProc.config(scrollregion=self.CanvasProc.bbox("all"))

        self.InstruccionProcLabel.place(y=self.yInstruccionLabelPos)
        self.InstruccionProc.place(y=self.yInstruccionPos)

        for i in self.FrameFilasProc.winfo_children()[len(self.FrameFilasProc.winfo_children())-2:]:i.destroy()
        self.RowProc -= 1

        self.MasBotonProc.place(x=250+(len(str(self.NumFilasProc))-1)*15)

        if self.NumFilasProc == 0:self.MenosBotonProc.config(state="disabled")

    def __CrearProc(self):

        ContenidoNombreProc = self.NombreProc.get()
        CamposIncompletos = False

        for i in self.FrameFilasProc.winfo_children():
            if len(i.get()) == 0:
                CamposIncompletos = True
                break

        if (len(ContenidoNombreProc) == 0 or
        len(self.InstruccionProc.get("1.0","end-1c")) == 0):CamposIncompletos = True

        if not CamposIncompletos:

            vals = ""
            lista = [i.get() + " " for i in self.FrameFilasProc.winfo_children()]
            for i in range(0,len(lista),2):vals += lista[i] + lista[i+1] + ("," if not i+2 == len(lista) else "")

            try:
                bd.Cursor.execute("CREATE PROCEDURE {} ({}) BEGIN {}; END ;".format(
                                    # Nombre
                                    ContenidoNombreProc,
                                    # Parametros
                                    vals,
                                    # Instruccion
                                    self.InstruccionProc.get('1.0','end-1c').strip(";")))

                self.MainFrame.destroy()

                messagebox.showinfo(NOMBRE_APP,f"Procedimiento '{ContenidoNombreProc}' creado con éxito.")
                
            except mysql.Error as Error:
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

# UPADATE

class Update():

    def __init__(self):
        

        if not bd.EstadoConexion:

            messagebox.showinfo(MSG_ATENCION,MSG_SIN_CONEXION)
            
        else:

            self.__IniciarUpdate()

    def __IniciarUpdate(self):

        self.IntVarCondiciones = tk.IntVar()
        self.NumFilas = 1
        self.yCondicionesLabel = 278
        self.yCondiciones = 323
        self.yCanvas = 233
        self.Row = 0
        self.Column = 0

        self.MainFrame = tk.Frame(root,height=840,width=925)
        self.MainFrame.place(x=20,y=37)
        self.MainFrame.pack_propagate(False)

        self.Canvas = tk.Canvas(self.MainFrame,width=782,height=390,highlightthickness=0)
        self.Canvas.place(x=50,y=233)
        self.Canvas.pack_propagate(False)
        self.Canvas.bind("<Configure>",lambda event:self.Canvas.config(scrollregion=self.Canvas.bbox("all")))
        self.FrameFilas = tk.Frame(self.Canvas,height=32,width=850)
        self.Canvas.create_window((0,0),window=self.FrameFilas,anchor="nw")
        self.yScrollBarFilas = tk.Scrollbar(self.Canvas,orient="vertical",command=self.Canvas.yview)

        tk.Label(self.MainFrame,text="UPDATE",font=("Helvetica",15),border=0,width=8,pady=40).pack()
        tk.Label(self.MainFrame,text="Tabla:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Columna(s):                                             Nuevo:",font=("Helvetica",14)).place(x=50,y=185)
        self.CondicionesLabel = tk.Label(self.MainFrame,text="Condiciones:",font=("Helvetica",14))
        self.CondicionesLabel.place(x=50,y=278)
        self.NumFilasLabel = tk.Label(self.MainFrame,text=self.NumFilas,font=("Helvetica",14),justify="center")
        self.NumFilasLabel.place(x=225,y=183)
        bd.Cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.tables WHERE TABLE_SCHEMA='{}' AND (TABLE_TYPE='BASE TABLE' OR TABLE_TYPE='SYSTEM VIEW')".format(bd.nombre))
        self.Tabla = ttk.Combobox(self.MainFrame,font=("Helvetica",14),values=[i for i in bd.Cursor],width=31,state="readonly")
        self.Tabla.place(x=194,y=125)
        self.MenosBoton = tk.Button(self.MainFrame,text="<",font=("Helvetica",14),border=0,state="disabled",command=self.__Menos)
        self.MenosBoton.place(x=188,y=180)
        self.MasBoton = tk.Button(self.MainFrame,text=">",font=("Helvetica",14),border=0,command=self.__Mas)
        self.MasBoton.place(x=250,y=180)
        ttk.Combobox(self.FrameFilas,font=("Helvetica",14),width=28,state="readonly").grid(column=self.Column,row=self.Row)
        self.Column += 1
        self.FrameFilas.winfo_children()[0].bind("<<ComboboxSelected>>",self.__ActualizarValorCombobox)
        tk.Entry(self.FrameFilas,font=("Helvetica",14),width=28,justify="center").grid(column=self.Column,row=self.Row)
        self.Row += 1
        self.Column = 0
        self.Condiciones = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),width=57,height=12,undo=True)
        self.CheckButtonCondiciones = tk.Checkbutton(self.MainFrame,variable=self.IntVarCondiciones,onvalue=1,offvalue=0,command=self.__MostrarCondiciones)
        self.CheckButtonCondiciones.place(x=200,y=278)
        self.SimularConsultaBoton = tk.Button(self.MainFrame,image=widgets.SimularIMG,border=0,command=self.__SimularConsulta)
        self.SimularConsultaBoton.place(x=250,y=275)
        Hovertip(self.SimularConsultaBoton,text=" Simular Consulta ",hover_delay=300)

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__EjecutarUpdate())
        root.bind("<Control-E>",lambda event:self.__EjecutarUpdate())
        self.Tabla.bind("<<ComboboxSelected>>",self.__ActualizarValuesFilas)
        self.Condiciones.bind("<space>",lambda event:self.Condiciones.edit_separator())
        self.Condiciones.bind("<Control-y>",lambda event:exec("try:self.Condiciones.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.Condiciones.bind("<Control-Y>",lambda event:exec("try:self.Condiciones.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.Condiciones.bind("<Control-c>",lambda event:copy(self.Condiciones.selection_get() if self.Condiciones.tag_ranges("sel") else ""))
        self.Condiciones.bind("<Control-C>",lambda event:copy(self.Condiciones.selection_get() if self.Condiciones.tag_ranges("sel") else ""))
        self.Condiciones.bind("<Control-v>",lambda event:paste())
        self.Condiciones.bind("<Control-V>",lambda event:paste())
        self.Condiciones.bind("<Control-l>",lambda event:self.Condiciones.delete("1.0","end-1c"))
        self.Condiciones.bind("<Control-L>",lambda event:self.Condiciones.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="EJECUTAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__EjecutarUpdate).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__Limpiar).place(x=600,y=700)

    def __MostrarCondiciones(self):

        if self.IntVarCondiciones.get() == 1:

            self.Condiciones.place(x=50,y=self.yCondiciones)
            self.Condiciones.focus()
            
            self.Canvas.config(height=131)

            self.yCanvas = 224 if self.NumFilas >= 4 else 233 - (self.NumFilas-1)*3
            self.Canvas.place(y=self.yCanvas)

            self.yCondicionesLabel = 362 if self.NumFilas >= 4 else 278 + (self.NumFilas-1)*28
            self.CondicionesLabel.place(y=self.yCondicionesLabel)
            self.SimularConsultaBoton.place(y=self.yCondicionesLabel-3)

            self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)

            if self.NumFilas >= 4:
                self.yScrollBarFilas.pack(side="right",fill="y")
                self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)

        else:

            self.Condiciones.place_forget()

            self.yCanvas = 233
            self.yCondicionesLabel = 278 + (self.NumFilas-1)*33 if self.NumFilas <= 12 else 641
            self.Canvas.config(height=390)
            self.Canvas.place(y=self.yCanvas)
            self.CondicionesLabel.place(y=self.yCondicionesLabel)
            self.SimularConsultaBoton.place(y=self.yCondicionesLabel-3)
            self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)

            if self.NumFilas >= 12:
                self.yScrollBarFilas.pack(side="right",fill="y")
                self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)
            else:
                self.yScrollBarFilas.pack_forget()

    def __Limpiar(self):

        self.Tabla.config(state="normal")
        self.Tabla.delete(0,END)
        self.Tabla.config(state="readonly")

        for i in self.FrameFilas.winfo_children():

            if isinstance(i,ttk.Combobox):
                i.config(values=[])
                i.config(state="normal")
                i.delete(0,END)
                i.config(state="readonly")

            else:

                i.delete(0,END)

        self.Condiciones.delete("1.0","end-1c")
        self.MasBoton.config(state="normal")

    def __SimularConsulta(self):

        CamposIncompletos = False

        if len(self.Tabla.get()) == 0:CamposIncompletos = True

        for i in self.FrameFilas.winfo_children():
            if len(i.get()) == 0:CamposIncompletos = True

        if self.IntVarCondiciones.get() == 1:
            if len(self.Condiciones.get("1.0","end-1c")) == 0:CamposIncompletos = True

        if not CamposIncompletos:

            vals = ""
            lista = [i.get() for i in self.FrameFilas.winfo_children()]
            for i in range(0,len(lista),2):
                vals += lista[i] + "=" + ("'" + lista[i+1] + "'" if not lista[i+1] == "NULL" else lista[i+1]) + ("," if not i+2 == len(lista) else "")
            
            try:
                Tiempo = time.time()
                bd.Cursor.execute("UPDATE {} SET {}{};".format(
                                # Tabla
                                self.Tabla.get(),
                                # Columnas/Valores
                                vals,
                                # Condiciones
                                (" " + self.Condiciones.get('1.0','end-1c').strip(";") if self.Condiciones.get('1.0','end-1c').upper().startswith("WHERE") else " WHERE " + self.Condiciones.get('1.0','end-1c').strip(";")) if self.IntVarCondiciones.get() == 1 else ""))
                                    
                bd.Conexion.rollback()

                messagebox.showinfo("Simulación consulta",f"Consulta SQL:\n\n{bd.Cursor.statement}\n\nFilas afectadas: {bd.Cursor.rowcount}\n\nConsulta simulada en: {str(time.time()-Tiempo)[:5]} segundos.")

            except mysql.Error as Error:
                messagebox.showerror("Error","Ha ocurrido un error al simular la consulta:\n{}".format(Error))

        else:
            messagebox.showinfo(MSG_ATENCION,"Por favor complete todos los campos antes de poder simular la consulta.")

    def __Mas(self):

        if len(self.Tabla.get()) == 0:
            messagebox.showinfo(MSG_ATENCION,MSG_SELECCIONE_TABLA)
            
        else:

            if self.IntVarCondiciones.get() == 0:
                        
                if self.NumFilas < 12:
                    self.yCondicionesLabel += 33

                if self.NumFilas < 4:
                    self.yCondiciones += 26
                    self.Condiciones.config(height=self.Condiciones["height"]-1)
            else:
                
                if self.NumFilas < 4:
                    self.Condiciones.config(height=self.Condiciones["height"]-1)
                    self.yCondicionesLabel += 28
                    self.yCondiciones += 26
                    self.yCanvas -= 3

            self.MenosBoton.config(state="normal")

            self.FrameFilas.config(height=self.FrameFilas.winfo_height()+33)
            self.Canvas.config(scrollregion=self.Canvas.bbox("all"))

            self.NumFilas += 1
            self.NumFilasLabel.config(text=self.NumFilas)

            self.CondicionesLabel.place(y=self.yCondicionesLabel)
            self.SimularConsultaBoton.place(y=self.yCondicionesLabel-3)
            self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)
            self.Canvas.place(y=self.yCanvas)

            ttk.Combobox(self.FrameFilas,font=("Helvetica",14),width=28,state="readonly",values=self.FilasValues).grid(column=self.Column,row=self.Row)
            self.Column += 1
            tk.Entry(self.FrameFilas,font=("Helvetica",14),width=28,justify="center").grid(column=self.Column,row=self.Row)
            self.Row += 1
            self.Column = 0

            for i in self.FrameFilas.winfo_children():
                if isinstance(i,ttk.Combobox):i.bind("<<ComboboxSelected>>",self.__ActualizarValorCombobox)

            self.MasBoton.place(x=250+(len(str(self.NumFilas))-1)*15)

            if self.NumFilas == len(self.FilasValues):self.MasBoton.config(state="disabled")

            if self.IntVarCondiciones.get() == 0:

                if self.NumFilas == 12:
                    self.yScrollBarFilas.pack(side="right",fill="y")
                    self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)
            else:

                if self.NumFilas == 4:
                    self.yScrollBarFilas.pack(side="right",fill="y")
                    self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)

            if self.IntVarCondiciones.get() == 1:self.Condiciones.place(y=self.yCondiciones)

    def __Menos(self):

        if self.IntVarCondiciones.get() == 1:

            if self.NumFilas <= 4:
                self.Condiciones.config(height=self.Condiciones["height"]+1)
                self.yCondicionesLabel -= 28
                self.yCondiciones -= 26
                self.yCanvas += 3
        
        else:

            if self.NumFilas <= 12:
                self.yCondicionesLabel -= 33

            if self.NumFilas <= 4:
                self.Condiciones.config(height=self.Condiciones["height"]+1)
                self.yCondiciones -= 26

        self.MasBoton.config(state="normal")

        self.FrameFilas.config(height=self.FrameFilas.winfo_height()-33)
        self.Canvas.config(scrollregion=self.Canvas.bbox("all"))

        self.NumFilas -= 1
        self.NumFilasLabel.config(text=self.NumFilas)

        self.CondicionesLabel.place(y=self.yCondicionesLabel)
        self.SimularConsultaBoton.place(y=self.yCondicionesLabel-3)
        self.CheckButtonCondiciones.place(y=self.yCondicionesLabel)
        self.Canvas.place(y=self.yCanvas)

        for i in self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-2:]:i.destroy()

        self.MasBoton.place(x=250+(len(str(self.NumFilas))-1)*15)

        if self.NumFilas == 1:self.MenosBoton.config(state="disabled")

        if self.IntVarCondiciones.get() == 1:

            if self.NumFilas == 3:self.yScrollBarFilas.pack_forget()

        else:

            if self.NumFilas == 11:self.yScrollBarFilas.pack_forget()

        if self.IntVarCondiciones.get() == 1:self.Condiciones.place(y=self.yCondiciones)

    def __EjecutarUpdate(self):

        CamposIncompletos = False
        
        if len(self.Tabla.get()) == 0:CamposIncompletos = True
        
        for i in self.FrameFilas.winfo_children():
            if len(i.get()) == 0:CamposIncompletos = True

        if self.IntVarCondiciones.get() == 1:
            if len(self.Condiciones.get("1.0","end-1c")) == 0:CamposIncompletos = True

        if not CamposIncompletos:

            vals = ""
            lista = [i.get() for i in self.FrameFilas.winfo_children()]
            for i in range(0,len(lista),2):
                vals += lista[i] + "=" + ("'" + lista[i+1] + "'" if not lista[i+1] == "NULL" else lista[i+1]) + ("," if not i+2 == len(lista) else "")

            try:

                bd.Cursor.execute("SELECT COUNT(*) FROM {} {}".format(
                                    self.Tabla.get(),
                                    (self.Condiciones.get('1.0','end-1c') if self.Condiciones.get('1.0','end-1c').upper().startswith("WHERE") else "WHERE " + self.Condiciones.get('1.0','end-1c')) if self.IntVarCondiciones.get() == 1 else ""))

                FilasAfectadas = bd.Cursor.fetchall()

                bd.Cursor.execute("UPDATE {} SET {} {}".format(
                                # Tabla
                                self.Tabla.get(),
                                # Columnas/Valores
                                vals,
                                # Condiciones
                                (self.Condiciones.get('1.0','end-1c') if self.Condiciones.get('1.0','end-1c').upper().startswith("WHERE") else "WHERE " + self.Condiciones.get('1.0','end-1c')) if self.IntVarCondiciones.get() == 1 else ""))  

                self.MainFrame.destroy()

                Mantener = messagebox.askyesno(NOMBRE_APP,f"Datos actualizados con éxito.\n\nFilas afectadas: {FilasAfectadas[0][0]}.\n\n¿Desea mantener los cambios?")

                if Mantener:

                    bd.Conexion.commit()

                else:

                    bd.Conexion.rollback()

            except mysql.Error as Error:
                bd.Conexion.rollback()
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else:
            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

    def __ActualizarValuesFilas(self,event):
        
        bd.Cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.Tabla.get(),bd.nombre))
        ContenidoFilasValues = bd.Cursor.fetchall()

        bd.Cursor.execute("SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.Tabla.get(),bd.nombre))
        ContenidoTipoDatoFilas = bd.Cursor.fetchall()

        TipoDatoFilas = []
        self.FilasValues = []

        for i in ContenidoTipoDatoFilas:

            i = str(i)[2:len(str(i))-1]
            i = i.replace(",","")
            i = i.replace("'","")
            i = i.replace("None","NULL")
            Pos = i.find(" ") + 1
            i = i[:Pos] + "(" + i[Pos:] + ")"
            TipoDatoFilas.append(i)

        for i,j in zip(ContenidoFilasValues,TipoDatoFilas):
            i = i[0] + "  " + j

            self.FilasValues.append(i)

        for i in self.FrameFilas.winfo_children()[2:]:i.destroy()

        for i in self.FrameFilas.winfo_children():

            if isinstance(i,ttk.Combobox):

                i.config(values=self.FilasValues)
                i.config(state="normal")
                i.delete(0,END)
                i.config(state="readonly")

            else:
                i.delete(0,END)

        self.NumFilas = 1
        self.NumFilasLabel.config(text=self.NumFilas)
        self.FrameFilas.config(height=32)

        self.MasBoton.config(state="disabled") if self.NumFilas == len(self.FilasValues) else self.MasBoton.config(state="normal")

        self.MenosBoton.config(state="disabled")
        self.yCondicionesLabel = 278
        self.yCondiciones = 323
        self.yCanvas = 233
        self.Condiciones.config(height=12)
        self.MasBoton.place(x=250)
        self.Canvas.place(y=233)
        self.CondicionesLabel.place(y=278)
        self.SimularConsultaBoton.place(y=275)
        self.CheckButtonCondiciones.place(y=278)
        self.yScrollBarFilas.pack_forget()

    def __ActualizarValorCombobox(self,event):

        self.FrameFilas.focus_get().set(self.FrameFilas.focus_get().get()[:self.FrameFilas.focus_get().get().find("  ")])

# INSERT
    
class Insert():

    def __init__(self):

        if not bd.EstadoConexion:

            messagebox.showinfo(MSG_ATENCION,MSG_SIN_CONEXION)

        else:

            self.__IniciarInsert()

    def __IniciarInsert(self):

        self.MainFrame = tk.Frame(root,height=840,width=925)
        self.MainFrame.place(x=20,y=37)
        self.MainFrame.pack_propagate(False)

        self.Canvas = tk.Canvas(self.MainFrame,width=776,height=390,highlightthickness=0)
        self.Canvas.place(x=50,y=233)
        self.Canvas.pack_propagate(False)
        self.Canvas.bind("<Configure>",lambda event:self.Canvas.config(scrollregion=self.Canvas.bbox("all")))
        self.FrameFilas = tk.Frame(self.Canvas,height=0,width=850)
        self.Canvas.create_window((0,0),window=self.FrameFilas,anchor="nw")
        self.yScrollBarFilas = tk.Scrollbar(self.Canvas,orient="vertical",command=self.Canvas.yview)

        tk.Label(self.MainFrame,text="INSERT",font=("Helvetica",15),border=0,width=8,pady=40).pack()
        tk.Label(self.MainFrame,text="Tabla:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Columna(s):                                 Valor:",font=("Helvetica",14)).place(x=50,y=185) 
        bd.Cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.tables WHERE TABLE_SCHEMA='{}' AND (TABLE_TYPE='BASE TABLE' OR TABLE_TYPE='SYSTEM VIEW')".format(bd.nombre))
        self.Tabla = ttk.Combobox(self.MainFrame,font=("Helvetica",14),values=[i for i in bd.Cursor],width=31,state="readonly")
        self.Tabla.place(x=194,y=125)
        tk.Label(self.MainFrame,text="Elige una tabla para poder empezar",font=("Helvetica",14),fg="grey",name="templabel").place(relx=0.5,rely=0.5,anchor="center")

        self.Tabla.bind("<<ComboboxSelected>>",self.__ActualizarValuesFilas)
        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__EjecutarInsert())
        root.bind("<Control-E>",lambda event:self.__EjecutarInsert())

        tk.Button(self.MainFrame,text="EJECUTAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__EjecutarInsert).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__Limpiar).place(x=600,y=700)

    def __Limpiar(self):

        for i in range(0,len(self.FrameFilas.winfo_children()),2):

            self.FrameFilas.winfo_children()[i+1].delete(0,END)
            if len(self.FrameFilas.winfo_children()[i].winfo_children()) == 0:self.FrameFilas.winfo_children()[i+1].insert(0,"NULL")

    def __EjecutarInsert(self):

        for i in range(0,len(self.FrameFilas.winfo_children()),2):

            if len(self.FrameFilas.winfo_children()[i+1].get()) == 0 and len(self.FrameFilas.winfo_children()[i].winfo_children()) == 0:
                self.FrameFilas.winfo_children()[i+1].insert(0,"NULL")

        CamposIncompletos = False

        if len(self.Tabla.get()) == 0:CamposIncompletos = True

        for i in self.FrameFilas.winfo_children():
            if isinstance(i,tk.Entry):
                if len(i.get()) == 0:
                    CamposIncompletos = True

        if not CamposIncompletos:

            try:
                bd.Cursor.execute("INSERT INTO {} VALUES ({})".format(
                                    # Tabla
                                    self.Tabla.get(),
                                    # Valores
                                    ",".join([("'" + i.get() + "'" if not i.get() == "NULL" else i.get()) for i in self.FrameFilas.winfo_children() if isinstance(i,tk.Entry)])))

                bd.Conexion.commit()

                self.MainFrame.destroy()
                messagebox.showinfo(NOMBRE_APP,f"Datos insertados correctamente.\n\nFilas insertadas: {bd.Cursor.rowcount}")

            except mysql.Error as Error:

                bd.Conexion.rollback()
                messagebox.showerror("Error",MSG_ERROR.format(Error))

        else:

            messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

    def __ActualizarValuesFilas(self,event):

        self.Column = 0
        self.Row = 0

        for i in self.MainFrame.winfo_children():
            if "templabel" in str(i):
                i.destroy()
                break

        for i in self.FrameFilas.winfo_children():i.destroy()

        self.Canvas.yview_moveto(0)

        bd.Cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.Tabla.get(),bd.nombre))
        ContenidoNombresColumnas = bd.Cursor.fetchall()
        
        bd.Cursor.execute("SELECT IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.Tabla.get(),bd.nombre))
        ContenidoNullable = bd.Cursor.fetchall()

        for i,j in zip(ContenidoNombresColumnas,ContenidoNullable):
            
            k = i[0][:14] + "..." if len(i[0]) > 14 else i[0]
            
            tk.Label(self.FrameFilas,text=k,font=("Helvetica",14),bg="white",width=18).grid(column=self.Column,row=self.Row,pady=7)
            self.Column += 1
            self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-1].pack_propagate(False)

            tk.Entry(self.FrameFilas,font=("Helvetica",14),width=33,justify="center").grid(column=self.Column,row=self.Row,padx=80)
            self.Column = 0
            self.Row += 1

            if j[0] == "NO":
                tk.Label(self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-2],text="*",fg="red",bg="white",font=("Helvetica",14)).pack(side="left")

                if len(k) == 14:
                    k = k[:12] + "..."
                    self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-2].config(text="   " + k)

            else:
                self.FrameFilas.winfo_children()[len(self.FrameFilas.winfo_children())-1].insert(0,"NULL")

        self.FrameFilas.config(height=len(self.FrameFilas.winfo_children())/2*46)
        self.Canvas.config(scrollregion=self.Canvas.bbox("all"))

        bd.Cursor.execute("SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}' ORDER BY ORDINAL_POSITION".format(self.Tabla.get(),bd.nombre))

        TipoDatoColumnas = []

        for i in bd.Cursor:

            i = str(i)[2:len(str(i))-1]
            i = i.replace(",","")
            i = i.replace("'","")
            i = i.replace("None","NULL")
            Pos = i.find(" ") + 1
            i = i[:Pos] + "(" + i[Pos:] + ")"
            TipoDatoColumnas.append(i)

        TipoDatoColumnas = iter(TipoDatoColumnas)

        for i in self.FrameFilas.winfo_children():
            if isinstance(i,tk.Label):
                Hovertip(i,text= " " + next(TipoDatoColumnas) + " ",hover_delay=300)

        for i in self.FrameFilas.winfo_children():i.bind("<FocusIn>",lambda event:SeleccionarTextoEntry())

        for i in self.FrameFilas.winfo_children():i.config(textvariable="")

        if len(self.FrameFilas.winfo_children()) > 24:
            
            self.yScrollBarFilas.pack(side="right",fill="y")
            self.Canvas.config(yscrollcommand=self.yScrollBarFilas.set)

        else:
            self.yScrollBarFilas.pack_forget()

        def SeleccionarTextoEntry():

            self.FrameFilas.focus_get().select_range(0,END)
            self.FrameFilas.focus_get().icursor(END)

# DELETE

class Delete():

    def __init__(self):

        if not bd.EstadoConexion:

            messagebox.showinfo(MSG_ATENCION,MSG_SIN_CONEXION)

        else:

            self.__IniciarDelete()

    def __IniciarDelete(self):

        self.IntVarCondiciones = tk.IntVar()

        self.MainFrame = tk.Frame(root,height=840,width=925)
        self.MainFrame.place(x=20,y=37)
        self.MainFrame.pack_propagate(False)

        tk.Label(self.MainFrame,text="DELETE",font=("Helvetica",15),border=0,width=8,pady=40).pack()
        tk.Label(self.MainFrame,text="Tabla:",font=("Helvetica",14)).place(x=50,y=125)
        tk.Label(self.MainFrame,text="Condiciones:",font=("Helvetica",14)).place(x=50,y=245)
        bd.Cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.tables WHERE TABLE_SCHEMA='{}' AND (TABLE_TYPE='BASE TABLE' OR TABLE_TYPE='SYSTEM VIEW')".format(bd.nombre))
        self.Tabla = ttk.Combobox(self.MainFrame,font=("Helvetica",14),values=[i for i in bd.Cursor],width=31,state="readonly")
        self.Tabla.place(x=50,y=185)
        tk.Checkbutton(self.MainFrame,offvalue=0,onvalue=1,variable=self.IntVarCondiciones,command=self.__MostrarCondiciones).place(x=200,y=245)
        self.Condiciones = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),width=57,height=12,undo=True)
        tk.Button(self.MainFrame,image=widgets.SimularIMG,border=0,command=self.__SimularConsulta).place(x=250,y=243)
        Hovertip(self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1],text=" Simular Consulta ",hover_delay=300)

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__EjecutarDelete())
        root.bind("<Control-E>",lambda event:self.__EjecutarDelete())
        self.Condiciones.bind("<space>",lambda event:self.Condiciones.edit_separator())
        self.Condiciones.bind("<Control-y>",lambda event:exec("try:self.Condiciones.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.Condiciones.bind("<Control-Y>",lambda event:exec("try:self.Condiciones.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.Condiciones.bind("<Control-c>",lambda event:copy(self.Condiciones.selection_get() if self.Condiciones.tag_ranges("sel") else ""))
        self.Condiciones.bind("<Control-C>",lambda event:copy(self.Condiciones.selection_get() if self.Condiciones.tag_ranges("sel") else ""))
        self.Condiciones.bind("<Control-v>",lambda event:paste())
        self.Condiciones.bind("<Control-V>",lambda event:paste())
        self.Condiciones.bind("<Control-l>",lambda event:self.Condiciones.delete("1.0","end-1c"))
        self.Condiciones.bind("<Control-L>",lambda event:self.Condiciones.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="EJECUTAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__EjecutarDelete).place(x=100,y=700)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=17,cursor="hand2",height=2,border=0,bg="white",command=self.MainFrame.destroy).place(x=348,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=17,height=2,cursor="hand2",border=0,bg="white",command=self.__Limpiar).place(x=600,y=700)

    def __MostrarCondiciones(self):

        self.Condiciones.place(x=50,y=305) if self.IntVarCondiciones.get() == 1 else self.Condiciones.place_forget()
        self.Condiciones.focus()

    def __Limpiar(self):

        self.Tabla.config(state="normal")
        self.Tabla.delete(0,END)
        self.Tabla.config(state="readonly")
        self.Condiciones.delete('1.0','end-1c')
        
    def __SimularConsulta(self):

        CamposIncompletos = False

        if len(self.Tabla.get()) == 0:CamposIncompletos = True
        
        if self.IntVarCondiciones.get() == 1:
            if len(self.Condiciones.get('1.0','end-1c')) == 0:CamposIncompletos = True

        if not CamposIncompletos:

            try:
                Tiempo = time.time()
                bd.Cursor.execute("DELETE FROM {}{};".format(
                            # Tabla
                            self.Tabla.get(),
                            # Condiciones
                            (" " + self.Condiciones.get('1.0','end-1c').strip(";") if self.Condiciones.get('1.0','end-1c').upper().startswith("WHERE") else " WHERE " + self.Condiciones.get('1.0','end-1c').strip(";")) if self.IntVarCondiciones.get() == 1 else ""))

                bd.Conexion.rollback()

                messagebox.showinfo("Simulación consulta",f"Consulta SQL:\n\n{bd.Cursor.statement}\n\nFilas afectadas: {bd.Cursor.rowcount}\n\nConsulta simulada en: {str(time.time()-Tiempo)[:5]} segundos.")

            except mysql.Error as Error:
                messagebox.showerror("Error","Ha ocurrido un error al simular la consulta:\n{}".format(Error))

        else:

            messagebox.showinfo(MSG_ATENCION,"Por favor complete todos los campos antes de poder simular la consulta.")

    def __EjecutarDelete(self):

       CamposIncompletos = False

       if len(self.Tabla.get()) == 0:CamposIncompletos = True

       if self.IntVarCondiciones.get() == 1:
        if len(self.Condiciones.get('1.0','end-1c')) == 0:CamposIncompletos = True

       if not CamposIncompletos:

            try:                
                bd.Cursor.execute("SELECT COUNT(*) FROM {} {}".format(
                                    self.Tabla.get(),
                                    (self.Condiciones.get('1.0','end-1c') if self.Condiciones.get('1.0','end-1c').upper().startswith("WHERE") else "WHERE " + self.Condiciones.get('1.0','end-1c')) if self.IntVarCondiciones.get() == 1 else ""))

                FilasAfectadas = bd.Cursor.fetchall()
                
                bd.Cursor.execute(bd.Cursor.execute("DELETE FROM {}{};".format(
                            # Tabla
                            self.Tabla.get(),
                            # Condiciones
                            (" " + self.Condiciones.get('1.0','end-1c').strip(";") if self.Condiciones.get('1.0','end-1c').upper().startswith("WHERE") else " WHERE " + self.Condiciones.get('1.0','end-1c').strip(";")) if self.IntVarCondiciones.get() == 1 else "")))

                self.MainFrame.destroy()

                Mantener = messagebox.askyesno(NOMBRE_APP,f"Datos eliminados con éxito.\n\nFilas afectadas: {FilasAfectadas[0][0]}.\n\n¿Desea mantener los cambios?")

                if Mantener:

                    bd.Conexion.commit()

                else:

                    bd.Conexion.rollback()

            except mysql.Error as Error:
                bd.Conexion.rollback()
                messagebox.showerror("Error",MSG_ERROR.format(Error))

       else:

           messagebox.showinfo(MSG_ATENCION,MSG_CAMPOS_INCOMPLETOS)

# SQL

class Sql():

    def __init__(self):

        if not bd.EstadoConexion:

            messagebox.showinfo(MSG_ATENCION,MSG_SIN_CONEXION)

        else:

            self.__IniciarSql()

    def __IniciarSql(self):

        root.geometry("1250x900")
        self.FramesResultados = []

        self.MainFrame = tk.Frame(root,height=840,width=1208)
        self.MainFrame.place(x=20,y=37)
        self.MainFrame.pack_propagate(False)

        tk.Label(self.MainFrame,text="SQL",font=("Helvetica",15),border=0,width=8,pady=40).pack()
        tk.Label(self.MainFrame,text="Instrucción SQL:",font=("Helvetica",14)).place(x=50,y=125)
        self.InstruccionSql = scrolledtext.ScrolledText(self.MainFrame,font=("Helvetica",14),width=85,height=17,undo=True)
        self.InstruccionSql.place(x=50,y=185)
        self.InstruccionSql.focus()

        root.unbind("<Control-e>")
        root.unbind("<Control-E>")
        root.bind("<Control-e>",lambda event:self.__EjecutarSql())
        root.bind("<Control-E>",lambda event:self.__EjecutarSql())
        self.InstruccionSql.bind("<space>",lambda event:self.InstruccionSql.edit_separator())
        self.InstruccionSql.bind("<Control-y>",lambda event:exec("try:self.InstruccionSql.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionSql.bind("<Control-Y>",lambda event:exec("try:self.InstruccionSql.edit_redo()\nexcept tk.TclError:pass",{"self":self,"tk":tk}))
        self.InstruccionSql.bind("<Control-c>",lambda event:copy(self.InstruccionSql.selection_get() if self.InstruccionSql.tag_ranges("sel") else ""))
        self.InstruccionSql.bind("<Control-C>",lambda event:copy(self.InstruccionSql.selection_get() if self.InstruccionSql.tag_ranges("sel") else ""))
        self.InstruccionSql.bind("<Control-v>",lambda event:paste())
        self.InstruccionSql.bind("<Control-V>",lambda event:paste())
        self.InstruccionSql.bind("<Control-l>",lambda event:self.InstruccionSql.delete("1.0","end-1c"))
        self.InstruccionSql.bind("<Control-L>",lambda event:self.InstruccionSql.delete("1.0","end-1c"))

        tk.Button(self.MainFrame,text="EJECUTAR",font=("Helvetica",14),width=23,height=2,cursor="hand2",border=0,bg="white",command=self.__EjecutarSql).place(x=105,y=700)
        Hovertip(self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1],text=" Ctrl+E ",hover_delay=300)
        tk.Button(self.MainFrame,text="CANCELAR",font=("Helvetica",14),width=23,cursor="hand2",height=2,border=0,bg="white",command=lambda:[self.MainFrame.destroy(),root.geometry("970x900")]).place(x=450,y=700)
        tk.Button(self.MainFrame,text="LIMPIAR",font=("Helvetica",14),width=23,height=2,cursor="hand2",border=0,bg="white",command=lambda:self.InstruccionSql.delete("1.0","end-1c")).place(x=795,y=700)
        Hovertip(self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1],text=" Ctrl+L ",hover_delay=300)

    def __EjecutarSql(self):

        CamposIncompletos = False

        if len(self.InstruccionSql.get('1.0','end-1c')) == 0:CamposIncompletos = True
        
        self.ContenidoConsulta = None

        if not CamposIncompletos:

            try:
                Tiempo = time.time()

                for j in bd.Cursor.execute(self.InstruccionSql.get('1.0','end-1c'),multi=True):
                    if j.with_rows:
                        self.ContenidoConsulta = j.fetchall()
                        self.__MostrarConsulta()

                if self.ContenidoConsulta is not None:

                    self.FramesResultados[0].master.lift()
                    
                    tk.Button(root,text="˂",font=("Helvetica",18),border=0,cursor="hand2",command=self.__Anterior,state="disabled").place(x=132,y=820)
                    tk.Button(root,text="˃",font=("Helvetica",18),border=0,cursor="hand2",command=self.__Siguiente,state=("disabled" if len(self.FramesResultados) == 1 else "normal")).place(x=1075,y=820)

                    self.FrameActual = 0

                    self.yScrollBar = tk.Scrollbar(root,orient="vertical",command=self.FramesResultados[0].yview)
                    self.xScrollBar = tk.Scrollbar(root,orient="horizontal",command=self.FramesResultados[0].xview)
                    self.yScrollBar.pack(side="right",fill="y")
                    self.xScrollBar.pack(side="bottom",fill="x")

                    self.FramesResultados[0].config(yscrollcommand=self.yScrollBar.set)
                    self.FramesResultados[0].config(xscrollcommand=self.xScrollBar.set)

                    self.VolverBoton = tk.Button(root,text="VOLVER",font=("Helvetica",14),border=0,cursor="hand2",bg="white",height=1,width=45,command=self.__Volver)
                    self.VolverBoton.pack(side="bottom",pady=7)


                messagebox.showinfo(NOMBRE_APP,f"Consulta realizada con éxito.\n\nConsulta SQL:\n\n{self.InstruccionSql.get('1.0','end-1c')}\n\nConsulta ejecutada en: {str(time.time()-Tiempo)[:5]} segundos.")
                
            except (mysql.errors.Error,mysql._mysql_connector.MySQLInterfaceError) as Error:
               bd.Conexion.rollback()
               for i in self.FramesResultados:i.destroy()
               for i in root.winfo_children()[9:]:i.destroy()
               self.FramesResultados.clear()
               messagebox.showerror("Error",MSG_ERROR.format(Error)) 

        else:

            messagebox.showinfo(MSG_ATENCION,"Por favor complete el campo.")

    def __MostrarConsulta(self):

        for i in range(len(self.ContenidoConsulta)):
            self.ContenidoConsulta[i] = list(self.ContenidoConsulta[i])

            for j in self.ContenidoConsulta[i]:
                if j is None:
                    self.ContenidoConsulta[i][self.ContenidoConsulta[i].index(None)] = "NULL"

        ColumnasTreeView = []

        for i in bd.Cursor.description:ColumnasTreeView.append(i[0])

        tk.Frame(self.MainFrame,height=750,width=1207,bg="white").place(x=0,y=30)
        self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1].pack_propagate(False)

        self.Treeview = ttk.Treeview(self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1],style="mystyle.Treeview",columns=ColumnasTreeView,height=16)
        self.Treeview.pack(side="left",pady=20)

        self.Treeview.column("#0",width=0,stretch="no")

        for i in range(len(ColumnasTreeView)):self.Treeview.column(i,width=250,minwidth=100,anchor="center")

        for i in range(len(ColumnasTreeView)):self.Treeview.heading(i,text=ColumnasTreeView[i])

        for i in range(len(self.ContenidoConsulta)):self.Treeview.insert("",END,values=self.ContenidoConsulta[i])

        self.FramesResultados.append(self.MainFrame.winfo_children()[len(self.MainFrame.winfo_children())-1].winfo_children()[0])

    def __Volver(self):

        for i in self.FramesResultados:i.master.destroy()
        for i in root.winfo_children()[9:]:i.destroy()
        self.FramesResultados.clear()

    def __Anterior(self):

        self.FrameActual -= 1
        self.FramesResultados[self.FrameActual].master.lift()
        self.yScrollBar.config(command=self.FramesResultados[self.FrameActual].yview)
        self.xScrollBar.config(command=self.FramesResultados[self.FrameActual].xview)
        self.FramesResultados[self.FrameActual].config(yscrollcommand=self.yScrollBar.set)
        self.FramesResultados[self.FrameActual].config(xscrollcommand=self.xScrollBar.set)
        self.FramesResultados[self.FrameActual].yview_moveto(0)
        self.FramesResultados[self.FrameActual].xview_moveto(0)

        root.winfo_children()[10].config(state="normal")
        if self.FrameActual == 0:root.winfo_children()[9].config(state="disabled")

    def __Siguiente(self):

        self.FrameActual += 1
        self.FramesResultados[self.FrameActual].master.lift()
        self.yScrollBar.config(command=self.FramesResultados[self.FrameActual].yview)
        self.xScrollBar.config(command=self.FramesResultados[self.FrameActual].xview)
        self.FramesResultados[self.FrameActual].config(yscrollcommand=self.yScrollBar.set)
        self.FramesResultados[self.FrameActual].config(xscrollcommand=self.xScrollBar.set)
        self.FramesResultados[self.FrameActual].yview_moveto(0)
        self.FramesResultados[self.FrameActual].xview_moveto(0)
        
        root.winfo_children()[9].config(state="normal")
        if self.FrameActual == len(self.FramesResultados)-1:root.winfo_children()[10].config(state="disabled")

bd = BD()
bd.EstadoConexion = False
widgets = Widgets()
            
root.mainloop()