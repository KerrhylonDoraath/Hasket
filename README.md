# Hasket Development

Hasket is a python based program that is designed to create a lightweight shell in python for streamlined writing of Haskell code.

The code contains options for extending Hasket functionality to include custom panels and designs for customisation and
extensions of practicality.

## Features

### The terminal Window

TODO: Insert pic of terminal window.

The terminal is the main way to interact with GHCI. You can enter any haskell command in the entry bar at the bottom of
the window, press enter, and the command will run.

TODO: Insert pic of terminal window with command usage.

The terminal also has additional commands implemented in Hasket:

***
- `\loadEditor` - If a program has been saved in the editor, then this command will load the script as if imported.
- `\restart` - Will attempt to restart GHCI if things have gone awry.
- `\clear` - Will clear the terminal output window.
- `\load <scriptPath>` - Will attempt to load the script provided
***

## Style Guides for future additions

This project will generally conform to established <a href="https://peps.python.org/pep-0008/">PEP-8</a> style guides
for python with one notable exception:

- Class methods and members shall conform to `mixedCase` convention. This is because
I like this standard and arguably this is my project.

Variable names inside of functions do not have to follow any specific naming conventions.

***

Class members that are public are to be named starting with a lowercase `m`. This distinguishes
them as member variables. 

Examples include: `mVector` `mParam1` `mAccelleration`

<i>Key note: Inheritance is a key part of including additional window tabs in Hasket.
If a new tab is created, please implement all base methods. To practice public and non-public standards,
any mangled names are to be kept mangled. Please do not go into the parent class, I will reject your merge request!</i>