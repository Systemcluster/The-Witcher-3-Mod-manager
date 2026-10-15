import tempfile
import unittest
from pathlib import Path

from src.core.fetcher import (
    containContentFolder,
    fetchDataIfRelevantFolder,
    fetchMod,
    fetchModFromDirectory,
    isArchive,
    isDataFolder,
    isDlcFolder,
    isModFolder,
    isValidModFolder,
)
from src.domain.mod import Mod

MOCKDATA = Path(__file__).parent / "mockdata/mods"
PACKAGES = {
    "mod-direct": (["mod-direct"], [], ["."]),
    "mod-with-dlc": (["mod-dlc"], ["mod-dlc"], ["mods/mod-dlc", "dlc/mod-dlc"]),
    "mod-with-dlc-same-name": (["modDlc"], ["modDlc"], ["mods/modDlc", "dlc/modDlc"]),
    "mod-with-inputs": (["mod-with-inputs"], [], ["."]),
    "mod-with-inputs-readme": (["mod-with-inputs-readme"], [], ["."]),
    "mod-without-dlc": (["mod-without-dlc"], [], ["."]),
    "normal": (["modNormal"], [], ["modNormal"]),
    "only-dlc": ([], ["dlc__only"], ["dlc__only"]),
    "patch": (["mod0000____CompilationTrigger"], [], [".", "mods/mod0000____CompilationTrigger"]),
    "valid": (
        ["MODTestmod", "modTestmodExtra"],
        ["dlcTestmod"],
        ["MODTestmod", "mods/modTestmodExtra", "dlcTestmod"],
    ),
    "mod-with-split-bins": ([], [], []),
    "weird": ([], [], ["foo 1.2", "foo extras"]),
}
ARCHIVES = {
    "mod-normal.zip": ("mod-normal", "mod-normal/mod-normal"),
    "mod-with-long-name.zip": ("mod" + "0" * 171, "mod-with-long-name/mod" + "0" * 171),
}


class FetcherDetectionTests(unittest.TestCase):
    def test_every_fixture_has_an_explicit_expectation(self):
        self.assertEqual({p.name for p in MOCKDATA.iterdir()}, set(PACKAGES) | set(ARCHIVES))

    def test_exact_detection_for_every_directory_fixture(self):
        for name, (mods, dlcs, directories) in PACKAGES.items():
            with self.subTest(package=name):
                package = MOCKDATA / name
                self.assertFalse(isArchive(str(package)))
                self.assertEqual(isValidModFolder(str(package)), bool(mods or dlcs))
                mod, found, _ = fetchModFromDirectory(str(package))
                self.assertCountEqual(mod.files, mods)
                self.assertCountEqual(mod.dlcs, dlcs)
                self.assertCountEqual([Path(p).relative_to(package).as_posix() for p in found], directories)
                for directory in directories:
                    candidate = package if directory == "." else package / directory
                    detected = Mod()
                    self.assertTrue(containContentFolder(str(candidate)))
                    self.assertTrue(fetchDataIfRelevantFolder(str(candidate), detected))
                    self.assertEqual(
                        detected.files,
                        [candidate.name] if candidate.name in mods and not directory.startswith("dlc/") else [],
                    )
                    self.assertEqual(
                        detected.dlcs,
                        [candidate.name] if candidate.name in dlcs and not directory.startswith("mods/") else [],
                    )
                with tempfile.TemporaryDirectory() as extraction:
                    if mods or dlcs:
                        fetched, found, _ = fetchMod(str(package), extraction)
                        self.assertCountEqual(fetched.files, mods)
                        self.assertCountEqual(fetched.dlcs, dlcs)
                        self.assertCountEqual([Path(p).relative_to(package).as_posix() for p in found], directories)
                    else:
                        with self.assertRaisesRegex(OSError, "Not detected as a valid mod"):
                            fetchMod(str(package), extraction)

    def test_exact_detection_for_every_archive_fixture(self):
        for name, (folder, relative) in ARCHIVES.items():
            with self.subTest(archive=name), tempfile.TemporaryDirectory() as extraction:
                archive = MOCKDATA / name
                self.assertTrue(isArchive(str(archive)))
                mod, directories, config_files = fetchMod(str(archive), extraction)
                self.assertEqual(mod.files, [folder])
                self.assertEqual(mod.dlcs, [])
                self.assertEqual([Path(p).relative_to(extraction).as_posix() for p in directories], [relative])
                self.assertEqual(config_files, [])

    def test_nested_mod_configuration_outside_content_is_still_discovered(self):
        package = MOCKDATA / "valid"
        mod, _, files = fetchModFromDirectory(str(package))
        self.assertCountEqual(mod.menus, ["modTest.xml", "rendering.xml", "modTestConfig.xml"])
        self.assertEqual(mod.inis, ["localization.ini"])
        self.assertCountEqual(
            [Path(p).relative_to(package).as_posix() for p in files],
            [
                "bin/config/base/localization.ini",
                "MODTestmod/modTest.xml",
                "MODTestmod/bin/config/r4game/user_config_matrix/pc/rendering.xml",
                "MODTestmod/bin/config/r4game/user_config_matrix/pc/modTestConfig.xml",
            ],
        )

    def test_content_payload_cannot_make_an_invalid_wrapper_valid(self):
        for content_name in ("content", "CONTENT", "Content"):
            with self.subTest(content=content_name), tempfile.TemporaryDirectory() as temporary:
                package = Path(temporary) / "wrapper"
                (package / content_name / "dlc/EP1/content").mkdir(parents=True)
                (package / content_name / "modNested/content").mkdir(parents=True)
                (package / content_name / "bin/config/base").mkdir(parents=True)
                (package / content_name / "bin/config/base/payload.ini").write_text("payload")
                self.assertFalse(isValidModFolder(str(package)))
                mod, directories, config_files = fetchModFromDirectory(str(package))
                self.assertEqual(mod.files, [])
                self.assertEqual(mod.dlcs, [])
                self.assertEqual(config_files, [])
                self.assertEqual(directories, [package.as_posix()])

    def test_content_payload_cannot_add_extra_packages_or_menus(self):
        for content_name in ("content", "CONTENT", "Content"):
            with self.subTest(content=content_name), tempfile.TemporaryDirectory() as temporary:
                package = Path(temporary) / "modExample"
                content = package / content_name
                (content / "dlc/EP1/content").mkdir(parents=True)
                (content / "modNested/content").mkdir(parents=True)
                (content / "payload.xml").write_text("<payload/>")
                self.assertTrue(isValidModFolder(str(package)))
                mod, directories, config_files = fetchModFromDirectory(str(package))
                self.assertEqual(mod.files, ["modExample"])
                self.assertEqual(mod.dlcs, [])
                self.assertEqual(mod.menus, [])
                self.assertEqual(config_files, [])
                self.assertEqual(directories, [package.as_posix()])

    def test_folder_classification_respects_case_and_immediate_parent(self):
        for name, parent, mod, dlc in (
            ("modExample", "mods", True, False),
            ("MODExample", "wrapper", True, False),
            ("modExample", "dlc", False, True),
            ("MODExample", "DLCs", False, True),
            ("dlcExample", "mods", False, True),
            ("DLCExample", "wrapper", False, True),
            ("ExtraAssets", "DLC", False, True),
            ("ExtraAssets", "mods", False, False),
            ("~modDisabled", "mods", False, False),
            ("content", "modExample", False, False),
        ):
            with self.subTest(name=name, parent=parent):
                self.assertEqual(isDataFolder(name), name.casefold().startswith("mod"))
                self.assertEqual(isModFolder(name, parent), mod)
                self.assertEqual(isDlcFolder(name, parent), dlc)


if __name__ == "__main__":
    unittest.main()
