

class EditorText:
    ##TEMPLATE CLASS

    ##Create object, and establish geometry
    def __init__(self, master: EditorText):
        self.__master = master
        self._mode = "UNDEFINED"
        self._outputPipe = self.printOut

    ##Set output to class provided
    def setOutPipe(self, output: EditorText) -> None:
        self._outputPipe = output.printOut

    ##Geometry to load
    def loadPanel(self):
        pass

    ##Geometry to delete
    def unloadPanel(self):
        pass

    ##Output method for window
    def printOut(self, text):
        print(text)