from tkinter import Button, Entry, Frame,  Label, Tk, TclError
import tkinter.messagebox


class __FindInterpreter:
    def __init__(self):
        self.temp = Tk()
        self.temp.title("Locate GHCi")
        self.temp.resizable(False, False)
        try:
            self.temp.iconbitmap("HASKET.ico")
        except TclError:
            pass
        self.temp.geometry("460x125")
        self.temp.config(bg="#404040")

        self.attemptString = ""
        self.__constructGeometry()

        self.mEntry.focus_force()

    def __constructGeometry(self):
        Label(self.temp, text="Please enter location of GHCi executable") \
            .pack(side="top", padx=10, pady=(10, 5))

        middleFrame = Frame(self.temp, background="#404040")
        middleFrame.pack(side="top", padx=10)

        self.mEntry = Entry(middleFrame, width=64)
        self.mEntry.pack(side="right", padx=10, pady=(10, 0))
        self.mEntry.bind("<Return>", lambda event: self.getReturn())

        mBFrame = Frame(self.temp, bg="#000080")
        mBFrame.pack(side="bottom", pady=(0, 10))

        mSubmitButton = Button(mBFrame, text="Submit", command=lambda: self.getReturn())
        mSubmitButton.pack(side="left", padx=5, pady=5)

        mCancelButton = Button(mBFrame, text="Cancel", command=lambda: self.temp.destroy())
        mCancelButton.pack(side="right", padx=5, pady=5)

    def getReturn(self):
        self.attemptString = self.mEntry.get()
        if self.attemptString[-1] == "\n":
            self.attemptString = self.attemptString[:-1]
        self.temp.destroy()

    def awaitWindow(self) -> None:
        self.temp.wait_window()


def findGHCI() -> str | None:
    """Simple procedure to find GHCI on the user's computer."""

    if tkinter.messagebox.askyesno("GHCi not found",
                                   "Would you like to specify the location of ghci.exe?"):
        locator = __FindInterpreter()
        locator.awaitWindow()
        return locator.attemptString
    return None
