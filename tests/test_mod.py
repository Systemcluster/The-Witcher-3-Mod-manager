import configparser
import tempfile
import unittest
import xml.etree.ElementTree as XML
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.core.model import Model
from src.domain.key import Key
from src.domain.mod import Mod
from src.domain.usersetting import Usersetting


class ModConfigurationTests(unittest.TestCase):
    def test_input_keys_round_trip_with_version_metadata(self):
        mod = Mod(inputsettings=[Key("[Input]", "Version=1"), Key("[Input]", "IK_A=(Action=Jump)")])
        self.assertEqual(mod.installInputKeys(), (2, 0))
        self.assertEqual(mod.installInputKeys(), (0, 0))
        self.assertIn("Version=1", (self.root / "input.settings").read_text())

    def test_mod_xml_round_trip_preserves_domain_objects(self):
        mod = Mod(inputsettings=[Key("Input", "IK_A=(Action=Jump)")], usersettings=[Usersetting("Mod", "Enabled=true")])
        root = Model.writeModToXml(mod, XML.ElementTree(XML.Element("installed")))
        element = root.find("mod")
        assert element is not None
        restored = Model.populateModFromXml(Mod(), element)
        self.assertEqual(restored.inputsettings, mod.inputsettings)
        self.assertIsInstance(restored.usersettings[0], Usersetting)

    def test_mod_xml_rejects_missing_key_context(self):
        with self.assertRaises(XML.ParseError):
            Model.populateModFromXml(Mod(), XML.fromstring("<mod><key>IK_A=(Action=Jump)</key></mod>"))

    def test_mod_xml_rejects_missing_root(self):
        with self.assertRaises(ValueError):
            Model.writeModToXml(Mod(), XML.ElementTree())

    def test_mod_paths_are_required_before_filesystem_operations(self):
        self.config.mods = None
        self.config.dlc = None
        for enabled in (True, False):
            for mod in (Mod(enabled=enabled, files=["modExample"]), Mod(enabled=enabled, dlcs=["dlcExample"])):
                with self.subTest(enabled=enabled, files=mod.files, dlcs=mod.dlcs):
                    with self.assertRaisesRegex(ValueError, "No game directory"):
                        mod.disable() if enabled else mod.enable()
                    self.assertEqual(mod.enabled, enabled)

    def test_version_only_keys_can_be_compared(self):
        first = Key("Input", "Version=1")
        second = Key("Input", "Version=1")
        self.assertEqual(first, second)
        self.assertFalse(first < second)
        self.assertFalse(first > second)
        self.assertTrue(first <= second)
        self.assertTrue(first >= second)
        self.assertEqual(sorted([second, first]), [first, second])

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
            self.assertEqual(
                (self.root / filename).read_text(encoding="utf-16").splitlines(), ["prefix_test.xml;", "test.xml;"]
            )
        mod.uninstallMenus()
        mod.uninstallMenus()
        for filename in ('dx11filelist.txt', 'dx12filelist.txt'):
            self.assertEqual((self.root / filename).read_text(encoding="utf-16").splitlines(), ["prefix_test.xml;"])

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
                    self.assertIn("Enabled=true", (directory / filename).read_text())
                mod.uninstallUserSettings()
                for filename in files:
                    settings = configparser.ConfigParser()
                    settings.read(directory / filename)
                    self.assertFalse(settings.has_option('ModSettings', 'Enabled'))


if __name__ == '__main__':
    unittest.main()
