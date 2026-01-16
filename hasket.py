##hasket.py - A pythonic interface for developing haskell.

#IMPORTS
from tkinter import *

from hasketCore.EditorPanel import EditorPanel
from hasketCore.TerminalPanel import EditorTerminalOut
from hasketCore.ScriptIO import ScriptIO
from hasketCore.Utils import lineParse


STATE_INACTIVE = "#D0D0D0"
STATE_ACTIVE = "#FFFFFF"

CONFIG_FILE_TOKENS = ["config"]

WINDOW_TITLE = "Hasket"
VERSION = "1.1"

#Main window
class HasketWindow:
    def __init__(self):
        self._outputPipe = None
        self._panels = []
        self._panelDictionaries = []
        self._mode = "UNDEFINED"

        self.__root = Tk()
        self.__panelBar = Frame(self.__root, bg="#000080")
        self.__paddingBar = Frame(self.__panelBar, bg="#808080")
        self.__drawSpace = Frame(self.__root, bg="#000080")

        self._generateWindow()

        self.createPanel("TERMINAL", EditorTerminalOut)
        self.createPanel("EDITOR", EditorPanel)

        mTerminal = self.searchDictionary("TERMINAL")
        mEntry = self.searchDictionary("EDITOR")
        mTerminal["Class"].bindEditor(mEntry["Class"])

        self._loadConfigFile()

    def _loadConfigFile(self) -> None:
        importData = ScriptIO.readConfigFile()
        if importData:
            resultantSet = lineParse(importData)
            for entry in resultantSet:
                if entry[0] == "config":
                    terminal = self.searchDictionary("TERMINAL")
                    terminal["Class"].startGHCI(entry[1])
        
    def start(self):
        self.loadPanel("TERMINAL")
        self.__root.mainloop()
        
    def createPanel(self, textName, panelClass):
        mTempObject = panelClass(self.__drawSpace)
        self._panelDictionaries.append({"ID": textName,
                                        "Class": mTempObject,
                                        "Label": self._generatePanelLabel(textName)})

    def _generatePanelLabel(self, panelName):
        self._panels.append(Label(self.__panelBar,
                                  text=panelName, bg=STATE_INACTIVE, highlightthickness=0))
        self._panels[-1].pack(side=LEFT, padx=2, pady=2)
        self._panels[-1].bind("<Button-1>", lambda event: self.swapMode(panelName))
        return self._panels[-1]


    def _generateWindow(self):
        self.__root.geometry("800x500")
        self.__root.config(bg="#404040")
        self.__root.iconbitmap("HASKET.ico")
        self.__root.minsize(800, 500)
        self.__root.title(f"{WINDOW_TITLE} {VERSION}")

        self.__panelBar.pack(pady=(20, 0), expand=False, fill="x", padx=30)
        self.__paddingBar.pack(side="right", fill="both", expand=True, padx=2, pady=2)
        self.__drawSpace.pack(side="bottom", padx=30, expand=True, fill="both", pady=(0, 30))

        self.__root.bind("<Control-Tab>", lambda e: self.nextPanel())

    def searchDictionary(self, nameID):
        for entry in self._panelDictionaries:
            if entry["ID"] == nameID:
                return entry
        return None

    def unloadCurrentPanel(self):
        if self.searchDictionary(self._mode):
            entry = self.searchDictionary(self._mode)
            entry["Class"].unloadPanel()
            entry["Label"].config(bg=STATE_INACTIVE)

    def loadPanel(self, panelID):
        if self.searchDictionary(panelID):
            entry = self.searchDictionary(panelID)
            entry["Class"].loadPanel()
            self._mode = panelID
            entry["Label"].config(bg=STATE_ACTIVE)

    def swapMode(self, newPanel):
        self.unloadCurrentPanel()
        self.loadPanel(newPanel)

    def nextPanel(self):
        if self._mode == "UNDEFINED":
            self.swapMode(self._panelDictionaries[0]["ID"])
        else:
            mEntry = self.searchDictionary(self._mode)
            mIndex = self._panelDictionaries.index(mEntry)
            mIndex = (mIndex+1) % len(self._panelDictionaries)
            self.swapMode(self._panelDictionaries[mIndex]["ID"])

    def __del__(self):
        for x in self._panelDictionaries:
            x["Class"].deletePanel()
            del x["Class"]

if __name__ == "__main__":
    mWindow = HasketWindow()
    mWindow.start()
