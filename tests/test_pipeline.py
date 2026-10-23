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
from src.domain.mod import Mod
from src.util.util import atomicWrite

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

    def test_native_packages_from_public_nexus_manifests(self):
        packages = {
            "Witcher Native Bridge": [
                "bin/x64_dx12/WitcherNativeBridge.asi",
                "bin/x64_dx12/dinput8.dll",
                "mods/modNativeBridge/content/scripts/imports.ws",
            ],
            "Darker Nights": ["bin/x64_dx12/tw3-darkernights-remastered.addon64"],
            "Immersive World": [
                "bin/x64_dx12/BeardmosImmersiveWorld.asi",
                "bin/x64_dx12/BeardmosImmersiveWorld.addon64",
                "bin/x64_dx12/BIW_edges_bob.bin",
                "bin/config/r4game/user_config_matrix/pc/BeardmosImmersiveWorld.xml",
                "mods/modBeardmosImmersiveWorld/content/scripts/local/BeardmosImmersiveWorld.ws",
            ],
        }
        for name, files in packages.items():
            with self.subTest(package=name), self.environment() as (root, model, installer):
                package = root / name
                for relative in files:
                    source = package / relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_bytes(b"<synthetic-test-payload/>")
                archive = make_archive(str(package), "zip", package)
                native = [file for file in files if file.startswith("bin/x64_dx12/")]
                count = len(native) + int(any(file.startswith("mods/") for file in files))
                self.assertEqual(installer.installMod(archive), (True, count, 0))
                loaded = Model(ignorelock=True)
                installed = next(iter(loaded.all()))
                self.assertCountEqual(installed.nativefiles, native)
                self.assertIn(native[0], str(installed))
                for relative in files:
                    self.assertEqual((root / "programs" / relative).read_bytes(), b"<synthetic-test-payload/>")
                installed.disable(loaded.all())
                loaded.write()
                loaded = Model(ignorelock=True)
                installed = next(iter(loaded.all()))
                self.assertFalse(installed.enabled)
                for relative in native:
                    self.assertFalse((root / "programs" / relative).exists())
                    self.assertTrue((root / "programs" / (relative + ".disabled")).is_file())
                self.assertEqual(installed.enable(loaded.all()), [])
                self.assertTrue(Installer(loaded).uninstallMod(installed))
                for relative in files:
                    self.assertFalse((root / "programs" / relative).exists())
                self.assertEqual(list(Model(ignorelock=True).all()), [])

    def test_native_resources_keep_layout_and_are_not_parsed_as_game_settings(self):
        with self.environment() as (root, model, installer):
            package = root / "native-resources"
            relatives = [
                "BIN/X64/Plugins/example.asi",
                "BIN/X64/Plugins/settings.xml",
                "BIN/X64/Plugins/settings.txt",
                "BIN/X64/Plugins/content/payload.bin",
                "BIN/X64/Plugins/modNested/content/payload.bin",
                "BIN/X64_DX12/ReShade.ini",
                "BIN/X64_DX12/reshade-shaders/Shaders/example.fx",
                "BIN/X64_DX12/reshade-shaders/Textures/example.png",
            ]
            payload = b"[Example]\nValue=1\n"
            for relative in relatives:
                source = package / "wrapper" / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(payload)
            self.assertEqual(installer.installMod(str(package)), (True, len(relatives), 0))
            installed = next(iter(model.all()))
            self.assertEqual(installed.menus, [])
            self.assertEqual(installed.usersettings, [])
            self.assertEqual(installed.inis, [])
            self.assertEqual(installed.files, [])
            for relative in installed.nativefiles:
                self.assertEqual((root / "programs" / relative).read_bytes(), payload)

    def test_native_updates_preserve_disabled_status_and_track_retained_files(self):
        with self.environment() as (root, model, installer):
            package = root / "native-update"
            source = package / "bin/x64_dx12/example.asi"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"first")
            companion = source.with_suffix(".ini")
            companion.write_bytes(b"configuration")
            self.assertEqual(installer.installMod(str(package)), (True, 2, 0))
            installed = next(iter(model.all()))
            installed.disable(model.all())
            companion.unlink()
            source.write_bytes(b"updated")
            self.assertEqual(installer.installMod(str(package)), (True, 1, 0))
            model.write()
            loaded = Model(ignorelock=True)
            installed = next(iter(loaded.all()))
            self.assertFalse(installed.enabled)
            self.assertCountEqual(installed.nativefiles, ["bin/x64_dx12/example.asi", "bin/x64_dx12/example.ini"])
            target = root / "programs/bin/x64_dx12/example.asi"
            self.assertFalse(target.exists())
            self.assertEqual(target.with_suffix(".asi.disabled").read_bytes(), b"updated")
            self.assertTrue(Installer(loaded).uninstallMod(installed))
            self.assertFalse(target.with_suffix(".asi.disabled").exists())
            self.assertFalse(target.with_suffix(".ini.disabled").exists())

    def test_shared_native_loader_tracks_remaining_enabled_owners(self):
        with self.environment() as (root, model, installer):
            for name in ("first", "second"):
                package = root / name / "bin/x64_dx12"
                package.mkdir(parents=True)
                (package / "dinput8.dll").write_bytes(b"shared loader")
                (package / (name + ".asi")).write_bytes(b"plugin")
                self.assertEqual(installer.installMod(str(root / name)), (True, 2, 0))
            first, second = model.get("first"), model.get("second")
            loader = root / "programs/bin/x64_dx12/dinput8.dll"
            inactive = loader.with_suffix(".dll.disabled")
            first.disable(model.all())
            self.assertTrue(loader.is_file())
            self.assertFalse(inactive.exists())
            second.disable(model.all())
            self.assertTrue(inactive.is_file())
            self.assertFalse(loader.exists())
            first.enable(model.all())
            self.assertTrue(loader.is_file())
            self.assertTrue(installer.uninstallMod(first))
            self.assertTrue(inactive.is_file())
            self.assertFalse(loader.exists())
            second.enable(model.all())
            self.assertTrue(loader.is_file())
            self.assertTrue(installer.uninstallMod(second))
            self.assertFalse(loader.exists())
            self.assertFalse(inactive.exists())

    def test_new_owner_can_activate_a_shared_disabled_loader(self):
        with self.environment() as (root, model, installer):
            for name in ("first", "second"):
                source = root / name / "bin/x64_dx12/dinput8.dll"
                source.parent.mkdir(parents=True)
                source.write_bytes(b"loader")
            self.assertEqual(installer.installMod(str(root / "first")), (True, 1, 0))
            model.get("first").disable(model.all())
            with patch("src.core.installer.MessageOverwrite") as prompt:
                self.assertEqual(installer.installMod(str(root / "second")), (True, 1, 0))
                prompt.assert_not_called()
            loader = root / "programs/bin/x64_dx12/dinput8.dll"
            self.assertTrue(loader.is_file())
            self.assertFalse(loader.with_suffix(".dll.disabled").exists())

    def test_declined_native_overwrite_does_not_acquire_ownership(self):
        with self.environment() as (root, model, installer):
            package = root / "native-declined"
            source = package / "bin/x64_dx12"
            source.mkdir(parents=True)
            target = root / "programs/bin/x64_dx12"
            target.mkdir(parents=True)
            for name in ("dinput8.dll", "ReShade.ini"):
                (source / name).write_bytes(b"new")
                (target / name).write_bytes(b"original")
            (source / "example.asi").write_bytes(b"plugin")
            output: list[str] = []
            installer.output = output.append
            with patch(
                "src.core.installer.MessageOverwrite", return_value=QMessageBox.StandardButton.NoToAll
            ) as prompt:
                self.assertEqual(installer.installMod(str(package)), (True, 1, 1))
                prompt.assert_called_once()
            installed = next(iter(model.all()))
            self.assertEqual(installed.nativefiles, ["bin/x64_dx12/example.asi"])
            self.assertTrue(installer.uninstallMod(installed))
            for name in ("dinput8.dll", "ReShade.ini"):
                self.assertEqual((target / name).read_bytes(), b"original")
                self.assertTrue(any("Skipped" in line and name in line for line in output))

    def test_disabled_native_update_does_not_replace_another_mods_active_loader(self):
        with self.environment() as (root, model, installer):
            for name in ("first", "second"):
                source = root / name / "bin/x64_dx12/dinput8.dll"
                source.parent.mkdir(parents=True)
                source.write_bytes(b"shared")
                self.assertEqual(installer.installMod(str(root / name)), (True, 1, 0))
            model.get("first").disable(model.all())
            (root / "first/bin/x64_dx12/dinput8.dll").write_bytes(b"replacement")
            self.assertEqual(installer.installMod(str(root / "first")), (True, 0, 1))
            self.assertEqual((root / "programs/bin/x64_dx12/dinput8.dll").read_bytes(), b"shared")
            self.assertFalse(model.get("first").enabled)
            self.assertEqual(model.get("first").nativefiles, ["bin/x64_dx12/dinput8.dll"])

    def test_native_variants_are_rejected_before_installing_other_payloads(self):
        with self.environment() as (root, model, installer):
            package = root / "variants"
            for variant in ("A", "B"):
                source = package / variant / "bin/x64_dx12/example.asi"
                source.parent.mkdir(parents=True)
                source.touch()
            (package / "modExample/content").mkdir(parents=True)
            output: list[str] = []
            installer.output = output.append
            self.assertEqual(installer.installMod(str(package)), (False, 0, 0))
            self.assertFalse((root / "programs/mods/modExample").exists())
            self.assertEqual(list(model.all()), [])
            self.assertTrue(any("Multiple variants" in line for line in output))

    def test_loose_or_protected_native_files_report_incomplete_installation(self):
        for with_content in (False, True):
            with self.subTest(with_content=with_content), self.environment() as (root, model, installer):
                package = root / "unsupported-native"
                source = package / "bin/x64_dx12"
                source.mkdir(parents=True)
                files = ["loose.asi", "bin/x64_dx12/witcher3.exe", "bin/x64_dx12/steam_api64.dll"]
                for relative in files:
                    (package / relative).write_bytes(b"not installed")
                if with_content:
                    (package / "modExample/content").mkdir(parents=True)
                output: list[str] = []
                installer.output = output.append
                self.assertEqual(installer.installMod(str(package)), (with_content, int(with_content), 1))
                for relative in files:
                    self.assertFalse((root / "programs" / relative).exists())
                    self.assertTrue(any("Manual installation required" in line and relative in line for line in output))

    def test_failed_native_install_cleans_new_files_and_restores_shared_status(self):
        with self.environment() as (root, model, installer):
            first = root / "first/bin/x64_dx12/dinput8.dll"
            first.parent.mkdir(parents=True)
            first.write_bytes(b"loader")
            installer.installMod(str(root / "first"))
            model.get("first").disable(model.all())
            package = root / "second/bin/x64_dx12"
            package.mkdir(parents=True)
            files = ["dinput8.dll", "new.asi", "fail.addon64"]
            for name in files:
                (package / name).write_bytes(b"loader")

            def write(filename, *args, **kwargs):
                if filename.endswith("fail.addon64"):
                    raise PermissionError("simulated failure")
                return atomicWrite(filename, *args, **kwargs)

            with (
                patch(
                    "src.core.installer.fetchMod",
                    return_value=(
                        Mod(_name="second", nativefiles=["bin/x64_dx12/" + name for name in files]),
                        [],
                        [str(package / name) for name in files],
                    ),
                ),
                patch("src.core.installer.atomicWrite", side_effect=write),
            ):
                self.assertEqual(installer.installMod(str(root / "second")), (False, 0, 0))
            target = root / "programs/bin/x64_dx12"
            self.assertEqual([file.name for file in target.iterdir()], ["dinput8.dll.disabled"])
            self.assertEqual((target / "dinput8.dll.disabled").read_bytes(), b"loader")
            self.assertEqual(list(model.list()), ["first"])

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
