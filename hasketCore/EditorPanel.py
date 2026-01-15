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
from typing import override

from hasketCore.GenericPanel import GenericPanel
from hasketCore.ScriptIO import ScriptIO

class EditorPanel(GenericPanel):

    def __init__(self, master):
        GenericPanel.__init__(self, master)
        self._mode = "EDITOR"
        self._scriptName = "Untitled"
        self._scriptPath = ""
        self.__modified = False

        self.__fileTitleFrame = Frame(master, bg="#000080")
        self.__fileTitleLabel = Label(master=self.__fileTitleFrame, bg="white",
                                      highlightthickness=1, fg="black",
                                      text=self._scriptName, justify="left"
                                      )
        self.__editorPanel = Text(master=master, bg="white",
                                  fg="black", highlightthickness=1,
                                  highlightcolor="black",
                                  insertbackground="black"
                                  )
        self.__mScrollbar = Scrollbar(master, orient="vertical", width=20,
                                      command=self.__editorPanel.yview)
        self.__editorPanel.config(yscrollcommand=self.__mScrollbar.set)

        self.__setBindings()
        self.__initial = self.__editorPanel.get("1.0", "end")

    def __setBindings(self) -> None:
        self.__editorPanel.bind(
            "<Control-s>",
            lambda event: self._saveScript(True)
        )

        self.__editorPanel.bind(
            "<Control-Shift-S>",
            lambda event: self._saveScript(False)
        )

        self.__editorPanel.bind(
            "<Control-o>",
            lambda event: self.openScript()
        )
        self.__editorPanel.bind(
            "<Control-n>",
            lambda event: self.newScript()
        )
        self.__editorPanel.bind(
            "<KeyRelease>",
            lambda event: self.__checkModified()
        )

    @override
    def loadPanel(self):
        """Loads this panel to the master widget."""

        self.__fileTitleFrame.pack(side="top", anchor="w",
                                   expand=False, fill="x",
                                   padx=2, pady=2)

        self.__fileTitleLabel.pack(side="left", anchor="w", padx=1)
        self.__mScrollbar.pack(side="right", fill="y", expand=False,
                               padx=2, pady=(0, 2)
                               )
        self.__editorPanel.pack(side="left", fill="both", expand=True,
                                padx=(2, 0), pady=(0, 2)
                                )
        self.__editorPanel.focus()

    @override
    def unloadPanel(self):
        """Unloads the panel from the master widget."""

        self.__fileTitleLabel.pack_forget()
        self.__fileTitleFrame.pack_forget()
        self.__editorPanel.pack_forget()
        self.__mScrollbar.pack_forget()

    def __checkModified(self):
        if not self.__modified:
            #No point comparing if already modified, so save time
            if (self.__editorPanel.get(
                    "1.0",
                    "end"
                    ) != self.__initial
            and self.__editorPanel.focus_get()):
                self.__modified = True
                self.__fileTitleLabel.config(text=self._scriptName + "*")


    def _checkSave(self) -> bool | None:
        if self.__modified:
            return messagebox.askyesnocancel(
                "Warning",
                f"Save changes to {self._scriptName}?",
                icon="warning"
            )

        return False

    @staticmethod
    def __funcSave(func: Callable) -> Callable:
        """Checks if a file is to be saved before it leaves the editor."""

        def wrap(self) -> None:
            checking = self._checkSave()
            if checking is None:
                return
            elif checking:
                if ScriptIO.saveScript(self._scriptPath + self._scriptName,
                                    self.__editorPanel.get(
                                        "1.0", "end"
                                        )
                                    ) != 0:
                    return
            func(self)
        return wrap

    def _restartEditor(self, scriptPath: str ="",
                       scriptName: str ="Untitled", text: str | None =None) -> None:

        self._master.focus_set()
        self._scriptName = scriptName
        self._scriptPath = scriptPath
        self.__editorPanel.delete("1.0", "end")
        self.__editorPanel.focus_set()

        if text:
            self.__editorPanel.insert("1.0", text)
            self.__initial = self.__editorPanel.get("1.0", "end")
            self.__editorPanel.delete("end-1c", "end")
        else:
            self.__initial = self.__editorPanel.get("1.0", "end")

        self.__fileTitleLabel.config(text=self._scriptName)
        self.__modified = False

    def _saveScript(self, filename: bool = False) -> None:
        if not filename:
            result, fileattr = ScriptIO.saveScript(
                fileName=None,
                text=self.__editorPanel.get("1.0", "end")
            )
        else:
            result, fileattr = ScriptIO.saveScript(
                fileName=self._scriptPath+self._scriptName,
                text=self.__editorPanel.get("1.0", "end")
            )
        if result == 0:
            self._restartEditor(fileattr[0], fileattr[1], fileattr[2])

    @__funcSave
    def newScript(self, *_) -> None:
        """Clears the editor and loads a new script."""

        self._restartEditor("", "Untitled")

    @__funcSave
    def openScript(self, *_) -> None:
        """Opens a script and loads it into the editor."""

        self._scriptPath, self._scriptName, text = ScriptIO.importScriptEntry()
        self._restartEditor(self._scriptPath, self._scriptName, text)

    @__funcSave
    @override
    def deletePanel(self) -> None:
        """Deletes the panel."""

        pass
