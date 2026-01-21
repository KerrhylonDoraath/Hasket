import os
import subprocess
import threading
from tkinter import Frame, Text, Scrollbar, TclError
import tkinter.messagebox

from hasketCore.EditorPanel import EditorPanel
from hasketCore._FindInterpreter import findGHCI
from hasketCore.GenericPanel import GenericPanel
from hasketCore.ScriptIO import ScriptIO


class EditorTerminalOut(GenericPanel):
    def __init__(self, master):
        GenericPanel.__init__(self, master)
        self._running = False
        self._GHCIThread = None
        self._GHCILoc = None
        self._process = None
        self._boundEditor = None
        self._awaitingCallback = False

        self.__microFrame = Frame(master, highlightthickness=0, highlightcolor="#000080")
        self.__mainTextWidget = Text(self.__microFrame, width=100, height=20, state="disabled",
                                     bg="black", fg="white", highlightthickness=1,
                                     highlightcolor="white", insertbackground="white")
        self.__entryLine = Text(master, height=1, bg="black", fg="white", highlightthickness=1,
                                highlightcolor="white", insertbackground="white")
        self.__entryLine.bind("<Return>", lambda event: self._submitTerminalEntry())
        self.__mScrollbar = Scrollbar(self.__microFrame, orient="vertical", width=20,
                                      command=self.__mainTextWidget.yview)
        self.__mainTextWidget.config(yscrollcommand=self.__mScrollbar.set)
        self.__mainTextWidget.bind("<FocusIn>", lambda event: self._focusReset())

    def _testGHCI(self):
        if not self._running:
            self.startGHCI()
            if not self._running:
                self._outputPipe(
                    "Could not start GHCi. Please run command \\restart to restart GHCi.\n")

    def loadPanel(self):
        self.__microFrame.pack(expand=True, fill="both", padx=2, pady=(0, 2))
        self.__entryLine.pack(side="bottom", fill="x", expand=False, padx=2, pady=(5, 2))
        self.__mScrollbar.pack(side="right", fill="y", expand=False)
        self.__mainTextWidget.pack(side="left", fill="both", expand=True)
        self.__mainTextWidget.focus()
        self.__entryLine.focus_set()

        self._testGHCI()

    def unloadPanel(self):
        self.__mainTextWidget.pack_forget()
        self.__mScrollbar.pack_forget()
        self.__microFrame.pack_forget()
        self.__entryLine.pack_forget()

    def _collectLine(self) -> str | None:
        mEntry = self.__entryLine.get("1.0", "end")
        self.__entryLine.delete("0.0", "end")
        if len(mEntry) == 0:
            return None
        while mEntry[0] == '\n':
            mEntry = mEntry[1:]
            if len(mEntry) == 0:
                return None
        return mEntry

    def _submitTerminalEntry(self) -> None:
        possibleLine = self._collectLine()
        if not possibleLine:
            return
        if self._awaitingCallback:
            self._outputPipe("> Please wait while GHCi reboots...\n")
            return

        if possibleLine[0] == "\\":
            self._callCommandLibrary(possibleLine[1:-1])
        else:
            try:
                self._process.stdin.write(possibleLine)
                self._process.stdin.flush()
                self._outputPipe(possibleLine)  ##pipe it to output
            except OSError:
                self._outputPipe("> GHCi has closed. Please run \\restart to restart GHCi.\n")

    def printOut(self, text: str) -> None:
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.insert("end", text)
        self.__mainTextWidget.config(state="disabled")
        self.__mainTextWidget.see("end")

    def clearOutput(self):
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.delete("1.0", "end")
        self.__mainTextWidget.config(state="disabled")

    def _focusReset(self, *_):
        self.__entryLine.focus_set()

    def _commLoadEditor(self) -> None:
        if not self._boundEditor:
            self._outputPipe("> No editor bound.\n")
            return
        if self._boundEditor.getFilePath() == "Untitled":
            self._outputPipe("> Please save the contents of the editor.\n")
            return
        if not self._running:
            self._outputPipe(
                "> Could not start GHCi. Please run command \\restart to restart GHCi.\n")
            return
        mEntry = r'"' + self._boundEditor.getFilePath() + r'"'
        mEntry = mEntry.encode("unicode_escape").decode()

        try:
            self._process.stdin.write(f":load {mEntry}\n")
            self._process.stdin.flush()
        except Exception as e:
            raise e

    def _commLoadScript(self, parameters: list[str]) -> None:
        if len(parameters) == 2:
            if not self._running:
                self._outputPipe(
                    "> Could not start GHCi. Please run command \\restart to restart GHCi.\n")
                return
            rawIn = parameters[1].encode("unicode_escape").decode()
            self._process.stdin.write(f":load {rawIn}\n")
            self._process.stdin.flush()
            scriptParameters = ScriptIO.importScript(rawIn)
            self._boundEditor.restartEditor(scriptParameters[0],
                                            scriptParameters[1],
                                            scriptParameters[2])
        elif len(parameters) >= 3:
            self._outputPipe("> Please only specify one script.\n")
        else:
            self._outputPipe("> Please specify a haskell script to load.\n")

    def _callCommandLibrary(self, mInput):
        mInput = mInput.split(" ")
        if mInput[0] == "loadEditor":
            self._commLoadEditor()
        elif mInput[0] == "restart":
            self._restartGHCI()
        elif mInput[0] == "clear":
            self.clearOutput()
        elif mInput[0] == "load":
            self._commLoadScript(mInput)
        else:
            self._outputPipe(f"> Unknown Command: {mInput[0]}\n")

    def _findGHCI(self, found: str | None) -> bool:
        if found:
            if os.path.isfile(found):
                self._GHCILoc = found
                return True
            return False

        elif not self._GHCILoc:
            mPath = findGHCI()
            if mPath:
                if os.path.isfile(mPath):
                    self._GHCILoc = mPath
                    ScriptIO.rewriteConfigFile("config", self._GHCILoc)
                    return True

        return False

    def _restartGHCI(self) -> None:
        if self._running:
            self._running = False
            self._process.stdin.write(":quit\r\n")
            self._process.stdin.flush()
            self._process.kill()
            self._process.stdout.flush()
            self._awaitingCallback = True
            self._outputPipe("> Please wait while GHCi reboots...\n")
        else:
            self.startGHCI(self._GHCILoc)

    def startGHCI(self, found: str | None = None) -> bool:
        """Attempts to start GHCi.

        Parameters:
            (str | None) found = None: Potential path to ghci.exe

        Returns:
             True: Successfully loaded ghci.
             False: Could not complete loading.
        """

        valid = self._findGHCI(found)
        if valid:
            self._process = subprocess.Popen([self._GHCILoc],
                                             shell=True, stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             text=True)
            self._running = True
            self._GHCIThread = threading.Thread(target=self._updater, daemon=True)
            self._GHCIThread.start()
            return True
        else:
            if self._GHCIThread:
                tkinter.messagebox.showwarning("Hasket", "GHCi is already running.")
            else:
                tkinter.messagebox.showwarning("Hasket", "GHCi could not be started.")
            return False

    def _updater(self):
        while True:
            if not self._running:
                break
            line = self._process.stdout.readline()
            if not line:
                self._running = False
                break
            try:
                self._outputPipe(line)
            except RuntimeError:
                pass
        self._running = False
        if self._awaitingCallback:
            self._awaitingCallback = False
            self.startGHCI(self._GHCILoc)


    def bindEditor(self, editor: EditorPanel) -> None:
        """Binds the provided editor panel to the terminal.

        Parameters
            (EditorPanel) editor: Editor panel to bind.
        """
        self._boundEditor = editor

    def deletePanel(self) -> None:
        """Deletes the panel."""

        self._running = False
        try:
            self.__entryLine.delete("1.0", "end")
            self.__entryLine.insert("1.0", ":quit\r\n")
            self._submitTerminalEntry()
            self._process.kill()
        except TclError:
            pass
