"""Standard interface for managing files.
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

        foundFile = filedialog.askopenfilename(
            filetypes=[("Haskell Scripts", ".hs")])
        if not foundFile:
            return "", "", ""
        return ScriptIO._importScript(foundFile)

    @staticmethod
    def __extractPath(itemName: str) -> str:
        if itemName[-1] not in ("\\", "/"):
          return ScriptIO.__extractPath(itemName[:-1])
        return itemName

    @staticmethod
    def _importScript(scriptName: str) -> tuple[str, str, str]:
        """Imports a script and returns its name and contents."""

        try:
            with open(scriptName, "r") as mEntry:
                return ScriptIO.__extractPath(scriptName), scriptName, mEntry.read()
        except OSError:
            messagebox.showerror(
                "Error",
                f"Unable to open file: {scriptName}"
            )
            return "", "", ""

    @staticmethod
    def _validateFileName(fileName : str | None) -> str:
        """Validates the filename."""

        if not fileName or fileName == "Untitled":
            fileName = ScriptIO._saveAsScript()[0]
            if not fileName:
                return ""
            if fileName[-3:] != ".hs":
                fileName += ".hs"
        return fileName

    # SAVING SCRIPT
    @staticmethod
    def saveScript(fileName : str | None, text : str) -> int:
        """Saves a script to a file.

        Parameters:
            (str) fileName: Name of the file to save.
            (str) text:     Text to write to the file.

        Returns:
            (int)  0: Success.
            (int)  1: Filename was invalid, or operation was cancelled.
            (int) -1: OSError occurred
        """

        fileName = ScriptIO._validateFileName(fileName)
        if fileName ==  "":
            return 1
        try:
            with open(fileName, "w") as mFile:
                mFile.write(text)
                messagebox.showinfo(
                    "Success",
                    f"Successfully saved to file: {fileName}!"
                )
                return 0
        except OSError:
            messagebox.showerror(
                "Error",
                f"Unable to open file: {fileName}"
            )
        return -1

    # SAVE AS SCRIPT
    @staticmethod
    def _saveAsScript(*_) -> str:
        """Requests a file name to save the file to."""

        return filedialog.asksaveasfilename(
            filetypes=[("Haskell Scripts", ".hs")])