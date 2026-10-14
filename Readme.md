# The Witcher 3 Mod Manager

**Mod Manager for The Witcher 3.**

Supports the Steam and GOG releases on Windows, Steam Proton installations on Linux and CrossOver installations on macOS.

Works with Original, Next-Gen, and Remastered installations.

## Description

The Witcher 3 Mod Manager is an application that simplifies installing and managing The Witcher 3 mods, originally developed by [stefan3372](https://github.com/stefan3372) and now being continued here.

See the [Nexus Mods page](https://www.nexusmods.com/witcher3/mods/2678) for releases, screenshots and more information.

## Usage

### Release Versions (Windows)

Download the latest release from Nexus Mods or from the [GitHub releases](https://github.com/Systemcluster/The-Witcher-3-Mod-manager/releases).

Existing configuration is picked up automatically when updating. Portable installations keep `config.ini` next to the executable; to update one, copy `config.ini` and `installed.xml` into the new directory.

Updates are manual: this manager does not check for, download, or install new versions automatically. Close the manager, back up its configuration directory, extract the complete new release into a new directory, and preserve the configuration as described above. Updating the manager does not require reinstalling your mods.

If no configuration exists on the first run, it is created in `AppData\Local\The Witcher 3 Mod Manager`. Existing configuration is searched for in the directory of the executable first and in `Documents\The Witcher 3 Mod Manager` second for compatibility with older versions, and can be moved freely between these locations.

Windows Explorer may hide the `.exe` extension and display the application as `TheWitcher3ModManager`. Enable **View > Show > File name extensions** to check; extract the entire release, not just the executable.

If Nexus quarantines a release, only Nexus can review and release that upload. Check the matching GitHub release linked above as an alternative, and do not disable antivirus protection to force a download. A packaging change does not certify a file as safe or lift an existing quarantine.

### File Safety

Shared game menus such as `graphics.xml` remain installed and registered when a mod is disabled or uninstalled. Their original contents are not backed up or restored; restore those separately when removing a shared-menu replacement.

INI files packaged under `bin/config/base` are copied to the same location in the game, including from INI-only packages. Folder names and the `.ini` extension are matched case-insensitively; INIs elsewhere in a package still require manual installation. Files are replaced whole, not merged. These shared base configuration files remain in place when a mod is disabled or uninstalled, and their previous contents are not backed up or restored. Back up affected files before installing a replacement.

Mod and DLC folders are only removed or replaced inside the `Mods` and `DLC` directories of the configured game, and other installed files only inside the game directory. Symbolic links and Windows junctions in the game directory are not supported and are never followed for deletion.

A replaced mod folder is kept until its new copy is in place. If it can't be restored after a failure, the error names the `.tw3mm-*` directory holding the original files. Mutable configuration and settings files are also written to sibling temporary files and atomically replaced. Linked configuration and Documents settings files are updated at their targets without replacing the links. A failed installation doesn't remove files it already copied; a complete installation or uninstall is not transactional.

Mod and DLC directories still referenced by another installed entry are retained rather than deleting that entry's files.

Overwrite **Yes to all** and **No to all** apply to the entire selected installation batch. The output log records copied destinations and skipped folders; unrecognized content in an otherwise valid package marks the installation incomplete.

Folders inside a package's `content` directory are treated as payload, not separate mods or DLCs. They are copied with their containing mod or DLC; sibling packages and configuration files outside `content` are still detected.

### Enabled and Disabled Mods

The checkbox records the manager's requested state in `installed.xml`; it is not a check that every file exists or that the game can load the mod. Reloading the inventory does not enable, disable, or repair files. Invalid or missing saved status is treated as an inventory error, allowing recovery from a valid backup rather than silently assuming a mod is disabled.

| Component | Disabled behavior | Rationale |
| --- | --- | --- |
| Mod folders | `Mods/modExample` becomes `Mods/~modExample`. | Keeps files and customizations without leaving the normal mod folder active. |
| DLC files | Non-dotfiles beneath `DLC/dlcExample` receive a `.disabled` suffix, including in nested directories. The DLC directory itself keeps its name. | Disables the payload while retaining its directory layout; folder browsing uses the unchanged DLC path. |
| Custom menu XML | Receives a `.disabled` suffix and is removed from existing DX11/DX12 menu file lists. | Prevents the disabled menu from being registered. Enabling restores the name and registration. |
| Extracted input/hidden XML additions | Removed on disable, reapplied on enable. | Keeps these additions aligned with the mod's state. |
| Protected game menus and base INIs | Remain installed, unchanged by toggling. | These are shared game files, not safely reversible per-mod assets. A package containing only these files cannot be deactivated with the checkbox. |
| User settings and input bindings | Remain during toggles. | Preserves customized preferences and bindings. Uninstall removes recorded user-setting options, but leaves input bindings. |
| Load-order priority | Retained during toggles. Priority-setting actions reject disabled mods; clearing a saved priority remains available. | Disabling should not lose the chosen load order. |

Updating a package with the same manager name preserves its disabled status, including mod/DLC payloads and custom menus. Disabled DLC updates are prepared before replacing the installed folder. Importing still applies shared-file replacements and settings as usual. **Restore default settings** deliberately enables a disabled mod and reapplies stored settings; it does not recover missing mod or menu files. **Uninstall** removes active and disabled copies directly, without enabling the mod first.

Toggles check paths and name collisions before changing files and never intentionally overwrite an existing active/disabled counterpart. If a rename or disable-time configuration update fails, the manager attempts to restore earlier changes and keeps the previous checkbox state. If restoration also fails, the error identifies the paths needing manual recovery. Enable-time XML/registration failures retain the existing incomplete-installation warnings. Missing assets are not recreated, and external changes, process interruption, and overlapping packages are not automatically reconciled. Packages sharing custom menus or XML additions are not reference-counted: toggling or removing one can affect another.

The checkbox does not override separate game controls such as `Enabled=0` in `mods.settings`, REDlauncher settings, or `-disablemods` launch arguments. If an enabled mod does not load, check those controls and missing files as well.

### Script Merger on Linux and macOS

Script Merger is run with `wine` using the executable selected in the manager. To run it in a specific Wine prefix, set `mergerlaunchcommand` in the `[PATHS]` section of `config.ini` while the manager is closed:

```ini
[PATHS]
scriptmerger=/home/user/Tools/Script Merger/WitcherScriptMerger.exe
mergerlaunchcommand=WINEPREFIX="/home/user/Games/Witcher 3/prefix" wine "/home/user/Tools/Script Merger/WitcherScriptMerger.exe"
```

With Steam and `protontricks-launch`, the Proton prefix of the game can be used instead:

```ini
mergerlaunchcommand=protontricks-launch --appid 292030 "/home/user/Tools/Script Merger/WitcherScriptMerger.exe"
```

Replace the paths with your own, and the app ID if the game was added as a non-Steam shortcut. For CrossOver, the command has to target the bottle the game is installed in.

The Script Merger executable still has to be selected in the manager, and its directory is used as the working directory of the command. Unlike `gamelaunchcommand`, the command is run through a shell, so paths containing spaces have to be quoted and only trusted commands should be used. On Windows, Script Merger is always run directly.

### Startup Diagnostics

When startup fails, a `TW3MM-startup-*.log` file is written to the system temporary directory, even if the GUI can't open. The path of the log is also printed to the console when there is one.

- On Windows and inside Wine, the log is in `%TEMP%` of that environment.
- On Linux and macOS, the log is in the temporary directory of the Python runtime, usually `TMPDIR` or `/tmp`.

### Game Configuration

Select `witcher3.exe` in `bin/x64` for DX11 or in `bin/x64_dx12` for DX12. The `--game` command-line option also accepts the installation directory itself.

If a game update removes the configured executable, the manager uses whichever renderer version is available in the same game directory, without changing `config.ini`. Detection always follows the current files and launcher metadata, so it keeps working after a rollback. Other installations are not searched.

Remastered ships launcher metadata identifying `remasteredEdition` and the store, which is used to detect the edition. Older installations without it are detected from the executable layout. The selected executable determines which user settings file is used. Existing menu file lists are updated, missing ones are not created.

Steam Remastered installations are launched through Steam on Windows, since starting that executable directly is reported to crash. Older Windows editions launch the selected executable directly. On Linux and macOS, detected Steam installations launch through Steam. Renderer and mod options for Steam launches are controlled by Steam and REDlauncher. Other Windows installations launch the selected executable directly; non-Steam Linux and macOS installations use `wine` unless a custom command is configured.

GOG installation records (`goggame-*.info`) take precedence over the store recorded in launcher metadata. If the launch route is still incorrect, use your store launcher directly or configure `gamelaunchcommand`. Starting through this manager is not required for installed mods to work.

For other launch environments, `gamelaunchcommand` in the `[PATHS]` section of `config.ini` replaces the automatic launch. The command is split into arguments and not run through a shell, so on Linux and macOS, paths and arguments containing spaces have to be quoted. With CrossOver, if the system `steam://` handler doesn't open Steam in the right bottle, the command has to do it instead. `--userdocuments` selects the Documents directory containing `The Witcher 3` in that environment, which is usually not the one of the host.

### Remastered Troubleshooting

- **Selecting the executable**\
  If `gameexe` isn't set, the selection dialog opens on startup. Select the existing DX12 executable.
- **Game crashes when launched from the manager**\
  Launch through Steam. `steam_api64.dll` is part of the game and shouldn't be deleted or renamed.
- **Mods are installed but don't load**\
  Check that mods are enabled in REDlauncher and that neither the Steam launch options nor a custom command contain `-disablemods`. With Proton or CrossOver, check that `--userdocuments` points to the settings directory the game actually uses. Older mods might not work with Remastered even if they install fine.
- **An installation appears to do nothing**\
  Check the output log for the destination paths, skipped files, errors, and incomplete-installation warnings. Confirm the selected executable belongs to the installation you play, especially after an update or when keeping multiple game versions. Report the manager version, game/store version, exact mod archive, selected game path, and output log if files are still missing.
- **Script compilation fails, including `CR4SecondScreenManagerScriptProxy`**\
  A successful copy does not make a mod compatible with the game version. Back up your setup, test without third-party mods or generated merges, and verify game files through your store if the clean game also fails. Install versions of the mods and Script Merger that explicitly support your game version, then rebuild merges. Do not delete or edit vanilla scripts to hide compiler errors.
- **Upgrading from Next-Gen to Remastered**\
  Retaining the existing setup means preserving manager configuration and installed-mod records, not converting old mods. Back up saves, Documents settings, mod archives, and all modded game files before changing editions. Use compatible replacements and rebuild merges; rolling back requires a matching game version and mod setup.
- **Several versions or variants of a mod are listed**\
  Follow that mod's installation instructions. Mutually exclusive variants should not all be enabled. The manager cannot infer which optional file you intended to use; uninstall obsolete versions before installing their replacements, and keep backups.
- **Merging fails**\
  Script Merger is a separate application, use [Fresh and Automated Edition](https://www.nexusmods.com/witcher3/mods/8405) or [Script Merger - Remastered](https://www.nexusmods.com/witcher3/mods/13076).
- **Script Merger recreates an old game directory**\
  Script Merger keeps its own `GameDirectory`, `ModsDirectory` and `VanillaScriptsDirectory` settings, which don't change with the game path in the manager. Change the game directory in Script Merger as well, and back up its configuration before resetting overrides or rebuilding merges. Use a Remastered-compatible Script Merger.
- **Finding or resetting manager settings**\
  Close the manager and back up its configuration directory first, usually in `User\AppData\Local\The Witcher 3 Mod Manager` on Windows or in one of the other locations described above. To reset paths, rename only `config.ini` and keep `installed.xml` to keep the list of installed mods. The load order of the game is stored separately in `The Witcher 3/mods.settings` in the Documents directory.

### Other Platforms and Managers

- **Steam Deck:** use Desktop Mode for setup. The native Python instructions below apply; pass the Steam library game directory with `--game` and the game's Proton-prefix Documents directory with `--userdocuments` if autodetection selects a different location. SD-card and non-default prefixes need their actual paths. Script Merger needs Wine or the Proton command described above.
- **Xbox app / PC Game Pass:** this distribution has not been verified. The manager requires an accessible game directory containing `content` and `bin/x64/witcher3.exe` or `bin/x64_dx12/witcher3.exe`. For a conventional layout, select that executable inside the installation, not an Xbox launcher shortcut. If the layout or access restrictions differ, provide the directory layout and exact error for investigation; do not change permissions on protected Windows application directories. Use the Xbox app to launch the game.
- **Vortex and other managers:** this manager offers direct archive installation, enable/disable controls, load-order editing, menu/input configuration, and Script Merger launching. It is not necessary to migrate a working setup. Avoid having multiple managers deploy or remove files in the same installation at the same time.

### Python (Windows, Linux, and macOS)

Dependencies are managed with [PDM](https://pdm-project.org/en/latest/). Python 3.10 to 3.12 is supported.

1. Install PDM using the [recommended installation method](https://pdm-project.org/en/latest/#recommended-installation-method)
2. Clone the repository
3. Install dependencies with `pdm install --prod`
4. Start the manager with `pdm run start`

On Linux and macOS:
- Configuration is stored in `~/.config/TheWitcher3ModManager`
- `wine` is required to run Script Merger
- Commands should be run with `pdm run` to use the project environment

### Development Checks

Development tools are installed with `pdm install`.

- `pdm run format` formats all Python files.
- `pdm run lint` checks imports and common errors without changing files.
- `pdm run ruff check --fix .` applies safe lint fixes, including import sorting.
- `pdm run check` runs the formatting and lint checks, Pyright, mypy and all tests.
- `pdm run typecheck-pyright` runs Pyright, the type checker behind Pylance, with the `standard` settings of the project.
- `pdm run typecheck` runs mypy as a second type checker.

### Build Release (Windows)

1. Install dependencies and development tools in a fresh environment with `pdm install`
2. Run the checks with `pdm run check`
3. Build the executable with `pdm run build-win`
4. The build is placed in `build/exe.[platform].[python version]`

The Python library is stored unpacked (`no_compress`) so the release ZIP contains no nested library ZIP. CI checks for nested archives and smoke-tests executable startup before packaging. Nexus can still quarantine an upload for other reasons.
