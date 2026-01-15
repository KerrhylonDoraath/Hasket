##hasket.py - A pythonic interface for developing haskell.

#IMPORTS
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog

from hasketCore.EditorPanel import EditorPanel
from hasketCore.TerminalPanel import EditorTerminalOut

#Title of the open file
MODIFIED = False
WINDOW_TITLE = ""
#MODE sets the usage of the text widget
MODE = "TERMINAL"
INITIAL_TEXT = ""

#Main window
class HasketWindow():
    def __init__(self):
        
        self.INACTIVE = "#D0D0D0"
        self.ACTIVE = "#FFFFFF"
        self.mode = "UNDEFINED"
    
        
        self.__fileTitle = "Untitled"
        self.OUPUT_PIPE = None
        self.panels = []
        self.panelDictionaries = []

        self.generateWindow()
        #self.generateMenubar()
        
        self.createPanel("TERMINAL", EditorTerminalOut)
        self.createPanel("EDITOR", EditorPanel)

        mTerminal = self.searchDictionary("TERMINAL")
        mEntry = self.searchDictionary("EDITOR")

        #mTerminal["Class"].bindEditor(mEntry["Class"])
        #mEntry["Class"].setTitleCommand(self.setFileTitle)

        self.loadConfigFile()

    def loadConfigFile(self):
        ##HaskConf.cfg
        importData = []
        try:
            with open ("HaskConf.cfg", "r") as configFile:
                mData = configFile.readline()
                while mData != "":
                    importData.append(mData)
                    mData = configFile.readline()
        except OSError:
            tkinter.messagebox.showwarning("Warning", "The Hasket configuration file could not be found.")
            return
        blockLoc = False
        for line in importData:
            scanner = ""
            fileString = r""
            mode = "UNKNOWN"
            for x in line:
                scanner += x
                if not blockLoc and scanner == "config:":
                    mode="CONFIG-START"
                    continue
                if mode == "CONFIG-START":
                    if x == " ":
                        continue
                    mode = "CONFIG-READ"
                if mode == "CONFIG-READ":
                    fileString += x
            if mode == "CONFIG-READ":
                if fileString[-1] == "\n":
                    fileString = fileString[:-1]
                terminal = self.searchDictionary("TERMINAL")
                print(fileString)
                if terminal["Class"].startGHCI(fileString):
                    blockLoc = True
        
    def start(self):
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
        """self.__fileMenu.add_command(label="New Script", command=newScript)
        self.__fileMenu.add_command(label="Open Script", command=importScriptEntry)
        self.__fileMenu.add_separator()
        self.__fileMenu.add_command(label="Save", command=lambda: saveScript(FILE_TITLE))
        self.__fileMenu.add_command(label="Save As", command=lambda: saveScript(saveAsScript))
        self.__fileMenu.add_separator()
        self.__fileMenu.add_command(label="Exit", command=self.__root.destroy)
        self.__root.config(menu=self.__mainMenu)"""


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
        self.panelBar.pack(pady=(20, 0), expand=False, fill="x", padx=30)

        ##And the padding for inside the panel bar
        self.paddingBar = Frame(self.panelBar, bg="#808080")
        self.paddingBar.pack(side="right", fill="both", expand=True, padx=2, pady=2)

        ##Now we create the main drawing area        
        self.drawSpace = Frame(self.__root, bg="#000080")
        self.drawSpace.pack(side="bottom", padx=30, expand=True, fill="both", pady=(0, 30))

        self.__root.bind("<Control-Tab>", lambda e: self.nextPanel())
        self.__root.bind("<Destroy>", lambda event: self.onDelete(event))

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
        if self.mode == "UNDEFINED":
            self.swapMode(self.panelDictionaries[0]["ID"])
        else:
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

    def onDelete(self, event):
        if event.widget == event.widget.winfo_toplevel():
            self.deleteAll()    

    def deleteAll(self):
        for x in self.panelDictionaries:
            x["Class"].deletePanel()
            del x["Class"]

if __name__ == "__main__":
    mWindow = HasketWindow()
    mWindow.setFileTitle("Untitled")

    mWindow.start()

    mWindow.Loop()
    del mWindow
