#############################################################################
#[not yet named project] aims to be a tool that serves as a bridge          #
#       between game writers and programmers                                #
#   Copyright (C) 2018  José Machado                                        #
#                                                                           #
#    This program is free software: you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License as published by   #
#    the Free Software Foundation, either version 3 of the License, or      #
#    (at your option) any later version.                                    #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>. #
#############################################################################

#External libraries
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter.ttk import Combobox, Notebook
import json
import csv
import webbrowser

#Internal libraries
import table as tbl
import spellchecker
import userpreferences as uprefs

#Defining the database and its funtions
class DB:
    def __init__(self):
        self.currentfilename = "autosave.json"
        self.savedbefore = False
        self.phrases = []

    def save(self, filename=None, phrasesdb=[]):
        with open(filename if filename is not None else self.currentfilename, "w") as file:
            json.dump(phrasesdb, file, indent=2)
    
    def export(self, phrasesdb, filename):
        with open(filename, "w") as file:
            fieldnames = ['text', 'category']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for key in phrasesdb.items():
                writer.writerow(key)

#Defining the app and its funtions
class Broccoli:
    def debug(self):
        #This serves merly to test new functions, and see if they're being called when they should
        print("debug was called")

    def __init__(self, db):
        self.phrasesdb = db.phrases
        self.db = db
        self.db.currentfilename = "Untitled.json"

        #Definition of root window
        self.rootwindow = tk.Tk()
        self.rootwindow.iconbitmap(default='img\\broccoli.ico')
        self.rootwindow.title(self.db.currentfilename + " - improved-broccoli")
        self.rootwindow.state("zoomed")

        self.tabcontrol = Notebook(self.rootwindow)

        self.tables = []

        self.assembletopmenu()
        self.landingpage()
        self.assemblestatusbar()

        self.keybinds()

        self.tabcontrol.pack(expand=1, fill="both")

        #Root Window draw
        self.rootwindow.update()
        self.rootwindow.mainloop()
    
    def keybinds(self):
        #File Menu Shortcuts
        self.rootwindow.bind("<Control-n>", lambda event: self.newprojectwindow())
        self.rootwindow.bind("<Control-s>", lambda event: self.savefile())
        self.rootwindow.bind("<Control-S>", lambda event: self.savefileas())
        self.rootwindow.bind("<Control-o>", lambda event: self.openfile())
        self.rootwindow.bind("<Control-e>", lambda event: self.exportfile())
        self.rootwindow.bind("<Control-p>", lambda event: uprefs.PreferencesWindow())

        #Edit Menu Shortcuts
        #self.rootwindow.bind("<Control-z>", lambda event: self.debug()) #Will serve as "undo"
        #self.rootwindow.bind("<Control-y>", lambda event: self.debug()) #Will serve as "redo"

        #Help Menu Shortcuts
        self.rootwindow.bind("<F1>", lambda event: self.showdocumentation())

    def landingpage(self):
        buttonframe = tk.Frame(self.rootwindow)
        buttonframe.pack(expand=1, fill="both")

        self.landing_newproject = tk.Button(buttonframe, text="New Project", padx=5, pady=5)
        self.landing_newproject.bind("<Button-1>", lambda event: self.newprojectwindow())
        self.landing_newproject.pack(expand=1)
        
        self.landing_openproject = tk.Button(buttonframe, text="Open Project", padx=5, pady=5)
        self.landing_openproject.bind("<Button-1>", lambda event: self.openfile())
        self.landing_openproject.pack(expand=1)

        self.landing_help = tk.Button(buttonframe, text="Help", padx=5, pady=5)
        self.landing_help.bind("<Button-1>", lambda event: self.showdocumentation())
        self.landing_help.pack(expand=1)

        self.landingbuttons = [self.landing_newproject, self.landing_openproject, buttonframe]
    
    def newprojectwindow(self):
        padx = 10
        maxcolumns = 100

        self.newprojwindow = tk.Tk()
        self.newprojwindow.resizable(width=tk.FALSE, height=tk.FALSE)
        self.newprojwindow.title("New Project?")
        self.newprojwindow.geometry("%sx%s"%(250, 100))

        tablelabel = tk.Label(self.newprojwindow, text="Table name: ", padx=padx)
        tablelabel.grid(row=0, column=0, sticky=tk.W)
        tableentry = tk.Entry(self.newprojwindow)
        tableentry.grid(row=0, column=1, sticky=tk.W)
        
        columnlabel = tk.Label(self.newprojwindow, text="Columns #: ", padx=padx)
        columnlabel.grid(row=1, column=0, sticky=tk.W)
        self.columnspinbox = tk.Spinbox(self.newprojwindow, from_=1, to_=maxcolumns, state="readonly", command=self.getcolumnnames)
        self.columnspinbox.grid(row=1, column=1, sticky=tk.W)

        confirm_button = tk.Button(self.newprojwindow, text="Confirm", command = lambda: self.newproject(tableentry.get() if tableentry.get() is not "" else "New Table"))
        confirm_button.grid(row=maxcolumns+1, column=0)
        cancel_button = tk.Button(self.newprojwindow, text="Cancel", command = lambda: self.newprojwindow.destroy())
        cancel_button.grid(row=maxcolumns+1, column=1)

        #Window draw
        self.newproject_holder = []
        self.newproject_holder.append(self.newprojwindow)
        self.newprojwindow.update()
        self.newprojwindow.mainloop()

    def getcolumnnames(self):
        for i in self.columnspinbox.get():
            columnlabel = tk.Label(self.newprojwindow, text="Column %d: "%(i))
            columnlabel.grid(row=i, column=0, sticky=tk.W)
            columnentry = tk.Entry(self.newprojwindow)
            columnentry.grid(row=i, column=1, sticky=tk.W)
            self.newprojwindow.update()


    def createtable(self, tablename="New Table", columns=3, titles=["#", "text", "category"]):
        for item in self.landingbuttons:
            item.pack_forget()

        #Creates a new tab and a new table in it
        self.tableframe = tk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.tableframe, text=tablename)

        table = tbl.Table(self.tableframe, titles)
        table.pack(expand=1, fill="both", padx=1,pady=1)
        table._change_index(len(self.phrasesdb) + 1)
        self.tables.append(table)
        table.columns = columns
        table.titles = titles

        tablenameobj = {"Table": tablename}
        self.phrasesdb.append(tablenameobj)

        table.bottom_cells[0]._bottom_entry.bind("<Return>", lambda event: table.bottom_cells[1]._bottom_entry.focus_set())
        table.bottom_cells[1]._bottom_entry.bind("<Return>", lambda event: self.addline(table))

        self.createeditinputs(table)
        self.updatestatusmetrics("Columns: %d | Rows: %d" % (table.columns, len(self.phrasesdb)))
        self.rootwindow.update()

    def createeditinputs(self, table):
        #this will be irrelevant once a better method of implementing the edit is arranjed
        #at that point, this whole def can be deleted
        self.enteryframe = tk.Frame(self.tableframe)
        self.enteryframe.pack(fill=tk.X)

        self.breakindex = tk.Label(self.enteryframe, text="VV Edit line in table VV")
        self.breakindex.grid(row=1, column=0)

        self.indexedittitle = tk.Label(self.enteryframe, text="index")
        self.indexedittitle.grid(row=2, column=0)
        self.edittexttitle = tk.Label(self.enteryframe, text="text")
        self.edittexttitle.grid(row=2, column=1)
        self.editcategorytitle = tk.Label(self.enteryframe, text="category")
        self.editcategorytitle.grid(row=2, column=2)

        self.indexedit = tk.Entry(self.enteryframe)
        self.indexedit.grid(row=3, column=0)
        self.edittext = tk.Entry(self.enteryframe)
        self.edittext.grid(row=3, column=1)
        self.editcategory = tk.Entry(self.enteryframe)
        self.editcategory.grid(row=3, column=2)

        self.indexedit.bind("<Return>", lambda event: self.edittext.focus_set())
        self.edittext.bind("<Return>", lambda event: self.editcategory.focus_set())
        self.editcategory.bind("<Return>", lambda event: self.editline(table))

    def newproject(self, tablename="New Table", columns=3, titles=["#", "text", "category"]):
        if self.newprojwindow is not None:
            self.newprojwindow.destroy()

        newproject = tkinter.messagebox.askquestion("New File?", "Are you sure you want to create a new file?")
        if newproject == "no":
            return

        for item in self.landingbuttons:
            item.pack_forget()

        save = tkinter.messagebox.askquestion("Save?","Do you want to save before you create a new file?")
        if save == "yes":
            self.savefile()

        self.updatestatusprocess("Cleaning table")
        for table in self.tables:
            table._pop_n_rows(len(self.phrasesdb))
            self.tables.pop(table)

        self.updatestatusprocess("Creating new file")
        self.db.currentfilename = "Untitled-1.json"
        self.db.savedbefore = False
        self.phrasesdb = []

        self.updatestatusprocess("")
        self.rootwindow.title(self.db.currentfilename + " - improved-broccoli")

        self.createtable(tablename, columns, titles)

        self.rootwindow.update()

    def openfile(self):
        self.updatestatusprocess("Opening file...")
        f = tk.filedialog.askopenfilename(filetypes=[("json","*.json")])
        if f == '':
            self.rootwindow.title(self.db.currentfilename + " - improved-broccoli")
            return

        self.updatestatusprocess("Cleaning table")
        for table in self.tables:
                    table._pop_n_rows(len(self.phrasesdb))
                    self.tables.pop(table)
        self.phrasesdb = []

        self.updatestatusprocess("Opening file at " + f)
        self.db.currentfilename = f
        self.db.savedbefore = True

        self.updatestatusprocess("")
        self.rootwindow.title(self.db.currentfilename + " - improved-broccoli")
        self.rootwindow.update()

        self.createtable()
        #self.createtable(self.phrasesdb[0]["Table"])

        with open(f if f is not None else self.db.currentfilename, "r") as file:
            data = json.load(file)
            for thing in data:
                newobj = {"text": thing["text"], "category": thing["category"]}
                self.phrasesdb.append(newobj)

                ##This shows new obj on the table
                for table in self.tables:
                    table.insert_row([len(self.phrasesdb), newobj["text"], newobj["category"]])

                for table in self.tables:
                    table.bottom_cells[0]._bottom_entry.delete(0, tk.END)
                    table.bottom_cells[1]._bottom_entry.delete(0, tk.END)

                self.rootwindow.update()

        for item in self.landingbuttons:
            item.pack_forget()

        for table in self.tables:
            table._change_index(len(self.phrasesdb) + 1)
        self.rootwindow.update()

    def savefile(self):
        if self.db.savedbefore:
            self.updatestatusprocess("Saving file to " + self.db.currentfilename)
            self.db.save(self.db.currentfilename, self.phrasesdb)

            self.updatestatusprocess("")
            self.rootwindow.title(self.db.currentfilename + " - improved-broccoli")
            self.rootwindow.update()
        else:
            self.savefileas()

    def savefileas(self):
        self.updatestatusprocess("Saving file...")

        f = tk.filedialog.asksaveasfilename(filetypes=[("json", "*.json")], defaultextension=".json", initialfile=self.db.currentfilename)

        self.updatestatusprocess("Saving file to " + f)

        if f == '':
           return

        self.db.currentfilename = f
        self.db.savedbefore = True
        self.db.save(f, self.phrasesdb)

        self.updatestatusprocess("")
        self.rootwindow.title(self.db.currentfilename + " - improved-broccoli")
        self.rootwindow.update()

    def reportbug(self):
        webbrowser.open("https://github.com/josemachado-dev/improved-broccoli/issues/new/choose", new=2, autoraise=True)
    
    def sendfeedback(self):
        webbrowser.open("https://github.com/josemachado-dev/improved-broccoli/issues/new/choose", new=2, autoraise=True)

    def showdocumentation(self):
        #url should be updated if documentation changes places, for example, a wiki is created
        webbrowser.open("https://github.com/josemachado-dev/improved-broccoli", new=2, autoraise=True)

    def addline(self, table):
        #Add obj to list
        newobj = {"text": table.bottom_cells[0]._bottom_entry.get(), "category": table.bottom_cells[1]._bottom_entry.get()}

        self.phrasesdb.append(newobj)

        table.insert_row([len(self.phrasesdb), newobj["text"], newobj["category"]])

        table.bottom_cells[0]._bottom_entry.delete(0, tk.END)
        table.bottom_cells[1]._bottom_entry.delete(0, tk.END)

        self.updatestatusmetrics("Columns: %d | Rows: %d" % (table.columns, len(self.phrasesdb)))

        table._change_index(len(self.phrasesdb) + 1)

        table.bottom_cells[0]._bottom_entry.focus_set()
        self.rootwindow.update()

    def editline(self, table):
        #Commits the edit of a given line
        self.index = int(self.indexedit.get()) - 1

        if(self.edittext != ""):
            table.cell(self.index, 1, self.edittext.get())

        if(self.editcategory != ""):
            table.cell(self.index, 2, self.editcategory.get())

    def removeline(self, table, n):
        #Remove obj from list, given it's index

        table.delete_row(n)
        self.updatestatusmetrics("Columns: %d | Rows: %d" % (table.columns, len(self.phrasesdb)))

    def exportfile(self):
        self.updatestatusprocess("Exporting file...")
        f = tk.filedialog.asksaveasfilename(filetypes=[("csv", "*.csv")], defaultextension=".csv", initialfile=self.db.currentfilename)

        self.updatestatusprocess("Exporting file to " + f)

        if f == '':
           return

        self.db.export(self.phrasesdb, f) #will need to include a table.titles once i get it working properly

        self.updatestatusprocess("")

    def createfilemenu(self):
        self.filesubmenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.filesubmenu)

        self.filesubmenu.add_command(label="New File    Ctrl+n", command=self.newprojectwindow)

        self.filesubmenu.add_separator()
        self.filesubmenu.add_command(label="Open    Ctrl+o", command=self.openfile)

        self.filesubmenu.add_separator()
        self.filesubmenu.add_command(label="Save    Ctrl+s", command=self.savefile)
        self.filesubmenu.add_command(label="Save As    Ctrl+Shift+s", command=self.savefileas)

        self.filesubmenu.add_separator()
        self.filesubmenu.add_command(label="Export    Ctrl+e", command=self.exportfile)

        self.filesubmenu.add_separator()
        self.filesubmenu.add_command(label="Preferences    Ctrl+p", command= lambda: uprefs.PreferencesWindow())


        self.filesubmenu.add_separator()
        self.filesubmenu.add_command(label="Exit", command=self.rootwindow.destroy)
    
    def createeditmenu(self):
        self.editmenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.editmenu)

        self.editmenu.add_command(label="Undo    Ctrl+z", command=self.debug)
        self.editmenu.add_command(label="Redo    Ctrl+y", command=self.debug)

        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=self.debug)
        self.editmenu.add_command(label="Copy", command=self.debug)
        self.editmenu.add_command(label="Paste", command=self.debug)

    def createhelpmenu(self):
        self.helpmenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)

        self.helpmenu.add_command(label="Report a Bug", command=self.reportbug)
        self.helpmenu.add_command(label="Request a Feature", command=self.sendfeedback)

        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Check documentation    F1", command=self.showdocumentation)

    def assembletopmenu(self):
        self.menu = tk.Menu(self.rootwindow)
        self.rootwindow.config(menu=self.menu)

        self.createfilemenu()
        #self.createeditmenu()
        self.createhelpmenu()

    def assemblestatusbar(self):
        self.statusframe = tk.Frame(self.rootwindow, bd = 1, relief=tk.SUNKEN)
        self.statusframe.pack(side=tk.BOTTOM, fill=tk.X)

        self.statusprocess = tk.Label(self.statusframe, text="", anchor=tk.W)
        self.statusprocess.pack(side=tk.RIGHT)

        self.statusmetrics = tk.Label(self.statusframe, text="Columns: 0 | Rows: 0", anchor=tk.W)
        self.statusmetrics.pack(side=tk.LEFT)
    
    def updatestatusprocess(self, text):
        self.statusprocess.config(text=text)
        self.rootwindow.update()

    def updatestatusmetrics(self, text):
        self.statusmetrics.config(text=text)
        self.rootwindow.update()

db = DB()
broccoli = Broccoli(db)