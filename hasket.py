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
FILE_TITLE = "Untitled"
MODIFIED = False
WINDOW_TITLE = ""
#MODE sets the usage of the text widget
MODE = "TERMINAL"
INITIAL_TEXT = ""

#INITIALISING THE WINDOW
root = Tk()
root.geometry("800x500")
root.config(bg="#404040")
root.iconbitmap("HASKET.ico")

#IMPORTING HASKELL SCRIPT
def importScriptEntry(*ignore):
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
    global WINDOW_TITLE, root
    originalTitle = "Hasket 1.0"
    WINDOW_TITLE = f"{scriptName} - {originalTitle}"
    root.title(WINDOW_TITLE)

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
def swapMode(event):
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


def updater():
    global mProcess, RUNNING, mainTextWidget
    while RUNNING:
        line = mProcess.stdout.readline()
        if not line:
            break
        try:
            mainTextWidget.insert(END, line)
            mainTextWidget.see(END)
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

#drawing window geometry
mainFrame = Frame(root, bg="#000080")
mainFrame.pack(pady=(20, 0), expand=False, fill=X, padx=30)

TerminalLabel = Label(mainFrame, text="TERMINAL", bg="white", highlightthickness=0)
TerminalLabel.pack(side=LEFT, padx=2, pady=2)
TerminalLabel.bind("<Button-1>", lambda event: swapMode("TERMINAL"))

EditorLabel = Label(mainFrame, text="EDITOR", bg="#D0D0D0", highlightthickness=0)
EditorLabel.pack(side=LEFT, padx=2, pady=2)
EditorLabel.bind("<Button-1>", lambda event: swapMode("EDITOR"))

BlankEntry = Frame(mainFrame, bg="#808080")
BlankEntry.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=2)

textWidgetFrame = Frame(root, bg="#000080")
textWidgetFrame.pack(side=BOTTOM, padx=30, expand=True, fill=BOTH, pady=(0, 30))

secondaryTextWidget = Text(textWidgetFrame, bg="white", fg="black", highlightthickness=1, highlightcolor="black", insertbackground="black")
secondaryTextWidget.bind("<Control-s>", lambda event: saveScript(FILE_TITLE))
secondaryTextWidget.bind("<Control-Shift-S>", lambda event: saveScript(saveAsScript))
secondaryTextWidget.bind("<Key>", ModifiedText)

mainTextWidget = Text(textWidgetFrame, bg="black", fg="white", highlightthickness=1, highlightcolor="white", insertbackground="white")
mainTextWidget.pack(side=LEFT, fill=BOTH, expand=True, padx=(2, 0), pady=(0, 2))
mainTextWidget.bind("<Return>", lambda event: retrieveInput(False))


root.bind("<Control-Tab>", lambda event: swapMode("EDITOR" if MODE == "TERMINAL" else "TERMINAL"))
root.bind("<Control-o>", importScriptEntry)
root.bind("<Control-n>", lambda event: newScript())

mScrollbar = Scrollbar(textWidgetFrame, orient=VERTICAL, width=20, command=mainTextWidget.yview)
mScrollbar.pack(side=RIGHT, fill=Y, expand=False, padx=2, pady=(0, 2))
mainTextWidget.config(yscrollcommand=mScrollbar.set)

#MENU CONFIGURATION
mainMenu = Menu(tearoff=0)
fileMenu = Menu(mainMenu, tearoff=0) 
mainMenu.add_cascade(menu=fileMenu, label="File")

#File Menu
fileMenu.add_command(label="New Script", command=newScript)
fileMenu.add_command(label="Open Script", command=importScriptEntry)
fileMenu.add_separator()
fileMenu.add_command(label="Save", command=lambda: saveScript(FILE_TITLE))
fileMenu.add_command(label="Save As", command=lambda: saveScript(saveAsScript))
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=root.destroy)
root.config(menu=mainMenu)

CreateWindowTitle("Untitled")

mProcess = subprocess.Popen(["C:\\HASKELL\\bin\\ghci.exe"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
RUNNING = True
t1 = threading.Thread(target = updater)
t1.start()

if len(sys.argv) == 2:
    importScript(sys.argv[1])
else:
    newScript()

root.mainloop()

RUNNING = False
try:
    mProcess.stdin.write(" :quit\r\n")
    mProcess.stdin.flush()
except OSError:
    pass
mProcess.kill()
