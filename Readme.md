# The Witcher 3 Mod Manager

An application to simplify installing and managing mods for the game The Witcher 3.

## Description

The Witcher 3 Mod Manager is an application that simplifies installing and managing The Witcher 3 mods, originally developed by [stefan3372](https://github.com/stefan3372) and now being continued here.

Now also found on the original [Nexus Mods page](https://www.nexusmods.com/witcher3/mods/2678)!
See there for screenshots and more information.

## Usage

### Release Versions

Download and unpack the latest release from Nexus Mods or from the GitHub releases. If you are upgrading from version 0.6 or later, directly overwrite the previous installation. Existing configuration files wll be searched in the same directory as the executable first, in `Documents\The Witcher 3 Mod Manager` second.

On the first run, if no configuration can be found, configuration files will be created under `Documents\The Witcher 3 Mod Manager`. They can be freely relocated between the two searched locations as preferred.

Note: If you encounter issues with Script Merger, update to the recent release of [Script Merger Unofficial Patch](https://www.nexusmods.com/witcher3/mods/3395).

### Python

Download the source and install the requirements with `pipenv install --python 3`. Python 3.7+ and Pipenv have to be installed. Afterwards run with `pipenv run python main.py`.

On Linux, the configuration files will be created in `~/.config/The Witcher 3 Mod Manager`.
