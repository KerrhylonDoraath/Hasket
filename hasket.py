##hasket.py - A pythonic interface for developing haskell.
import tkinter.colorchooser
# IMPORTS
from tkinter import *
#from tkinter import colorchooser

from hasketCore.EditorPanel import EditorPanel
from hasketCore.GenericPanel import GenericPanel
from hasketCore.TerminalPanel import EditorTerminalOut
#from hasketCore.SamplePanel import SamplePanel
from hasketCore.ScriptIO import ScriptIO
from hasketCore.Utils import lineParse

STATE_INACTIVE = "#D0D0D0"
STATE_ACTIVE = "#FFFFFF"

CONFIG_FILE_TOKENS = ["config"]

WINDOW_TITLE = "Hasket"
VERSION = "1.1"

DEFAULT_PANEL_COLOUR = "#808080"
DEFAULT_ACCENT_COLOUR = "#000080"

# Main window
class HasketWindow:
    def __init__(self):
        self._outputPipe = None
        self._panels = []
        self._panelDictionaries = []
        self._loadedPanelID = "UNDEFINED"

        self._backgroundColour = DEFAULT_PANEL_COLOUR
        self._accentColour = DEFAULT_ACCENT_COLOUR

        self.__root = Tk()
        self.__panelBar = Frame(self.__root, bg=self._accentColour)
        self.__paddingBar = Frame(self.__panelBar, bg=self._backgroundColour)
        self.__drawSpace = Frame(self.__root, bg=self._accentColour)

        self._generateWindow()
        self._setMenubar()

        self.createPanel("TERMINAL", EditorTerminalOut)
        self.createPanel("EDITOR", EditorPanel)

        mTerminal = self.searchDictionary("TERMINAL")
        mEntry = self.searchDictionary("EDITOR")
        mTerminal["Class"].bindEditor(mEntry["Class"])

        self._loadConfigFile()

    def _selectAccentColour(self) -> None:
        self._reloadAccentColour(tkinter.colorchooser.askcolor()[1])
        ScriptIO.rewriteConfigFile("accentColour", self._accentColour)

    def _selectBackgroundColour(self) -> None:
        self._reloadBackgroundColour(tkinter.colorchooser.askcolor()[1])
        ScriptIO.rewriteConfigFile("accentColour", self._accentColour)

    def _setMenubar(self) -> None:
        menubar = Menu(self.__root)
        preferences = Menu(menubar, title="Preferences", tearoff=False)
        preferences.add_command(label="Select Accent Colour", command=self._selectAccentColour)
        preferences.add_command(label="Select Background Colour", command=self._selectBackgroundColour)
        menubar.add_cascade(menu=preferences, label="Preferences")
        self.__root.config(menu=menubar)


    def _reloadBackgroundColour(self, newColour: str | None) -> None:
        if not newColour:
            newColour = self._backgroundColour
        self._backgroundColour = newColour
        self._reloadColours()
        ScriptIO.rewriteConfigFile("backgroundColour", self._backgroundColour)

    def _reloadAccentColour(self, newColour: str | None) -> None:
        if not newColour:
            newColour = self._accentColour
        self._accentColour = newColour.upper()
        self._reloadColours()
        mEditor = self.searchDictionary("EDITOR")["Class"]
        mEditor.setAccentColour(self._accentColour)
        ScriptIO.rewriteConfigFile("accentColour", self._accentColour)

    def _loadConfigFile(self) -> None:
        importData = ScriptIO.readConfigFile()
        if importData:
            resultantSet = lineParse(importData)
            for entry in resultantSet:
                if entry[0] == "config":
                    terminal = self.searchDictionary("TERMINAL")
                    terminal["Class"].startGHCI(entry[1])
                elif entry[0] == "backgroundColour":
                    self._reloadBackgroundColour(entry[1])
                elif entry[0] == "accentColour":
                    self._reloadAccentColour(entry[1])

    def _reloadColours(self):
        self.__panelBar.config(bg=self._accentColour)
        self.__root.config(bg=self._backgroundColour)
        self.__drawSpace.config(bg=self._accentColour)

    def start(self) -> None:
        """Starts Hasket."""

        self.loadPanel("TERMINAL")
        self.__root.mainloop()

    def createPanel(self, textName: str, panelClass: type[GenericPanel]) -> None:
        """Creates a new panel, and adds it to the panel list.

        Parameters:
            (str) textName:                ID of the panel to create.
            type[GenericPanel] panelClass: Class of the panel to create.
        """

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
        self.__root.bind("<<Destroy>>", lambda e: self._onDelete())

    def searchDictionary(self, nameID: str) -> type[str, type[GenericPanel], type[Label]] | None:
        """Searches for a panel with the given ID.

        Parameters:
            (str) nameID:   ID of the panel to search.

        Returns:
            type[str, type[GenericPanel], type[Label]]: The entry related to the searched panel.
            None:  If there is no entry for the given ID.
        """

        for entry in self._panelDictionaries:
            if entry["ID"] == nameID:
                return entry
        return None

    def unloadCurrentPanel(self) -> None:
        """Unloads the currently active panel."""

        if self.searchDictionary(self._loadedPanelID):
            entry = self.searchDictionary(self._loadedPanelID)
            entry["Class"].unloadPanel()
            entry["Label"].config(bg=STATE_INACTIVE)

    def loadPanel(self, panelID: str) -> None:
        """Attempts to load the panel with the given ID."""

        if self.searchDictionary(panelID):
            entry = self.searchDictionary(panelID)
            entry["Class"].loadPanel()
            self._loadedPanelID = panelID
            entry["Label"].config(bg=STATE_ACTIVE)

    def swapMode(self, newPanel: str) -> None:
        """Swaps the loaded panel with the panel of given ID."""

        self.unloadCurrentPanel()
        self.loadPanel(newPanel)

    def nextPanel(self) -> None:
        """Moves the currently active panel to the next one."""

        if self._loadedPanelID == "UNDEFINED":
            self.swapMode(self._panelDictionaries[0]["ID"])
        else:
            mEntry = self.searchDictionary(self._loadedPanelID)
            mIndex = self._panelDictionaries.index(mEntry)
            mIndex = (mIndex + 1) % len(self._panelDictionaries)
            self.swapMode(self._panelDictionaries[mIndex]["ID"])

    def _onDelete(self):
        for x in self._panelDictionaries:
            x["Class"].deletePanel()
            del x["Class"]


if __name__ == "__main__":
    mWindow = HasketWindow()

    #Adding a new panel.
    #mWindow.createPanel("EXAMPLE", SamplePanel)

    mWindow.start()
