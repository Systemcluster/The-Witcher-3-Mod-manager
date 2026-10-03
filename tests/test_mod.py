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
from src.util.util import checkInstalledPath, copyFolder, removeDirectory, removeInstalledFile


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
            configuration=str(self.root / "Manager"),
        )
        Path(self.config.configuration).mkdir()
        config_patch = patch("src.globals.data.config", self.config)
        config_patch.start()
        self.addCleanup(config_patch.stop)

    def populated(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "asset").write_text("keep")
        return directory

    def link(self, link: Path, target: Path) -> None:
        try:
            resolved_target = target if target.is_absolute() else link.parent / target
            link.symlink_to(target, target_is_directory=resolved_target.is_dir())
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

    def test_never_deletes_through_external_links(self):
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
        self.assertEqual((external / "asset").read_text(), "keep")
        self.assertEqual((self.outside / "example.xml").read_text(), "keep")

    def test_allows_linked_game_root(self):
        linked_game = self.root / "Linked Game"
        self.link(linked_game, self.game)
        self.config.game = str(linked_game)
        real = self.populated(self.game / "Mods" / "modReal")
        removeDirectory(str(linked_game / "Mods" / real.name))
        self.assertFalse(real.exists())
        self.assertTrue(linked_game.is_symlink())

    def test_allows_internal_links_without_rewriting_returned_path(self):
        internal = self.populated(self.game / "content" / "modReal")
        linked = self.game / "Mods" / "modLinked"
        self.link(linked, internal)
        for target in (linked, linked / "new" / "asset"):
            with self.subTest(target=target):
                self.assertEqual(checkInstalledPath(str(target), modDirectory=True), str(target))
        removeInstalledFile(str(linked / "asset"))
        self.assertFalse((internal / "asset").exists())
        self.assertTrue(linked.is_symlink())

    def test_allows_internal_link_chains_and_dangling_targets(self):
        internal = self.populated(self.game / "content" / "modReal")
        linked = self.game / "Mods" / "modLinked"
        self.link(linked, Path("../content/modReal"))
        chained = self.game / "Mods" / "modChained"
        self.link(chained, linked)
        self.assertEqual(checkInstalledPath(str(chained), modDirectory=True), str(chained))
        missing = self.game / "bin" / "missing.xml"
        self.link(missing, internal / "missing.xml")
        self.assertEqual(checkInstalledPath(str(missing), modDirectory=False), str(missing))

    def test_dangling_targets_canonicalize_existing_ancestor(self):
        realpath = os.path.realpath
        for directory in (self.game / "content", self.outside):
            alias = self.root / (directory.name + "-alias")
            self.link(alias, directory)
            for index, suffix in enumerate((Path("missing.xml"), Path("missing") / "nested" / "file.xml")):
                with self.subTest(directory=directory, suffix=suffix):
                    missing = self.game / "bin" / f"{directory.name}-{index}.xml"
                    self.link(missing, directory / suffix)

                    def resolve(filename, *, strict=False):
                        if filename == str(missing) and not strict:
                            return str(alias / suffix)
                        return realpath(filename, strict=strict)

                    with patch("src.util.util.os.path.realpath", side_effect=resolve):
                        if directory == self.outside:
                            with self.assertRaises(ValueError):
                                checkInstalledPath(str(missing), modDirectory=False)
                        else:
                            self.assertEqual(checkInstalledPath(str(missing), modDirectory=False), str(missing))
                    missing.unlink()

    def test_refuses_external_link_chains_and_dangling_targets(self):
        linked = self.game / "content" / "linked"
        self.link(linked, self.outside)
        chained = self.game / "Mods" / "modChained"
        self.link(chained, linked)
        missing = self.game / "bin" / "missing.xml"
        self.link(missing, self.outside / "missing.xml")
        for target in (chained, chained / "new" / "asset", missing):
            with self.subTest(target=target), self.assertRaises(ValueError):
                checkInstalledPath(str(target), modDirectory=False)

    def test_refuses_link_cycles_and_targets_resolving_to_game_root(self):
        cycle = self.game / "Mods" / "modCycle"
        self.link(cycle, cycle)
        root_link = self.game / "Mods" / "modRoot"
        self.link(root_link, self.game)
        for target in (cycle, root_link):
            with self.subTest(target=target), self.assertRaises(ValueError):
                checkInstalledPath(str(target), modDirectory=True)

    def test_windows_junctions_use_resolved_destination(self):
        directory = self.populated(self.game / "Mods" / "modExample")
        lstat = os.lstat

        def junction(path, *args, **kwargs):
            metadata = lstat(path, *args, **kwargs)
            if os.fspath(path) == str(directory):
                return SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return metadata

        realpath = os.path.realpath
        for destination in (str(directory), str(self.outside)):

            def resolve(path, *, strict=False):
                if os.fspath(path) == str(directory):
                    return realpath(destination)
                return realpath(path, strict=strict)

            with (
                self.subTest(destination=destination),
                patch("src.util.util.os.lstat", side_effect=junction),
                patch("src.util.util.os.path.realpath", side_effect=resolve),
            ):
                if destination == str(directory):
                    self.assertEqual(checkInstalledPath(str(directory), modDirectory=True), str(directory))
                else:
                    with self.assertRaises(ValueError):
                        checkInstalledPath(str(directory), modDirectory=True)
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

    def test_toggle_refuses_links_and_parent_traversal(self):
        outside_file = self.outside / "asset"
        outside_file.write_text("keep")
        self.link(self.game / "DLC" / "linked", self.outside)
        with self.assertRaises(ValueError):
            Mod(dlcs=["linked"]).disable()
        self.assertEqual(outside_file.read_text(), "keep")
        self.assertFalse((self.outside / "asset.disabled").exists())

        escaped_menu = self.game / "victim.xml"
        escaped_menu.write_text("keep")
        with self.assertRaises(ValueError):
            Mod(menus=["../victim.xml"]).disable()
        self.assertEqual(escaped_menu.read_text(), "keep")
        self.assertFalse((self.game / "victim.xml.disabled").exists())

    def test_shared_xml_write_refuses_linked_target(self):
        external_input = self.outside / "input.xml"
        external_input.write_text('<!-- [BASE_CharacterMovement] -->')
        self.link(self.game / "bin" / "input.xml", external_input)
        with self.assertRaises(ValueError):
            Mod(xmlkeys=['<Var id="Example" />']).installXmlKeys()
        self.assertEqual(external_input.read_text(), '<!-- [BASE_CharacterMovement] -->')

    def test_linked_documents_settings_update_targets_without_replacing_links(self):
        self.config.gameversion = 're'
        input_target = self.outside / 'shared-input.settings'
        input_target.write_text('[Input]\nIK_A=(Action=Jump)\n')
        self.link(self.root / 'input.settings', input_target)
        mod = Mod(
            inputsettings=[Key('[Input]', 'IK_B=(Action=Run)')],
            usersettings=[Usersetting('Example', 'Enabled=true')],
        )
        targets = []
        for filename in ('user.settings', 'dx12user.settings'):
            target = self.outside / filename
            target.write_text('[Example]\nOther=keep\n')
            self.link(self.root / filename, target)
            targets.append(target)
        self.assertEqual(mod.installInputKeys(), (1, 0))
        self.assertEqual(mod.installUserSettings(), 1)
        self.assertTrue((self.root / 'input.settings').is_symlink())
        self.assertIn('IK_B=(Action=Run)', input_target.read_text())
        for target in targets:
            self.assertTrue((self.root / target.name).is_symlink())
            self.assertIn('Enabled=true', target.read_text())
        mod.uninstallUserSettings()
        for target in targets:
            self.assertTrue((self.root / target.name).is_symlink())
            self.assertNotIn('Enabled=', target.read_text())
            self.assertIn('Other=keep', target.read_text())
        original = input_target.read_bytes()
        mod.inputsettings = [Key('[Input]', 'IK_C=(Action=Dodge)')]
        with patch('src.util.util.os.replace', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                mod.installInputKeys()
        self.assertTrue((self.root / 'input.settings').is_symlink())
        self.assertEqual(input_target.read_bytes(), original)
        self.assertEqual(list(self.outside.glob('.tw3mm-*')), [])

    def test_failed_install_keeps_existing_mod_files(self):
        existing = self.populated(self.game / "Mods" / "modExample")
        mod = Mod(_name="Example", files=["modExample"])
        with (
            patch("src.core.installer.fetchMod", return_value=(mod, [], [])),
            patch.object(mod, "checkPriority", side_effect=OSError("failed")),
        ):
            self.assertEqual(Installer(Mock()).installMod(str(self.root / "source")), (False, 0, 0))
        self.assertEqual((existing / "asset").read_text(), "keep")

    def test_declined_overwrite_preserves_legacy_inventory_behavior(self):
        existing = self.populated(self.game / "Mods" / "modExample")
        source = self.populated(self.root / "source" / "modExample")
        mod = Mod(_name="Example", files=["modExample"])
        model = Mock()
        model.all.return_value = []
        with (
            patch("src.core.installer.fetchMod", return_value=(mod, [str(source)], [])),
            patch("src.core.installer.MessageOverwrite", return_value=QMessageBox.StandardButton.No),
        ):
            self.assertEqual(Installer(model).installMod(str(source.parent)), (True, 0, 0))
        self.assertEqual((existing / "asset").read_text(), "keep")
        model.add.assert_called_once_with(mod.name, mod)
        self.assertEqual(mod.files, ["modExample"])

    def test_protected_menus_are_never_disabled_or_deleted(self):
        protected = (
            "audio.xml",
            "display.xml",
            "dx11filelist.txt",
            "dx12filelist.txt",
            "gameplay.xml",
            "gamma.xml",
            "graphics.xml",
            "graphicsdx11.xml",
            "hidden.xml",
            "hud.xml",
            "input.xml",
            "localization.xml",
            "postprocess.xml",
            "rendering.xml",
        )
        for filename in protected:
            for name in (filename, filename.upper()):
                with self.subTest(menu=name):
                    target = Path(self.config.menu) / name
                    target.write_bytes(b"protected game contents")
                    element = XML.fromstring(
                        f'<mod name="Legacy" enabled="True" priority="-"><menu>{name}</menu></mod>'
                    )
                    mod = Model.populateModFromXml(Mod(), element)
                    model = Model(ignorelock=True)
                    model.add(mod.name, mod)
                    mod.disable()
                    self.assertEqual(target.read_bytes(), b"protected game contents")
                    self.assertFalse(Path(str(target) + ".disabled").exists())
                    mod.enable()
                    self.assertEqual(target.read_bytes(), b"protected game contents")
                    self.assertTrue(Installer(model).uninstallMod(mod))
                    self.assertEqual(target.read_bytes(), b"protected game contents")
                    target.unlink()

    def test_protected_menu_registration_survives_disable_and_uninstall(self):
        menu = Path(self.config.menu)
        (menu / 'graphics.xml').write_text('shared')
        (menu / 'custom.xml').write_text('custom')
        filelist = menu / 'dx12filelist.txt'
        filelist.write_text('graphics.xml;\ncustom.xml;\n', encoding='utf-16')
        mod = Mod(_name='Example', menus=['graphics.xml', 'custom.xml'])
        mod.disable()
        self.assertEqual(filelist.read_text(encoding='utf-16'), 'graphics.xml;\n')
        self.assertEqual((menu / 'graphics.xml').read_text(), 'shared')
        mod.enable()
        self.assertIn('custom.xml;', filelist.read_text(encoding='utf-16'))
        self.assertTrue(Installer(Mock()).uninstallMod(mod))
        self.assertEqual(filelist.read_text(encoding='utf-16'), 'graphics.xml;\n')
        self.assertEqual((menu / 'graphics.xml').read_text(), 'shared')

    def test_xml_only_package_is_installed_and_recorded(self):
        source = self.root / "True Next-Gen Graphic Enhancements"
        package_menu = source / "bin/config/r4game/user_config_matrix/pc"
        package_menu.mkdir(parents=True)
        (package_menu / "graphics.xml").write_text("modded graphics")
        (package_menu / "graphicsdx11.xml").write_text("modded dx11")
        (source / "bin/config/platform/pc").mkdir(parents=True)
        (source / "bin/config/platform/pc/rendering.ini").write_text("ignored rendering override")

        installed_menu = Path(self.config.menu)
        (installed_menu / "graphics.xml").write_text("original graphics")
        (installed_menu / "graphicsdx11.xml").write_text("original dx11")
        model = Model(ignorelock=True)
        installer = Installer(model)

        self.assertEqual(installer.installMod(str(source)), (True, 0, 0))
        self.assertEqual(list(model.list()), [source.name])
        restored = Model(ignorelock=True).get(source.name)
        self.assertCountEqual(restored.menus, ['graphics.xml', 'graphicsdx11.xml'])
        self.assertEqual((installed_menu / "graphics.xml").read_text(), "modded graphics")
        self.assertEqual((installed_menu / "graphicsdx11.xml").read_text(), "modded dx11")
        self.assertFalse((self.game / "bin/config/platform/pc/rendering.ini").exists())
        self.assertFalse((Path(self.config.configuration) / "menu-backups").exists())

    def test_disabled_menu_reimport_replaces_disabled_copy_until_enabled(self):
        source = self.root / 'Menu Package'
        package_menu = source / 'bin/config/r4game/user_config_matrix/pc'
        package_menu.mkdir(parents=True)
        (package_menu / 'custom.xml').write_text('<v1/>')
        menu = Path(self.config.menu)
        filelist = menu / 'dx12filelist.txt'
        filelist.write_text('base.xml;\n', encoding='utf-16')
        model = Model(ignorelock=True)
        installer = Installer(model)
        self.assertTrue(installer.installMod(str(source))[0])
        mod = model.get(source.name)
        mod.disable()
        (package_menu / 'custom.xml').write_text('<v2/>')
        self.assertTrue(installer.installMod(str(source))[0])
        self.assertFalse(mod.enabled)
        self.assertFalse((menu / 'custom.xml').exists())
        self.assertEqual((menu / 'custom.xml.disabled').read_text(), '<v2/>')
        self.assertEqual(filelist.read_text(encoding='utf-16'), 'base.xml;\n')
        model.write()
        restored = Model(ignorelock=True).get(source.name)
        self.assertFalse(restored.enabled)
        restored.enable()
        self.assertEqual((menu / 'custom.xml').read_text(), '<v2/>')
        self.assertFalse((menu / 'custom.xml.disabled').exists())
        self.assertIn('custom.xml;', filelist.read_text(encoding='utf-16'))

    def test_empty_normalized_install_name_is_rejected_before_copying(self):
        model = Model(ignorelock=True)
        for name in ('mod', 'modmod'):
            source = self.root / name
            self.populated(source / 'content')
            with self.subTest(name=name), patch.object(model, 'write') as save:
                self.assertEqual(Installer(model).installMod(str(source)), (False, 0, 0))
                save.assert_not_called()
                self.assertFalse((self.game / 'Mods' / name).exists())
                self.assertEqual(list(model.list()), [])

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

    def test_partial_update_records_fetched_folders_including_declined_copies(self):
        source = self.root / "Example"
        for name in ("modFirst", "modSecond", "dlcFirst", "dlcSecond"):
            content = source / name / "content"
            content.mkdir(parents=True)
            (content / "asset").write_text("original")
        model = Model(ignorelock=True)
        installer = Installer(model)
        self.assertEqual(installer.installMod(str(source)), (True, 4, 0))
        unowned = self.populated(self.game / "Mods" / "modUnowned")
        (source / "modUnowned" / "content").mkdir(parents=True)
        for asset in source.glob("*/content/asset"):
            asset.write_text("updated")

        def overwrite(name, category):
            return QMessageBox.StandardButton.Yes if name.endswith("First") else QMessageBox.StandardButton.No

        with patch("src.core.installer.MessageOverwrite", side_effect=overwrite):
            self.assertEqual(installer.installMod(str(source)), (True, 2, 0))
        reloaded = Model(ignorelock=True)
        mod = reloaded.get("Example")
        self.assertCountEqual(mod.files, ["modFirst", "modSecond", "modUnowned"])
        self.assertCountEqual(mod.dlcs, ["dlcFirst", "dlcSecond"])
        self.assertEqual((self.game / "Mods/modSecond/content/asset").read_text(), "original")
        self.assertTrue(Installer(reloaded).uninstallMod(mod))
        self.assertFalse((self.game / "Mods/modSecond").exists())
        self.assertFalse((self.game / "DLC/dlcSecond").exists())
        self.assertFalse(unowned.exists())

    def test_repeated_menu_import_updates_existing_record_until_ui_saves(self):
        source = self.root / 'Example'
        self.populated(source / 'modExample/content')
        package_menu = source / 'bin/config/r4game/user_config_matrix/pc'
        package_menu.mkdir(parents=True)
        (package_menu / 'custom.xml').write_text('first')
        menu = Path(self.config.menu)
        (menu / 'custom.xml').write_text('preexisting unregistered menu')
        (menu / 'dx11filelist.txt').write_text('base.xml;\n', encoding='utf-16')
        model = Model(ignorelock=True)
        installer = Installer(model)
        self.assertEqual(installer.installMod(str(source)), (True, 1, 0))
        self.assertIn('custom.xml;', (menu / 'dx11filelist.txt').read_text(encoding='utf-16'))
        (package_menu / 'custom.xml').write_text('second')
        (package_menu / 'extra.xml').write_text('extra')
        installed = model.get('Example')
        with patch('src.core.installer.MessageOverwrite', return_value=QMessageBox.StandardButton.Yes):
            self.assertEqual(installer.installMod(str(source)), (True, 1, 0))
        self.assertIs(model.get('Example'), installed)
        self.assertEqual(Model(ignorelock=True).get('Example').menus, ['custom.xml'])
        model.write()
        reloaded = Model(ignorelock=True)
        mod = reloaded.get('Example')
        self.assertCountEqual(mod.menus, ['custom.xml', 'extra.xml'])
        self.assertEqual((menu / 'custom.xml').read_text(), 'second')
        self.assertTrue(Installer(reloaded).uninstallMod(mod))
        self.assertFalse((menu / 'custom.xml').exists())
        self.assertFalse((menu / 'extra.xml').exists())
        self.assertEqual((menu / 'dx11filelist.txt').read_text(encoding='utf-16'), 'base.xml;\n')

    def test_overlapping_protected_replacements_never_restore_stale_contents(self):
        target = Path(self.config.menu) / 'graphics.xml'
        target.write_text('original')
        model = Model(ignorelock=True)
        installer = Installer(model)
        for name in ('First', 'Second'):
            self.populated(self.root / name / ('mod' + name) / 'content')
            source = self.root / name / 'bin/config/r4game/user_config_matrix/pc'
            source.mkdir(parents=True)
            (source / 'graphics.xml').write_text(name)
            self.assertEqual(installer.installMod(str(self.root / name)), (True, 1, 0))
        self.assertTrue(installer.uninstallMod(model.get('First')))
        self.assertEqual(target.read_text(), 'Second')
        self.assertTrue(installer.uninstallMod(model.get('Second')))
        self.assertEqual(target.read_text(), 'Second')

    def test_case_variant_menu_copies_do_not_create_backup_state(self):
        menu = Path(self.config.menu)
        (menu / 'graphics.xml').write_text('original')
        source = self.root / 'source'
        source.mkdir()
        first = source / 'graphics.xml'
        first.write_text('first')
        second = self.root / 'Graphics.xml'
        second.write_text('second')
        self.populated(source / 'modExample/content')
        mod = Mod(_name='Example', files=['modExample'], menus=['graphics.xml', 'Graphics.xml'])
        model = Model(ignorelock=True)
        installer = Installer(model)
        with patch(
            'src.core.installer.fetchMod',
            return_value=(mod, [str(source / 'modExample')], [str(first), str(second)]),
        ):
            self.assertEqual(installer.installMod(str(source)), (True, 1, 0))
        before = {name: (menu / name).read_bytes() for name in mod.menus}
        mod.disable()
        mod.enable()
        self.assertTrue(installer.uninstallMod(mod))
        self.assertEqual({name: (menu / name).read_bytes() for name in mod.menus}, before)
        self.assertFalse((Path(self.config.configuration) / 'menu-backups').exists())

    def test_interim_backup_metadata_is_passive_and_recovery_files_are_kept(self):
        identifier = '0123456789abcdef0123456789abcdef'
        backup = Path(self.config.configuration) / 'menu-backups' / identifier / 'original/graphics.xml'
        backup.parent.mkdir(parents=True)
        backup.write_text('old recovery contents')
        target = Path(self.config.menu) / 'graphics.xml'
        target.write_text('current contents')
        element = XML.fromstring(
            f'<mod name="Example" enabled="True" backup="{identifier}"><menu>graphics.xml</menu></mod>'
        )
        mod = Model.populateModFromXml(Mod(), element)
        self.assertEqual(mod.menus, ['graphics.xml'])
        model = Model(ignorelock=True)
        model.add(mod.name, mod)
        reloaded = Model(ignorelock=True)
        restored = reloaded.get(mod.name)
        self.assertEqual(restored.menus, ['graphics.xml'])
        restored.disable()
        restored.enable()
        self.assertTrue(Installer(reloaded).uninstallMod(restored))
        self.assertEqual(target.read_text(), 'current contents')
        self.assertEqual(backup.read_text(), 'old recovery contents')

    def test_uninstall_can_retry_after_asset_deletion_failure(self):
        target = Path(self.config.menu) / 'graphics.xml'
        target.write_text('keep')
        self.populated(self.game / 'Mods/modExample')
        mod = Mod(_name='Example', menus=['graphics.xml'], files=['modExample'])
        model = Model(ignorelock=True)
        model.add(mod.name, mod)
        installer = Installer(model)
        with patch.object(installer, 'removeModData', side_effect=PermissionError('denied')):
            self.assertFalse(installer.uninstallMod(mod))
        self.assertTrue(installer.uninstallMod(mod))
        self.assertEqual(target.read_text(), 'keep')
        self.assertEqual(list(model.list()), [])

    def test_shared_custom_menu_uses_existing_toggle_and_removal_rules(self):
        target = Path(self.config.menu) / "custom.xml"
        target.write_text("shared")
        filelist = Path(self.config.menu) / "dx11filelist.txt"
        filelist.write_text("custom.xml;\n", encoding="utf-16")
        first = Mod(_name="First", menus=["custom.xml"])
        second = Mod(_name="Second", menus=["custom.xml"])
        model = Model(ignorelock=True)
        model.add(first.name, first)
        model.add(second.name, second)
        first.disable()
        self.assertFalse(target.exists())
        self.assertEqual(Path(str(target) + ".disabled").read_text(), "shared")
        self.assertEqual(filelist.read_text(encoding="utf-16"), "\n")
        self.assertTrue(Installer(model).uninstallMod(first))
        self.assertFalse(target.exists())
        self.assertEqual(filelist.read_text(encoding="utf-16"), "\n")
        self.assertTrue(Installer(model).uninstallMod(second))
        self.assertFalse(target.exists())
        self.assertEqual(filelist.read_text(encoding="utf-16"), "\n")

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
        mod = Mod(
            inputsettings=[Key("Input", "IK_A=(Action=Jump)")],
            usersettings=[Usersetting("Mod", "Enabled=true")],
            menus=["graphics.xml"],
        )
        root = Model.writeModToXml(mod, XML.ElementTree(XML.Element("installed")))
        element = root.find("mod")
        assert element is not None
        restored = Model.populateModFromXml(Mod(), element)
        self.assertEqual(restored.inputsettings, mod.inputsettings)
        self.assertIsInstance(restored.usersettings[0], Usersetting)
        self.assertEqual(restored.menus, mod.menus)

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
        self.config = SimpleNamespace(
            game=str(self.root), menu=str(self.root), settings=str(self.root), gameversion='re'
        )
        config_patch = patch('src.domain.mod.data.config', self.config)
        config_patch.start()
        self.addCleanup(config_patch.stop)

    def test_install_without_input_keys_leaves_file_unchanged(self):
        input_settings = self.root / "input.settings"
        original = b"; custom comment\n[Input]\nIK_A=(Action=Jump)\nCustom=preserve\n"
        input_settings.write_bytes(original)
        self.assertEqual(Mod().installInputKeys(), (0, 0))
        self.assertEqual(input_settings.read_bytes(), original)

    def test_install_input_keys_preserves_unrecognized_content(self):
        input_settings = self.root / "input.settings"
        input_settings.write_text(
            "; custom comment\n[Input]\nIK_A=(Action=Jump)\nCustom=preserve\n\n[Unrelated]\nOther=value\n"
        )
        mod = Mod(inputsettings=[Key("[Input]", "IK_B=(Action=Run)")])
        self.assertEqual(mod.installInputKeys(), (1, 0))
        text = input_settings.read_text()
        self.assertIn("; custom comment", text)
        self.assertIn("Custom=preserve", text)
        self.assertIn("[Unrelated]\nOther=value", text)
        self.assertIn("IK_A=(Action=Jump)", text)
        self.assertIn("IK_B=(Action=Run)", text)

    def test_input_binding_trailing_comments_do_not_hide_conflicts(self):
        settings = self.root / 'input.settings'
        mod = Mod(inputsettings=[Key('[Input]', 'IK_B=(Action=Jump)')])
        for comment in ('; keep (custom)', '# keep (custom)'):
            original = f'[Input]\r\nIK_A=(Action=Jump) {comment}\r\n'.encode()
            for answer in (QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes):
                with self.subTest(comment=comment, answer=answer):
                    settings.write_bytes(original)
                    with patch('src.domain.mod.MessageRebindKeys', return_value=answer) as prompt:
                        expected_counts = (0, 1) if answer == QMessageBox.StandardButton.No else (1, 0)
                        self.assertEqual(mod.installInputKeys(), expected_counts)
                        prompt.assert_called_once()
                    expected = (
                        original if answer == QMessageBox.StandardButton.No else b'[Input]\r\nIK_B=(Action=Jump)\r\n'
                    )
                    self.assertEqual(settings.read_bytes(), expected)

    def test_input_section_trailing_comments_keep_bindings_in_their_context(self):
        settings = self.root / 'input.settings'
        for comment in ('; keep [custom]', '# keep [custom]'):
            with self.subTest(comment=comment):
                original = f'[Input]\nIK_A=(Action=Jump)\n[Other] {comment}\nIK_B=(Action=Run)\n'
                settings.write_text(original)
                mod = Mod(inputsettings=[Key('[Input]', 'IK_C=(Action=Run)')])
                with patch('src.domain.mod.MessageRebindKeys') as prompt:
                    self.assertEqual(mod.installInputKeys(), (1, 0))
                    prompt.assert_not_called()
                expected = original.replace('[Other]', 'IK_C=(Action=Run)\n[Other]')
                self.assertEqual(settings.read_text(), expected)
                mod = Mod(inputsettings=[Key('[Other]', 'IK_D=(Action=Run)')])
                with patch('src.domain.mod.MessageRebindKeys', return_value=QMessageBox.StandardButton.Yes) as prompt:
                    self.assertEqual(mod.installInputKeys(), (1, 0))
                    prompt.assert_called_once()
                self.assertEqual(settings.read_text(), expected.replace('IK_B=', 'IK_D='))

    def test_input_trailing_comments_preserved_for_duplicate_keys_and_versions(self):
        settings = self.root / 'input.settings'
        original = b'[Input] ; keep\r\nVersion=1 # version\r\nIK_A=(Action=Jump) ; binding\r\n'
        settings.write_bytes(original)
        mod = Mod(inputsettings=[Key('[Input]', 'Version=1'), Key('[Input]', 'IK_A=(Action=Jump)')])
        with patch('src.domain.mod.MessageRebindKeys') as prompt:
            self.assertEqual(mod.installInputKeys(), (0, 0))
            prompt.assert_not_called()
        self.assertEqual(settings.read_bytes(), original)

    def test_failed_input_settings_promotion_preserves_original(self):
        input_settings = self.root / "input.settings"
        original = b"[Input]\nIK_A=(Action=Jump)\n"
        input_settings.write_bytes(original)
        mod = Mod(inputsettings=[Key("[Input]", "IK_B=(Action=Run)")])
        with patch("src.util.util.os.replace", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                mod.installInputKeys()
        self.assertEqual(input_settings.read_bytes(), original)
        self.assertEqual(sorted(entry.name for entry in self.root.iterdir()), ["input.settings"])

    def test_rebind_removes_original_despite_action_whitespace(self):
        settings = self.root / "input.settings"
        settings.write_text('[Input]\nIK_A=(Action=Jump,  State=Duration)\n')
        mod = Mod(inputsettings=[Key('[Input]', 'IK_B=(Action=Jump,State=Duration)')])
        with patch('src.domain.mod.MessageRebindKeys', return_value=QMessageBox.StandardButton.Yes) as prompt:
            self.assertEqual(mod.installInputKeys(), (1, 0))
            prompt.assert_called_once()
        self.assertEqual(settings.read_text(), '[Input]\nIK_B=(Action=Jump,State=Duration)\n')

    def test_rebind_between_package_additions_keeps_only_final_binding(self):
        mod = Mod(inputsettings=[Key('[Input]', 'IK_A=(Action=Jump)'), Key('[Input]', 'IK_B=(Action=Jump)')])
        with patch('src.domain.mod.MessageRebindKeys', return_value=QMessageBox.StandardButton.Yes):
            self.assertEqual(mod.installInputKeys(), (2, 0))
        self.assertEqual((self.root / 'input.settings').read_text(), '[Input]\nIK_B=(Action=Jump)\n')

    def test_input_conflicts_are_collected_before_rebinding(self):
        settings = self.root / 'input.settings'
        settings.write_text('[Input]\nIK_A=(Action=Jump)\n')
        mod = Mod(inputsettings=[Key('[Input]', 'IK_B=(Action=Jump)'), Key('[Input]', 'IK_A=(Action=Jump)')])
        with patch('src.domain.mod.MessageRebindKeys', return_value=QMessageBox.StandardButton.Yes) as prompt:
            self.assertEqual(mod.installInputKeys(), (1, 0))
            prompt.assert_called_once()
            self.assertEqual(prompt.call_args.args[:2], (mod.inputsettings[1], mod.inputsettings[0]))
        self.assertEqual(settings.read_text(), '[Input]\nIK_B=(Action=Jump)\n')

    def test_input_conflict_answers_apply_to_all_remaining_conflicts(self):
        settings = self.root / 'input.settings'
        original = '[Input]\nIK_A=(Action=Jump)\nIK_C=(Action=Run)\n'
        mod = Mod(inputsettings=[Key('[Input]', 'IK_B=(Action=Jump)'), Key('[Input]', 'IK_D=(Action=Run)')])
        for answer, result, expected in (
            (QMessageBox.StandardButton.YesToAll, (2, 0), '[Input]\nIK_B=(Action=Jump)\nIK_D=(Action=Run)\n'),
            (QMessageBox.StandardButton.NoToAll, (0, 2), original),
        ):
            with self.subTest(answer=answer):
                settings.write_text(original)
                with patch('src.domain.mod.MessageRebindKeys', return_value=answer) as prompt:
                    self.assertEqual(mod.installInputKeys(), result)
                    prompt.assert_called_once()
                self.assertEqual(settings.read_text(), expected)

    def test_empty_input_contexts_are_not_serialized_as_bindings(self):
        settings = self.root / 'input.settings'
        original = b'[Existing]\n; keep\n'
        settings.write_bytes(original)
        mod = Mod(inputsettings=[Key('[Existing]'), Key('[New]')])
        self.assertEqual(mod.installInputKeys(), (2, 0))
        self.assertEqual(settings.read_bytes(), original + b'\n[New]\n')
        self.assertEqual(mod.installInputKeys(), (2, 0))
        self.assertNotIn(b'=(None)', settings.read_bytes())

    def test_input_keys_after_unknown_lines_are_recognized_and_keep_crlf(self):
        settings = self.root / 'input.settings'
        original = b'[Input]\r\n; comment\r\nCustom=keep\r\nIK_A=(Action=Jump)\r\n'
        settings.write_bytes(original)
        mod = Mod(inputsettings=[Key('[Input]', 'IK_A=(Action=Jump)'), Key('[Input]', 'IK_B=(Action=Run)')])
        self.assertEqual(mod.installInputKeys(), (1, 0))
        expected = original + b'IK_B=(Action=Run)\r\n'
        self.assertEqual(settings.read_bytes(), expected)
        self.assertEqual(mod.installInputKeys(), (0, 0))
        self.assertEqual(settings.read_bytes(), expected)

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
        self.config = SimpleNamespace(configuration=str(self.root))
        config_patch = patch("src.core.model.data.config", self.config)
        config_patch.start()
        self.addCleanup(config_patch.stop)
        for name in ("MessageAlertReadingConfigurationFailed", "MessageAlertWritingFailed"):
            alert_patch = patch("src.core.model." + name)
            alert_patch.start()
            self.addCleanup(alert_patch.stop)

    def write_inventory(self, filename, name):
        tree = Model.writeModToXml(Mod(_name=name), XML.ElementTree(XML.Element("installed")))
        tree.write(self.root / filename, encoding="utf-8", xml_declaration=True)

    def test_empty_normalized_rename_keeps_existing_inventory(self):
        self.write_inventory('installed.xml', 'Original')
        model = Model(ignorelock=True)
        original = (self.root / 'installed.xml').read_bytes()
        for name in ('', 'mod', 'modmod'):
            with self.subTest(name=name):
                self.assertFalse(model.rename('Original', name))
                self.assertEqual(list(model.list()), ['Original'])
                self.assertEqual((self.root / 'installed.xml').read_bytes(), original)

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
                with patch("src.core.model.MessageAlertWritingFailed") as alert:
                    model.write()
                alert.assert_called_once()
                self.assertIsInstance(alert.call_args.args[1], RuntimeError)
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

        with (
            patch("src.core.model.os.replace", side_effect=fail_promotion),
            patch("src.core.model.MessageAlertWritingFailed") as alert,
        ):
            model.write()
        alert.assert_called_once()
        self.assertIsInstance(alert.call_args.args[1], PermissionError)
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
                with (
                    patch("src.core.model.os.fsync", side_effect=failures),
                    patch("src.core.model.MessageAlertWritingFailed") as alert,
                ):
                    model.write()
                alert.assert_called_once()
                self.assertIsInstance(alert.call_args.args[1], OSError)
                self.assertEqual((self.root / "installed.xml").read_bytes(), original)
                self.assertTrue(XML.parse(self.root / "installed.xml.old").findall("mod"))
                self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])

    def test_invalid_serialized_inventory_never_replaces_live_file(self):
        self.write_inventory("installed.xml", "Original")
        model = Model(ignorelock=True)
        original = (self.root / "installed.xml").read_bytes()
        model.modList["Invalid"] = Mod(_name="Invalid\x00")
        with patch("src.core.model.MessageAlertWritingFailed") as alert:
            model.write()
        alert.assert_called_once()
        self.assertIsInstance(alert.call_args.args[1], (ValueError, XML.ParseError))
        self.assertEqual((self.root / "installed.xml").read_bytes(), original)
        self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])

    def test_legacy_encoding_declaration_remains_readable(self):
        self.write_inventory("installed.xml", "Original")
        filename = self.root / "installed.xml"
        filename.write_bytes(filename.read_bytes().replace(b"utf-8", b"utf_8"))
        self.assertEqual(list(Model(ignorelock=True).list()), ["Original"])


if __name__ == "__main__":
    unittest.main()
