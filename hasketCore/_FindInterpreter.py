from tkinter import Entry, Frame, Tk, Label, Button, PhotoImage
import tkinter.messagebox

class __FindInterpreter:
    def __init__(self):
        self.temp = Tk()
        self.temp.title("Locate GHCi")
        self.temp.resizable(False, False)
        self.temp.iconbitmap("HASKET.ico")
        self.temp.geometry("520x175")
        self.temp.config(bg="#404040")

        self.attemptString = ""
        self.__constructGeometry()

        self.mEntry.focus_set()
        self.temp.grab_set()

    def __constructGeometry(self):
        Label(self.temp, text="Please enter location of GHCi executable")\
            .pack(side="top", padx=10, pady=(10, 5))

        middleFrame = Frame(self.temp, background="#404040")
        middleFrame.pack(side="top", padx=10)

        self.mEntry = Entry(middleFrame, width=64)
        self.mEntry.pack(side="right", padx=10, pady=(10, 0))
        self.mEntry.bind("<Return>", lambda event: self.getReturn())

        imgFrame = Frame(middleFrame, background="white", highlightthickness=2,
                         highlightbackground="black", highlightcolor="black")
        imgFrame.pack(side="left", padx=10, pady=10, expand=True)

        img = PhotoImage(file="Haskell.png")
        mLabel = Label(imgFrame, image=img)
        mLabel.pack(padx=2, pady=2)

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
    if tkinter.messagebox.askyesno("GHCi not found",
                                   "Would you like to specify the location of ghci.exe?"):
        locator = __FindInterpreter()
        locator.awaitWindow()
        return locator.attemptString
    return None