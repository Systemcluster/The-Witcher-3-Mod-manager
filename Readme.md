# The Witcher 3 Mod Manager

**Mod Manager for The Witcher 3.**

Supports the Steam and GOG releases on Windows, Steam Proton installations on Linux and CrossOver installations on macOS.

Works with Original, Next-Gen, and Remastered installations.

## Description

The Witcher 3 Mod Manager is an application that simplifies installing and managing The Witcher 3 mods, originally developed by [stefan3372](https://github.com/stefan3372) and now being continued here.

See the [Nexus Mods page](https://www.nexusmods.com/witcher3/mods/2678) for releases, screenshots and more information.

## Usage

### Release Versions (Windows)

Download the release archive from Nexus Mods or from the [maintained GitHub releases](https://github.com/Systemcluster/The-Witcher-3-Mod-manager/releases).
The user configuration is reused automatically. For a portable installation with `config.ini` beside the executable, copy that configuration, `installed.xml`, and the `extracted` directory into the new manager directory.

On the first run, if no configuration can be found, configuration files will be created under `AppData\Local\The Witcher 3 Mod Manager`.
Existing configuration files will be read from the directory of the executable first and in `Documents\The Witcher 3 Mod Manager` second for compatibility with prior versions. They can be freely relocated between the searched locations as preferred.

### Script Merger on Linux and macOS

Choose the Script Merger executable in the manager first. To use a particular Wine prefix, close the manager and add `mergerlaunchcommand` to the existing `[PATHS]` section of `config.ini`, for example:

```ini
[PATHS]
scriptmerger=/home/user/Tools/Script Merger/WitcherScriptMerger.exe
mergerlaunchcommand=WINEPREFIX="/home/user/Games/Witcher 3/prefix" wine "/home/user/Tools/Script Merger/WitcherScriptMerger.exe"
```

For Steam with `protontricks-launch` installed, an alternative is:

```ini
mergerlaunchcommand=protontricks-launch --appid 292030 "/home/user/Tools/Script Merger/WitcherScriptMerger.exe"
```

Replace the paths and, for a non-Steam shortcut, the app ID with the actual values. CrossOver users need a command targeting the correct bottle. The executable path must remain configured, and its directory is the command's working directory. Unlike `gamelaunchcommand`, this override is interpreted by a shell on Linux/macOS: use only trusted commands and quote paths containing spaces. Without an override, the manager runs `wine` with the selected executable. Windows runs the executable directly.

### Startup Diagnostics

Early startup failures, including missing Qt DLL imports, write a `TW3MM-startup-*.log` file in the system temporary directory when it is writable, even when the GUI cannot open. On Windows or inside a Wine bottle, check that environment's `%TEMP%`; on Linux/macOS, check the Python runtime's temporary directory, usually selected through `TMPDIR` or `/tmp`. The log path is also printed to the console when one is available. Review personal paths before sharing the log.

A log does not fix a missing runtime dependency. Running the Windows executable under Wine/Proton/CrossOver still needs release-artifact compatibility testing; do not install arbitrary DLL downloads. Running the manager from Python natively is an alternative.

### Game Configuration

Select `witcher3.exe` under `bin/x64` (DX11) or `bin/x64_dx12` (DX12). The command-line `--game` option also accepts the installation root.

If an update removes the configured executable, the manager uses an available renderer version from the same game directory without rewriting `config.ini`. Detection follows the current files and launcher metadata, including after a rollback; it does not search other installations.

Remastered's supplied launcher metadata identifies `remasteredEdition` and the store. Edition detection uses that metadata, with an executable-layout fallback for older installations. The selected executable determines which user-settings file the manager opens. Existing menu file lists are updated when present; missing lists are not created.

Steam installations launch through Steam, including on Windows, to avoid the reported crash when starting the Remastered executable directly. The renderer and mod options used for that launch are controlled by Steam/REDlauncher. Non-Steam Windows installations launch the selected executable directly.

For another launch environment, set `gamelaunchcommand` in the `[PATHS]` section of `config.ini`. It overrides automatic launching. On Linux/macOS, quote paths and arguments containing spaces; commands are parsed into arguments, not interpreted by a shell. CrossOver users must configure a command that launches Steam in the correct bottle if the system's `steam://` handler does not do so. Use `--userdocuments` to select that environment's Documents directory containing `The Witcher 3`; do not assume the host's Documents directory is the game's.

### Remastered Troubleshooting

- **Startup or executable selection:** a missing `gameexe` setting opens the selection dialog. Select the existing DX12 executable, without making dummy executables or directories.
- **Game crashes from the manager:** use the Steam launch route. Do not delete or rename `steam_api64.dll`; it is part of the game installation.
- **Mods install but do not load:** check that mods are enabled in REDlauncher and that neither Steam launch options nor a custom command includes `-disablemods`. Check that `--userdocuments` points at the game's actual settings directory when using Proton/CrossOver. A successful installation does not make an older mod compatible with Remastered.
- **Merging fails:** Script Merger is a separate application. The [Fresh and Automated Edition page](https://www.nexusmods.com/witcher3/mods/8405) reported Remastered bundle-format support as still being tested on September 29, 2026. Check its current compatibility notes; the manager cannot repair incompatible scripts or bundle readers.
- **Script Merger recreates an old game folder:** change the game directory inside Script Merger too. Its own configuration can retain `GameDirectory`, `ModsDirectory`, and `VanillaScriptsDirectory` overrides. Changing the manager's game path does not rewrite those external settings. Back up the merger's configuration before resetting overrides or rebuilding merges.
- **Finding/resetting manager settings:** close the manager and back up its configuration directory first. Check for a portable `config.ini` beside the executable, then the locations described above. To reset paths, rename only `config.ini`; retain `installed.xml` and `extracted` to preserve the manager's mod inventory. Game load order remains in `The Witcher 3/mods.settings` under the configured Documents directory.

### Python (Windows, Linux, and macOS)

The project uses [PDM](https://pdm-project.org/en/latest/) for dependency management. Requires Python 3.10 or newer (3.10+), up to Python 3.12.

1. Install PDM with [recommended installation method](https://pdm-project.org/en/latest/#recommended-installation-method)
2. Clone the repository
3. Install dependencies: `pdm install --prod`
4. Run the application: `pdm run start`

On Linux:
- Configuration files are created in `~/.config/TheWitcher3ModManager`
- `wine` must be available to run Script Merger
- Consider using `pdm run` prefix for all commands

### Development Checks

Install development tools with `pdm install`.

- `pdm run format`: format every project Python file.
- `pdm run lint`: check imports and core Python errors without changing files.
- `pdm run ruff check --fix .`: apply safe lint fixes, including import sorting.
- `pdm run check`: check formatting, lint, Pyright, mypy, and all tests.
- `pdm run typecheck-pyright`: run the CLI checker underlying Pylance with the project's `standard` settings.
- `pdm run typecheck`: run mypy as a second type check.

### Build Release (Windows)

1. Use a fresh environment and install dependencies with development tools: `pdm install`.
2. Run checks: `pdm run check`
3. Build executable: `pdm run build-win`
4. Find files in `build/exe.[platform identifier].[python version]`
