##hasket.py - A pythonic interface for developing haskell.

#IMPORTS
import sys
import os
import subprocess
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import threading

#Title of the open file
MODIFIED = False
WINDOW_TITLE = ""
#MODE sets the usage of the text widget
MODE = "TERMINAL"
INITIAL_TEXT = ""


##New method for opening a script
def importScript(scriptName):
    with open(scriptName, "r") as importText:
        pass

##TEMPLATE CLASS
class EditorText():
    def __init__(self, master):
        self.MODE = "UNDEFINED"
        self.__master = master

    def setOutPipe(self, output):
        pass

    def loadPanel(self):
        pass

    def unloadPanel(self):
        pass

    def printOut(self, text):
        pass


##TEXT EDITOR
class EditorFile(EditorText):

    #Designed to be a writeable area for haskell code development
    def __init__(self, master):
        self.MODE = "EDITOR"

        self.__modified = False
        self.__secondaryTextWidget = Text(master, bg="white", fg="black", highlightthickness=1, highlightcolor="black", insertbackground="black")
        self.__secondaryTextWidget.bind("<Control-s>", lambda event: saveScript(FILE_TITLE))
        self.__secondaryTextWidget.bind("<Control-Shift-S>", lambda event: saveScript(saveAsScript))
        #self.__secondaryTextWidget.bind("<Key>", ModifiedText)                                         #Binding saving keys

        self.__mScrollbar = Scrollbar(master, orient=VERTICAL, width=20, command=self.__secondaryTextWidget.yview)
        self.__secondaryTextWidget.config(yscrollcommand=self.__mScrollbar.set)

    #inherited method
    def loadPanel(self):
        self.__mScrollbar.pack(side=RIGHT, fill=Y, expand=False, padx=2, pady=(0, 2))
        self.__secondaryTextWidget.pack(side=LEFT, fill=BOTH, expand=True, padx=(2, 0), pady=(0, 2))
        self.__secondaryTextWidget.focus()

    #inherited method
    def unloadPanel(self):
        self.__secondaryTextWidget.pack_forget()
        self.__mScrollbar.pack_forget()


##TERMINAL
class EditorTerminalOut(EditorText):
    def __init__(self, master):
        self.MODE = "TERMINAL"

        ##Create the terminal widgets

        self.__microFrame = Frame(master, highlightthickness=0, highlightcolor = "#000080")
        self.__mainTextWidget = Text(self.__microFrame, width=100, height=20, state="disabled", bg="black", fg="white", highlightthickness=1, highlightcolor="white", insertbackground="white")
        self.__entryLine = Text(master, height=1, bg="black", fg="white", highlightthickness=1, highlightcolor = "white", insertbackground="white")
        self.__entryLine.bind("<Return>", lambda event: self.submitTerminalEntry(event))
        self.__mScrollbar = Scrollbar(self.__microFrame, orient=VERTICAL, width=20, command=self.__mainTextWidget.yview)
        self.__mainTextWidget.config(yscrollcommand=self.__mScrollbar.set)
        self.__mainTextWidget.bind("<FocusIn>", self.focusReset)    #Set binding to only the entry bar

    #inherited method
    def loadPanel(self):
        self.__microFrame.pack(expand=True, fill=BOTH, padx=2, pady=(0, 2))
        self.__entryLine.pack(side=BOTTOM, fill=X, expand=False, padx=2, pady=(5, 2))
        self.__mScrollbar.pack(side=RIGHT, fill=Y, expand=False)
        self.__mainTextWidget.pack(side=LEFT, fill=BOTH, expand=True)
        self.__mainTextWidget.focus()
        self.__entryLine.focus_set()

    #inherited method
    def unloadPanel(self):
        self.__mainTextWidget.pack_forget()
        self.__mScrollbar.pack_forget()
        self.__microFrame.pack_forget()
        self.__entryLine.pack_forget()

    #Input from the user in terminal mode
    def submitTerminalEntry(self, event):
        mEntry = self.__entryLine.get("1.0", END)
        self.__entryLine.delete("0.0", END)         ##Clear the existing terminal code, pulling the entry
        if mEntry[0] == '\n':
            mEntry = mEntry[1:]
        self.OUTPUT_PIPE(mEntry)                ##pipe it to wanted output
        

    #inherited method
    def printOut(self, pText):
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.insert(END, pText)
        self.__mainTextWidget.config(state="disabled")
        self.__mainTextWidget.see(END)

    def setOutPipe(self, output):
        self.OUTPUT_PIPE = output.printOut

    #If the terminal out had focus... it doesn't anymore!
    def focusReset(self, *ignore):
        self.__entryLine.focus_set()

#Main window
class HasketWindow():
    def __init__(self):
        
        self.INACTIVE = "#D0D0D0"
        self.ACTIVE = "#FFFFFF"
        
        self.__fileTitle = "Untitled"
        self.OUPUT_PIPE = None
        self.panels = []
        self.panelDictionaries = []

        self.generateWindow()
        self.generateMenubar()
        
        self.createPanel("TERMINAL", EditorTerminalOut)
        self.createPanel("EDITOR", EditorFile)

        self.loadPanel("TERMINAL")
        self.SetOuptutPipe("TERMINAL")
        
    def createPanel(self, textName, panelClass):
        mTempObject = panelClass(self.drawSpace)
        self.panelDictionaries.append({"ID": textName, "Class": mTempObject, "Label": self.generateEditorPanel(textName)})

    def generateMenubar(self):
        #MENU CONFIGURATION
        self.__mainMenu = Menu(tearoff=0)
        self.__fileMenu = Menu(self.__mainMenu, tearoff=0) 
        self.__mainMenu.add_cascade(menu=self.__fileMenu, label="File")

        #File Menu
        self.__fileMenu.add_command(label="New Script", command=newScript)
        self.__fileMenu.add_command(label="Open Script", command=importScriptEntry)
        self.__fileMenu.add_separator()
        self.__fileMenu.add_command(label="Save", command=lambda: saveScript(FILE_TITLE))
        self.__fileMenu.add_command(label="Save As", command=lambda: saveScript(saveAsScript))
        self.__fileMenu.add_separator()
        self.__fileMenu.add_command(label="Exit", command=self.__root.destroy)
        self.__root.config(menu=self.__mainMenu)


    def generateEditorPanel(self, panelName):
        self.panels.append(Label(self.panelBar, text=panelName, bg=self.INACTIVE, highlightthickness=0))
        self.panels[-1].pack(side=LEFT, padx=2, pady=2)
        self.panels[-1].bind("<Button-1>", lambda event: self.swapMode(panelName))
        return self.panels[-1]

    def generateWindow(self):
        #Initialise the window
        self.__root = Tk()
        self.__root.geometry("800x500")
        self.__root.config(bg="#404040")
        self.__root.iconbitmap("HASKET.ico")
        self.__root.minsize(800, 500)

        #Establish the panel drawing space
        self.panelBar = Frame(self.__root, bg="#000080")
        self.panelBar.pack(pady=(20, 0), expand=False, fill=X, padx=30)

        ##And the padding for inside the panel bar
        self.paddingBar = Frame(self.panelBar, bg="#808080")
        self.paddingBar.pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)

        ##Now we create the main drawing area        
        self.drawSpace = Frame(self.__root, bg="#000080")
        self.drawSpace.pack(side=BOTTOM, padx=30, expand=True, fill=BOTH, pady=(0, 30))

    def searchDictionary(self, nameID):
        for entry in self.panelDictionaries:
            if entry["ID"] == nameID:
                return entry
        return None

    def SetOuptutPipe(self, nameID):
        mEntry = self.searchDictionary(nameID)
        self.OUTPUT_PIPE = mEntry["Class"].printOut

    def Loop(self):
        self.__root.mainloop()

    def pipeOut(self, outputText):
        self.OUTPUT_PIPE(outputText)

    def unloadCurrentPanel(self):
        if self.searchDictionary(self.mode):
            entry = self.searchDictionary(self.mode)
            entry["Class"].unloadPanel()
            entry["Label"].config(bg=self.INACTIVE)

    def loadPanel(self, panelID):
        if self.searchDictionary(panelID):
            entry = self.searchDictionary(panelID)
            entry["Class"].loadPanel()
            self.mode = panelID
            entry["Label"].config(bg=self.ACTIVE)

    def swapMode(self, newPanel):
        self.unloadCurrentPanel()
        self.loadPanel(newPanel)

    def setFileTitle(self, fileTitle):
        self.__root.title(CreateWindowTitle(fileTitle))
        


#IMPORTING HASKELL SCRIPT
def importScriptEntry(*ignore, HasketWindow):
    if SaveCheck():
        saveScript()
    mFile = tkinter.filedialog.askopenfile(filetypes=[("Haskell Scripts", ".hs")])
    if not mFile:
        return
    importScript(mFile.name)



def importScript(scriptName):
    global FILE_TITLE, secondaryTextWidget, mainTextWidget, INITIAL_TEXT
    with open(scriptName, "r") as mEntry:
        FILE_TITLE = scriptName
        secondaryTextWidget.delete("1.0", END)
        x = mEntry.readline()
        while x != "":
            secondaryTextWidget.insert(END, x)
            x = mEntry.readline()
    mainTextWidget.insert(END, f':load "{scriptName}"')
    retrieveInput(True)
    mainTextWidget.edit_modified(False)
    CreateWindowTitle(scriptName)
    INITIAL_TEXT = secondaryTextWidget.get("1.0", END)


#Create Window Title
def CreateWindowTitle(scriptName):
    originalTitle = "Hasket 1.0"
    returnTitle = f"{scriptName} - {originalTitle}"
    return returnTitle

#Modified event callback
def ModifiedText(*ignore):
    global MODIFIED, secondaryTextWidget
    if secondaryTextWidget.get("1.0", END) != INITIAL_TEXT:
        CreateWindowTitle(f"*{FILE_TITLE}")
        MODIFIED = True

#Saving Verification Link
def SaveCheck():
    if MODIFIED:
        return tkinter.messagebox.askyesno("Save Changes", f"Save changes to {FILE_TITLE}?")

#CREATING NEW SCRIPT
def newScript():
    global FILE_TITLE, MODIFIED, secondaryTextWidget, INITIAL_TEXT
    if SaveCheck():
        saveScript()
    FILE_TITLE = "Untitled"
    CreateWindowTitle("Untitled")
    secondaryTextWidget.delete("1.0", END)
    MODIFIED = False
    secondaryTextWidget.edit_modified(False)
    INITIAL_TEXT = secondaryTextWidget.get("1.0", END)

#SAVING SCRIPT
def saveScript(fileName):
    global MODIFIED, INITIAL_TEXT, FILE_TITLE
    if fileName == None or fileName == "Untitled":
        fileName = saveAsScript()
        if fileName == None:
            return
        if fileName[-3:] != ".hs":
            fileName += ".hs"
    with open(fileName, "w") as mFile:
        mFile.write(secondaryTextWidget.get("1.0", END))
    CreateWindowTitle(fileName)
    MODIFIED = False
    INITIAL_TEXT = secondaryTextWidget.get("1.0", END)
    FILE_TITLE = fileName

#SAVE AS SCRIPT
def saveAsScript(*ignore):
    return tkinter.filedialog.asksaveasfilename(filetypes=[("Haskell Scripts", ".hs")])

#MODE SWAP
"""def swapMode(event):
    return


    global MODE, mainTextWidget, secondaryTextWidget
    if event == "EDITOR":
        MODE = "EDITOR"
        ##Sets the editor set
        EditorLabel.config(bg="white")
        TerminalLabel.config(bg="#D0D0D0")
        mainTextWidget.pack_forget()
        secondaryTextWidget.pack(side=LEFT, fill=BOTH, expand=True, padx=(2, 0), pady=(0, 2))
        secondaryTextWidget.focus()
    else:
        if MODIFIED:
            tkinter.messagebox.showwarning("Warning", "Hasket cannot process the updated script until it is saved. It is recommended to go back and save your script.")
        MODE = "TERMINAL"
        ##Sets the terminal set
        EditorLabel.config(bg="#D0D0D0")
        TerminalLabel.config(bg="white")
        secondaryTextWidget.pack_forget()
        mainTextWidget.pack(side=LEFT, fill=BOTH, expand=True, padx=(2, 0), pady=(0, 2))
        mainTextWidget.focus()
"""

def updater():
    global mProcess, RUNNING, mWindow
    while RUNNING:
        line = mProcess.stdout.readline()
        if not line:
            break
        try:
            mWindow.pipeOut(line)
        except Exception as e:
            pass
            
##Reads the last line of the terminal
def retrieveInput(addNewLine=False):
    global mProcess, mainTextWidget
    text = mainTextWidget.get("end-1c linestart", f"end-1c") + "\r\n"
    if ":quit" in text:
        tkinter.messagebox.showwarning("Warning", "Executing this may cause the program to stop running haskell scripts. Command aborted.")
        return
    mainTextWidget.insert(END, "\n" if addNewLine else "")
    try:
        mProcess.stdin.write(text)
        mProcess.stdin.flush()
    except OSError:
        mainTextWidget.insert(END, "\nHASKELL has closed, cannot process command.\n")
    mainTextWidget.see(END)

#SYNTAX HIGHLIGHTING

mWindow = HasketWindow()
mWindow.setFileTitle("Untitled")
    
mProcess = subprocess.Popen(["C:\\HASKELL\\bin\\ghci.exe"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
RUNNING = True
t1 = threading.Thread(target = updater)
t1.start()

"""if len(sys.argv) == 2:
    importScript(sys.argv[1])
else:
    newScript()
"""
mWindow.Loop()

RUNNING = False
try:
    mProcess.stdin.write(" :quit\r\n")
    mProcess.stdin.flush()
except OSError:
    pass
mProcess.kill()
