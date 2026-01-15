from typing import override

import os
import subprocess
import threading
from tkinter import Frame, Text, Scrollbar, Tk, Label, Entry, Button, PhotoImage
import tkinter.messagebox

from hasketCore.GenericPanel import GenericPanel
from hasketCore._FindInterpreter import findGHCI

class EditorTerminalOut(GenericPanel):
    def __init__(self, master):
        GenericPanel.__init__(self, master)
        self._mode = "TERMINAL"
        self._running = False
        self._GHCIThread = None
        self._GHCILoc = None
        self._process = None

        self.__microFrame = Frame(master, highlightthickness=0, highlightcolor="#000080")
        self.__mainTextWidget = Text(self.__microFrame, width=100, height=20, state="disabled",
                                     bg="black", fg="white", highlightthickness=1,
                                     highlightcolor="white", insertbackground="white")
        self.__entryLine = Text(master, height=1, bg="black", fg="white", highlightthickness=1,
                                highlightcolor="white", insertbackground="white")
        self.__entryLine.bind("<Return>", lambda event: self.submitTerminalEntry(event))
        self.__mScrollbar = Scrollbar(self.__microFrame, orient="vertical", width=20,
                                      command=self.__mainTextWidget.yview)
        self.__mainTextWidget.config(yscrollcommand=self.__mScrollbar.set)
        self.__mainTextWidget.bind("<FocusIn>",self.focusReset)

        self.boundEditor = None

    @override
    def loadPanel(self):
        self.__microFrame.pack(expand=True, fill="both", padx=2, pady=(0, 2))
        self.__entryLine.pack(side="bottom", fill="x", expand=False, padx=2, pady=(5, 2))
        self.__mScrollbar.pack(side="right", fill="y", expand=False)
        self.__mainTextWidget.pack(side="left", fill="both", expand=True)
        self.__mainTextWidget.focus()
        self.__entryLine.focus_set()

        if not self._running:
            self.startGHCI()
            if not self._running:
                self._outputPipe(
                    "Could not start GHCi. Please run command \\restart to restart GHCi.\n")

    @override
    def unloadPanel(self):
        self.__mainTextWidget.pack_forget()
        self.__mScrollbar.pack_forget()
        self.__microFrame.pack_forget()
        self.__entryLine.pack_forget()

    # Input from the user in terminal mode
    def submitTerminalEntry(self, event):
        mEntry = self.__entryLine.get("1.0", "end")
        self.__entryLine.delete("0.0", "end")
        while mEntry[0] == '\n':
            mEntry = mEntry[1:]
        if mEntry[0] == "\\":
            self.callCommandLibrary(mEntry[1:-1])
        else:
            if len(mEntry) == 0:
                return
            ##Pipe entry to GHCi instead
            self._process.stdin.write(mEntry)
            self._process.stdin.flush()
            self._outputPipe(mEntry)  ##pipe it to output

    @override
    def printOut(self, text: str) -> None:
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.insert("end", text)
        self.__mainTextWidget.config(state="disabled")
        self.__mainTextWidget.see("end")

    def clearOutput(self):
        self.__mainTextWidget.config(state="normal")
        self.__mainTextWidget.delete("1.0", "end")
        self.__mainTextWidget.config(state="disabled")

    def focusReset(self, *ignore):
        self.__entryLine.focus_set()

    # The terminal can have some commands
    def callCommandLibrary(self, mInput):
        mInput = mInput.split(" ")

        if mInput[0] == "loadEditor":
            try:
                if self.boundEditor.scriptName == "Untitled" or not self.boundEditor.scriptName:
                    self._outputPipe("> Please save the contents of the editor.\n")
                    return
                if not self._running:
                    self._outputPipe(
                        "> Could not start GHCi. Please run command \\restart to restart GHCi.\n")
                    return
                mEntry = r'"' + self.boundEditor.scriptName + r'"'
                mEntry = mEntry.encode("unicode_escape").decode()
                self._process.stdin.write(f":load {mEntry}\n")
                self._process.stdin.flush()
            except Exception as e:
                self._outputPipe(f"> {e}\n")
        elif mInput[0] == "restart":
            self.startGHCI()

        elif mInput[0] == "clear":
            self.clearOutput()

        elif mInput[0] == "load":
            if len(mInput) == 2:
                if not self._running:
                    self._outputPipe(
                        "> Could not start GHCi. Please run command \\restart to restart GHCi.\n")
                    return
                rawIn = mInput[1].encode("unicode_escape").decode()
                self._process.stdin.write(f":load {rawIn}\n")
                self._process.stdin.flush()
            else:
                self._outputPipe("> Please specify a haskell script to load.\n")
        else:
            self._outputPipe("> Unknown Command.\n")

    def startGHCI(self, found=None):
        valid = False
        mPath = None

        if found:
            if os.path.isfile(found):
                valid = True
                self._GHCILoc = found
                mPath = self._GHCILoc
            else:
                return False

        if not self._GHCILoc:
            mPath = findGHCI()
            if mPath:
                if os.path.isfile(mPath):
                    valid = True
                    self._GHCILoc = mPath
                    self.writeConfigFile()
        if valid:
            self._process = subprocess.Popen([mPath], shell=True, stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             text=True)
            self._running = True
            self._GHCIThread = threading.Thread(target=self.updater)
            self._GHCIThread.start()
        else:
            tkinter.messagebox.showerror("Hasket", "GHCi could not be started.")

        return True

    def updater(self):
        while self._running:
            line = self._process.stdout.readline()
            if not line:
                break
            try:
                self._outputPipe(line)
            except RuntimeError:
                pass

    def writeConfigFile(self):
        try:
            with open("HaskConf.cfg", "a") as configFile:
                configFile.write(f"config: {self._GHCILoc}\n")
        except OSError:
            pass

    @override
    def deletePanel(self) -> None:
        self._running = False
        try:
            self._process.stdin.write(" :quit\r\n")
            self._process.stdin.flush()
            self._process.kill()
        except AttributeError:
            pass