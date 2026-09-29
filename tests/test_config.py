import os
import tempfile
import unittest

from src.configuration.config import Configuration


class ConfigurationPathTests(unittest.TestCase):
    def test_get_correct_game_path_accepts_remastered_dx12_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "The Witcher 3")
            exe = os.path.join(root, "bin", "x64_dx12", "witcher3.exe")
            os.makedirs(os.path.join(root, "content"), exist_ok=True)
            os.makedirs(os.path.dirname(exe), exist_ok=True)
            with open(exe, "w", encoding="utf-8") as handle:
                handle.write("x")

            self.assertEqual(Configuration.getCorrectGamePath(exe), exe)
            self.assertEqual(Configuration.getGameRoot(exe), root)

    def test_get_correct_game_path_accepts_game_directory_for_remastered_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "The Witcher 3")
            exe = os.path.join(root, "bin", "x64_dx12", "witcher3.exe")
            os.makedirs(os.path.join(root, "content"), exist_ok=True)
            os.makedirs(os.path.dirname(exe), exist_ok=True)
            with open(exe, "w", encoding="utf-8") as handle:
                handle.write("x")

            self.assertEqual(Configuration.getCorrectGamePath(root), exe)


if __name__ == "__main__":
    unittest.main()
