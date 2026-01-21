"""Hasket Editor Panel

Common editor panel for haskell development.

This inherits from the GenericPanel to create a panel that will
sit in the Hasket Window. The editor is the main place to
input into the program; an environment to write clean haskell code.

It does not have many responsibilities other than holding text, and loading
scripts. It works well when paired with a terminal panel.
"""

from collections.abc import Callable
from tkinter import Frame, Label, Text, Scrollbar
from tkinter import messagebox

from hasketCore.GenericPanel import GenericPanel
from hasketCore.ScriptIO import ScriptIO


class EditorPanel(GenericPanel):

    def __init__(self, master):
        GenericPanel.__init__(self, master)
        self._scriptName = "Untitled"
        self._scriptPath = ""
        self._modified = False
        self._initial = "\n"
        self._ignoreModified = True
        self._accentColour = "#000080"
        self.__fileTitleFrame = Frame(master, bg=self._accentColour)
        self.__fileTitleLabel = Label(master=self.__fileTitleFrame, bg="white",
                                      highlightthickness=1, fg="black",
                                      text=self._scriptName, justify="left")
        self.__editorPanel = Text(master=master, bg="white",
                                  fg="black", highlightthickness=1,
                                  highlightcolor="black",
                                  insertbackground="black")
        self.__mScrollbar = Scrollbar(master, orient="vertical", width=20,
                                      command=self.__editorPanel.yview)
        self.__editorPanel.config(yscrollcommand=self.__mScrollbar.set)

        self.__setBindings()

    def __setBindings(self) -> None:
        self.__editorPanel.bind("<Control-s>", lambda event: self._saveScript(True))
        self.__editorPanel.bind("<Control-Shift-S>", lambda event: self._saveScript(False))
        self.__editorPanel.bind("<Control-o>", lambda event: self.openScript())
        self.__editorPanel.bind("<Control-n>", lambda event: self.newScript())
        self.__editorPanel.bind("<KeyRelease>", self.__checkModified)
        self.__editorPanel.bind("<KeyPress>", self.__blockadeModified)

    def loadPanel(self):
        """Loads this panel to the master widget."""

        self.__fileTitleFrame.pack(side="top", anchor="w", expand=False, fill="x", padx=2, pady=2)
        self.__fileTitleLabel.pack(side="left", anchor="w", padx=1)
        self.__mScrollbar.pack(side="right", fill="y", expand=False, padx=2, pady=(0, 2))
        self.__editorPanel.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=(0, 2))
        self.__editorPanel.focus()

    def unloadPanel(self):
        """Unloads the panel from the master widget."""

        self.__fileTitleLabel.pack_forget()
        self.__fileTitleFrame.pack_forget()
        self.__editorPanel.pack_forget()
        self.__mScrollbar.pack_forget()

    def __blockadeModified(self, event):
        if event.keycode == 17:
            self._ignoreModified = True

    def __checkModified(self, event):
        if not self._modified and not self._ignoreModified:
            # No point comparing if already modified, so save time
            if (self.__editorPanel.get("1.0", "end") != self._initial
                    and self.__editorPanel.focus_get()):

                self._modified = True
                self.__fileTitleLabel.config(text=self._scriptName + "*")
        elif self._ignoreModified and event.keycode == 17:
            self._ignoreModified = False

    def _checkSave(self) -> bool | None:
        if self._modified:
            return messagebox.askyesnocancel("Warning",
                                             f"Save changes to {self._scriptName}?", icon="warning")
        return False

    def setAccentColour(self, accentColour: str) -> None:
        self._accentColour = accentColour
        self.__fileTitleFrame.config(bg=self._accentColour)

    @staticmethod
    def __funcSave(func: Callable) -> Callable:
        """Checks if a file is to be saved before it leaves the editor."""

        def wrap(self) -> None:
            checking = self._checkSave()
            if checking is None:
                return
            elif checking:
                if (ScriptIO.saveScript(self._scriptPath + self._scriptName,
                                        self.__editorPanel.get("1.0", "end")) != 0):
                    return
            func(self)

        return wrap

    def restartEditor(
            self, scriptPath: str = "",
            scriptName: str = "Untitled", text: str | None = None,
            fromSave: bool = False) -> None:

        self._master.focus_set()
        self._scriptName = scriptName
        self._scriptPath = scriptPath
        self.__editorPanel.delete("1.0", "end")
        self.__editorPanel.focus_set()

        if text:
            self.__editorPanel.insert("1.0", text)
            if not fromSave:
                self._initial = self.__editorPanel.get("1.0", "end")
                self.__editorPanel.delete("end-1c", "end")
            else:
                self.__editorPanel.delete("end-1c", "end")
                self._initial = self.__editorPanel.get("1.0", "end")
        else:
            self._initial = self.__editorPanel.get("1.0", "end")

        self.__fileTitleLabel.config(text=self._scriptName)
        self._modified = False

    def _saveScript(self, filename: bool = False) -> None:
        if not filename:
            result, fileAttr = ScriptIO.saveScript(
                fileName=None,
                text=self.__editorPanel.get("1.0", "end"))
        else:
            result, fileAttr = ScriptIO.saveScript(
                fileName=self._scriptPath + self._scriptName,
                text=self.__editorPanel.get("1.0", "end"))
        if result == 0:
            self.restartEditor(fileAttr[0], fileAttr[1], fileAttr[2], True)

    def getFilePath(self) -> str:
        """Returns the full path of the file in the editor."""
        return self._scriptPath + self._scriptName

    @__funcSave
    def newScript(self, *_) -> None:
        """Clears the editor and loads a new script."""

        self.restartEditor("", "Untitled")

    @__funcSave
    def openScript(self, *_) -> None:
        """Opens a script and loads it into the editor."""
        paramPath, paramName, text = ScriptIO.importScriptEntry()
        if not (paramPath == "" and paramName == "Untitled"):
            self.restartEditor(paramPath, paramName, text)
        else:
            self.restartEditor(self._scriptPath, self._scriptName,
                               self.__editorPanel.get("1.0", "end"), True)

    @__funcSave
    def deletePanel(self) -> None:
        """Deletes the panel."""

        pass
