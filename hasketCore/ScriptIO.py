"""Hasket Script IO

Standard interface for managing files.
Provides methods to save a script, or import a script.

Purely an IO library, so does not deal with any
panels.

"""

from tkinter import filedialog, messagebox

class ScriptIO:

    @staticmethod
    def importScriptEntry(*_) -> tuple[str, str, str]:
        """Selects a script to load. Presumed a check has happened.

        Returns:
            (str) File path
            (str) File name
            (str) File contents
        """

        foundFile = filedialog.askopenfilename(filetypes=[("Haskell Scripts", ".hs")])
        if not foundFile:
            return "", "", ""
        return ScriptIO._importScript(foundFile)

    @staticmethod
    def __extractPath(itemName: str) -> str:
        if itemName[-1] not in ("\\", "/"):
          return ScriptIO.__extractPath(itemName[:-1])
        return itemName

    @staticmethod
    def __extractName(itemName: str) -> str:
        if itemName[-1] not in ("\\", "/"):
            return ScriptIO.__extractName(itemName[:-1]) + itemName[-1]
        return ""

    @staticmethod
    def _importScript(scriptName: str) -> tuple[str, str, str]:
        """Imports a script and returns its name and contents."""

        try:
            with open(scriptName, "r") as mEntry:
                return (ScriptIO.__extractPath(scriptName),
                        ScriptIO.__extractName(scriptName),
                        mEntry.read())
        except OSError:
            messagebox.showerror("Error", f"Unable to open file: {scriptName}")
            return "", "", ""

    @staticmethod
    def _validateFileName(fileName : str | None) -> str:
        """Validates the filename."""

        if not fileName or fileName == "Untitled":
            fileName = ScriptIO._saveAsScript()
            if not fileName:
                return ""
            if fileName[-3:] != ".hs":
                fileName += ".hs"
        return fileName

    # SAVING SCRIPT
    @staticmethod
    def saveScript(fileName : str | None, text : str) -> tuple [int, tuple[str, str, str] | None]:
        """Saves a script to a file.

        Parameters:
            (str) fileName: Name of the file to save.
            (str) text:     Text to write to the file.

        Returns:    int, (str str str)
            result (int):
                 0: Success.
                 1: Filename was invalid, or operation was cancelled.
                -1: OSError occurred
            textVariables (tuple(str, str, str))
                [0]: File path
                [1]: File name
                [2]: File contents
        """

        fileName = ScriptIO._validateFileName(fileName)
        if fileName ==  "":
            return 1, None
        try:
            with open(fileName, "w") as mFile:
                mFile.write(text)
        except OSError:
            messagebox.showerror("Error", f"Unable to open file: {fileName}")
            return -1, None
        messagebox.showinfo("Success", f"Successfully saved to file: {fileName}!")
        return 0, ScriptIO._importScript(fileName)

    @staticmethod
    def _saveAsScript(*_) -> str:
        """Requests a file name to save the file to."""

        return filedialog.asksaveasfilename(filetypes=[("Haskell Scripts", ".hs")])

    @staticmethod
    def writeConfigFile(inputString: str) -> int:
        """Writes to the HaskConf.cfg configuration file.

        Parameters:
              (str) inputString: Text to write to the file.

        Returns:    int
            result (int):
                0: Success.
                1: OSError occurred
        """

        try:
            with open("HaskConf.cfg", "a") as configFile:
                configFile.write(inputString)
            return 0
        except OSError:
            return 1

    @staticmethod
    def writeConfigFileN(inputString: str) -> int:
        """Same as writeConfigFile, just adds a newline character."""

        return ScriptIO.writeConfigFile(inputString + "\n")

    @staticmethod
    def readConfigFile() -> list[str] | None:
        importData = []
        try:
            with open("HaskConf.cfg", "r") as configFile:
                mData = configFile.readline()
                while mData != "":
                    importData.append(mData)
                    mData = configFile.readline()
                return importData
        except OSError:
            messagebox.showwarning("Warning",
                                    "The Hasket configuration file could not be found.")
            return None