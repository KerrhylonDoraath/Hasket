from tkinter import Label, Widget

from hasketCore.GenericPanel import GenericPanel

class SamplePanel(GenericPanel):
    def __init__(self, master: Widget):
        super().__init__(master)
        self.handyLabel = Label(master, text="I am a new label!")

    def loadPanel(self) -> None:
        self.handyLabel.pack(anchor="center")

    def unloadPanel(self) -> None:
        self.handyLabel.pack_forget()