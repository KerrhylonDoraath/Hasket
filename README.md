# Hasket Development

Hasket is a python based program that is designed to create a lightweight shell in python for streamlined writing of Haskell code.

The code contains options for extending Hasket functionality to include custom panels and designs for customisation and extensions of practicality.

## Features

### The terminal Window

TODO: Insert pic of terminal window.

The terminal is the main way to interact with GHCI. You can enter any haskell command in the entry bar at the bottom of the window, press enter, and the command will run.

TODO: Insert pic of terminal window with command usage.

The terminal also has additional commands implemented in Hasket:

***
- `\loadEditor` - If a program has been saved in the editor, then this command will load the script as if imported.

- `\restart` - Will attempt to restart GHCI if things have gone awry.
- `\clear` - Will clear the terminal output window.
- `\load <scriptPath>` - Will attempt to load the script provided
***