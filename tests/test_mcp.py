from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from mcp import Client

from mahrem.server import mcp


class McpContractTests(unittest.TestCase):
    def test_tools_are_exposed_and_scan_result_has_no_raw_value(self) -> None:
        async def exercise() -> None:
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory, "source.txt")
                source.write_text("private@example.com", encoding="utf-8")
                async with Client(mcp) as client:
                    tools = await client.list_tools()
                    self.assertEqual(
                        {tool.name for tool in tools.tools},
                        {"scan_file", "mask_file", "restore_file", "forget_session"},
                    )
                    result = await client.call_tool("scan_file", {"source_path": str(source)})
                    self.assertFalse(result.is_error)
                    self.assertNotIn("private@example.com", json.dumps(result.structured_content))

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
