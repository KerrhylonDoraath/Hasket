from tkinter import *


from GenericPanel import GenericPanel

##TEXT EDITOR
class EditorFile(GenericPanel):

    # Designed to be a writeable area for haskell code development
    def __init__(self, master):
        GenericPanel.__init__(self, master)
        self.MODE = "EDITOR"

        # Script Name is what to call the file open
        self.scriptName = "Untitled"

        # Function pointer, points to a function to set the window title
        self.setTitle = None

        # Tracks the state of open files in the Hasket window
        self.MODIFIED = False

        # Text widget
        self.__secondaryTextWidget = Text(master, bg="white", fg="black",
                                          highlightthickness=1,
                                          highlightcolor="black",
                                          insertbackground="black")

        # Bindings
        self.__secondaryTextWidget.bind("<Control-s>",
                                        lambda event: self.saveScript())
        self.__secondaryTextWidget.bind("<Control-Shift-S>",
                                        lambda event: ScriptIO.saveScript(
                                            ScriptIO.saveAsScript,
                                            self.__secondaryTextWidget))
        self.__secondaryTextWidget.bind("<Control-o>",
                                        lambda event: self.openScript())
        self.__secondaryTextWidget.bind("<Control-n>",
                                        lambda event: self.newScript())
        self.__secondaryTextWidget.bind("<<Modified>>",
                                        lambda event: self.setModified())

        # Scrollbar setup
        self.__mScrollbar = Scrollbar(master, orient=VERTICAL, width=20,
                                      command=self.__secondaryTextWidget.yview)
        self.__secondaryTextWidget.config(yscrollcommand=self.__mScrollbar.set)

    # Modification callback
    def setModified(self):
        self.MODIFIED = True

    # inherited method
    def loadPanel(self):
        self.__mScrollbar.pack(side=RIGHT, fill=Y, expand=False, padx=2,
                               pady=(0, 2))
        self.__secondaryTextWidget.pack(side=LEFT, fill=BOTH, expand=True,
                                        padx=(2, 0), pady=(0, 2))
        self.__secondaryTextWidget.focus()

    # inherited method
    def unloadPanel(self):
        self.__secondaryTextWidget.pack_forget()
        self.__mScrollbar.pack_forget()

    # Prompts saving
    def checkSave(self):
        if self.MODIFIED:
            saveTest = tkinter.messagebox.askyesnocancel("Warning",
                                                         f"Save changes to {self.scriptName}?")
            if saveTest == None:
                return False  ##User hit cancel
            if saveTest:
                self.saveScript()  ##Save the user script
        return True  ##Completed check

    # User creates a new script
    def newScript(self, *ignore):
        if self.MODIFIED:
            if not self.checkSave():
                return
        self.scriptName = "Untitled"
        self.setWindowTitle()  # Create window title with untitled document
        self.__secondaryTextWidget.delete("1.0", END)  # Clear text in widget
        self.__secondaryTextWidget.edit_modified(False)  # Reset modified flag
        self.MODIFIED = False  # Reset class modified flag

    def openScript(self, *ignore):
        if not self.checkSave():  ##Check if the user wants to save
            return
        self.scriptName, text = ScriptIO.importScriptEntry()  # Get import name and text
        self.__secondaryTextWidget.delete("1.0", END)
        self.__secondaryTextWidget.insert("1.0", text)
        self.__secondaryTextWidget.edit_modified(False)
        # Even if we have no text, nothing will be put in so we need not check
        self.MODIFIED = False
        self.setWindowTitle()  # Untitled, or file path
        ##Planning to deprecate

    def saveScript(self, *ignore):
        self.scriptName = ScriptIO.saveScript(self.scriptName,
                                              self.__secondaryTextWidget)  # save script
        self.setWindowTitle()
        self.__secondaryTextWidget.edit_modified(False)
        self.MODIFIED = False  # Reset the modified tags

    def saveAsScript(self, *ignore):
        self.scriptName = ScriptIO.saveScript(ScriptIO.saveAsScript(),
                                              self.__secondaryTextWidget)  # save as...
        self.setWindowTitle()
        self.__secondaryTextWidget.edit_modified(False)
        self.MODIFIED = False  # Reset the modified tags

    def setTitleCommand(self, command):
        self.setTitle = command  # Called by main window to set title function(No globals!)

    def setWindowTitle(self):
        self.setTitle(self.scriptName)  # Wrapper to call setTitle more easily

    def setOutPipe(self):
        pass  # No need for an output pipe

    def __del__(self):
        self.checkSave()