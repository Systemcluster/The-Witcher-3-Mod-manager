import configparser
import os
import tempfile
import unittest
import xml.etree.ElementTree as XML
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QMessageBox

from src.core.installer import Installer
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

    def test_restore_uses_stored_metadata_without_replacing_mod_assets(self):
        self.config.mods = str(self.root / "Mods")
        self.config.dlc = str(self.root / "DLC")
        disabled = Path(self.config.mods) / "~modExample"
        disabled.mkdir(parents=True)
        (disabled / "custom.txt").write_text("customized asset")
        for filename in ("user.settings", "dx12user.settings"):
            (self.root / filename).write_text("[Example]\nEnabled=false\nUnrelated=keep\n")
        mod = Mod(
            _name="Example",
            enabled=False,
            files=["modExample"],
            usersettings=[Usersetting("Example", "Enabled=true")],
            inputsettings=[Key("[Input]", "IK_A=(Action=Jump)")],
        )
        tree = Model.writeModToXml(mod, XML.ElementTree(XML.Element("installed")))
        restored = Model.populateModFromXml(Mod(), tree.findall("mod")[0])
        with patch("src.core.installer.fetchMod") as fetch, patch("src.core.installer.copyFolder") as copy:
            installer = Installer(Mock())
            self.assertEqual(installer.reinstallMod(restored), (True, False))
            self.assertEqual(installer.reinstallMod(restored), (True, False))
            fetch.assert_not_called()
            copy.assert_not_called()
        self.assertTrue(restored.enabled)
        self.assertEqual((Path(self.config.mods) / "modExample" / "custom.txt").read_text(), "customized asset")
        self.assertEqual((self.root / "input.settings").read_text().count("IK_A=(Action=Jump)"), 1)
        for filename in ("user.settings", "dx12user.settings"):
            self.assertIn("Enabled=true", (self.root / filename).read_text())
            self.assertIn("Unrelated=keep", (self.root / filename).read_text())

    def test_restoring_key_bindings_can_preserve_custom_binding(self):
        (self.root / "input.settings").write_text("[Input]\nIK_B=(Action=Jump)\n")
        mod = Mod(inputsettings=[Key("[Input]", "IK_A=(Action=Jump)")])
        with patch("src.domain.mod.MessageRebindKeys", return_value=QMessageBox.StandardButton.No) as confirm:
            self.assertEqual(mod.installInputKeys(), (0, 1))
            confirm.assert_called_once()
        text = (self.root / "input.settings").read_text()
        self.assertIn("IK_B=(Action=Jump)", text)
        self.assertNotIn("IK_A=", text)

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


class InventoryPersistenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        config_patch = patch("src.core.model.data.config", SimpleNamespace(configuration=str(self.root)))
        config_patch.start()
        self.addCleanup(config_patch.stop)
        for name in ("MessageAlertReadingConfigurationFailed", "MessageAlertWritingFailed"):
            alert_patch = patch("src.core.model." + name)
            alert_patch.start()
            self.addCleanup(alert_patch.stop)

    def write_inventory(self, filename, name):
        tree = Model.writeModToXml(Mod(_name=name), XML.ElementTree(XML.Element("installed")))
        tree.write(self.root / filename, encoding="utf-8", xml_declaration=True)

    def test_live_inventory_survives_interruption_before_replacement(self):
        self.write_inventory("installed.xml", "Original")
        model = Model(ignorelock=True)
        model.modList["Added"] = Mod(_name="Added")
        real_replace = os.replace

        def interrupt_promotion(source, destination):
            if source == str(self.root / "installed.xml.new"):
                self.assertTrue((self.root / "installed.xml").is_file())
                raise SystemExit("simulated process interruption")
            return real_replace(source, destination)

        with patch("src.core.model.os.replace", side_effect=interrupt_promotion):
            with self.assertRaises(SystemExit):
                model.write()
        self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])

    def test_recovery_prefers_committed_backup_then_pending_inventory(self):
        for primary in (None, "<broken", "<unrelated />"):
            for backup in (True, False):
                with self.subTest(primary=primary, backup=backup):
                    for file in self.root.iterdir():
                        file.unlink()
                    if primary is not None:
                        (self.root / "installed.xml").write_text(primary)
                    if backup:
                        self.write_inventory("installed.xml.old", "Committed")
                    else:
                        (self.root / "installed.xml.old").write_text("<broken")
                    self.write_inventory("installed.xml.new", "Pending")
                    model = Model(ignorelock=True)
                    expected = "Committed" if backup else "Pending"
                    self.assertEqual(list(model.list()), [expected])
                    model.write()
                    self.assertEqual(list(Model(ignorelock=True).list()), [expected])
                    self.assertEqual(XML.parse(self.root / "installed.xml.old").findall("mod")[0].get("name"), expected)

    def test_invalid_inventory_blocks_reload_and_subsequent_writes(self):
        self.write_inventory("installed.xml", "Original")
        model = Model(ignorelock=True)
        for invalid in ("<broken", "<unrelated />", "<installed><mod /></installed>"):
            with self.subTest(invalid=invalid):
                (self.root / "installed.xml").write_text(invalid)
                with self.assertRaises(XML.ParseError):
                    model.reload()
                model.write()
                self.assertEqual((self.root / "installed.xml").read_text(), invalid)
                self.assertFalse((self.root / "installed.xml.new").exists())

    def test_unreadable_inventory_is_not_treated_as_empty(self):
        self.write_inventory("installed.xml", "Original")
        with patch("builtins.open", side_effect=PermissionError("access denied")):
            with self.assertRaises(XML.ParseError):
                Model(ignorelock=True)

    def test_failed_promotion_preserves_live_inventory_and_backup(self):
        self.write_inventory("installed.xml", "Original")
        model = Model(ignorelock=True)
        model.modList["Added"] = Mod(_name="Added")
        real_replace = os.replace

        def fail_promotion(source, destination):
            if source == str(self.root / "installed.xml.new"):
                raise PermissionError("replacement denied")
            return real_replace(source, destination)

        with patch("src.core.model.os.replace", side_effect=fail_promotion):
            model.write()
        self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])
        self.assertEqual(XML.parse(self.root / "installed.xml.old").findall("mod")[0].get("name"), "Original")

    def test_readme_control_characters_round_trip(self):
        model = Model(ignorelock=True)
        model.add("Example", Mod(_name="Example", readmes=["text\x00\x01\x1f"]))
        self.assertEqual(Model(ignorelock=True).get("Example").readmes, ["text\x00\x01\x1f"])

    def test_failed_flush_preserves_live_inventory_and_previous_backup(self):
        self.write_inventory("installed.xml", "Original")
        self.write_inventory("installed.xml.old", "Previous")
        model = Model(ignorelock=True)
        model.modList["Added"] = Mod(_name="Added")
        for failures in ([OSError("backup flush failed")], [None, OSError("inventory flush failed")]):
            with self.subTest(failures=failures):
                original = (self.root / "installed.xml").read_bytes()
                with patch("src.core.model.os.fsync", side_effect=failures):
                    model.write()
                self.assertEqual((self.root / "installed.xml").read_bytes(), original)
                self.assertTrue(XML.parse(self.root / "installed.xml.old").findall("mod"))
                self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])

    def test_invalid_serialized_inventory_never_replaces_live_file(self):
        self.write_inventory("installed.xml", "Original")
        model = Model(ignorelock=True)
        original = (self.root / "installed.xml").read_bytes()
        model.modList["Invalid"] = Mod(_name="Invalid\x00")
        model.write()
        self.assertEqual((self.root / "installed.xml").read_bytes(), original)
        self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])

    def test_legacy_encoding_declaration_remains_readable(self):
        self.write_inventory("installed.xml", "Original")
        filename = self.root / "installed.xml"
        filename.write_bytes(filename.read_bytes().replace(b"utf-8", b"utf_8"))
        self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])


if __name__ == "__main__":
    unittest.main()
