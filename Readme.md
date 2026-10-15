# The Witcher 3 Mod Manager

**Mod Manager for The Witcher 3.**

Supports the Steam and GOG releases on Windows, Steam Proton installations on Linux and CrossOver installations on macOS.

Works with Original, Next-Gen, and Remastered installations.

## Description

The Witcher 3 Mod Manager is an application that simplifies installing and managing The Witcher 3 mods, originally developed by [stefan3372](https://github.com/stefan3372) and now being continued here.

See the [Nexus Mods page](https://www.nexusmods.com/witcher3/mods/2678) for releases, screenshots and more information.

## Usage

### Release Versions (Windows)

Download the latest release from Nexus Mods or from the [GitHub releases](https://github.com/Systemcluster/The-Witcher-3-Mod-manager/releases) and extract the entire archive.

Existing configuration is picked up automatically when updating. Portable installations keep `config.ini` next to the executable; to update one, close the manager and copy `config.ini` and `installed.xml` into the new release directory. Updates are manual and don't require reinstalling your mods.

New configuration is created in `AppData\Local\The Witcher 3 Mod Manager`. The executable directory and `Documents\The Witcher 3 Mod Manager` are checked first for existing configuration.

### Game Configuration

Select `witcher3.exe` in `bin/x64` for DX11 or `bin/x64_dx12` for DX12. The `--game` command-line option also accepts the installation directory.

Steam Remastered installations launch through Steam on Windows. Other Windows installations launch the selected executable directly. On Linux and macOS, Steam installations launch through Steam and other installations use `wine`.

To use a different launcher, set `gamelaunchcommand` in the `[PATHS]` section of `config.ini` while the manager is closed. The command isn't run through a shell; quote paths and arguments containing spaces on Linux and macOS.

With Proton or CrossOver, use `--userdocuments` to select the Documents directory containing the game's `The Witcher 3` settings folder. For CrossOver, a custom launch command may also be needed to select the right bottle. On Steam Deck, use Desktop Mode for setup.

Starting the game through the manager isn't required for installed mods to work.

### Managing Mods

Use the checkbox to enable or disable a mod. Disabled mod folders get a `~` prefix, DLC files and custom menus get a `.disabled` suffix, and extracted XML additions are removed until the mod is enabled again. Load-order priorities are kept.

Shared game menus and base INI files stay installed when a mod is disabled or uninstalled. Their previous contents aren't backed up or restored, so back up affected files before installing replacements. User settings and input bindings stay in place during toggles; uninstall removes recorded user-setting options but leaves input bindings.

Enabling an older disabled mod restores shared menus left with a `.disabled` suffix, including their file-list entries. If an active copy also exists, the manager reports a conflict rather than overwriting it.

Official expansion folders (`bob`, `ep1`, and `dlc1` through `dlc16`) are not managed as custom DLC. Declining a directory overwrite does not give a new package ownership of that directory. Failed installations remove newly created asset paths; replacements of pre-existing files are not rolled back, and cleanup failures are reported with their paths.

Updating a package with the same manager name keeps its disabled status. **Restore default settings** enables the mod and reapplies its stored settings; it doesn't reinstall missing files.

Follow each mod's installation instructions, especially for optional or mutually exclusive variants. Avoid using multiple managers to change the same installation at the same time.

### Script Merger on Linux and macOS

Script Merger runs with `wine` using the executable selected in the manager. To use a specific Wine prefix, set `mergerlaunchcommand` in the `[PATHS]` section of `config.ini` while the manager is closed:

```ini
[PATHS]
scriptmerger=/home/user/Tools/Script Merger/WitcherScriptMerger.exe
mergerlaunchcommand=WINEPREFIX="/home/user/Games/Witcher 3/prefix" wine "/home/user/Tools/Script Merger/WitcherScriptMerger.exe"
```

With Steam and `protontricks-launch`, the game's Proton prefix can be used instead:

```ini
mergerlaunchcommand=protontricks-launch --appid 292030 "/home/user/Tools/Script Merger/WitcherScriptMerger.exe"
```

Replace the paths with your own, and the app ID if the game was added as a non-Steam shortcut. For CrossOver, the command needs to target the game's bottle.

The Script Merger executable still needs to be selected in the manager. Unlike `gamelaunchcommand`, this command runs through a shell, so quote paths containing spaces and only use trusted commands. On Windows, Script Merger always runs directly.

### Troubleshooting

- **Mods don't load:** check that mods are enabled in REDlauncher and `mods.settings`, and remove any `-disablemods` launch argument. With Proton or CrossOver, check the Documents path. Mods need to support your game version.
- **Files seem to be missing:** check the output log for destination paths, skipped files and errors. Make sure the selected executable belongs to the installation you play.
- **Remastered crashes on launch:** try launching through Steam. Don't delete or rename `steam_api64.dll`.
- **Script compilation or merging fails:** use compatible mod versions and rebuild merges with [Script Merger - Fresh and Automated Edition](https://www.nexusmods.com/witcher3/mods/8405) or [Script Merger - Remastered](https://www.nexusmods.com/witcher3/mods/13076). Script Merger keeps its own game path, so update that as well if the game has moved.
- **Switching game editions:** back up saves, settings and modded files first. Keeping the manager's configuration doesn't make older mods compatible.
- **Resetting manager paths:** close the manager, back up its configuration directory and rename `config.ini`. Keep `installed.xml` to preserve the installed-mod list.
- **The manager won't start:** look for a `TW3MM-startup-*.log` file in the system temporary directory (`%TEMP%` on Windows or inside Wine, usually `TMPDIR` or `/tmp` on Linux and macOS).

When reporting a problem, include the manager version, game version and store, affected mod, selected game path and output log.

### Python (Windows, Linux, and macOS)

Dependencies are managed with [PDM](https://pdm-project.org/en/latest/). Python 3.10 to 3.12 is supported.

1. Install PDM using the [recommended installation method](https://pdm-project.org/en/latest/#installation)
2. Clone the repository
3. Install dependencies with `pdm install --prod`
4. Start the manager with `pdm run start`

On Linux and macOS, an existing `~/.config/TheWitcher3ModManager` directory is reused. Otherwise configuration is stored in `~/.config/TheWitcher3ModManager` on Linux or `~/Library/Preferences/TheWitcher3ModManager` on macOS. A local `config.ini` or `--config` overrides this.

Use `pdm run` for commands in the project environment. Running Script Merger also requires `wine`.

## Development

Install development tools with `pdm install`. Use `pdm run format` to format the code and `pdm run check` to run formatting, lint, type checks and tests.

### Build Release (Windows)

1. Install dependencies and development tools with `pdm install`
2. Run `pdm run check`
3. Build the executable with `pdm run build-win`

The build is placed in `build/exe.[platform].[python version]`.
