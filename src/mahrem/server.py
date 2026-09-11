from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from .service import LocalPrivacyService


INSTRUCTIONS = (
    "Mahrem protects local files before AI processing. Never ask the user to paste sensitive text "
    "and never pass raw document content as a tool argument. Accept an absolute local path, call "
    "scan_file or mask_file, and work only with masked_text. To restore a completed masked file, "
    "call restore_file; never open or read the restored output because that would expose it to the model."
)

mcp = MCPServer("mahrem", instructions=INSTRUCTIONS)
service = LocalPrivacyService()


@mcp.tool()
def scan_file(source_path: str, rules_path: str = "") -> dict[str, Any]:
    """Count detectable sensitive data in a local TXT/Markdown file without returning raw values."""
    return service.scan_file(source_path, rules_path)


@mcp.tool()
def mask_file(
    source_path: str,
    rules_path: str = "",
    output_path: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Mask a local file and return only the safe masked text plus an in-memory session id."""
    return service.mask_file(source_path, rules_path, output_path, overwrite)


@mcp.tool()
def restore_file(
    masked_path: str,
    session_id: str,
    output_path: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Restore placeholders into a local output file; never returns the restored clear text."""
    return service.restore_file(masked_path, session_id, output_path, overwrite)


@mcp.tool()
def forget_session(session_id: str) -> dict[str, Any]:
    """Erase one in-memory placeholder mapping after the restored file is created."""
    return service.forget_session(session_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
