import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.gui.main_widget import CustomMainWidget


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.config = SimpleNamespace(
            gamelaunchcommand=None, steam=False, gameversion='re',
            gameexe='/games/The Witcher 3/bin/x64_dx12/witcher3.exe',
            graphicsapi='dx12',
            scriptmerger=None, mergerlaunchcommand=None)
        self.widget = Mock()
        self.config_patch = patch('src.gui.main_widget.data.config', self.config)
        self.config_patch.start()
        self.addCleanup(self.config_patch.stop)

    def test_remastered_steam_launch_on_all_supported_platforms(self):
        self.config.steam = True
        for platform in ('win32', 'cygwin', 'linux', 'darwin'):
            with self.subTest(platform=platform), \
                    patch('src.gui.main_widget.platform', platform), \
                    patch('src.gui.main_widget.openUrl') as open_url, \
                    patch('src.gui.main_widget.subprocess.Popen') as popen:
                CustomMainWidget.runTheGame(self.widget)
                open_url.assert_called_once_with('steam://rungameid/292030')
                popen.assert_not_called()
        self.widget.output.assert_not_called()

    def test_windows_executable_launches_preserve_selected_exe_and_cwd(self):
        for gameversion, steam in (('og', False), ('og', True),
                                   ('ng', False), ('ng', True), ('re', False)):
            with self.subTest(gameversion=gameversion, steam=steam), \
                    patch('src.gui.main_widget.platform', 'win32'), \
                    patch('src.gui.main_widget.openUrl') as open_url, \
                    patch('src.gui.main_widget.subprocess.Popen') as popen:
                self.config.gameversion = gameversion
                self.config.steam = steam
                CustomMainWidget.runTheGame(self.widget)
                popen.assert_called_once_with(
                    [self.config.gameexe], cwd='/games/The Witcher 3/bin/x64_dx12')
                open_url.assert_not_called()
        self.widget.output.assert_not_called()

    def test_windows_button_label_reflects_launch_method(self):
        for gameversion, steam, expected in (
                ('og', False, 'dx12'), ('og', True, 'dx12'),
                ('ng', False, 'dx12'), ('ng', True, 'dx12'),
                ('re', False, 'dx12'), ('re', True, 'Steam')):
            with self.subTest(gameversion=gameversion, steam=steam), \
                    patch('src.gui.main_widget.platform', 'win32'):
                self.config.gameversion = gameversion
                self.config.steam = steam
                self.assertEqual(CustomMainWidget.gameLaunchLabel(), expected)

    def test_custom_launch_command_takes_precedence(self):
        self.config.steam = True
        self.config.gamelaunchcommand = 'custom-launch-command'
        with patch('src.gui.main_widget.platform', 'win32'), \
            patch('src.gui.main_widget.openUrl') as open_url, \
                patch('src.gui.main_widget.subprocess.Popen') as popen:
            CustomMainWidget.runTheGame(self.widget)
            popen.assert_called_once_with('custom-launch-command')
            open_url.assert_not_called()

    def test_custom_launch_command_preserves_quoted_arguments(self):
        self.config.gamelaunchcommand = '"/tools/wine launcher" --bottle "Steam Games"'
        for platform in ('win32', 'linux', 'darwin'):
            with self.subTest(platform=platform), \
                    patch('src.gui.main_widget.platform', platform), \
                    patch('src.gui.main_widget.subprocess.Popen') as popen:
                CustomMainWidget.runTheGame(self.widget)
                expected = self.config.gamelaunchcommand if platform == 'win32' else [
                    '/tools/wine launcher', '--bottle', 'Steam Games']
                popen.assert_called_once_with(expected)
        self.widget.output.assert_not_called()

    def test_cancel_script_merger_selection_does_not_launch(self):
        with patch('src.gui.main_widget.subprocess.Popen') as popen:
            CustomMainWidget.runScriptMerger(self.widget)
            self.widget.changeScriptMergerPath.assert_called_once_with()
            popen.assert_not_called()
            self.widget.output.assert_not_called()

    def test_launch_failure_is_reported(self):
        self.config.steam = True
        with patch('src.gui.main_widget.openUrl', side_effect=OSError('launch failed')), \
            patch('sys.stderr'):
            CustomMainWidget.runTheGame(self.widget)
        self.widget.output.assert_called_once()
        self.assertIn('launch failed', self.widget.output.call_args.args[0])


if __name__ == '__main__':
    unittest.main()