import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


@unittest.skipUnless(os.name == 'nt', 'Windows setup test')
class WindowsSetupTests(unittest.TestCase):
    def test_connection_preserves_existing_settings_and_backs_up(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/connect-claude.ps1'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / 'claude_desktop_config.json'
            original = {'theme': 'dark', 'mcpServers': {'existing': {'command': 'example'}}}
            config.write_text(json.dumps(original), encoding='utf-8')
            (root / 'claude-baglanti.json').write_text(json.dumps({
                'mcpServers': {'mahrem': {'command': 'C:/Test/mahrem-mcp.exe', 'args': []}}
            }), encoding='utf-8')
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                       '-File', str(script), '-ConfigPath', str(config), '-InstallRoot', str(root)]
            subprocess.run(command, check=True, capture_output=True)
            updated = json.loads(config.read_text(encoding='utf-8'))
            self.assertEqual(updated['theme'], 'dark')
            self.assertEqual(updated['mcpServers']['existing'], original['mcpServers']['existing'])
            self.assertIn('mahrem', updated['mcpServers'])
            backup = list(root.glob('*.mahrem-backup-*'))
            self.assertEqual(len(backup), 1)
            self.assertEqual(json.loads(backup[0].read_text()), original)
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(len(list(root.glob('*.mahrem-backup-*'))), 1)

    def test_invalid_config_is_not_changed(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/connect-claude.ps1'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / 'claude_desktop_config.json'
            config.write_text('{broken', encoding='utf-8')
            (root / 'claude-baglanti.json').write_text('{}', encoding='utf-8')
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                     '-File', str(script), '-ConfigPath', str(config),
                                     '-InstallRoot', str(root)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(config.read_text(), '{broken')
