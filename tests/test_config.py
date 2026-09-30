import configparser
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.configuration.config import Configuration
from src.util.util import normalizePath, reconfigureGamePath


class ConfigurationPathTests(unittest.TestCase):
    def test_unconfigured_game_properties(self):
        config = Configuration.__new__(Configuration)
        config.config = configparser.ConfigParser()
        for value in (None, ''):
            with self.subTest(value=value):
                if value is not None:
                    config.config['PATHS'] = {'gameexe': value}
                self.assertEqual(config.game, '')
                self.assertEqual(config.graphicsapi, 'dx11')
                self.assertEqual(Configuration.getCorrectGamePath(value), '')

    def test_supported_layouts_preserve_selected_executable(self):
        for directories in (('x64',), ('x64', 'x64_dx12'), ('x64_dx12',)):
            with self.subTest(directories=directories), tempfile.TemporaryDirectory() as root:
                os.makedirs(os.path.join(root, 'content'))
                for directory in directories:
                    exe = os.path.join(root, 'bin', directory, 'witcher3.exe')
                    os.makedirs(os.path.dirname(exe))
                    with open(exe, 'w', encoding='utf-8'):
                        pass
                    self.assertEqual(Configuration.getCorrectGamePath(exe), normalizePath(exe))
                    self.assertEqual(Configuration.getGameRoot(exe), normalizePath(root))

    def test_game_version_falls_back_to_installed_renderers(self):
        for directories, expected in ((('x64',), 'og'),
                                      (('x64', 'x64_dx12'), 'ng'),
                                      (('x64_dx12',), 're')):
            with self.subTest(directories=directories), tempfile.TemporaryDirectory() as root:
                os.makedirs(os.path.join(root, 'content'))
                for directory in directories:
                    exe = os.path.join(root, 'bin', directory, 'witcher3.exe')
                    os.makedirs(os.path.dirname(exe))
                    with open(exe, 'w', encoding='utf-8'):
                        pass
                config = Configuration.__new__(Configuration)
                config.config = configparser.ConfigParser()
                config.config['PATHS'] = {
                    'gameexe': os.path.join(root, 'bin', directories[0], 'witcher3.exe')}
                self.assertEqual(config.gameversion, expected)

    def test_edition_and_store_use_launcher_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, 'content'))
            exe = os.path.join(root, 'bin', 'x64_dx12', 'witcher3.exe')
            os.makedirs(os.path.dirname(exe))
            with open(exe, 'w', encoding='utf-8'):
                pass
            config = Configuration.__new__(Configuration)
            config.config = configparser.ConfigParser()
            config.config['PATHS'] = {'gameexe': exe}
            self.assertEqual(config.gameversion, 're')
            self.assertFalse(config.steam)
            for store in ('steam', 'gog'):
                with self.subTest(store=store):
                    with open(os.path.join(root, 'launcher-configuration.json'), 'w', encoding='utf-8') as file:
                        json.dump({'gameId': 'witcher3', 'platform': store,
                                   'editions': [{'name': 'remasteredEdition'}]}, file)
                    self.assertEqual(config.gameversion, 're')
                    self.assertEqual(config.steam, store == 'steam')
                    self.assertEqual(config.usersettings, 'dx12user.settings')

    def test_graphics_api_uses_executable_directory_only(self):
        config = Configuration.__new__(Configuration)
        config.config = configparser.ConfigParser()
        for exe, expected in (
                ('/games/x64_dx12 backup/bin/x64/witcher3.exe', 'dx11'),
                ('C:\\Games\\bin\\X64_DX12\\WITCHER3.EXE', 'dx12')):
            with self.subTest(exe=exe):
                config.config['PATHS'] = {'gameexe': exe}
                self.assertEqual(config.graphicsapi, expected)

    def test_invalid_launcher_metadata_falls_back_to_installed_executables(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'content').mkdir()
            exe = root / 'bin/x64_dx12/witcher3.exe'
            exe.parent.mkdir(parents=True)
            exe.touch()
            config = Configuration.__new__(Configuration)
            config.config = configparser.ConfigParser()
            config.config['PATHS'] = {'gameexe': str(exe)}
            for text in ('{', 'null', '[]', '{"gameId":"other","platform":"steam"}',
                         '{"gameId":"witcher3","editions":null}'):
                with self.subTest(text=text):
                    (root / 'launcher-configuration.json').write_text(text, encoding='utf-8')
                    self.assertEqual(config.gameversion, 're')
                    self.assertFalse(config.steam)

    def test_legacy_steam_manifest_fallback_respects_explicit_store(self):
        with tempfile.TemporaryDirectory() as temporary:
            steamapps = Path(temporary)
            root = steamapps / 'common/The Witcher 3'
            (root / 'content').mkdir(parents=True)
            exe = root / 'bin/x64/witcher3.exe'
            exe.parent.mkdir(parents=True)
            exe.touch()
            (steamapps / 'appmanifest_292030.acf').touch()
            config = Configuration.__new__(Configuration)
            config.config = configparser.ConfigParser()
            config.config['PATHS'] = {'gameexe': str(exe)}
            self.assertTrue(config.steam)
            (root / 'launcher-configuration.json').write_text(
                '{"gameId":"witcher3","platform":"gog"}', encoding='utf-8')
            self.assertFalse(config.steam)

    def test_fresh_configuration_and_game_path_override(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(Configuration, 'write_config'):
            root = Path(temporary)
            documents = root / 'Documents'
            documents.mkdir()
            game = root / 'Game'
            (game / 'content').mkdir(parents=True)
            exe = game / 'bin/x64_dx12/witcher3.exe'
            exe.parent.mkdir(parents=True)
            exe.touch()
            config = Configuration(str(documents), configPath=str(root / 'Manager'))
            self.assertEqual(config.game, '')
            for selected in (game, exe):
                with self.subTest(selected=selected):
                    config = Configuration(str(documents), str(selected), str(root / 'Manager'))
                    self.assertEqual(config.gameexe, exe.as_posix())
                    self.assertEqual(config.game, game.as_posix())

    def test_changing_game_path_invalidates_cached_mod_and_dlc_paths(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(Configuration, 'write_config'):
            config = Configuration.__new__(Configuration)
            config.config = configparser.ConfigParser()
            for name in ('Old Game', 'New Game'):
                root = Path(temporary) / name
                (root / 'content').mkdir(parents=True)
                exe = root / 'bin/x64_dx12/witcher3.exe'
                exe.parent.mkdir(parents=True)
                exe.touch()
                config.gameexe = str(exe)
                self.assertEqual(config.mods, str(root / 'Mods'))
                self.assertEqual(config.dlc, str(root / 'DLC'))
            exe.unlink()
            self.assertEqual(config.game, '')
            self.assertEqual(Configuration.getCorrectGamePath(config.gameexe), '')

    def test_fresh_game_dialog_can_be_canceled_or_select_dx12(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(Configuration, 'write_config'):
            root = Path(temporary)
            (root / 'content').mkdir()
            exe = root / 'bin/x64_dx12/witcher3.exe'
            exe.parent.mkdir(parents=True)
            exe.touch()
            config = Configuration.__new__(Configuration)
            config.config = configparser.ConfigParser()
            with patch('src.globals.data.config', config), \
                    patch('src.gui.alerts.MessageNotConfigured'), \
                    patch('src.util.util.QFileDialog') as dialog:
                dialog.return_value.exec.return_value = False
                self.assertFalse(reconfigureGamePath())
                self.assertIsNone(config.gameexe)
                dialog.return_value.exec.return_value = True
                dialog.return_value.selectedFiles.return_value = [str(exe)]
                self.assertTrue(reconfigureGamePath())
                self.assertEqual(config.gameexe, exe.as_posix())

    def test_rejects_unrelated_paths_inside_installation(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, 'content'))
            exe = os.path.join(root, 'bin', 'x64_dx12', 'witcher3.exe')
            os.makedirs(os.path.dirname(exe))
            with open(exe, 'w', encoding='utf-8'):
                pass
            unrelated = os.path.join(root, 'Mods', 'witcher3.exe')
            os.makedirs(os.path.dirname(unrelated))
            with open(unrelated, 'w', encoding='utf-8'):
                pass
            for selected in (os.path.join(root, 'missing'), unrelated):
                with self.subTest(selected=selected):
                    self.assertEqual(Configuration.getCorrectGamePath(selected), '')

    def test_get_correct_game_path_accepts_remastered_dx12_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "The Witcher 3")
            exe = os.path.join(root, "bin", "x64_dx12", "witcher3.exe")
            os.makedirs(os.path.join(root, "content"), exist_ok=True)
            os.makedirs(os.path.dirname(exe), exist_ok=True)
            with open(exe, "w", encoding="utf-8") as handle:
                handle.write("x")

            self.assertEqual(Configuration.getCorrectGamePath(exe), normalizePath(exe))
            self.assertEqual(Configuration.getGameRoot(exe), normalizePath(root))

    def test_get_correct_game_path_accepts_game_directory_for_remastered_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "The Witcher 3")
            exe = os.path.join(root, "bin", "x64_dx12", "witcher3.exe")
            os.makedirs(os.path.join(root, "content"), exist_ok=True)
            os.makedirs(os.path.dirname(exe), exist_ok=True)
            with open(exe, "w", encoding="utf-8") as handle:
                handle.write("x")

            self.assertEqual(Configuration.getCorrectGamePath(root), normalizePath(exe))


class ConfigurationUpgradeTests(unittest.TestCase):
    def assert_remastered_upgrade(self, edition, renderer):
        with tempfile.TemporaryDirectory() as temporary, patch.object(Configuration, 'write_config') as write_config:
            root = Path(temporary)
            game = root / 'The Witcher 3'
            documents = root / 'Documents'
            manager = root / 'Manager'
            documents.mkdir()
            manager.mkdir()
            (game / 'content').mkdir(parents=True)
            dx11 = game / 'bin/x64/witcher3.exe'
            dx12 = game / 'bin/x64_dx12/witcher3.exe'
            dx11.parent.mkdir(parents=True)
            dx11.touch()
            if edition == 'ng':
                dx12.parent.mkdir()
                dx12.touch()
                (game / 'launcher-configuration.json').write_text(json.dumps({
                    'gameId': 'witcher3', 'platform': 'steam', 'editions': []
                }), encoding='utf-8')

            selected = dx11 if renderer == 'dx11' else dx12
            saved = configparser.ConfigParser()
            saved['PATHS'] = {'gameexe': selected.as_posix(), 'documents': str(documents),
                              'scriptmerger': ''}
            saved['SETTINGS'] = {'AllowPopups': '1', 'language': 'English.qm'}
            saved['TOOLBAR'] = {}
            config_file = manager / 'config.ini'
            with config_file.open('w', encoding='utf-8') as file:
                saved.write(file)
            original_bytes = config_file.read_bytes()
            config = Configuration(configPath=str(manager))
            self.assertEqual(config.gameversion, edition)
            self.assertEqual(config.graphicsapi, renderer)
            self.assertEqual(config.gameexe, selected.as_posix())
            self.assertEqual(config.usersettings,
                             'user.settings' if renderer == 'dx11' else 'dx12user.settings')
            self.assertEqual(config.mods, str(game / 'Mods'))
            self.assertEqual(config.dlc, str(game / 'DLC'))

            dx11.unlink()
            dx11.parent.rmdir()
            dx12.parent.mkdir(exist_ok=True)
            dx12.touch()
            (game / 'launcher-configuration.json').write_text(json.dumps({
                'gameId': 'witcher3', 'platform': 'steam',
                'editions': [{'name': 'remasteredEdition'}],
                'executables': [{'description': 'DirectX 12', 'executable': {
                    'directoryPath': 'bin\\x64_dx12', 'fileName': 'witcher3.exe'}}]
            }), encoding='utf-8')

            for state, current in (('running', config),
                                   ('restarted', Configuration(configPath=str(manager)))):
                with self.subTest(state=state):
                    self.assertEqual(current.gameversion, 're')
                    self.assertEqual(current.gameexe, dx12.as_posix())
                    self.assertEqual(current.game, game.as_posix())
                    self.assertEqual(current.graphicsapi, 'dx12')
                    self.assertEqual(current.usersettings, 'dx12user.settings')
                    self.assertTrue(current.steam)
                    self.assertEqual(current.mods, str(game / 'Mods'))
                    self.assertEqual(current.dlc, str(game / 'DLC'))
                    self.assertEqual(Configuration.getCorrectGamePath(current.gameexe), dx12.as_posix())
                    self.assertEqual(current.config, saved)

            dx11.parent.mkdir()
            dx11.touch()
            if edition == 'og':
                dx12.unlink()
                dx12.parent.rmdir()
                (game / 'launcher-configuration.json').unlink()
            else:
                (game / 'launcher-configuration.json').write_text(json.dumps({
                    'gameId': 'witcher3', 'platform': 'steam', 'editions': []
                }), encoding='utf-8')
            for state, current in (('running', config),
                                   ('restarted', Configuration(configPath=str(manager)))):
                with self.subTest(state=state, phase='rollback'):
                    self.assertEqual(current.gameversion, edition)
                    self.assertEqual(current.gameexe, selected.as_posix())
                    self.assertEqual(current.graphicsapi, renderer)
                    self.assertEqual(current.usersettings,
                                     'user.settings' if renderer == 'dx11' else 'dx12user.settings')
                    self.assertEqual(current.steam, edition == 'ng')
                    self.assertEqual(current.config, saved)
            self.assertEqual(config_file.read_bytes(), original_bytes)
            write_config.assert_not_called()

    def test_original_upgrades_to_remastered_without_config_changes(self):
        self.assert_remastered_upgrade('og', 'dx11')

    def test_next_gen_dx11_upgrades_to_remastered_without_config_changes(self):
        self.assert_remastered_upgrade('ng', 'dx11')

    def test_next_gen_dx12_upgrades_to_remastered_without_config_changes(self):
        self.assert_remastered_upgrade('ng', 'dx12')

    def test_missing_renderer_does_not_switch_to_another_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_game = root / 'Old Game'
            (old_game / 'content').mkdir(parents=True)
            selected = old_game / 'bin/x64/witcher3.exe'
            selected.parent.mkdir(parents=True)
            selected.touch()
            replacement = root / 'Other Game/bin/x64_dx12/witcher3.exe'
            replacement.parent.mkdir(parents=True)
            replacement.touch()
            (root / 'Other Game/content').mkdir()
            config = Configuration.__new__(Configuration)
            config.config = configparser.ConfigParser()
            config.config['PATHS'] = {'gameexe': selected.as_posix()}
            self.assertEqual(config.game, old_game.as_posix())
            selected.unlink()
            self.assertEqual(config.gameexe, selected.as_posix())
            self.assertEqual(config.game, '')
            self.assertEqual(Configuration.getCorrectGamePath(config.gameexe), '')


if __name__ == "__main__":
    unittest.main()
