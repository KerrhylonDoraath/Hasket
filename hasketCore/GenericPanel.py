"""Generic editor panel for the Hasket editor.

The Hasket interface acts as a container for a selection of panels
which perform related functions. At its root, every panel is an editor,
except its precise implementation is left up to the programmer.
"""

from tkinter import Widget

class GenericPanel:

    def __init__(self, master: Widget):
        """master parameter is for attaching to a valid tkinter context."""

        self._master = master
        self._mode = "UNDEFINED"
        self._outputPipe = self.printOut


    def setOutPipe(self, output: GenericPanel) -> None:
        """Sets the output pipe."""

        self._outputPipe = output.printOut


    def loadPanel(self) -> None:
        """Loads the editor panel into the master's context."""

        pass


    def unloadPanel(self) -> None:
        """Unloads the editor panel from the master's context."""

        pass

    def printOut(self, text: str) -> None:
        """Outputs the given text to the output pipe.
        However, this is defaulted to standard output.
        """

        print(text)
