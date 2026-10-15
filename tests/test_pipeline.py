import configparser
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from shutil import copytree, make_archive
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QMessageBox

from src.core.installer import Installer
from src.core.model import Model

MOCKDATA = Path(__file__).parent / "mockdata"


class TestConfiguration(SimpleNamespace):
    priority: configparser.ConfigParser

    def getPriority(self, section: str) -> str | None:
        if self.priority.has_option(section, "priority"):
            return self.priority.get(section, "priority")
        return None

    def setPriority(self, section: str, value: str) -> None:
        if not self.priority.has_section(section):
            self.priority.add_section(section)
        self.priority.set(section, "priority", value)

    def removePriority(self, section: str) -> None:
        self.priority.remove_section(section)


class FullPipelineTests(unittest.TestCase):
    @contextmanager
    def environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copytree(MOCKDATA, root, dirs_exist_ok=True)
            game = root / "programs"
            documents = root / "documents"
            configuration = root / "configuration"
            menu = game / "bin" / "config" / "r4game" / "user_config_matrix" / "pc"
            configuration.mkdir()
            menu.mkdir(parents=True)
            (menu / "input.xml").write_text(
                '<Group id="PCInput"><VisibleVars><!-- [BASE_CharacterMovement] --></VisibleVars></Group>',
                encoding="utf-8",
            )
            (menu / "hidden.xml").write_text("<VisibleVars>\n</VisibleVars>\n", encoding="utf-8")
            for filename in ("dx11filelist.txt", "dx12filelist.txt"):
                (menu / filename).write_text("base.xml;\n", encoding="utf-16")
            config = TestConfiguration(
                game=str(game),
                mods=str(game / "mods"),
                dlc=str(game / "dlc"),
                menu=str(menu),
                settings=str(documents),
                configuration=str(configuration),
                gameversion="og",
                priority=configparser.ConfigParser(),
            )
            with (
                patch("src.globals.data.config", config),
                patch("src.core.installer.MessageOverwrite", return_value=QMessageBox.StandardButton.Yes),
                patch("src.domain.mod.MessageRebindKeys", return_value=QMessageBox.StandardButton.No),
            ):
                model = Model(ignorelock=True)
                yield root, model, Installer(model)

    def test_installs_base_ini_files(self):
        for with_content in (False, True):
            with self.subTest(with_content=with_content), self.environment() as (root, model, installer):
                package = root / "ini-package"
                base = package / "wrapper" / "BIN" / "CONFIG" / "BASE"
                base.mkdir(parents=True)
                payload = b"[General]\r\nConfigVersion=5\r\n"
                (base / "general.INI").write_bytes(payload)
                (package / "unrelated.ini").write_text("not game configuration", encoding="utf-8")
                menu = package / "bin" / "config" / "r4game" / "user_config_matrix" / "pc"
                menu.mkdir(parents=True)
                (menu / "example.xml").write_text("<VisibleVars/>", encoding="utf-8")
                if with_content:
                    (package / "modExample" / "content").mkdir(parents=True)
                self.assertEqual(installer.installMod(str(package)), (True, int(with_content), 0))
                target = root / "programs" / "bin" / "config" / "base" / "general.INI"
                self.assertTrue(target.is_file())
                self.assertEqual(target.read_bytes(), payload)
                self.assertFalse((target.parent / "unrelated.ini").exists())
                installed = next(iter(Model(ignorelock=True).all()))
                self.assertEqual(installed.inis, ["general.INI"])
                self.assertEqual(installed.menus, ["example.xml"])
                installed_menu = root / "programs" / "bin" / "config" / "r4game" / "user_config_matrix" / "pc"
                self.assertEqual((installed_menu / "example.xml").read_text(encoding="utf-8"), "<VisibleVars/>")
                self.assertFalse((installed_menu / "general.INI").exists())

    def test_installs_ini_only_package(self):
        with self.environment() as (root, model, installer):
            package = root / "ini-only"
            base = package / "bin" / "config" / "base"
            base.mkdir(parents=True)
            (base / "general.ini").write_bytes(b"[General]\nConfigVersion=5\n")
            self.assertEqual(installer.installMod(str(package)), (True, 0, 0))
            installed = next(iter(model.all()))
            target = root / "programs" / "bin" / "config" / "base" / "general.ini"
            installed.disable()
            self.assertTrue(target.is_file())
            self.assertTrue(installer.uninstallMod(installed))
            self.assertTrue(target.is_file())

    def test_mixed_graphics_package_reports_omitted_platform_ini(self):
        # Nexus 8448's public archive preview contains both rendering.ini paths and these two XMLs.
        with self.environment() as (root, model, installer):
            package = root / "True Next-Gen Graphic Enhancements"
            payloads = {
                "bin/config/base/rendering.ini": b"[Rendering]\nBase=2\n",
                "bin/config/platform/pc/rendering.ini": b"[Rendering]\nPlatform=3\n",
                "bin/config/r4game/user_config_matrix/pc/graphics.xml": b"<UserConfig/>",
                "bin/config/r4game/user_config_matrix/pc/graphicsdx11.xml": b"<UserConfig/>",
            }
            for relative, contents in payloads.items():
                source = package / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(contents)
            platform = root / "programs/bin/config/platform/pc/rendering.ini"
            platform.parent.mkdir(parents=True)
            original = b"[Rendering]\nPlatform=1\n"
            platform.write_bytes(original)
            output: list[str] = []
            installer.output = output.append
            self.assertEqual(installer.installMod(str(package)), (True, 0, 1))
            self.assertEqual(platform.read_bytes(), original)
            self.assertEqual(
                (root / "programs/bin/config/base/rendering.ini").read_bytes(),
                payloads["bin/config/base/rendering.ini"],
            )
            self.assertTrue(
                any(
                    "Manual installation required" in line and "bin/config/platform/pc/rendering.ini" in line
                    for line in output
                )
            )
            self.assertEqual(next(iter(model.all())).inis, ["rendering.ini"])

    def test_ini_archive_reimport_replaces_shared_file(self):
        with self.environment() as (root, model, installer):
            package = root / "ini-archive"
            base = package / "bin" / "config" / "base"
            base.mkdir(parents=True)
            source = base / "general.ini"
            target = root / "programs" / "bin" / "config" / "base" / "general.ini"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"original game settings")
            source.write_bytes(b"first replacement")
            archive = make_archive(str(package), "zip", package)
            self.assertEqual(installer.installMod(archive), (True, 0, 0))
            self.assertEqual(target.read_bytes(), b"first replacement")
            installed = next(iter(model.all()))
            installed.disable()
            source.write_bytes(b"second replacement\r\n")
            archive = make_archive(str(package), "zip", package)
            self.assertEqual(installer.installMod(archive), (True, 0, 0))
            self.assertIs(model.get(installed.name), installed)
            self.assertEqual(installed.inis, ["general.ini"])
            self.assertFalse(installed.enabled)
            self.assertEqual(target.read_bytes(), b"second replacement\r\n")
            self.assertEqual(installed.enable(), [])
            self.assertEqual(target.read_bytes(), b"second replacement\r\n")

    def test_ini_install_rejects_external_destination_links(self):
        for link_directory in (False, True):
            with self.subTest(link_directory=link_directory), self.environment() as (root, model, installer):
                package = root / "ini-package"
                base = package / "bin" / "config" / "base"
                base.mkdir(parents=True)
                (base / "general.ini").write_bytes(b"replacement")
                outside = root / "outside"
                outside.mkdir()
                (outside / "general.ini").write_bytes(b"untouched")
                destination = root / "programs" / "bin" / "config" / "base"
                if link_directory:
                    destination.symlink_to(outside, target_is_directory=True)
                else:
                    destination.mkdir()
                    (destination / "general.ini").symlink_to(outside / "general.ini")
                self.assertEqual(installer.installMod(str(package)), (False, 0, 0))
                self.assertEqual((outside / "general.ini").read_bytes(), b"untouched")
                self.assertEqual(model.modList, {})

    def test_installs_each_supported_mock_mod(self):
        packages = {
            "mod-direct": (1, ("mods/mod-direct/content/blob0.bundle",)),
            "mod-with-dlc": (2, ("mods/mod-dlc/content/blob0.bundle", "dlc/mod-dlc/content/blob0.bundle")),
            "mod-with-dlc-same-name": (
                2,
                ("mods/modDlc/content/blob0.bundle", "dlc/modDlc/content/blob0.bundle"),
            ),
            "mod-with-inputs": (1, ("mods/mod-with-inputs/content/blob0.bundle",)),
            "mod-with-inputs-readme": (1, ("mods/mod-with-inputs-readme/content/blob0.bundle",)),
            "mod-without-dlc": (
                1,
                (
                    "mods/mod-without-dlc/content/blob0.bundle",
                    "mods/mod-without-dlc/content/dlc/EP1/content/en.w3strings",
                ),
            ),
            "normal": (1, ("mods/modNormal/content/blob0.bundle",)),
            "only-dlc": (1, ("dlc/dlc__only/content/blob0.bundle",)),
            "patch": (1, ("mods/mod0000____CompilationTrigger/content/scripts/compilationTrigger.ws",)),
            "valid": (
                3,
                (
                    "mods/MODTestmod/content/blob0.bundle",
                    "mods/modTestmodExtra/content/blob0.bundle",
                    "dlc/dlcTestmod/content/blob0.bundle",
                ),
            ),
        }
        for package, (install_count, installed_files) in packages.items():
            with self.subTest(package=package), self.environment() as (root, model, installer):
                result = installer.installMod(str(root / "mods" / package))
                self.assertEqual(result[0:2], (True, install_count))
                self.assertEqual(result[2], int(package == "patch"))
                self.assertEqual(len(model.modList), 1)
                for filename in installed_files:
                    self.assertTrue((root / "programs" / filename).is_file(), filename)
                expected_mods = {"modAlreadyInstalled"}
                expected_dlcs = {"ep1"}
                for filename in installed_files:
                    category, folder, _ = filename.split("/", 2)
                    (expected_mods if category == "mods" else expected_dlcs).add(folder)
                self.assertEqual({p.name for p in (root / "programs/mods").iterdir()}, expected_mods)
                self.assertEqual({p.name for p in (root / "programs/dlc").iterdir()}, expected_dlcs)
                if package == "mod-without-dlc":
                    source = root / "mods" / package / "content"
                    target = root / "programs/mods" / package / "content"
                    for payload in source.rglob("*"):
                        if payload.is_file():
                            self.assertEqual((target / payload.relative_to(source)).read_bytes(), payload.read_bytes())

    def test_rejects_each_unsupported_mock_mod(self):
        for package in ("mod-with-split-bins", "weird"):
            with self.subTest(package=package), self.environment() as (root, model, installer):
                self.assertEqual(installer.installMod(str(root / "mods" / package)), (False, 0, 0))
                self.assertEqual(model.modList, {})

    def test_installs_each_mock_archive(self):
        for archive in ("mod-normal.zip", "mod-with-long-name.zip"):
            with self.subTest(archive=archive), self.environment() as (root, model, installer):
                self.assertEqual(installer.installMod(str(root / "mods" / archive))[0:2], (True, 1))
                self.assertEqual(len(model.modList), 1)
                installed = next(iter(model.all()))
                self.assertEqual(len(installed.files), 1)
                self.assertTrue(
                    (root / "programs" / "mods" / installed.files[0] / "content" / "blob0.bundle").is_file()
                )

    def test_matching_reimport_updates_existing_record_without_merging(self):
        with self.environment() as (root, model, installer):
            package = str(root / "mods" / "mod-direct")
            self.assertEqual(installer.installMod(package), (True, 1, 0))
            installed = next(iter(model.all()))
            installed.dlcs = ["oldDlc"]
            installed.menus = ["oldMenu.xml"]
            installed.disable()
            self.assertEqual(installer.installMod(package), (True, 1, 0))
            self.assertIs(model.get(installed.name), installed)
            self.assertEqual(installed.dlcs, [])
            self.assertEqual(installed.menus, [])
            self.assertFalse(installed.enabled)
            self.assertFalse((root / "programs/mods/mod-direct").exists())
            self.assertTrue((root / "programs/mods/~mod-direct/content/blob0.bundle").is_file())

    def test_changed_folders_replace_same_name_record_without_merging(self):
        with self.environment() as (root, model, installer):
            package = str(root / "mods" / "mod-direct")
            self.assertEqual(installer.installMod(package), (True, 1, 0))
            installed = next(iter(model.all()))
            installed.disable()
            installed.files = ["modPrevious"]
            installed.dlcs = ["oldDlc"]
            installed.menus = ["oldMenu.xml"]
            self.assertEqual(installer.installMod(package), (True, 1, 0))
            replacement = model.get(installed.name)
            self.assertIsNot(replacement, installed)
            self.assertEqual(replacement.files, ["mod-direct"])
            self.assertEqual(replacement.dlcs, [])
            self.assertEqual(replacement.menus, [])
            self.assertFalse(replacement.enabled)
            self.assertFalse((root / "programs/mods/mod-direct").exists())
            self.assertTrue((root / "programs/mods/~mod-direct/content/blob0.bundle").is_file())

    def test_declined_overwrite_keeps_package_inventory(self):
        with self.environment() as (root, model, installer):
            package = str(root / "mods" / "mod-direct")
            self.assertEqual(installer.installMod(package), (True, 1, 0))
            installed = next(iter(model.all()))
            with patch("src.core.installer.MessageOverwrite", return_value=QMessageBox.StandardButton.No):
                self.assertEqual(installer.installMod(package), (True, 0, 0))
            self.assertIs(model.get(installed.name), installed)
            self.assertEqual(installed.files, ["mod-direct"])

    def test_install_reload_disable_enable_and_uninstall(self):
        with self.environment() as (root, model, installer):
            self.assertEqual(installer.installMod(str(root / "mods" / "mod-direct")), (True, 1, 0))
            installed = next(iter(model.all()))

            reloaded = Model(ignorelock=True)
            restored = reloaded.get(installed.name)
            self.assertEqual(restored.files, ["mod-direct"])
            self.assertTrue(restored.enabled)

            restored.disable()
            self.assertFalse((root / "programs" / "mods" / "mod-direct").exists())
            self.assertTrue((root / "programs" / "mods" / "~mod-direct").is_dir())
            restored.enable()
            self.assertTrue((root / "programs" / "mods" / "mod-direct").is_dir())
            self.assertFalse((root / "programs" / "mods" / "~mod-direct").exists())

            self.assertTrue(Installer(reloaded).uninstallMod(restored))
            self.assertEqual(reloaded.modList, {})
            self.assertFalse((root / "programs" / "mods" / "mod-direct").exists())


if __name__ == "__main__":
    unittest.main()
