##TEMPLATE CLASS
class EditorText:
    ##Create object, and establish geometry
    def __init__(self, master):
        self.MODE = "UNDEFINED"
        self.__master = master
        self.OUTPUT_PIPE = self.printOut

    ##Set output to class provided
    def setOutPipe(self, output):
        self.OUTPUT_PIPE = output.printOut

    ##Geometry to load
    def loadPanel(self):
        pass

    ##Geometry to delete
    def unloadPanel(self):
        pass

    ##Output method for window
    def printOut(self, text):
        print(text)