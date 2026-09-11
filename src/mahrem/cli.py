from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .server import main as serve
from .service import LocalPrivacyService


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mahrem", description="Yerel hassas veri maskeleme araci")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Ham degerleri gostermeden hassas veri turlerini say")
    scan.add_argument("source_path")
    scan.add_argument("--rules", default="", dest="rules_path")

    mask = subparsers.add_parser("mask", help="Dosyanin rumuzlu bir kopyasini olustur")
    mask.add_argument("source_path")
    mask.add_argument("--rules", default="", dest="rules_path")
    mask.add_argument("--output", default="", dest="output_path")
    mask.add_argument("--overwrite", action="store_true")

    subparsers.add_parser("serve", help="MCP stdio sunucusunu baslat")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    if args.command == "serve":
        serve()
        return

    service = LocalPrivacyService()
    if args.command == "scan":
        result = service.scan_file(args.source_path, args.rules_path)
    else:
        result = service.mask_file(args.source_path, args.rules_path, args.output_path, args.overwrite)
        result.pop("masked_text", None)
        result["warning"] = "CLI kapaninca bellek ici geri acma tablosu silinir."
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
