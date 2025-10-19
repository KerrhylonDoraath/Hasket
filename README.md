# Hasket Development - LEGACY

Hasket is a python based program that is designed to create a light shell for streamlined writing of Haskell code.

## LEGACY version w1.0

This branch is no longer maintained. It is the release of Haskell when it was stable to begin with.
Since it was never designed to run on any other systems, there are many bugs and issues, most notably...

- <b>This program relies on the Glasgow Haskell Compiler (GHCi) for Haskell, please ensure you have a functional version of GHCi before attempting to run this program! </b>
- (Please see the license for GHC below:)
	[https://www.haskell.org/ghc/license.html](https://www.haskell.org/ghc/license.html)

- <b>You have to change the path of your ghci executable on line 207, else Hasket will not find ghci.</b>
- <b>This program was designed for WINDOWS OS, so may be incompatible with MacOS and Linux-based systems.</b>

### Features in legacy 1.0:



- Terminal I/O.
	When the program is launched, it immediately attempts to spawn a secondary process. This process will run ghci, and pipe the output to the terminal.
	When the user wishes to interact with the terminal, they must start a new line in the terminal window, and type their command
	If the command is not registered, it is most likely that you are not on the final line of the editor, navigate downwards a bit.

- Editor
	When toggling over to the editor, Hasket will create a new haskell script file, where you can write and edit haskell code.
	If this program is saved for the first time, or if the program is loaded into Hasket, then it should already be loaded into the terminal.

That's it! It isn't complicated really, but at the time it streamlined working on my haskell projects, and I hope it will be of use to you too!
