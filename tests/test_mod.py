import configparser
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.domain.mod import Mod
from src.domain.usersetting import Usersetting


class ModConfigurationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = SimpleNamespace(menu=str(self.root), settings=str(self.root), gameversion='re')
        config_patch = patch('src.domain.mod.data.config', self.config)
        config_patch.start()
        self.addCleanup(config_patch.stop)

    def test_missing_menu_lists_are_not_created(self):
        mod = Mod(menus=['test.xml'])
        mod.installMenus()
        mod.uninstallMenus()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_menu_registration_is_exact_and_idempotent(self):
        for filename in ('dx11filelist.txt', 'dx12filelist.txt'):
            (self.root / filename).write_text('prefix_test.xml;\n', encoding='utf-16')
        mod = Mod(menus=['test.xml'])
        mod.installMenus()
        mod.installMenus()
        for filename in ('dx11filelist.txt', 'dx12filelist.txt'):
            self.assertEqual((self.root / filename).read_text(encoding='utf-16').splitlines(),
                             ['prefix_test.xml;', 'test.xml;'])
        mod.uninstallMenus()
        mod.uninstallMenus()
        for filename in ('dx11filelist.txt', 'dx12filelist.txt'):
            self.assertEqual((self.root / filename).read_text(encoding='utf-16').splitlines(),
                             ['prefix_test.xml;'])

    def test_uninstall_removes_first_line_without_touching_other_menus(self):
        filelist = self.root / 'dx12filelist.txt'
        filelist.write_text('TEST.xml;\nother.xml;\n', encoding='utf-16')
        Mod(menus=['test.xml']).uninstallMenus()
        self.assertEqual(filelist.read_text(encoding='utf-16'), 'other.xml;\n')
        self.assertFalse((self.root / 'dx11filelist.txt').exists())

    def test_user_settings_install_and_uninstall_across_editions(self):
        mod = Mod(usersettings=[Usersetting('ModSettings', 'Enabled=true')])
        for edition in ('og', 'ng', 're'):
            with self.subTest(edition=edition):
                directory = self.root / edition
                directory.mkdir()
                self.config.settings = str(directory)
                self.config.gameversion = edition
                self.assertEqual(mod.installUserSettings(), 1)
                files = ['user.settings']
                if edition != 'og':
                    files.append('dx12user.settings')
                self.assertEqual(sorted(file.name for file in directory.iterdir()), sorted(files))
                for filename in files:
                    settings = configparser.ConfigParser()
                    settings.read(directory / filename)
                    self.assertEqual(settings['ModSettings']['Enabled'], 'true')
                mod.uninstallUserSettings()
                for filename in files:
                    settings = configparser.ConfigParser()
                    settings.read(directory / filename)
                    self.assertFalse(settings.has_option('ModSettings', 'Enabled'))


if __name__ == '__main__':
    unittest.main()