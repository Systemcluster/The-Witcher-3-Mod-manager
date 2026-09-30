import builtins
import io
import os
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QToolBar, QTreeWidget, QWidget
from watchdog.events import DirModifiedEvent, FileCreatedEvent, FileModifiedEvent, PatternMatchingEventHandler

from main import logStartupFailure
from src.domain.mod import Mod
from src.globals import data
from src.gui.alerts import MessageUnsupportedOSAction
from src.gui.details_dialog import DetailsDialog
from src.gui.main_widget import CustomMainWidget, ModsSettingsEventHandler
from src.gui.tree_widget import CustomTreeWidgetItem
from src.util.util import debounceGui, openFile


class LaunchTests(unittest.TestCase):
    def test_global_access_requires_initialization(self):
        with patch.object(data, "config", None), patch.object(data, "app", None):
            with self.assertRaisesRegex(RuntimeError, "Configuration has not been initialized"):
                data.getConfig()
            with self.assertRaisesRegex(RuntimeError, "Application has not been initialized"):
                data.getApp()
        self.assertIs(data.getConfig(), self.config)

    def test_settings_watcher_dispatches_only_matching_files(self):
        old_callback = Mock()
        old_handler = PatternMatchingEventHandler(
            patterns=["*mods.settings"], ignore_patterns=[], ignore_directories=True
        )
        old_handler.on_modified = lambda event: old_callback(event)

        new_callback = Mock()
        new_handler = ModsSettingsEventHandler(new_callback)

        matching_event = FileModifiedEvent("/settings/mods.settings")
        events = (
            matching_event,
            FileModifiedEvent("/settings/other.ini"),
            DirModifiedEvent("/settings/mods.settings"),
            FileCreatedEvent("/settings/mods.settings"),
        )
        for event in events:
            old_handler.dispatch(event)
            new_handler.dispatch(event)

        self.assertEqual(old_callback.call_args_list, new_callback.call_args_list)
        new_callback.assert_called_once_with(matching_event)

    def test_unsupported_action_alert_preserves_description(self):
        with patch("src.gui.alerts.QMessageBox") as dialog:
            MessageUnsupportedOSAction("Cannot open this folder")
        self.assertIn("Cannot open this folder", dialog.return_value.setText.call_args.args[0])

    def setUp(self):
        self.config = SimpleNamespace(
            gamelaunchcommand=None,
            steam=False,
            gameversion="re",
            gameexe='/games/The Witcher 3/bin/x64_dx12/witcher3.exe',
            graphicsapi='dx12',
            scriptmerger=None,
            mergerlaunchcommand=None,
        )
        self.widget = Mock()
        self.config_patch = patch('src.gui.main_widget.data.config', self.config)
        self.config_patch.start()
        self.addCleanup(self.config_patch.stop)

    def test_remastered_steam_launch_on_all_supported_platforms(self):
        self.config.steam = True
        for platform in ('win32', 'cygwin', 'linux', 'darwin'):
            with (
                self.subTest(platform=platform),
                patch("src.gui.main_widget.platform", platform),
                patch("src.gui.main_widget.openUrl") as open_url,
                patch("src.gui.main_widget.subprocess.Popen") as popen,
            ):
                CustomMainWidget.runTheGame(self.widget)
                open_url.assert_called_once_with('steam://rungameid/292030')
                popen.assert_not_called()
        self.widget.output.assert_not_called()

    def test_windows_executable_launches_preserve_selected_exe_and_cwd(self):
        for gameversion, steam in (("og", False), ("og", True), ("ng", False), ("ng", True), ("re", False)):
            with (
                self.subTest(gameversion=gameversion, steam=steam),
                patch("src.gui.main_widget.platform", "win32"),
                patch("src.gui.main_widget.openUrl") as open_url,
                patch("src.gui.main_widget.subprocess.Popen") as popen,
            ):
                self.config.gameversion = gameversion
                self.config.steam = steam
                CustomMainWidget.runTheGame(self.widget)
                popen.assert_called_once_with([self.config.gameexe], cwd="/games/The Witcher 3/bin/x64_dx12")
                open_url.assert_not_called()
        self.widget.output.assert_not_called()

    def test_windows_button_label_reflects_launch_method(self):
        for gameversion, steam, expected in (
            ("og", False, "dx12"),
            ("og", True, "dx12"),
            ("ng", False, "dx12"),
            ("ng", True, "dx12"),
            ("re", False, "dx12"),
            ("re", True, "Steam"),
        ):
            with self.subTest(gameversion=gameversion, steam=steam), patch("src.gui.main_widget.platform", "win32"):
                self.config.gameversion = gameversion
                self.config.steam = steam
                self.assertEqual(CustomMainWidget.gameLaunchLabel(), expected)

    def test_custom_launch_command_takes_precedence(self):
        self.config.steam = True
        self.config.gamelaunchcommand = 'custom-launch-command'
        with (
            patch("src.gui.main_widget.platform", "win32"),
            patch("src.gui.main_widget.openUrl") as open_url,
            patch("src.gui.main_widget.subprocess.Popen") as popen,
        ):
            CustomMainWidget.runTheGame(self.widget)
            popen.assert_called_once_with('custom-launch-command')
            open_url.assert_not_called()

    def test_custom_launch_command_preserves_quoted_arguments(self):
        self.config.gamelaunchcommand = '"/tools/wine launcher" --bottle "Steam Games"'
        for platform in ('win32', 'linux', 'darwin'):
            with (
                self.subTest(platform=platform),
                patch("src.gui.main_widget.platform", platform),
                patch("src.gui.main_widget.subprocess.Popen") as popen,
            ):
                CustomMainWidget.runTheGame(self.widget)
                expected = (
                    self.config.gamelaunchcommand
                    if platform == "win32"
                    else ["/tools/wine launcher", "--bottle", "Steam Games"]
                )
                popen.assert_called_once_with(expected)
        self.widget.output.assert_not_called()

    def test_cancel_script_merger_selection_does_not_launch(self):
        with patch('src.gui.main_widget.subprocess.Popen') as popen:
            CustomMainWidget.runScriptMerger(self.widget)
            self.widget.changeScriptMergerPath.assert_called_once_with()
            popen.assert_not_called()
            self.widget.output.assert_not_called()

    def test_custom_script_merger_commands_preserve_prefix_and_arguments(self):
        self.config.scriptmerger = "/tools/Script Merger/WitcherScriptMerger.exe"
        for platform in ("linux", "darwin"):
            for command in (
                'WINEPREFIX="/prefix with spaces" wine "/tools/Script Merger/WitcherScriptMerger.exe"',
                'protontricks-launch --appid 292030 "/tools/Script Merger/WitcherScriptMerger.exe"',
            ):
                with (
                    self.subTest(platform=platform, command=command),
                    patch("src.gui.main_widget.platform", platform),
                    patch("src.gui.main_widget.subprocess.Popen") as popen,
                ):
                    self.config.mergerlaunchcommand = command
                    CustomMainWidget.runScriptMerger(self.widget)
                    popen.assert_called_once_with(command, cwd="/tools/Script Merger", shell=True)
        self.widget.output.assert_not_called()

    def test_script_merger_default_launch_routes_remain_unchanged(self):
        self.config.scriptmerger = "/tools/Script Merger/WitcherScriptMerger.exe"
        for platform in ("linux", "darwin", "win32"):
            with (
                self.subTest(platform=platform),
                patch("src.gui.main_widget.platform", platform),
                patch("src.gui.main_widget.subprocess.Popen") as popen,
            ):
                CustomMainWidget.runScriptMerger(self.widget)
                command = [self.config.scriptmerger] if platform == "win32" else ["wine", self.config.scriptmerger]
                popen.assert_called_once_with(command, cwd="/tools/Script Merger")
        self.widget.output.assert_not_called()

    def test_restore_confirmation_explains_side_effects_and_can_be_canceled(self):
        self.widget.getSelectedMods.return_value = ["Example"]
        with (
            patch("src.gui.main_widget.QMessageBox.question", return_value=QMessageBox.StandardButton.No) as confirm,
            patch("src.gui.main_widget.Installer") as installer,
        ):
            CustomMainWidget.reinstallMods(self.widget)
        text = confirm.call_args.args[2]
        self.assertIn("Restore default settings", text)
        self.assertIn("enables disabled mods", text)
        self.assertIn("missing menu XML files are not restored", text)
        installer.assert_not_called()
        self.widget.output.assert_not_called()

    def test_external_executable_launch_preserves_spaces_and_working_directory(self):
        with patch("src.util.util.subprocess.Popen") as popen:
            openFile("/tools/Menu Filelist Updater/updater.exe")
        popen.assert_called_once_with(["/tools/Menu Filelist Updater/updater.exe"], cwd="/tools/Menu Filelist Updater")

    def test_launch_failure_is_reported(self):
        self.config.steam = True
        with patch("src.gui.main_widget.openUrl", side_effect=OSError("launch failed")), patch("sys.stderr"):
            CustomMainWidget.runTheGame(self.widget)
        self.widget.output.assert_called_once()
        self.assertIn('launch failed', self.widget.output.call_args.args[0])


class StartupFailureTests(unittest.TestCase):
    def test_missing_qt_produces_log_and_failure_exit_without_gui_helpers(self):
        original_import = builtins.__import__
        original_temporary_file = tempfile.NamedTemporaryFile
        imported = []

        def without_qt(name, *args, **kwargs):
            imported.append(name)
            if name.startswith("PySide6"):
                raise ImportError("simulated missing Qt DLL")
            return original_import(name, *args, **kwargs)

        for stream in (io.StringIO(), None):
            with self.subTest(console=stream is not None), tempfile.TemporaryDirectory() as directory:
                with (
                    patch("builtins.__import__", side_effect=without_qt),
                    patch("sys.stderr", stream),
                    patch(
                        "tempfile.NamedTemporaryFile",
                        side_effect=lambda **kwargs: original_temporary_file(dir=directory, **kwargs),
                    ),
                    self.assertRaises(SystemExit) as exit_context,
                ):
                    runpy.run_path(str(Path(__file__).parents[1] / "main.py"), run_name="__main__")
                self.assertEqual(exit_context.exception.code, 1)
                logs = list(Path(directory).glob("TW3MM-startup-*.log"))
                self.assertEqual(len(logs), 1)
                self.assertIn("simulated missing Qt DLL", logs[0].read_text())
                self.assertNotIn("src.util.util", imported)
                if stream is not None:
                    self.assertIn("simulated missing Qt DLL", stream.getvalue())
                    self.assertIn(str(logs[0]), stream.getvalue())

    def test_log_failure_keeps_original_diagnostic_on_stderr(self):
        stream = io.StringIO()
        with patch("tempfile.NamedTemporaryFile", side_effect=OSError("disk full")), patch("sys.stderr", stream):
            self.assertIsNone(logStartupFailure("original startup failure"))
        self.assertIn("original startup failure", stream.getvalue())
        self.assertIn("disk full", stream.getvalue())

    def test_logging_failure_without_console_does_not_raise(self):
        with patch("tempfile.NamedTemporaryFile", side_effect=OSError("disk full")), patch("sys.stderr", None):
            self.assertIsNone(logStartupFailure("original startup failure"))


class GuiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict(os.environ, {"QT_QPA_PLATFORM": "offscreen"}):
            cls.app = QApplication.instance() or QApplication([])

    def test_custom_toolbar_action_is_persisted_and_launches_selected_file(self):
        window = QMainWindow()
        self.addCleanup(window.close)
        toolbar = QToolBar(window)
        widget = Mock(mainWindow=window, toolBar=toolbar)
        selected = "/tools/Menu Filelist Updater/updater.exe"
        with patch.object(data, "config") as config, patch("src.gui.main_widget.openFile") as open_file:
            CustomMainWidget.addToToolbar(widget, selected)
            self.assertEqual(len(toolbar.actions()), 1)
            toolbar.actions()[0].trigger()
            open_file.assert_called_once_with(selected)
            config.setOption.assert_called_once_with("TOOLBAR", selected)
        widget.output.assert_not_called()

    def test_details_dialog_keeps_qt_layout_callable(self):
        parent = QWidget()
        self.addCleanup(parent.close)
        dialog = DetailsDialog(parent, Mod())
        self.assertIs(dialog.layout(), dialog.contentLayout)
        dialog.adjustWidth()
        self.assertGreaterEqual(dialog.width(), dialog.minimumWidth())

    def test_tree_item_constructor_supports_existing_forms(self):
        self.assertIsNone(CustomTreeWidgetItem().treeWidget())
        self.assertIsNone(CustomTreeWidgetItem(None).treeWidget())
        self.assertEqual(CustomTreeWidgetItem(["modExample"]).text(0), "modExample")
        tree = QTreeWidget()
        self.addCleanup(tree.close)
        parent = CustomTreeWidgetItem(tree)
        child = CustomTreeWidgetItem(parent)
        self.assertIs(child.parent(), parent)
        self.assertEqual(tree.topLevelItemCount(), 1)

    def test_gui_debounce_uses_latest_arguments_and_discards_return(self):
        class Receiver(QObject):
            def __init__(self):
                super().__init__()
                self.received: list[str] = []

            @debounceGui(0)
            def receive(self, value: str) -> str:
                self.received.append(value)
                return "ignored"

        receiver = Receiver()
        first_timer = receiver.receive("first")
        last_timer = receiver.receive("last")
        self.assertIs(first_timer, last_timer)
        self.app.processEvents()
        self.assertEqual(receiver.received, ["last"])


if __name__ == '__main__':
    unittest.main()
