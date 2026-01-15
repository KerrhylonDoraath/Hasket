from collections.abc import Callable
from tkinter import *
from tkinter import messagebox

from typing import override

from hasketCore.GenericPanel import GenericPanel
from hasketCore.ScriptIO import ScriptIO

##TEXT EDITOR
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
        self.__editorPanel.bind("<Control-s>",
                                lambda event: ScriptIO.saveScript(
                                    fileName=self._scriptPath + self._scriptName,
                                    text=self.__editorPanel.get(
                                        "1.0", "end")
                                )
                                )
        self.__editorPanel.bind("<Control-Shift-S>",
                                lambda event: ScriptIO.saveScript(
                                    fileName=None,
                                    text=self.__editorPanel.get(
                                        "1.0", "end")
                                    )
                                )
        self.__editorPanel.bind("<Control-o>",
                                lambda event: self.openScript()
                                )
        self.__editorPanel.bind("<Control-n>",
                                lambda event: self.newScript()
                                )
        self.__editorPanel.bind("<KeyRelease>",
                                lambda event: self.__checkModified()
                                )

    @override
    def loadPanel(self):
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
        self.__fileTitleLabel.pack_forget()
        self.__fileTitleFrame.pack_forget()
        self.__editorPanel.pack_forget()
        self.__mScrollbar.pack_forget()

    def __checkModified(self):
        if (self.__editorPanel.get(
                "1.0",
                "end"
                ) != self.__initial
        and self.__modified != True):
            self.__modified = True


    def _checkSave(self) -> bool | None:
        if self.__modified:
            return messagebox.askyesnocancel(
                "Warning",
                f"Save changes to {self._scriptName}?",
                icon="warning"
            )

        return False

    @staticmethod
    def __funcSave(func: Callable):
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

    def _restartEditor(self, scriptPath: str ="", scriptName: str ="") -> None:
        self._scriptName = scriptName
        self._scriptPath = scriptPath
        self.__editorPanel.delete("1.0", "end")
        self.__initial = self.__editorPanel.get("1.0", "end")
        self.__modified = False


    @__funcSave
    def newScript(self, *_) -> None:
        self._restartEditor("", "Untitled")

    @__funcSave
    def openScript(self, *_) -> None:
        return
        self.scriptName, text = ScriptIO.importScriptEntry()  # Get import name and text
        self.__editorPanel.delete("1.0", END)
        self.__editorPanel.insert("1.0", text)
        self.__editorPanel.edit_modified(False)
        # Even if we have no text, nothing will be put in so we need not check
        self.MODIFIED = False
        ##Planning to deprecate

    @__funcSave
    @override
    def deletePanel(self) -> None:
        pass
