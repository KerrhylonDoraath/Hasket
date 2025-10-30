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
    ##Create object, and establish geometry
    def __init__(self, master):
        self.MODE = "UNDEFINED"
        self.__master = master
        self.OUTPUT_PIPE = self.printOut

    ##Set output to class provided
    def setOutPipe(self, output):
        self.OUTPUT_PIPE = output.printOut

    ##Geometry to load
    def loadPanel(self):
        pass

    ##Geometry to delete
    def unloadPanel(self):
        pass

    ##Output method for window
    def printOut(self, text):
        print(text)


class DebugPanel(EditorText):
    def __init__(self, master):
        EditorText.__init__(self, master)
        self.MODE = "DEBUG"

        self.lab1 = Label(master, text="Will this work?")
        self.lab2 = Label(master, text="Debugging option. If this appears, then we can add our own panels!")

    def loadPanel(self):

##TEXT EDITOR
class EditorFile(EditorText):

    #Designed to be a writeable area for haskell code development
    def __init__(self, master):
        EditorText.__init__(self, master)
        self.MODE = "EDITOR"

        self.__modified = False
        self.__secondaryTextWidget = Text(master, bg="white", fg="black", highlightthickness=1, highlightcolor="black", insertbackground="black")
        self.__secondaryTextWidget.bind("<Control-s>", lambda event: saveScript(FILE_TITLE))
        self.__secondaryTextWidget.bind("<Control-Shift-S>", lambda event: saveScript(saveAsScript))

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

    def setOutPipe(self):
        pass

    def __del__(self):
        pass
    


##TERMINAL
class EditorTerminalOut(EditorText):
    def __init__(self, master):
        EditorText.__init__(self, master)
        self.MODE = "TERMINAL"

        ##Boolean to determine if GHCi is running
        self.RUNNING = False
        ##Thread for GHCi to run
        self.GHCiThread = None
        self.GHCILoc = None

        
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

        ##Now displaying, we can be sure everything we need exists.
        if not self.RUNNING:
            self.startGHCI()
            if not self.RUNNING:
                self.OUTPUT_PIPE("Could not start GHCi. Please run command \\restart to restart GHCi.\n")

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

        if mEntry[0] == "\\":
            self.OUTPUT_PIPE("Command recognised as Hasket command.")
        else:
            ##Pipe entry to GHCi instead
            self.mProcess.stdin.write(mEntry)
            self.mProcess.stdin.flush()
            self.OUTPUT_PIPE(mEntry)                ##pipe it to wanted output
        

    #inherited method
    def printOut(self, pText):
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.insert(END, pText)
        self.__mainTextWidget.config(state="disabled")
        self.__mainTextWidget.see(END)

    #If the terminal out had focus... it doesn't anymore!
    def focusReset(self, *ignore):
        self.__entryLine.focus_set()


    def startGHCI(self):
        valid = False
        if self.GHCILoc == None:
            mPath = self.FindGHCi()
            if mPath != None:
                if os.path.isfile(mPath):
                    valid = True
        if valid:
            self.mProcess = subprocess.Popen([mPath], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.RUNNING = True
            self.GHCiThread = threading.Thread(target=self.updater)
            self.GHCiThread.start()
        else:
            tkinter.messagebox.showerror("Hasket", "GHCi could not be started.")


    def updater(self):
        while self.RUNNING:
            line = self.mProcess.stdout.readline()
            if not line:
                break
            try:
                self.OUTPUT_PIPE(line)
            except Exception as e:
                pass

    def __del__(self):
        self.RUNNING = False
        self.mProcess.stdin.write(" :quit\r\n")
        self.mProcess.stdin.flush()
        self.GHCiThread.join()
        self.mProcess.kill()

    ##CONTINUE_POINT: Have this run ONCE on startup, then get the program to load a CONFIGURATION file
    def FindGHCi(self):
        def getReturn():
            global returnString
            returnString = mEntry.get()
            temp.destroy()

        if tkinter.messagebox.askyesno("GHCi not found", "GHCi was not found in the configuration file, or the configuration file is not present. Would you like to specify where GHCi is located?"):
            
            temp = Toplevel()
            temp.title("Locate GHCi")
            temp.resizable(False, False)
            temp.iconbitmap("HASKET.ico")
            temp.geometry("520x175")
            temp.config(bg="#404040")

            Label(temp, text="Please enter location of GHCi executable").pack(side=TOP, padx=10, pady=(10, 5))

            middleFrame = Frame(temp, background="#404040")
            middleFrame.pack(side=TOP, padx=10)

            mEntry = Entry(middleFrame, width=64)
            mEntry.pack(side=RIGHT, padx=10, pady=(10, 0))

            imgFrame = Frame(middleFrame, background="white", highlightthickness=2, highlightbackground="black", highlightcolor="black")
            imgFrame.pack(side=LEFT, padx=10, pady=10, expand=True)
            
            img = PhotoImage(file="Haskell.png")
            mLabel = Label(imgFrame, image=img)
            mLabel.pack(padx=2, pady=2)

            mBFrame = Frame(temp, bg="#000080")
            mBFrame.pack(side=BOTTOM, pady=(0, 10))

            mSubmitButton = Button(mBFrame, text="Submit", command=lambda: getReturn())
            mSubmitButton.pack(side=LEFT, padx=5, pady=5)

            mCancelButton = Button(mBFrame, text="Cancel", command=lambda: temp.destroy())
            mCancelButton.pack(side=RIGHT, padx=5, pady=5)
            temp.grab_set()
            temp.wait_window()

            try:
                return returnString
            except NameError:
                return None
        else:
            return None


#File Class


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

        self.__root.title(self.CreateWindowTitle())
    
        #Establish the panel drawing space
        self.panelBar = Frame(self.__root, bg="#000080")
        self.panelBar.pack(pady=(20, 0), expand=False, fill=X, padx=30)

        ##And the padding for inside the panel bar
        self.paddingBar = Frame(self.panelBar, bg="#808080")
        self.paddingBar.pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)

        ##Now we create the main drawing area        
        self.drawSpace = Frame(self.__root, bg="#000080")
        self.drawSpace.pack(side=BOTTOM, padx=30, expand=True, fill=BOTH, pady=(0, 30))

        self.__root.bind("<Control-Tab>", lambda e: self.nextPanel())

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

    def nextPanel(self, *ignore):
        mEntry = self.searchDictionary(self.mode)
        mIndex = self.panelDictionaries.index(mEntry)
        mIndex = (mIndex+1) % len(self.panelDictionaries)
        self.swapMode(self.panelDictionaries[mIndex]["ID"])
            

    def setFileTitle(self, fileTitle):
        self.__root.title(self.CreateWindowTitle(fileTitle))

    #Create Window Title
    def CreateWindowTitle(self, scriptName=None):
        originalTitle = "Hasket 1.0"
        if scriptName != None:
            returnTitle = f"{scriptName} - {originalTitle}"
        else:
            returnTitle = originalTitle
        return returnTitle

    def __del__(self):
        for x in self.panelDictionaries:

            x["Class"].__del__()
            del x["Class"]
        


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
            

if __name__ == "__main__":
    mWindow = HasketWindow()
    mWindow.setFileTitle("Untitled")
    
    mWindow.Loop()
    del mWindow
