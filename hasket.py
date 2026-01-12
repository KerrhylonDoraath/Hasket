##hasket.py - A pythonic interface for developing haskell.

#IMPORTS
import sys
import os
import subprocess
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import threading

from hasketCore.templateWindow import EditorText

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

##TEXT EDITOR
class EditorFile(EditorText):

    #Designed to be a writeable area for haskell code development
    def __init__(self, master):
        EditorText.__init__(self, master)
        self.MODE = "EDITOR"

        #Script Name is what to call the file open
        self.scriptName = "Untitled"

        #Function pointer, points to a function to set the window title
        self.setTitle = None

        #Tracks the state of open files in the Hasket window
        self.MODIFIED = False

        #Text widget
        self.__secondaryTextWidget = Text(master, bg="white", fg="black", highlightthickness=1, highlightcolor="black", insertbackground="black")

        #Bindings
        self.__secondaryTextWidget.bind("<Control-s>", lambda event: self.saveScript())
        self.__secondaryTextWidget.bind("<Control-Shift-S>", lambda event: ScriptIO.saveScript(ScriptIO.saveAsScript, self.__secondaryTextWidget))
        self.__secondaryTextWidget.bind("<Control-o>", lambda event: self.openScript())
        self.__secondaryTextWidget.bind("<Control-n>", lambda event: self.newScript())
        self.__secondaryTextWidget.bind("<<Modified>>", lambda event: self.setModified())

        #Scrollbar setup
        self.__mScrollbar = Scrollbar(master, orient=VERTICAL, width=20, command=self.__secondaryTextWidget.yview)
        self.__secondaryTextWidget.config(yscrollcommand=self.__mScrollbar.set)

    #Modification callback
    def setModified(self):
        self.MODIFIED = True

    #inherited method
    def loadPanel(self):
        self.__mScrollbar.pack(side=RIGHT, fill=Y, expand=False, padx=2, pady=(0, 2))
        self.__secondaryTextWidget.pack(side=LEFT, fill=BOTH, expand=True, padx=(2, 0), pady=(0, 2))
        self.__secondaryTextWidget.focus()

    #inherited method
    def unloadPanel(self):
        self.__secondaryTextWidget.pack_forget()
        self.__mScrollbar.pack_forget()

    #Prompts saving
    def checkSave(self):
        if self.MODIFIED:
            saveTest = tkinter.messagebox.askyesnocancel("Warning", f"Save changes to {self.scriptName}?")
            if saveTest == None:    
                return False    ##User hit cancel
            if saveTest:
                self.saveScript()   ##Save the user script
        return True ##Completed check
        
    #User creates a new script
    def newScript(self, *ignore):
        if self.MODIFIED:
            if not self.checkSave():
                return
        self.scriptName = "Untitled"    
        self.setWindowTitle()   #Create window title with untitled document 
        self.__secondaryTextWidget.delete("1.0", END)   #Clear text in widget
        self.__secondaryTextWidget.edit_modified(False) #Reset modified flag
        self.MODIFIED = False   #Reset class modified flag

    def openScript(self, *ignore):
        if not self.checkSave():        ##Check if the user wants to save
                return
        self.scriptName, text = ScriptIO.importScriptEntry()    #Get import name and text
        self.__secondaryTextWidget.delete("1.0", END)
        self.__secondaryTextWidget.insert("1.0", text)
        self.__secondaryTextWidget.edit_modified(False)
        #Even if we have no text, nothing will be put in so we need not check
        self.MODIFIED = False
        self.setWindowTitle()   #Untitled, or file path
        ##Planning to deprecate

    def saveScript(self, *ignore):
        self.scriptName = ScriptIO.saveScript(self.scriptName, self.__secondaryTextWidget) #save script
        self.setWindowTitle()
        self.__secondaryTextWidget.edit_modified(False) 
        self.MODIFIED = False   #Reset the modified tags

    def saveAsScript(self, *ignore):
        self.scriptName = ScriptIO.saveScript(ScriptIO.saveAsScript(), self.__secondaryTextWidget) #save as...
        self.setWindowTitle()
        self.__secondaryTextWidget.edit_modified(False)
        self.MODIFIED = False   #Reset the modified tags
    
    def setTitleCommand(self, command):
        self.setTitle = command         #Called by main window to set title function(No globals!)

    def setWindowTitle(self):
        self.setTitle(self.scriptName)  #Wrapper to call setTitle more easily
    
    def setOutPipe(self):
        pass                #No need for an output pipe

    def __del__(self):
        self.checkSave()
    


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
        self.mProcess = None

        
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
        #So if not, ask again for GHCi to run
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
        while mEntry[0] == '\n':
            mEntry = mEntry[1:]
        if mEntry[0] == "\\":
            self.callCommandLibrary(mEntry[1:-1])
        else:
            if len(mEntry) == 0:
                return
            ##Pipe entry to GHCi instead
            self.mProcess.stdin.write(mEntry)
            self.mProcess.stdin.flush()
            self.OUTPUT_PIPE(mEntry)                ##pipe it to wanted output
        

    #inherited method
    def printOut(self, pText):
        #The terminal panel blocks the text widget
        #So we need to reset it, input the text, then set it
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.insert(END, pText)
        self.__mainTextWidget.config(state="disabled")
        self.__mainTextWidget.see(END)

    def clearOutput(self):
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.delete("1.0", END)
        self.__mainTextWidget.config(state="disabled")
    
    #If the terminal out had focus... it doesn't anymore!
    def focusReset(self, *ignore):
        self.__entryLine.focus_set()

    #The terminal can have some commands
    def callCommandLibrary(self, mInput):
        mInput = mInput.split(" ")
        
        if mInput[0] == "loadEditor":
            if self.boundEditor.scriptName == "Untitled" or self.boundEditor.scriptName == None:
                self.OUTPUT_PIPE("> Please save the contents of the editor.\n")
                return
            if not self.RUNNING:
               self.OUTPUT_PIPE("> Could not start GHCi. Please run command \\restart to restart GHCi.\n")
               return
            mEntry = r'"' + self.boundEditor.scriptName + r'"'
            mEntry = mEntry.encode("unicode_escape").decode()
            self.mProcess.stdin.write(f":load {mEntry}\n")
            self.mProcess.stdin.flush()

        elif mInput[0] == "restart":
            self.startGHCI()

        elif mInput[0] == "clear":
            self.clearOutput()

        elif mInput[0] == "load":
            if len(mInput) == 2:
                if not self.RUNNING:
                   self.OUTPUT_PIPE("> Could not start GHCi. Please run command \\restart to restart GHCi.\n")
                   return
                rawIn = mInput[1].encode("unicode_escape").decode()
                self.mProcess.stdin.write(f":load {rawIn}\n")
                self.mProcess.stdin.flush()
            else:
                self.OUTPUT_PIPE("> Please specify a haskell script to load.\n")
        else:
            self.OUTPUT_PIPE("> Unknown Command.\n")
                
    def bindEditor(self, editorObject):
        self.boundEditor = editorObject    

    def startGHCI(self, found=None):
        valid = False
        
        if found != None:
            if os.path.isfile(found):
                valid = True
                self.GHCILoc = found
                mPath = self.GHCILoc
            else:
                return False
                
        if self.GHCILoc == None:
            mPath = self.FindGHCi()
            if mPath != None:
                if os.path.isfile(mPath):
                    valid = True
                    self.GHCILoc = mPath
                    self.writeConfigFile()
        if valid:
            self.mProcess = subprocess.Popen([mPath], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.RUNNING = True
            self.GHCiThread = threading.Thread(target=self.updater)
            self.GHCiThread.start()
        else:
            tkinter.messagebox.showerror("Hasket", "GHCi could not be started.")

        return True


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
        try:
            self.mProcess.stdin.write(" :quit\r\n")
            self.mProcess.stdin.flush()
            self.mProcess.kill()
        except:
            pass


    def writeConfigFile(self):
        try:
            with open("HaskConf.cfg", "a") as configFile:
                configFile.write(f"config: {self.GHCILoc}\n")
        except OSError:
            pass        ##Cannot write config. Maybe create a log file?
        
    def FindGHCi(self):
        def getReturn():
            global returnString
            returnString = mEntry.get()
            if returnString[-1] == "\n":
                returnString = returnString[:-1]
            temp.destroy()

        #if tkinter.messagebox.askyesno("GHCi not found", "GHCi was not found in the configuration file, or the configuration file is not present. Would you like to specify where GHCi is located?"):
        if tkinter.messagebox.askyesno("GHCi not found", "Would you like to specify the location of ghci.exe?"):   
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
            mEntry.bind("<Return>", lambda event: getReturn())

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
            mEntry.focus_set()
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
        self.mode = "UNDEFINED"
    
        
        self.__fileTitle = "Untitled"
        self.OUPUT_PIPE = None
        self.panels = []
        self.panelDictionaries = []

        self.generateWindow()
        #self.generateMenubar()
        
        self.createPanel("TERMINAL", EditorTerminalOut)
        self.createPanel("EDITOR", EditorFile)

        mTerminal = self.searchDictionary("TERMINAL")
        mEntry = self.searchDictionary("EDITOR")
        
        mTerminal["Class"].bindEditor(mEntry["Class"])
        mEntry["Class"].setTitleCommand(self.setFileTitle)

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
        self.panelBar.pack(pady=(20, 0), expand=False, fill=X, padx=30)

        ##And the padding for inside the panel bar
        self.paddingBar = Frame(self.panelBar, bg="#808080")
        self.paddingBar.pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)

        ##Now we create the main drawing area        
        self.drawSpace = Frame(self.__root, bg="#000080")
        self.drawSpace.pack(side=BOTTOM, padx=30, expand=True, fill=BOTH, pady=(0, 30))

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
            x["Class"].__del__()
            del x["Class"]
            
class ScriptIO():
    FILE_TITLE = ""
    #IMPORTING HASKELL SCRIPT
    @staticmethod
    def importScriptEntry(*ignore):
        mFile = tkinter.filedialog.askopenfilename(filetypes=[("Haskell Scripts", ".hs")])
        if not mFile:
            return (None, "")
        return ScriptIO.importScript(mFile)
    @staticmethod
    def importScript(scriptName):
        try:
            with open(scriptName, "r") as mEntry:
                x = mEntry.readline()
                scriptText = []
                while x != "":
                    scriptText.append(x)
                    x = mEntry.readline()
                resString = ""
                for item in scriptText:
                    resString += item
                return (scriptName, resString)
        except OSError:
            tkinter.messagebox.showerror("Error", f"Unable to open file: {scriptName}")
            return (None, "")
        
    #Saving Verification Link
    @staticmethod
    def SaveCheck(MODIFIED=True):
        if MODIFIED:
            return tkinter.messagebox.askyesno("Save Changes", f"Save changes to {FILE_TITLE}?")
        
    #SAVING SCRIPT
    @staticmethod
    def saveScript(fileName, textWidget):
        if fileName == None or fileName == "Untitled":
            fileName = ScriptIO.saveAsScript()
            if fileName == None:
                return None
            if fileName[-3:] != ".hs":
                fileName += ".hs"
        if fileName != None and fileName != "Untitled":
            with open(fileName, "w") as mFile:
                mFile.write(textWidget.get("1.0", END))
            tkinter.messagebox.showinfo("Success", f"Successfully saved to file: {fileName}!")
            return fileName
        return None

    #SAVE AS SCRIPT
    @staticmethod
    def saveAsScript(*ignore):
        return tkinter.filedialog.asksaveasfilename(filetypes=[("Haskell Scripts", ".hs")])

if __name__ == "__main__":
    mWindow = HasketWindow()
    mWindow.setFileTitle("Untitled")

    mWindow.start()

    mWindow.Loop()
    del mWindow
