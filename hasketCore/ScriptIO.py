"""Standard interface for managing files.
Provides methods to save a script, or import a script.

Purely an IO library, so does not deal with any
panels.
"""

from tkinter import filedialog, messagebox

class ScriptIO:
    mFileTitle = ""

    @staticmethod
    def importScriptEntry(*_) -> tuple[str, str, str]:
        """Selects a script to load. Presumed a check has happened."""

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

    # Saving Verification Link
    @classmethod
    def saveCheck(cls, modified: bool =True) -> bool:
        """Checks if the script is saved or not."""

        if modified:
            return messagebox.askyesno(
                "Save Changes",
                f"Save changes to {cls.mFileTitle}?",
                icon="warning"
            )
        return False

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
    def saveScript(fileName : str | None, textToSave : str) -> str | None:
        """Saves a script to a file.
        :param fileName: The name of the file to save. None if the filename
        is to be selected.
        :param textToSave: The content string to write out.
        """

        fileName = ScriptIO._validateFileName(fileName)
        if fileName ==  "":
            return None
        try:
            with open(fileName, "w") as mFile:
                mFile.write(textToSave)
                messagebox.showinfo(
                    "Success",
                    f"Successfully saved to file: {fileName}!"
                )
                return fileName
        except OSError:
            messagebox.showerror(
                "Error",
                f"Unable to open file: {fileName}"
            )
        return None

    # SAVE AS SCRIPT
    @staticmethod
    def _saveAsScript(*_) -> str:
        """Requests a file name to save the file to."""

        return filedialog.asksaveasfilename(
            filetypes=[("Haskell Scripts", ".hs")])