import configparser
import os
import stat
import tempfile
import unittest
import xml.etree.ElementTree as XML
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch

from PySide6.QtWidgets import QMessageBox

from src.core.installer import Installer
from src.core.model import Model
from src.domain.key import Key
from src.domain.mod import Mod
from src.domain.usersetting import Usersetting
from src.util.util import copyFolder, removeDirectory, removeInstalledFile


class InstalledFileSafetyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.game = self.root / "The Witcher 3"
        self.outside = self.root / "Documents"
        for directory in ("content", "Mods", "DLC", "bin"):
            (self.game / directory).mkdir(parents=True)
        self.outside.mkdir()
        self.config = SimpleNamespace(
            game=str(self.game),
            mods=str(self.game / "Mods"),
            dlc=str(self.game / "DLC"),
            menu=str(self.game / "bin"),
            settings=str(self.root),
        )
        config_patch = patch("src.globals.data.config", self.config)
        config_patch.start()
        self.addCleanup(config_patch.stop)

    def populated(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "asset").write_text("keep")
        return directory

    def link(self, link: Path, target: Path) -> None:
        try:
            link.symlink_to(target, target_is_directory=target.is_dir())
        except OSError as error:
            self.skipTest(f"Symbolic links unavailable: {error}")

    def test_removes_targets_inside_game_boundaries(self):
        for directory in (self.game / "Mods" / "modExample", self.game / "DLC" / "dlcExample"):
            removeDirectory(str(self.populated(directory)))
            self.assertFalse(directory.exists())
        menu = self.game / "bin" / "example.xml"
        menu.write_text("data")
        removeInstalledFile(str(menu))
        self.assertFalse(menu.exists())
        self.assertEqual(sorted(entry.name for entry in self.game.iterdir()), ["DLC", "Mods", "bin", "content"])

    def test_refuses_directories_outside_mods_and_dlc(self):
        for directory in (
            self.game,
            self.game / "Mods",
            self.game / "DLC",
            self.game / "content",
            self.game / "Mods-old" / "modExample",
            self.root / "The Witcher 3 Backup" / "Mods" / "modExample",
            self.outside,
        ):
            self.populated(directory)
            with self.subTest(directory=directory), self.assertRaises(ValueError):
                removeDirectory(str(directory))
            self.assertEqual((directory / "asset").read_text(), "keep")
        for directory in ("Mods/modExample", str(self.game / "Mods" / ".." / "content")):
            with self.subTest(directory=directory), self.assertRaises(ValueError):
                removeDirectory(directory)
        self.assertEqual((self.game / "content" / "asset").read_text(), "keep")

    def test_refuses_files_outside_game(self):
        for filename in (self.outside / "user.settings", self.root / "The Witcher 3 Backup" / "example.xml"):
            filename.parent.mkdir(exist_ok=True)
            filename.write_text("keep")
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                removeInstalledFile(str(filename))
            self.assertEqual(filename.read_text(), "keep")

    def test_refuses_without_configured_game(self):
        directory = self.populated(self.game / "Mods" / "modExample")
        self.config.game = ""
        with self.assertRaises(ValueError):
            removeDirectory(str(directory))
        self.assertEqual((directory / "asset").read_text(), "keep")

    def test_never_deletes_through_links(self):
        external = self.populated(self.outside / "modExample")
        (self.outside / "example.xml").write_text("keep")
        self.link(self.game / "Mods" / "modLinked", external)
        self.link(self.game / "DLC" / "linked", self.outside)
        (self.game / "bin").rmdir()
        self.link(self.game / "bin", self.outside)
        for remove, target in (
            (removeDirectory, self.game / "Mods" / "modLinked"),
            (removeDirectory, self.game / "DLC" / "linked" / "modExample"),
            (removeInstalledFile, self.game / "bin" / "example.xml"),
        ):
            with self.subTest(target=target), self.assertRaises(ValueError):
                remove(str(target))
        linked_game = self.root / "Linked Game"
        self.link(linked_game, self.game)
        self.config.game = str(linked_game)
        real = self.populated(self.game / "Mods" / "modReal")
        with self.assertRaises(ValueError):
            removeDirectory(str(linked_game / "Mods" / real.name))
        self.assertEqual((real / "asset").read_text(), "keep")
        self.assertEqual((external / "asset").read_text(), "keep")
        self.assertEqual((self.outside / "example.xml").read_text(), "keep")

    def test_refuses_windows_junctions(self):
        directory = self.populated(self.game / "Mods" / "modExample")
        lstat = os.lstat

        def junction(path, *args, **kwargs):
            metadata = lstat(path, *args, **kwargs)
            if os.fspath(path) == str(directory):
                return SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return metadata

        with patch("src.util.util.os.lstat", side_effect=junction), self.assertRaises(ValueError):
            removeDirectory(str(directory))
        self.assertEqual((directory / "asset").read_text(), "keep")

    def test_nested_links_are_removed_without_following(self):
        directory = self.populated(self.game / "Mods" / "modExample")
        (self.outside / "save").write_text("keep")
        self.link(directory / "linked", self.outside)
        removeDirectory(str(directory))
        self.assertFalse(directory.exists())
        self.assertEqual((self.outside / "save").read_text(), "keep")

    def test_hardlinked_mod_files_are_only_unlinked(self):
        source = self.outside / "asset.bundle"
        source.write_text("keep")
        directory = self.game / "Mods" / "modExample"
        directory.mkdir()
        try:
            os.link(source, directory / "asset.bundle")
        except OSError as error:
            self.skipTest(f"Hard links unavailable: {error}")
        removeDirectory(str(directory))
        self.assertFalse(directory.exists())
        self.assertEqual(source.read_text(), "keep")

    def test_replacement_keeps_original_until_copy_is_in_place(self):
        source = self.root / "source"
        source.mkdir()
        (source / "asset").write_text("new")
        target = self.populated(self.game / "Mods" / "modExample")
        replace = os.replace

        def failPromotion(origin, destination):
            if Path(origin).name == "new":
                raise PermissionError("denied")
            return replace(origin, destination)

        for failure in (
            patch("src.util.util.copytree", side_effect=OSError("disk full")),
            patch("src.util.util.os.replace", side_effect=failPromotion),
        ):
            with self.subTest(failure=failure), failure, self.assertRaises(OSError):
                copyFolder(str(source), str(target))
            self.assertEqual((target / "asset").read_text(), "keep")
            self.assertEqual([entry.name for entry in target.parent.iterdir()], ["modExample"])
        copyFolder(str(source), str(target))
        self.assertEqual((target / "asset").read_text(), "new")
        self.assertEqual([entry.name for entry in target.parent.iterdir()], ["modExample"])
        with self.assertRaises(ValueError):
            copyFolder(str(source), str(self.game / "content"))

    def test_failed_restore_keeps_original_files(self):
        source = self.root / "source"
        source.mkdir()
        target = self.populated(self.game / "Mods" / "modExample")
        replace = os.replace

        def failAfterBackup(origin, destination):
            if Path(origin).name in ("new", "old"):
                raise PermissionError("denied")
            return replace(origin, destination)

        with (
            patch("src.util.util.os.replace", side_effect=failAfterBackup),
            self.assertRaisesRegex(RuntimeError, "original files are kept"),
        ):
            copyFolder(str(source), str(target))
        self.assertEqual([backup.read_text() for backup in target.parent.glob(".tw3mm-*/old/asset")], ["keep"])

    def test_uninstall_refuses_entries_outside_game_boundaries(self):
        save = self.outside / "user.settings"
        save.write_text("keep")
        for mod in (
            Mod(_name="Parent", files=[".."]),
            Mod(_name="Absolute", dlcs=[str(self.outside)]),
            Mod(_name="Menu", menus=[str(save)]),
        ):
            model = Mock()
            with self.subTest(mod=mod.name):
                self.assertFalse(Installer(model).uninstallMod(mod))
                model.remove.assert_not_called()
        self.assertEqual(save.read_text(), "keep")
        self.assertEqual(sorted(entry.name for entry in self.game.iterdir()), ["DLC", "Mods", "bin", "content"])

    def test_failed_install_keeps_existing_mod_files(self):
        existing = self.populated(self.game / "Mods" / "modExample")
        mod = Mod(_name="Example", files=["modExample"])
        with (
            patch("src.core.installer.fetchMod", return_value=(mod, [], [])),
            patch.object(mod, "checkPriority", side_effect=OSError("failed")),
        ):
            self.assertEqual(Installer(Mock()).installMod(str(self.root / "source")), (False, 0, 0))
        self.assertEqual((existing / "asset").read_text(), "keep")

    def test_install_source_containment_is_component_and_case_aware(self):
        inside = str(self.game / "Mods" / "modExample").upper()
        sibling = str(self.root / "The Witcher 3 Backup" / "modExample")
        with (
            patch("src.core.installer.path.normcase", side_effect=str.lower),
            patch("src.core.installer.MessageAlertModFromGamePath") as alert,
            patch("src.core.installer.fetchMod", side_effect=OSError("stop")) as fetch,
        ):
            self.assertEqual(Installer(Mock()).installMod(inside), (False, 0, 0))
            alert.assert_called_once()
            fetch.assert_not_called()

            alert.reset_mock()
            self.assertEqual(Installer(Mock()).installMod(sibling), (False, 0, 0))
            alert.assert_not_called()
            fetch.assert_called_once_with(sibling, ANY)

            fetch.reset_mock()
            self.config.game = ""
            source = str(Path.cwd() / "modExample")
            self.assertEqual(Installer(Mock()).installMod(source), (False, 0, 0))
            alert.assert_not_called()
            fetch.assert_called_once_with(source, ANY)

    def test_archive_extraction_is_private_and_removed(self):
        archive = self.root / "modExample.zip"
        with zipfile.ZipFile(archive, "w") as package:
            package.writestr("modExample/content/asset.bundle", "new")
        extracted = []

        def unpack(source, destination):
            extracted.append(destination)
            with zipfile.ZipFile(source) as package:
                package.extractall(destination)

        model = Mock()
        model.all.return_value = []
        with (
            patch("src.core.fetcher.sys", SimpleNamespace(platform="linux")),
            patch("src.core.fetcher.shutil.unpack_archive", unpack),
        ):
            self.assertEqual(Installer(model).installMod(str(archive)), (True, 1, 0))
        self.assertEqual((self.game / "Mods" / "modExample" / "content" / "asset.bundle").read_text(), "new")
        self.assertFalse(Path(extracted[0]).exists())


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
